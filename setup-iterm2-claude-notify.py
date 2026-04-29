#!/usr/bin/env python3
"""
iTerm2 / Claude Code / Codex 通知配置脚本

功能：
  - 安装统一运行时通知脚本，用于 Claude hooks 通过 iTerm2 notify 提醒
  - 受管迁移旧版 BellTrigger / BEL 配置到 notify-only 模式
  - 受管合并 ~/.claude/settings.json 与 ~/.codex/config.toml
  - 受管关闭 Claude 内建通知通道，避免与即时完成提醒重复
  - 幂等安装、检查、卸载，不覆盖无关用户配置

用法：
  python3 setup-iterm2-claude-notify.py           # 安装
  python3 setup-iterm2-claude-notify.py --remove  # 卸载
  python3 setup-iterm2-claude-notify.py --check   # 检查

要求：
  - macOS + iTerm2
  - 运行前请关闭 iTerm2（或运行后重启 iTerm2 使配置生效）

重要说明：
  - 本脚本会受管开启 iTerm2 的 "Notification Center alerts"
  - 但 iTerm2 的 "Filter Alerts" 细分项目前仍需手动确认
  - 若没有把 Filter Alerts 收敛为仅 "Send escape sequence-generated alerts"
    iTerm2 仍可能对输出、空闲、铃声、会话关闭等事件弹通知
"""

from __future__ import annotations

import json
import plistlib
import re
import shlex
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────

PLIST_PATH = Path.home() / "Library/Preferences/com.googlecode.iterm2.plist"
CLAUDE_SETTINGS_PATH = Path.home() / ".claude/settings.json"
CLAUDE_GLOBAL_CONFIG_PATH = Path.home() / ".claude.json"
CODEX_CONFIG_PATH = Path.home() / ".codex/config.toml"
HELPER_SOURCE_PATH = Path(__file__).with_name("agent-notify-runtime.py")
HELPER_INSTALL_PATH = Path.home() / ".local/bin/agent-notify"
STATE_PATH = Path.home() / ".config/agent-notify/state.json"

# 标记 tag，用于识别旧版受管 trigger，供迁移/卸载使用
SCRIPT_TAG = "[claude-notify]"
MANAGED_TAG = "managed-by=agent-notify"
CODEX_NOTIFY_BEGIN = "# BEGIN agent-notify managed notify"
CODEX_NOTIFY_END = "# END agent-notify managed notify"
CODEX_TUI_BEGIN = "# BEGIN agent-notify managed tui notifications"
CODEX_TUI_END = "# END agent-notify managed tui notifications"
CLAUDE_PREFERRED_NOTIF_DISABLED = "notifications_disabled"
MISSING = object()

CODEX_TUI_DEFAULTS = {
    "notifications": "true",
    "notification_method": json.dumps("osc9"),
    "notification_condition": json.dumps("unfocused"),
}


# ─── 工具函数 ─────────────────────────────────────────────────────────────────


def ensure_parent_dir(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)


def read_json_file(path: Path, default: dict | None = None) -> dict:
    if not path.exists():
        return {} if default is None else default
    try:
        data = json.loads(path.read_text())
    except Exception:
        return {} if default is None else default
    return data if isinstance(data, dict) else ({} if default is None else default)


def write_json_file(path: Path, data: dict) -> None:
    ensure_parent_dir(path)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n")


def load_state() -> dict:
    state = read_json_file(
        STATE_PATH,
        default={"version": 4, "iterm2": {"profiles": {}}, "codex": {}, "claude": {}},
    )
    state["version"] = 4
    return state


def save_state(state: dict) -> None:
    write_json_file(STATE_PATH, state)


def prune_state(state: dict) -> dict:
    if "iterm2" in state:
        state["iterm2"].pop("bells", None)
    if "iterm2" in state and state["iterm2"].get("profiles") == {}:
        state["iterm2"].pop("profiles", None)
    if state.get("iterm2") == {}:
        state.pop("iterm2", None)
    if state.get("codex") == {}:
        state.pop("codex", None)
    if state.get("claude") == {}:
        state.pop("claude", None)
    if state.get("version") is None:
        state.pop("version", None)
    return state


def read_plist() -> dict:
    """读取 iTerm2 plist 配置（支持 binary 和 xml 格式）"""
    if not PLIST_PATH.exists():
        print(f"错误: 找不到 iTerm2 配置文件 {PLIST_PATH}")
        print("请确认已安装 iTerm2 并至少运行过一次。")
        sys.exit(1)

    try:
        with open(PLIST_PATH, "rb") as fh:
            return plistlib.load(fh)
    except Exception:
        subprocess.run(
            ["plutil", "-convert", "xml1", str(PLIST_PATH)],
            check=True,
            capture_output=True,
        )
        with open(PLIST_PATH, "rb") as fh:
            return plistlib.load(fh)


def write_plist(data: dict) -> None:
    with open(PLIST_PATH, "wb") as fh:
        plistlib.dump(data, fh, fmt=plistlib.FMT_XML)


def backup_file(path: Path) -> Path:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = path.with_suffix(f".backup_{timestamp}{path.suffix}")
    shutil.copy2(path, backup_path)
    return backup_path


def is_our_trigger(trigger: dict) -> bool:
    param = trigger.get("parameter", "")
    return SCRIPT_TAG in str(param)


def get_profiles(plist_data: dict) -> list[dict]:
    bookmarks = plist_data.get("New Bookmarks", [])
    if not bookmarks:
        print("警告: 未找到任何 iTerm2 Profile。")
    return bookmarks


def get_profile_id(profile: dict) -> str:
    return str(profile.get("Guid") or profile.get("Name") or "unknown")


def configure_profile_notification_center(profile: dict, state: dict) -> list[str]:
    changes = []
    profiles = state.setdefault("iterm2", {}).setdefault("profiles", {})
    profile_id = get_profile_id(profile)

    saved = profiles.setdefault(profile_id, {})
    if "notification_center_alerts" not in saved:
        saved.update(
            {
                "name": profile.get("Name", "Unknown"),
                "notification_center_alerts": bool(profile.get("BM Growl", False)),
            }
        )

    if not profile.get("BM Growl", False):
        profile["BM Growl"] = True
        changes.append("Notification Center alerts → True")
    return changes


def restore_profile_bell(profile: dict, state: dict) -> list[str]:
    # 仅用于从旧版 bell 安装迁移/卸载时恢复历史值。
    changes = []
    bells = state.setdefault("iterm2", {}).setdefault("bells", {})
    profile_id = get_profile_id(profile)
    saved = bells.get(profile_id)
    if not isinstance(saved, dict):
        return []

    profile["Flashing Bell"] = bool(saved.get("flashing_bell", False))
    profile["Silence Bell"] = bool(saved.get("silence_bell", False))
    bells.pop(profile_id, None)
    changes.append(
        "恢复 Flashing Bell="
        f"{profile['Flashing Bell']}, Silence Bell={profile['Silence Bell']}"
    )
    return changes


def restore_profile_notification_center(profile: dict, state: dict) -> list[str]:
    changes = []
    profiles = state.setdefault("iterm2", {}).setdefault("profiles", {})
    profile_id = get_profile_id(profile)
    saved = profiles.get(profile_id)
    if not isinstance(saved, dict) or "notification_center_alerts" not in saved:
        return changes

    profile["BM Growl"] = bool(saved.get("notification_center_alerts", False))
    profiles.pop(profile_id, None)
    changes.append(f"恢复 Notification Center alerts={profile['BM Growl']}")
    return changes


def record_legacy_bell_state(profile: dict, state: dict) -> None:
    # 仅记录旧版 BellTrigger 方案曾改写过的字段，供迁移/卸载使用。
    bells = state.setdefault("iterm2", {}).setdefault("bells", {})
    profile_id = get_profile_id(profile)
    if profile_id not in bells:
        bells[profile_id] = {
            "name": profile.get("Name", "Unknown"),
            "flashing_bell": bool(profile.get("Flashing Bell", False)),
            "silence_bell": bool(profile.get("Silence Bell", False)),
        }


def install_runtime_helper() -> bool:
    if not HELPER_SOURCE_PATH.exists():
        raise FileNotFoundError(f"找不到运行时通知脚本源文件: {HELPER_SOURCE_PATH}")

    ensure_parent_dir(HELPER_INSTALL_PATH)
    old_content = HELPER_INSTALL_PATH.read_text() if HELPER_INSTALL_PATH.exists() else None
    new_content = HELPER_SOURCE_PATH.read_text()
    HELPER_INSTALL_PATH.write_text(new_content)
    HELPER_INSTALL_PATH.chmod(0o755)
    return old_content != new_content


def remove_runtime_helper() -> bool:
    if not HELPER_INSTALL_PATH.exists():
        return False
    HELPER_INSTALL_PATH.unlink()
    return True


def helper_shell_command(source: str) -> str:
    return (
        f"{shlex.quote(str(HELPER_INSTALL_PATH))} "
        f"--source {shlex.quote(source)} "
        f"--managed-by {shlex.quote(MANAGED_TAG)}"
    )


def build_managed_claude_hooks() -> dict[str, list[dict]]:
    return {
        "Stop": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": helper_shell_command("claude-stop"),
                    }
                ],
            }
        ],
        "UserPromptSubmit": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": helper_shell_command("claude-user-prompt-submit"),
                    }
                ],
            }
        ],
        "Notification": [
            {
                "hooks": [
                    {
                        "type": "command",
                        "command": helper_shell_command("claude-notification"),
                    }
                ],
            },
        ],
        "SessionEnd": [
            {
                "matcher": "",
                "hooks": [
                    {
                        "type": "command",
                        "command": helper_shell_command("claude-session-end"),
                    }
                ],
            }
        ],
    }


def is_managed_claude_hook_group(group: dict) -> bool:
    hooks = group.get("hooks")
    if not isinstance(hooks, list):
        return False
    for hook in hooks:
        if MANAGED_TAG in str(hook.get("command", "")):
            return True
    return False


def validate_claude_preferred_notification_value(data: dict) -> tuple[bool, str | None]:
    value = data.get("preferredNotifChannel", MISSING)
    if value is MISSING:
        return (False, None)
    if not isinstance(value, str):
        raise ValueError(
            f"{CLAUDE_GLOBAL_CONFIG_PATH} 中 preferredNotifChannel 不是字符串，无法自动合并"
        )
    return (True, value)


def ensure_claude_hooks() -> list[str]:
    data = read_json_file(CLAUDE_SETTINGS_PATH, default={})
    hooks = data.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise ValueError(f"{CLAUDE_SETTINGS_PATH} 中 hooks 不是对象，无法自动合并")

    changes = []
    for event_name, managed_groups in build_managed_claude_hooks().items():
        current_groups = hooks.get(event_name, [])
        if not isinstance(current_groups, list):
            raise ValueError(f"{CLAUDE_SETTINGS_PATH} 中 hooks.{event_name} 不是数组")

        filtered = [group for group in current_groups if not is_managed_claude_hook_group(group)]
        hooks[event_name] = filtered + managed_groups
        changes.append(
            f"Claude hooks [{event_name}]: 安装 {len(managed_groups)} 组受管配置"
        )

    write_json_file(CLAUDE_SETTINGS_PATH, data)
    return changes


def ensure_claude_preferred_notification_channel(state: dict) -> list[str]:
    data = read_json_file(CLAUDE_GLOBAL_CONFIG_PATH, default={})
    has_existing, existing_value = validate_claude_preferred_notification_value(data)

    claude_state = state.setdefault("claude", {})
    saved = claude_state.setdefault("preferred_notification_channel", {})
    if "present" not in saved:
        saved["present"] = has_existing
        if has_existing:
            saved["value"] = existing_value

    current_value = existing_value if has_existing else None
    if current_value == CLAUDE_PREFERRED_NOTIF_DISABLED:
        return []

    data["preferredNotifChannel"] = CLAUDE_PREFERRED_NOTIF_DISABLED
    write_json_file(CLAUDE_GLOBAL_CONFIG_PATH, data)

    if has_existing:
        return [
            "Claude preferredNotifChannel: 已从 "
            f"{existing_value} 切换为 {CLAUDE_PREFERRED_NOTIF_DISABLED}"
        ]
    return [
        "Claude preferredNotifChannel: 已设置为 "
        f"{CLAUDE_PREFERRED_NOTIF_DISABLED}"
    ]


def remove_claude_hooks() -> list[str]:
    if not CLAUDE_SETTINGS_PATH.exists():
        return []

    data = read_json_file(CLAUDE_SETTINGS_PATH, default={})
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return [f"跳过 Claude hooks 卸载：{CLAUDE_SETTINGS_PATH} 结构无法识别"]

    changes = []
    for event_name in list(hooks.keys()):
        current_groups = hooks.get(event_name, [])
        if not isinstance(current_groups, list):
            continue
        filtered = [group for group in current_groups if not is_managed_claude_hook_group(group)]
        removed = len(current_groups) - len(filtered)
        if removed > 0:
            if filtered:
                hooks[event_name] = filtered
            else:
                hooks.pop(event_name, None)
            changes.append(f"Claude hooks [{event_name}]: 移除 {removed} 组受管配置")

    if changes:
        if hooks:
            data["hooks"] = hooks
        else:
            data.pop("hooks", None)
        write_json_file(CLAUDE_SETTINGS_PATH, data)
    return changes


def remove_claude_preferred_notification_channel(state: dict) -> list[str]:
    if not CLAUDE_GLOBAL_CONFIG_PATH.exists():
        return []

    data = read_json_file(CLAUDE_GLOBAL_CONFIG_PATH, default={})
    validate_claude_preferred_notification_value(data)

    claude_state = state.setdefault("claude", {})
    saved = claude_state.pop("preferred_notification_channel", None)
    if not isinstance(saved, dict):
        return []

    changes = []
    if saved.get("present"):
        original_value = saved.get("value")
        if not isinstance(original_value, str):
            raise ValueError("受管 state 中 preferredNotifChannel 原值损坏，无法恢复")
        if data.get("preferredNotifChannel") != original_value:
            data["preferredNotifChannel"] = original_value
            changes.append(
                "Claude preferredNotifChannel: 已恢复安装前的原值 "
                f"{original_value}"
            )
    elif "preferredNotifChannel" in data:
        data.pop("preferredNotifChannel", None)
        changes.append("Claude preferredNotifChannel: 已移除受管字段并恢复为未设置")

    if changes:
        write_json_file(CLAUDE_GLOBAL_CONFIG_PATH, data)
    return changes


def find_first_table_index(text: str) -> int | None:
    match = re.search(r"(?m)^\[", text)
    return match.start() if match else None


def strip_managed_codex_block(text: str) -> tuple[str, bool]:
    # 兼容旧版顶层 notify 注入块，供迁移/卸载时清理。
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(CODEX_NOTIFY_BEGIN)}\n.*?^\s*{re.escape(CODEX_NOTIFY_END)}\n?"
    )
    new_text, count = pattern.subn("", text, count=1)
    return new_text, count > 0


def strip_managed_codex_tui_block(text: str) -> tuple[str, bool]:
    pattern = re.compile(
        rf"(?ms)^\s*{re.escape(CODEX_TUI_BEGIN)}\n.*?^\s*{re.escape(CODEX_TUI_END)}\n?"
    )
    new_text, count = pattern.subn("", text, count=1)
    return new_text, count > 0


def find_root_notify_span(text: str) -> tuple[int, int] | None:
    # 兼容迁移旧版顶层 notify，当前主路径已改为 [tui] notifications。
    table_index = find_first_table_index(text)
    root_end = len(text) if table_index is None else table_index
    root_text = text[:root_end]
    match = re.search(r"(?m)^notify\s*=\s*", root_text)
    if not match:
        return None

    start = match.start()
    array_start = root_text.find("[", match.end())
    if array_start == -1:
        return None

    in_string = False
    escaped = False
    depth = 0
    end = None
    for index in range(array_start, len(root_text)):
        char = root_text[index]
        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "[":
            depth += 1
        elif char == "]":
            depth -= 1
            if depth == 0:
                end = index + 1
                break

    if end is None:
        return None

    while end < len(root_text) and root_text[end] in " \t":
        end += 1
    if end < len(root_text) and root_text[end] == "\n":
        end += 1
    return (start, end)


def parse_notify_array(assignment: str) -> list[str] | None:
    right = assignment.split("=", 1)[1].strip()
    try:
        parsed = json.loads(right)
    except Exception:
        return None
    if not isinstance(parsed, list) or not all(isinstance(item, str) for item in parsed):
        return None
    return parsed


def format_toml_string_array(items: list[str]) -> str:
    return "[" + ", ".join(json.dumps(item) for item in items) + "]"


def build_managed_codex_tui_block() -> str:
    lines = [f"{CODEX_TUI_BEGIN}\n", "[tui]\n"]
    for key, value in CODEX_TUI_DEFAULTS.items():
        lines.append(f"{key} = {value}\n")
    lines.append(f"{CODEX_TUI_END}\n")
    return "".join(lines)


def find_table_span(text: str, table_name: str) -> tuple[int, int] | None:
    match = re.search(rf"(?m)^\[{re.escape(table_name)}\]\s*$", text)
    if not match:
        return None

    next_table = re.search(r"(?m)^\[", text[match.end() :])
    if next_table is None:
        return (match.start(), len(text))
    return (match.start(), match.end() + next_table.start())


def find_assignment_span(text: str, key: str) -> tuple[int, int] | None:
    match = re.search(rf"(?m)^{re.escape(key)}\s*=\s*[^\n]*(?:\n|$)", text)
    if not match:
        return None
    return (match.start(), match.end())


def ensure_assignment_in_section(
    section_text: str, key: str, value: str, saved_state: dict
) -> tuple[str, bool]:
    header_end = section_text.find("\n")
    if header_end == -1:
        section_text += "\n"
        header_end = section_text.find("\n")
    prefix = section_text[: header_end + 1]
    body = section_text[header_end + 1 :]
    span = find_assignment_span(body, key)

    if key not in saved_state:
        if span is None:
            saved_state[key] = {"present": False}
        else:
            saved_state[key] = {"present": True, "line": body[span[0] : span[1]]}

    new_line = f"{key} = {value}\n"
    changed = False
    if span is None:
        if body and not body.endswith("\n"):
            body += "\n"
        body += new_line
        changed = True
    else:
        current_line = body[span[0] : span[1]]
        if current_line != new_line:
            body = body[: span[0]] + new_line + body[span[1] :]
            changed = True
    return prefix + body, changed


def restore_assignment_in_section(section_text: str, key: str, saved: dict) -> tuple[str, bool]:
    header_end = section_text.find("\n")
    if header_end == -1:
        section_text += "\n"
        header_end = section_text.find("\n")
    prefix = section_text[: header_end + 1]
    body = section_text[header_end + 1 :]
    span = find_assignment_span(body, key)
    changed = False

    if saved.get("present"):
        original_line = str(saved.get("line", ""))
        if span is None:
            if body and not body.endswith("\n"):
                body += "\n"
            body += original_line
            changed = True
        else:
            current_line = body[span[0] : span[1]]
            if current_line != original_line:
                body = body[: span[0]] + original_line + body[span[1] :]
                changed = True
    elif span is not None:
        body = body[: span[0]] + body[span[1] :]
        changed = True

    return prefix + body, changed


def section_has_notification_defaults(section_text: str) -> bool:
    header_end = section_text.find("\n")
    body = section_text[header_end + 1 :] if header_end != -1 else ""
    for key, value in CODEX_TUI_DEFAULTS.items():
        span = find_assignment_span(body, key)
        if span is None:
            return False
        if body[span[0] : span[1]] != f"{key} = {value}\n":
            return False
    return True


def insert_before_first_table(text: str, block: str) -> str:
    table_index = find_first_table_index(text)
    if table_index is None:
        if text and not text.endswith("\n"):
            text += "\n"
        return text + block

    prefix = text[:table_index]
    suffix = text[table_index:]
    if prefix and not prefix.endswith("\n\n"):
        if prefix.endswith("\n"):
            prefix += "\n"
        else:
            prefix += "\n\n"
    return prefix + block + suffix


def ensure_codex_tui_notifications(state: dict) -> list[str]:
    text = CODEX_CONFIG_PATH.read_text() if CODEX_CONFIG_PATH.exists() else ""
    text, _ = strip_managed_codex_block(text)
    text, _ = strip_managed_codex_tui_block(text)

    codex_state = state.setdefault("codex", {})
    changes = []
    notify_span = find_root_notify_span(text)
    if notify_span is not None:
        original_assignment = text[notify_span[0] : notify_span[1]]
        parsed = parse_notify_array(original_assignment)
        if parsed is None:
            raise ValueError("检测到现有 Codex notify，但格式无法自动解析，已停止合并。")
        if "original_notify" not in codex_state:
            codex_state["original_notify"] = parsed
        text = text[: notify_span[0]] + text[notify_span[1] :]
        changes.append("Codex notify: 已接管原 notify，并迁移到 [tui] 通知")

    table_span = find_table_span(text, "tui")
    if table_span is None:
        text = insert_before_first_table(text, build_managed_codex_tui_block())
        codex_state["tui_mode"] = "managed_block"
        codex_state.pop("tui_fields", None)
        changes.append("Codex [tui]: 已安装受管 OSC 9 通知配置")
    else:
        section = text[table_span[0] : table_span[1]]
        tui_fields = codex_state.setdefault("tui_fields", {})
        changed_any = False
        for key, value in CODEX_TUI_DEFAULTS.items():
            section, changed = ensure_assignment_in_section(section, key, value, tui_fields)
            changed_any = changed_any or changed
        text = text[: table_span[0]] + section + text[table_span[1] :]
        codex_state["tui_mode"] = "existing_table"
        if changed_any:
            changes.append("Codex [tui]: 已更新为受管 OSC 9 通知配置")

    ensure_parent_dir(CODEX_CONFIG_PATH)
    CODEX_CONFIG_PATH.write_text(text)
    return changes


def remove_codex_tui_notifications(state: dict) -> list[str]:
    if not CODEX_CONFIG_PATH.exists():
        return []

    text = CODEX_CONFIG_PATH.read_text()
    changes = []
    text, removed_block = strip_managed_codex_block(text)
    if removed_block:
        changes.append("Codex notify: 已移除旧版受管顶层 notify")
    text, removed_tui_block = strip_managed_codex_tui_block(text)
    if removed_tui_block:
        changes.append("Codex [tui]: 已移除受管 OSC 9 通知配置")

    codex_state = state.setdefault("codex", {})
    tui_mode = codex_state.pop("tui_mode", None)
    tui_fields = codex_state.pop("tui_fields", None)
    if tui_mode == "existing_table" and isinstance(tui_fields, dict):
        table_span = find_table_span(text, "tui")
        if table_span is not None:
            section = text[table_span[0] : table_span[1]]
            changed_any = False
            for key, saved in tui_fields.items():
                if not isinstance(saved, dict):
                    continue
                section, changed = restore_assignment_in_section(section, key, saved)
                changed_any = changed_any or changed
            if changed_any:
                text = text[: table_span[0]] + section + text[table_span[1] :]
                changes.append("Codex [tui]: 已恢复安装前的通知字段")

    original = codex_state.pop("original_notify", None)
    if isinstance(original, list) and original:
        restored = f"notify = {format_toml_string_array(original)}\n"
        text = insert_before_first_table(text, restored)
        changes.append("Codex notify: 已恢复安装前的原始 notify")

    CODEX_CONFIG_PATH.write_text(text)
    return changes


def check_codex_notify_status() -> list[str]:
    if not CODEX_CONFIG_PATH.exists():
        return ["未找到 ~/.codex/config.toml"]
    text = CODEX_CONFIG_PATH.read_text()
    results = []
    if CODEX_NOTIFY_BEGIN in text:
        results.append("检测到旧版受管顶层 notify 配置")

    table_span = find_table_span(text, "tui")
    if table_span is None:
        results.append("未检测到 [tui] 表")
        return results

    section = text[table_span[0] : table_span[1]]
    if CODEX_TUI_BEGIN in text or section_has_notification_defaults(section):
        results.append("已启用受管 OSC 9 通知配置")
    else:
        results.append("未启用受管 OSC 9 通知配置")
    return results


def check_claude_hook_status() -> list[str]:
    if not CLAUDE_SETTINGS_PATH.exists():
        return ["未找到 ~/.claude/settings.json"]

    data = read_json_file(CLAUDE_SETTINGS_PATH, default={})
    hooks = data.get("hooks", {})
    if not isinstance(hooks, dict):
        return ["hooks 结构无法识别"]

    results = []

    # Stop event
    stop_groups = hooks.get("Stop", [])
    stop_managed = [g for g in stop_groups if is_managed_claude_hook_group(g)] if isinstance(stop_groups, list) else []
    results.append(f"Stop: {'已安装' if stop_managed else '未安装'}受管 hook")

    # UserPromptSubmit event
    prompt_submit_groups = hooks.get("UserPromptSubmit", [])
    prompt_submit_managed = (
        [g for g in prompt_submit_groups if is_managed_claude_hook_group(g)]
        if isinstance(prompt_submit_groups, list)
        else []
    )
    results.append(
        "UserPromptSubmit: "
        f"{'已安装' if prompt_submit_managed else '未安装'}受管 hook"
    )

    # Notification event — Notification hooks 不支持 matcher，受管 helper 在运行时区分类型。
    notif_groups = hooks.get("Notification", [])
    if not isinstance(notif_groups, list):
        notif_groups = []
    notification_managed = [g for g in notif_groups if is_managed_claude_hook_group(g)]
    results.append(
        f"Notification: {'已安装' if notification_managed else '未安装'}受管 hook"
    )
    if notification_managed:
        results.append(
            "Notification(idle_prompt): 由受管 helper 在运行时抑制，不再发送第二次提醒"
        )
        results.append(
            "Notification(permission_prompt): 由受管 helper 在运行时放行"
        )

    # SessionEnd event
    session_end_groups = hooks.get("SessionEnd", [])
    session_end_managed = (
        [g for g in session_end_groups if is_managed_claude_hook_group(g)]
        if isinstance(session_end_groups, list)
        else []
    )
    results.append(
        f"SessionEnd: {'已安装' if session_end_managed else '未安装'}受管 hook"
    )

    global_config = read_json_file(CLAUDE_GLOBAL_CONFIG_PATH, default={})
    has_pref, pref_value = validate_claude_preferred_notification_value(global_config)
    if not has_pref:
        results.append(
            "preferredNotifChannel: 未设置 "
            "(Claude 内建通知默认仍可能启用，可能与受管即时通知重复)"
        )
    elif pref_value == CLAUDE_PREFERRED_NOTIF_DISABLED:
        results.append(
            "preferredNotifChannel: notifications_disabled "
            "(已禁用 Claude 内建通知，保留受管即时提醒)"
        )
    else:
        results.append(
            "preferredNotifChannel: "
            f"{pref_value} (⚠ Claude 内建通知仍开启，可能与受管即时通知重复)"
        )

    return results


def install_iterm2_profiles(state: dict) -> None:
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()

    print("💾 备份当前 iTerm2 配置...")
    backup_path = backup_file(PLIST_PATH)
    print(f"   备份已保存到: {backup_path}")

    profiles = get_profiles(plist_data)
    modified_count = 0
    removed_total = 0
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        profile_id = get_profile_id(profile)
        existing_triggers = profile.get("Triggers", [])
        cleaned_triggers = [trigger for trigger in existing_triggers if not is_our_trigger(trigger)]
        removed = len(existing_triggers) - len(cleaned_triggers)
        profile["Triggers"] = cleaned_triggers
        modified_count += 1
        removed_total += removed
        if removed > 0:
            print(f"   Profile [{profile_name}]: 移除 {removed} 条旧版受管 trigger")

        legacy_bells = state.setdefault("iterm2", {}).setdefault("bells", {})
        if removed > 0 and profile_id not in legacy_bells:
            record_legacy_bell_state(profile, state)
        for change in restore_profile_bell(profile, state):
            print(f"   Profile [{profile_name}]: {change}")
        for change in configure_profile_notification_center(profile, state):
            print(f"   Profile [{profile_name}]: {change}")

    print("💾 写入 iTerm2 配置...")
    write_plist(plist_data)
    print(f"已检查 {modified_count} 个 Profile，清理 {removed_total} 条旧版 trigger。")


def remove_iterm2_profiles(state: dict) -> None:
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()

    print("💾 备份当前 iTerm2 配置...")
    backup_path = backup_file(PLIST_PATH)
    print(f"   备份已保存到: {backup_path}")

    profiles = get_profiles(plist_data)
    removed_total = 0
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        existing_triggers = profile.get("Triggers", [])
        cleaned_triggers = [trigger for trigger in existing_triggers if not is_our_trigger(trigger)]
        removed = len(existing_triggers) - len(cleaned_triggers)
        profile["Triggers"] = cleaned_triggers
        removed_total += removed
        if removed > 0:
            print(f"   Profile [{profile_name}]: 移除 {removed} 条旧版受管 trigger")

        for change in restore_profile_bell(profile, state):
            print(f"   Profile [{profile_name}]: {change}")
        for change in restore_profile_notification_center(profile, state):
            print(f"   Profile [{profile_name}]: {change}")

    if removed_total == 0:
        print("   未找到本脚本添加的 trigger。")

    print("💾 写入 iTerm2 配置...")
    write_plist(plist_data)
    print(f"已移除 {removed_total} 条 trigger，并恢复受管 Notification Center alerts。")


def check_iterm2_status() -> None:
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()
    profiles = get_profiles(plist_data)

    found_any = False
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        existing_triggers = profile.get("Triggers", [])
        our_triggers = [trigger for trigger in existing_triggers if is_our_trigger(trigger)]

        if our_triggers:
            found_any = True
            print(f"\n   Profile [{profile_name}]: {len(our_triggers)} 条旧版受管 trigger")
            for trigger in our_triggers:
                status = "启用" if trigger.get("enabled", True) else "禁用"
                print(f"     [{status}] {trigger['action']}: {trigger['regex']}")

    if not found_any:
        print("   未检测到旧版受管 trigger。")

    print("\n🔔 Profile Notification Center alerts:")
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        notify_enabled = profile.get("BM Growl", False)
        print(f"   Profile [{profile_name}]: Notification Center alerts={notify_enabled}")
        if notify_enabled:
            print(
                "     提示: 请在 iTerm2 的 Filter Alerts 中仅保留 "
                "'Send escape sequence-generated alerts'，否则 /exit 等非受管事件也可能弹通知"
            )
        flashing = profile.get("Flashing Bell", False)
        silence = profile.get("Silence Bell", False)
        if flashing or silence:
            print(
                f"     信息: Bell 字段当前值为 Flashing Bell={flashing}, "
                f"Silence Bell={silence}；notify-only 受管路径不依赖它们"
            )


def install_all() -> None:
    state = load_state()

    helper_changed = install_runtime_helper()
    print(
        "🛠️ 运行时通知脚本: "
        + ("已安装/更新" if helper_changed else "已就绪，无需更新")
        + f" → {HELPER_INSTALL_PATH}"
    )

    install_iterm2_profiles(state)

    print("\n⚙️ 安装 Claude hooks...")
    for change in ensure_claude_hooks():
        print(f"   {change}")

    print("\n⚙️ 安装 Claude 通知通道设置...")
    changes = ensure_claude_preferred_notification_channel(state)
    if changes:
        for change in changes:
            print(f"   {change}")
    else:
        print(
            "   Claude preferredNotifChannel: 已为 "
            f"{CLAUDE_PREFERRED_NOTIF_DISABLED}"
        )

    print("\n⚙️ 安装 Codex [tui] 通知...")
    for change in ensure_codex_tui_notifications(state):
        print(f"   {change}")

    save_state(prune_state(state))

    print()
    print("后续步骤:")
    print("  1. 重启 iTerm2 使 Notification Center alerts 配置生效")
    print("  2. 重启 Claude Code / Codex 会话，使 hooks / [tui] 通知生效")
    print("     (旧版会话可能仍按旧 hooks 触发，helper 会自动抑制重复通知)")
    print("  3. 在 iTerm2 -> Profiles -> Terminal -> Filter Alerts 中")
    print("     仅勾选 'Send escape sequence-generated alerts'")
    print("     不要保留 output / idle / bell / close 类 alerts，否则 /exit 仍可能弹通知")
    print(
        "  4. Claude 内建 iTerm2 通知已受管关闭，完成提醒应只走受管即时路径"
    )
    print("  5. 在 Claude Code 或 Codex 中触发一次确认/完成场景测试")
    print("  6. 若在 tmux 中运行，请确保当前 tmux 会话由 iTerm2 启动")
    print()
    print("检查: python3 setup-iterm2-claude-notify.py --check")
    print("卸载: python3 setup-iterm2-claude-notify.py --remove")


def remove_all() -> None:
    state = load_state()

    remove_iterm2_profiles(state)

    print("\n⚙️ 卸载 Claude hooks...")
    changes = remove_claude_hooks()
    if changes:
        for change in changes:
            print(f"   {change}")
    else:
        print("   未找到受管 Claude hooks。")

    print("\n⚙️ 恢复 Claude 通知通道设置...")
    changes = remove_claude_preferred_notification_channel(state)
    if changes:
        for change in changes:
            print(f"   {change}")
    else:
        print("   未找到受管 preferredNotifChannel 状态。")

    print("\n⚙️ 卸载 Codex [tui] 通知...")
    changes = remove_codex_tui_notifications(state)
    if changes:
        for change in changes:
            print(f"   {change}")
    else:
        print("   未找到受管 Codex 通知配置。")

    helper_removed = remove_runtime_helper()
    print(
        "\n🛠️ 运行时通知脚本: "
        + ("已移除" if helper_removed else "未找到，无需移除")
    )

    state = prune_state(state)
    if state in ({}, {"version": 1}, {"version": 2}, {"version": 3}, {"version": 4}):
        if STATE_PATH.exists():
            STATE_PATH.unlink()
    else:
        save_state(state)

    print("\n已完成受管配置卸载。重启 iTerm2 / Claude Code / Codex 生效。")


def check_status() -> None:
    check_iterm2_status()

    print("\n🛠️ 运行时通知脚本:")
    if HELPER_INSTALL_PATH.exists():
        print(f"   已安装: {HELPER_INSTALL_PATH}")
    else:
        print(f"   未安装: {HELPER_INSTALL_PATH}")

    print("\n🤖 Claude hooks:")
    for line in check_claude_hook_status():
        print(f"   {line}")

    print("\n🤖 Codex [tui] 通知:")
    for line in check_codex_notify_status():
        print(f"   {line}")


def main() -> None:
    print("=" * 60)
    print("  iTerm2 / Claude Code / Codex 通知配置工具")
    print("=" * 60)
    print()

    if sys.platform != "darwin":
        print("错误: 此脚本仅支持 macOS。")
        sys.exit(1)

    args = sys.argv[1:]
    try:
        if "--remove" in args or "remove" in args:
            remove_all()
        elif "--check" in args or "check" in args:
            check_status()
        else:
            install_all()
    except Exception as exc:
        print(f"错误: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()
