#!/usr/bin/env python3
"""
Skills 环境配置脚本

功能：
  - 生成 .claude/settings.local.json（权限白名单）
  - 为根目录自定义 skill 在 .claude/skills/ 创建符号链接
  - 交叉校验 SKILL.md 的 allowed-tools 与标准权限列表的一致性

用法：
  python3 setup-skills-env.py

要求：
  - Python 3.6+
  - 无第三方依赖
"""

import json
import os
import re
import sys
from glob import glob
from pathlib import Path

# ─── 配置 ────────────────────────────────────────────────────────────────────

# 项目根目录（脚本所在目录）
PROJECT_ROOT = Path(__file__).resolve().parent

# 标准权限列表（truth）
STANDARD_PERMISSIONS: list[str] = [
    "Bash(openspec --version)",
    "Bash(openspec list:*)",
    "Bash(openspec new:*)",
    "Bash(openspec status:*)",
    "Bash(openspec instructions:*)",
    "Bash(git init:*)",
    "Bash(git remote:*)",
    "Bash(git add:*)",
    "Bash(git commit:*)",
    "Bash(git push:*)",
    "Bash(git worktree:*)",
    "Bash(git merge:*)",
    "Bash(git branch:*)",
    "Bash(git checkout:*)",
    "Bash(git rebase:*)",
    "Bash(git rev-parse:*)",
    "Bash(git log:*)",
    "Bash(git diff:*)",
    "Bash(git status:*)",
    "Bash(git check-ignore:*)",
    "Bash(git show:*)",
    "Bash(mkdir -p /tmp/my-dev-skills-wt)",
    "mcp__web-reader__webReader",
]


# ─── 1. 权限配置 ──────────────────────────────────────────────────────────────


def generate_settings(permissions: list[str]) -> tuple[int, int, Path]:
    """生成或更新 .claude/settings.local.json。

    幂等逻辑：读取已有 settings，合并标准权限，保留用户自定义条目，去重后写入。

    Args:
        permissions: 标准权限列表

    Returns:
        (configured_count, custom_preserved_count, output_path)
    """
    settings_path = PROJECT_ROOT / ".claude" / "settings.local.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    standard_set = set(permissions)
    custom_entries: list[str] = []

    # 读取已有 settings
    if settings_path.exists():
        try:
            with open(settings_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
            existing_allow = existing.get("permissions", {}).get("allow", [])
            for entry in existing_allow:
                if entry not in standard_set:
                    custom_entries.append(entry)
        except (json.JSONDecodeError, KeyError):
            pass  # 文件损坏，从头生成

    # 合并：标准权限 + 用户自定义
    merged = list(permissions) + custom_entries

    settings = {"permissions": {"allow": merged}}

    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")

    return len(permissions), len(custom_entries), settings_path


# ─── 2. Skill 符号链接安装 ──────────────────────────────────────────────────


def scan_custom_skills() -> list[tuple[str, Path]]:
    """扫描根目录 */SKILL.md 文件（排除 .claude/ 和 openspec/）。

    Returns:
        [(skill_name, source_path), ...]
    """
    skills: list[tuple[str, Path]] = []
    exclude_dirs = {".claude", "openspec"}

    for entry in sorted(PROJECT_ROOT.iterdir()):
        if not entry.is_dir():
            continue
        if entry.name in exclude_dirs or entry.name.startswith("."):
            continue
        skill_file = entry / "SKILL.md"
        if skill_file.exists():
            skills.append((entry.name, skill_file))

    return skills


def install_skill_symlinks(
    skills: list[tuple[str, Path]],
) -> tuple[int, int, int]:
    """为每个 skill 创建符号链接。

    Args:
        skills: [(skill_name, source_path), ...]

    Returns:
        (created_count, skipped_count, warning_count)
    """
    created = 0
    skipped = 0
    warnings = 0

    skills_dir = PROJECT_ROOT / ".claude" / "skills"

    for name, source_path in skills:
        link_dir = skills_dir / name
        link_path = link_dir / "SKILL.md"
        # .claude/skills/<name>/ → 需上溯 3 级到项目根
        relative_target = f"../../../{name}/SKILL.md"

        # 检查目标路径是否存在
        if link_path.is_symlink():
            # 读 symlink 目标比较（用 os.readlink 避免 resolve 路径差异）
            current_target = os.readlink(str(link_path))
            if current_target == relative_target:
                skipped += 1
                continue
            else:
                # symlink 目标不一致 → 重建
                link_path.unlink()
        elif link_path.exists():
            # 普通文件 → 跳过并警告
            print(
                f"  Warning: {link_path.relative_to(PROJECT_ROOT)} "
                f"is a regular file, skipping symlink creation"
            )
            warnings += 1
            continue

        # 创建目录和 symlink
        link_dir.mkdir(parents=True, exist_ok=True)
        os.symlink(relative_target, str(link_path))
        created += 1

    return created, skipped, warnings


# ─── 3. SKILL.md 扫描与解析 ──────────────────────────────────────────────────


def parse_skill_frontmatter(
    skill_path: Path,
) -> tuple[list[str], bool]:
    """解析 SKILL.md 的 frontmatter，提取 allowed-tools 和 disable-model-invocation。

    Args:
        skill_path: SKILL.md 文件路径

    Returns:
        (bash_prefixes, is_disabled)
        bash_prefixes: Bash(xxx *) 模式提取的命令前缀列表
        is_disabled: 是否有 disable-model-invocation: true
    """
    content = skill_path.read_text(encoding="utf-8")

    # 提取 frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return [], False

    frontmatter = match.group(1)

    # 检测 disable-model-invocation
    is_disabled = bool(
        re.search(r"disable-model-invocation:\s*true", frontmatter, re.IGNORECASE)
    )

    # 提取 allowed-tools 行
    tools_match = re.search(r"allowed-tools:\s*(.+)", frontmatter)
    if not tools_match:
        return [], is_disabled

    tools_line = tools_match.group(1)

    # 提取 Bash(xxx *) 模式
    bash_prefixes: list[str] = []
    for m in re.finditer(r"Bash\((\S+?)\s*\*?\)", tools_line):
        prefix = m.group(1)
        bash_prefixes.append(prefix)

    return bash_prefixes, is_disabled


# ─── 4. 交叉校验 ──────────────────────────────────────────────────────────────


def extract_standard_bash_prefixes(permissions: list[str]) -> set[str]:
    """从标准权限列表提取 bash 命令前缀集合。

    例如 "Bash(git add:*)" → "git"
    """
    prefixes: set[str] = set()
    for perm in permissions:
        m = re.match(r"Bash\((\S+?)[\s:]", perm)
        if m:
            prefixes.add(m.group(1))
    return prefixes


def check_skill_consistency(
    skills: list[tuple[str, Path]],
    standard_permissions: list[str],
) -> int:
    """交叉校验 SKILL.md 与标准权限列表的一致性。

    Returns:
        warning_count
    """
    warnings = 0
    standard_prefixes = extract_standard_bash_prefixes(standard_permissions)

    for name, source_path in skills:
        bash_prefixes, is_disabled = parse_skill_frontmatter(source_path)

        # 4.1 缺失权限警告
        for prefix in bash_prefixes:
            if prefix not in standard_prefixes:
                print(
                    f"  Warning: skill '{name}' uses Bash({prefix} *) "
                    f"but no matching permission in standard list"
                )
                warnings += 1

        # 4.2 无 guardrails 警告
        if not bash_prefixes and not is_disabled:
            print(
                f"  Warning: skill '{name}' has no allowed-tools and no "
                f"disable-model-invocation — may be auto-invoked by model"
            )
            warnings += 1

    return warnings


# ─── 5. 主入口 ────────────────────────────────────────────────────────────────


def main() -> None:
    print("=" * 60)
    print("  Skills 环境配置工具")
    print("=" * 60)
    print()

    # Step 1: 安装 skill 符号链接
    print("📦 扫描自定义 skills...")
    skills = scan_custom_skills()
    print(f"   发现 {len(skills)} 个自定义 skill: {[s[0] for s in skills]}")

    print("🔗 安装符号链接...")
    created, skipped, link_warnings = install_skill_symlinks(skills)
    print(
        f"   Skills installed: {created} created, {skipped} already linked"
        + (f", {link_warnings} warning(s)" if link_warnings else "")
    )

    # Step 2: 一致性校验
    print()
    print("🔍 交叉校验 allowed-tools...")
    check_warnings = check_skill_consistency(skills, STANDARD_PERMISSIONS)

    # Step 3: 生成 settings
    print()
    print("⚙️  生成权限配置...")
    configured, custom_preserved, settings_path = generate_settings(
        STANDARD_PERMISSIONS
    )
    print(
        f"   Done. {configured} permissions configured, "
        f"{custom_preserved} custom entries preserved. "
        f"Written to {settings_path.relative_to(PROJECT_ROOT)}"
    )

    # Step 4: 摘要
    print()
    print("=" * 60)
    print("  执行摘要")
    print("=" * 60)
    print(f"  符号链接: {created} created, {skipped} linked, {link_warnings} warning(s)")
    print(f"  权限配置: {configured} standard, {custom_preserved} custom preserved")
    total_warnings = link_warnings + check_warnings
    print(f"  校验警告: {total_warnings}")
    if total_warnings == 0:
        print("  ✓ 一切正常")
    print()


if __name__ == "__main__":
    main()
