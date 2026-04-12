#!/usr/bin/env python3
"""
iTerm2 Claude Code 通知配置脚本

功能：
  - 为 iTerm2 所有 Profile 添加 Trigger，当 Claude Code 等待用户确认时：
    1. 发送 macOS 通知（点击可精确定位到对应 Tab）
    2. Tab 标签闪烁高亮 + 闹钟图标
  - 自动配置 Profile: 开启 Flashing Bell（tab 闪烁）、静音 Bell（无声音）

用法：
  python3 setup-iterm2-claude-notify.py          # 安装 triggers
  python3 setup-iterm2-claude-notify.py --remove  # 卸载 triggers
  python3 setup-iterm2-claude-notify.py --check   # 检查当前状态

要求：
  - macOS + iTerm2
  - 运行前请关闭 iTerm2（或运行后重启 iTerm2 使配置生效）
"""

import plistlib
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────

PLIST_PATH = Path.home() / "Library/Preferences/com.googlecode.iterm2.plist"

# 标记 tag，用于识别本脚本添加的 trigger（方便卸载）
SCRIPT_TAG = "[claude-notify]"

# Claude Code 等待确认时的终端输出匹配模式
TRIGGER_PATTERNS = [
    {
        "regex": r"(Allow once|Allow always|Deny)",
        "name": "Claude Code 权限确认",
    },
    {
        "regex": r"Do you want to proceed",
        "name": "Claude Code 操作确认",
    },
    {
        "regex": r"Press Enter to continue|Y/n|y/N",
        "name": "CLI 交互确认",
    },
]

# iTerm2 Trigger Action 常量
# 参考: https://iterm2.com/documentation-triggers.html
ACTION_POST_NOTIFICATION = "PostNotificationTrigger"
ACTION_RING_BELL = "BellTrigger"


# ─── 工具函数 ─────────────────────────────────────────────────────────────────


def read_plist() -> dict:
    """读取 iTerm2 plist 配置（支持 binary 和 xml 格式）"""
    if not PLIST_PATH.exists():
        print(f"错误: 找不到 iTerm2 配置文件 {PLIST_PATH}")
        print("请确认已安装 iTerm2 并至少运行过一次。")
        sys.exit(1)

    # iTerm2 可能使用 binary plist，先转换为 xml
    try:
        with open(PLIST_PATH, "rb") as f:
            return plistlib.load(f)
    except Exception:
        # 尝试用 plutil 转换
        subprocess.run(
            ["plutil", "-convert", "xml1", str(PLIST_PATH)],
            check=True,
            capture_output=True,
        )
        with open(PLIST_PATH, "rb") as f:
            return plistlib.load(f)


def write_plist(data: dict) -> None:
    """写入 iTerm2 plist 配置"""
    with open(PLIST_PATH, "wb") as f:
        plistlib.dump(data, f, fmt=plistlib.FMT_XML)


def backup_plist() -> Path:
    """备份当前配置"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = PLIST_PATH.with_suffix(f".backup_{timestamp}.plist")
    shutil.copy2(PLIST_PATH, backup_path)
    return backup_path


def build_triggers() -> list[dict]:
    """构建要添加的 trigger 列表"""
    triggers = []
    for pattern in TRIGGER_PATTERNS:
        # 通知 trigger — 点击可定位到对应 Tab
        triggers.append(
            {
                "action": ACTION_POST_NOTIFICATION,
                "regex": pattern["regex"],
                "parameter": f"{SCRIPT_TAG} {pattern['name']}",
                "partial": True,  # 不要求整行匹配
                "enabled": True,
            }
        )
        # 响铃 trigger — Tab 标签闪烁高亮 + 闹钟图标
        triggers.append(
            {
                "action": ACTION_RING_BELL,
                "regex": pattern["regex"],
                "parameter": f"{SCRIPT_TAG}",
                "partial": True,
                "enabled": True,
            }
        )
    return triggers


def is_our_trigger(trigger: dict) -> bool:
    """判断 trigger 是否由本脚本创建"""
    param = trigger.get("parameter", "")
    return SCRIPT_TAG in str(param)


def get_profiles(plist_data: dict) -> list[dict]:
    """获取所有 Profile"""
    bookmarks = plist_data.get("New Bookmarks", [])
    if not bookmarks:
        print("警告: 未找到任何 iTerm2 Profile，将创建默认配置。")
    return bookmarks


# ─── 主操作 ────────────────────────────────────────────────────────────────────


def configure_profile_bell(profile: dict) -> list[str]:
    """配置 Profile 的 Bell 行为: 闪烁高亮 + 静音"""
    changes = []
    if not profile.get("Flashing Bell", False):
        profile["Flashing Bell"] = True
        changes.append("Flashing Bell → True")
    if not profile.get("Silence Bell", False):
        profile["Silence Bell"] = True
        changes.append("Silence Bell → True")
    return changes


def install_triggers() -> None:
    """安装 triggers 到所有 Profile"""
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()

    print("💾 备份当前配置...")
    backup_path = backup_plist()
    print(f"   备份已保存到: {backup_path}")

    profiles = get_profiles(plist_data)
    new_triggers = build_triggers()

    modified_count = 0
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        existing_triggers = profile.get("Triggers", [])

        # 移除旧的本脚本 trigger（避免重复）
        cleaned_triggers = [t for t in existing_triggers if not is_our_trigger(t)]

        # 追加新 trigger
        updated_triggers = cleaned_triggers + new_triggers
        profile["Triggers"] = updated_triggers
        modified_count += 1
        added = len(updated_triggers) - len(cleaned_triggers)
        print(f"   Profile [{profile_name}]: 添加 {added} 条 trigger")

        # 配置 Bell 行为: 闪烁高亮 + 静音
        bell_changes = configure_profile_bell(profile)
        for change in bell_changes:
            print(f"   Profile [{profile_name}]: {change}")

    print("💾 写入配置...")
    write_plist(plist_data)

    print()
    print(f"已为 {modified_count} 个 Profile 安装 {len(new_triggers)} 条 trigger。")
    print()
    print("后续步骤:")
    print("  1. 重启 iTerm2 使配置生效")
    print("  2. 确认 macOS 通知权限: 系统设置 → 通知 → iTerm2 → 开启")
    print("  3. 确认关闭勿扰模式: 控制中心 → 专注模式 → 关闭")
    print("  4. 在 Claude Code 中触发一次权限请求来测试")
    print()
    print("卸载: python3 setup-iterm2-claude-notify.py --remove")


def remove_triggers() -> None:
    """从所有 Profile 移除本脚本添加的 triggers"""
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()

    profiles = get_profiles(plist_data)
    removed_total = 0

    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        existing_triggers = profile.get("Triggers", [])
        before_count = len(existing_triggers)

        cleaned_triggers = [t for t in existing_triggers if not is_our_trigger(t)]
        profile["Triggers"] = cleaned_triggers

        removed = before_count - len(cleaned_triggers)
        removed_total += removed
        if removed > 0:
            print(f"   Profile [{profile_name}]: 移除 {removed} 条 trigger")

    # 恢复 Bell 设置
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        profile["Flashing Bell"] = False
        profile["Silence Bell"] = False
        print(f"   Profile [{profile_name}]: 恢复 Flashing Bell=False, Silence Bell=False")

    if removed_total == 0:
        print("   未找到本脚本添加的 trigger。")

    print("💾 写入配置...")
    write_plist(plist_data)
    print(f"已移除 {removed_total} 条 trigger，已恢复 Bell 设置。重启 iTerm2 生效。")


def check_status() -> None:
    """检查当前 trigger 安装状态"""
    print("📋 读取 iTerm2 配置...")
    plist_data = read_plist()

    profiles = get_profiles(plist_data)
    found_any = False

    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        existing_triggers = profile.get("Triggers", [])
        our_triggers = [t for t in existing_triggers if is_our_trigger(t)]

        if our_triggers:
            found_any = True
            print(f"\n   Profile [{profile_name}]: {len(our_triggers)} 条 claude-notify trigger")
            for t in our_triggers:
                status = "启用" if t.get("enabled", True) else "禁用"
                print(f"     [{status}] {t['action']}: {t['regex']}")

    if not found_any:
        print("   未安装。运行 python3 setup-iterm2-claude-notify.py 安装。")
        return

    print("\n🔔 Profile Bell 设置:")
    for profile in profiles:
        profile_name = profile.get("Name", "Unknown")
        flashing = profile.get("Flashing Bell", False)
        silence = profile.get("Silence Bell", False)
        print(f"   Profile [{profile_name}]: Flashing Bell={flashing}, Silence Bell={silence}")


def check_notification_permission() -> None:
    """检查 macOS 通知权限（提示性检查）"""
    print("\n🔔 通知权限检查:")
    # 发送一条测试通知
    result = subprocess.run(
        [
            "osascript",
            "-e",
            'display notification "iTerm2 Claude 通知测试" with title "配置成功"',
        ],
        capture_output=True,
    )
    if result.returncode == 0:
        print("   已发送测试通知（通过 osascript），请确认是否收到。")
        print("   注意: 实际 Trigger 通知由 iTerm2 发出，与此测试通道不同。")
        print("   请确保: 系统设置 → 通知 → iTerm2 → 开启")
    else:
        print("   测试通知发送失败（不影响 iTerm2 Trigger 通知）。")
        print("   请确保: 系统设置 → 通知 → iTerm2 → 开启")


# ─── 入口 ──────────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("  iTerm2 Claude Code 通知配置工具")
    print("=" * 60)
    print()

    if sys.platform != "darwin":
        print("错误: 此脚本仅支持 macOS。")
        sys.exit(1)

    args = sys.argv[1:]

    if "--remove" in args or "remove" in args:
        remove_triggers()
    elif "--check" in args or "check" in args:
        check_status()
    else:
        install_triggers()
        check_notification_permission()


if __name__ == "__main__":
    main()
