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
import json
import os
import sys
from pathlib import Path


TTY_TARGET = Path("/dev/tty")


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
        title, message = build_claude_stop_message(payload)
    elif args.source == "claude-notification":
        payload = read_stdin_payload()
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
