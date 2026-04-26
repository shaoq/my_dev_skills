#!/usr/bin/env python3
"""
Claude Code / Codex 运行时通知脚本。

来源：
  - Claude hooks: 从 stdin 读取 JSON
  - Codex notify: 从最后一个命令行参数读取 JSON（仅兼容旧版受管配置）

动作：
  - 向当前终端发送 iTerm2 OSC 9 通知
  - 在 tmux 中自动包裹 passthrough，以便外层 iTerm2 仍能收到通知
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from pathlib import Path


TTY_TARGET = Path("/dev/tty")
DEDUP_STATE_PATH = Path.home() / ".config/agent-notify/claude-dedup.json"
DEDUP_WINDOW_SECONDS = 10  # Stop 短窗口去重
LEGACY_IDLE_SUPPRESS_SECONDS = 120  # 遗留 idle_prompt 抑制窗口


def truncate_text(value: str, limit: int = 120) -> str:
    text = " ".join(str(value).split())
    if len(text) <= limit:
        return text
    return text[: limit - 1] + "…"


def load_json_payload(raw: str | None) -> dict:
    if not raw:
        return {}
    try:
        data = json.loads(raw)
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def read_stdin_payload() -> dict:
    if sys.stdin.isatty():
        return {}
    try:
        raw = sys.stdin.read().strip()
    except OSError:
        return {}
    return load_json_payload(raw)


def build_claude_stop_message(_: dict) -> tuple[str, str]:
    return ("Claude Code 已完成当前任务", "等待你的下一条指令。")


def build_claude_notification_message(payload: dict) -> tuple[str, str]:
    notification_type = str(payload.get("notification_type", "")).strip()
    title = str(payload.get("title", "")).strip()
    message = str(payload.get("message", "")).strip()

    if notification_type == "permission_prompt":
        return (
            title or "Claude Code 需要确认",
            truncate_text(message or "检测到权限或确认提示。"),
        )
    if notification_type == "idle_prompt":
        return (
            title or "Claude Code 正在等待输入",
            truncate_text(message or "Claude Code 已空闲，等待你的下一条指令。"),
        )
    return (
        title or "Claude Code 通知",
        truncate_text(message or "收到 Claude Code 通知。"),
    )


def build_codex_message(payload: dict) -> tuple[str, str]:
    # 兼容旧版顶层 notify 路径；当前主路径已迁移到 Codex TUI notifications。
    preview = ""
    for key in ("last-assistant-message", "last_assistant_message", "message"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            preview = value.strip()
            break

    if preview:
        return ("Codex 已完成当前任务", truncate_text(preview))
    return ("Codex 已完成当前任务", "等待你的下一条指令。")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Agent runtime notifier")
    parser.add_argument("--source", required=True)
    parser.add_argument("--managed-by", default="")
    parser.add_argument("payload", nargs="?")
    return parser.parse_args()


# ─── Claude 去重 ──────────────────────────────────────────────────────────────


def _load_dedup_state() -> dict:
    if not DEDUP_STATE_PATH.exists():
        return {}
    try:
        data = json.loads(DEDUP_STATE_PATH.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def _save_dedup_state(state: dict) -> None:
    DEDUP_STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    DEDUP_STATE_PATH.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n")


def _extract_session_id(payload: dict) -> str | None:
    """从 Claude hook payload 提取 session_id。"""
    sid = payload.get("session_id") or payload.get("sessionId")
    return str(sid).strip() if sid else None


def _compute_fingerprint(payload: dict) -> str:
    """构造 completion fingerprint，用于识别重复投递。"""
    parts = []
    for key in ("session_id", "sessionId", "stop_hook_event_id"):
        val = payload.get(key)
        if val:
            parts.append(str(val))
    if not parts:
        # 退化：用消息摘要
        raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
        return hashlib.md5(raw.encode()).hexdigest()
    return hashlib.md5("|".join(parts).encode()).hexdigest()


def _prune_sessions(state: dict, max_age: float = 600.0) -> None:
    """清理过期的 session 条目（超过 max_age 秒的）。"""
    now = time.time()
    sessions = state.get("sessions", {})
    expired = [sid for sid, info in sessions.items()
               if now - info.get("last_completion_at", 0) > max_age]
    for sid in expired:
        sessions.pop(sid, None)


def should_suppress_stop(payload: dict) -> bool:
    """检查是否应抑制重复 Stop 通知。返回 True 表示应抑制。"""
    session_id = _extract_session_id(payload)
    fingerprint = _compute_fingerprint(payload)
    state = _load_dedup_state()
    _prune_sessions(state)

    if session_id:
        sessions = state.setdefault("sessions", {})
        info = sessions.get(session_id, {})
        prev_fp = info.get("last_completion_fingerprint")
        prev_at = info.get("last_completion_at", 0)

        if prev_fp == fingerprint and (time.time() - prev_at) < DEDUP_WINDOW_SECONDS:
            return True  # 重复投递，抑制
    else:
        # 无 session_id：退化为全局短窗口去重
        last_global = state.get("_global_last_stop_at", 0)
        if (time.time() - last_global) < DEDUP_WINDOW_SECONDS:
            return True

    # 不抑制 — 记录并发通知
    now = time.time()
    if session_id:
        sessions = state.setdefault("sessions", {})
        sessions[session_id] = {
            "last_completion_at": now,
            "last_completion_fingerprint": fingerprint,
            "last_event_type": "stop",
        }
    else:
        state["_global_last_stop_at"] = now

    _save_dedup_state(state)
    return False


def should_suppress_idle(payload: dict) -> bool:
    """检查是否应抑制遗留 idle_prompt。返回 True 表示应抑制。"""
    session_id = _extract_session_id(payload)
    state = _load_dedup_state()

    if session_id:
        info = state.get("sessions", {}).get(session_id, {})
        last_at = info.get("last_completion_at", 0)
        if last_at and (time.time() - last_at) < LEGACY_IDLE_SUPPRESS_SECONDS:
            return True
    else:
        # 保守策略：仅当最近有全局完成通知时才抑制
        last_global = state.get("_global_last_stop_at", 0)
        if last_global and (time.time() - last_global) < DEDUP_WINDOW_SECONDS:
            return True

    return False


def escape_osc9_message(message: str) -> str:
    sanitized = []
    for char in message:
        if char in ("\x1b", "\x07"):
            continue
        if ord(char) < 32 and char not in ("\t", " "):
            continue
        sanitized.append(char)
    return "".join(sanitized)


def build_notification_sequence(title: str, message: str) -> str:
    combined = title.strip()
    if message.strip():
        combined = f"{combined}: {message.strip()}"
    payload = escape_osc9_message(truncate_text(combined, limit=200))

    if os.environ.get("TMUX"):
        escaped_payload = payload.replace("\x1b", "\x1b\x1b")
        return f"\x1bPtmux;\x1b\x1b]9;{escaped_payload}\x07\x1b\\"
    return f"\x1b]9;{payload}\x07"


def emit_iterm2_notification(title: str, message: str) -> None:
    sequence = build_notification_sequence(title, message)
    for target in (TTY_TARGET,):
        try:
            with target.open("w") as fh:
                fh.write(sequence)
                fh.flush()
                return
        except OSError:
            continue

    try:
        sys.stderr.write(sequence)
        sys.stderr.flush()
    except OSError:
        pass


def main() -> int:
    args = parse_args()

    if args.source == "claude-stop":
        payload = read_stdin_payload()
        if should_suppress_stop(payload):
            return 0
        title, message = build_claude_stop_message(payload)
    elif args.source == "claude-notification":
        payload = read_stdin_payload()
        notification_type = str(payload.get("notification_type", "")).strip()
        # permission_prompt 始终放行，不参与去重
        if notification_type == "idle_prompt" and should_suppress_idle(payload):
            return 0
        title, message = build_claude_notification_message(payload)
    elif args.source == "codex-notify":
        payload = load_json_payload(args.payload)
        title, message = build_codex_message(payload)
    else:
        print(f"未知来源: {args.source}", file=sys.stderr)
        return 1

    emit_iterm2_notification(title, message)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
