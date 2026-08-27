#!/usr/bin/env python3
"""
Skills 全局环境配置脚本

功能：
  - 在 ~/.claude/skills/ 和 ~/.codex/skills/ 创建符号链接（全局安装）
  - 合并权限白名单到 ~/.claude/settings.json（全局配置）
  - 交叉校验 SKILL.md 的 allowed-tools 与标准权限列表的一致性
  - 支持 --uninstall 卸载全局安装的符号链接和权限

用法：
  python3 setup-skills-env.py              # 安装
  python3 setup-skills-env.py --uninstall  # 卸载

要求：
  - Python 3.6+
  - 无第三方依赖
"""

import json
import os
import re
import sys
from pathlib import Path
from typing import NamedTuple, Optional

# ─── 配置 ────────────────────────────────────────────────────────────────────

# 项目根目录（脚本所在目录，自动适配 clone 路径）
PROJECT_ROOT = Path(__file__).resolve().parent

# 用户全局 .claude 目录
HOME_CLAUDE_DIR = Path.home() / ".claude"

# 用户全局 .codex 目录（仅管理 skills 链接，不写 Codex 配置）
HOME_CODEX_DIR = Path.home() / ".codex"

# 全局 settings.json 路径
GLOBAL_SETTINGS_PATH = HOME_CLAUDE_DIR / "settings.json"

# 标准权限列表（truth）
STANDARD_PERMISSIONS: list[str] = [
    "Bash(openspec --version)",
    "Bash(openspec list:*)",
    "Bash(openspec new:*)",
    "Bash(openspec status:*)",
    "Bash(openspec instructions:*)",
    "Bash(openspec validate:*)",
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


# ─── 1. Skill 扫描 ──────────────────────────────────────────────────────────


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


# ─── 2. 全局符号链接安装/卸载 ────────────────────────────────────────────────


class LinkInstallResult(NamedTuple):
    created: int
    skipped: int
    replaced: int
    warnings: int


class LinkUninstallResult(NamedTuple):
    removed: int
    not_found: int
    warnings: int


def runtime_skill_dirs() -> tuple[tuple[str, Path], ...]:
    """返回受管运行时及其 skill 目录。"""
    return (
        ("Claude Code", HOME_CLAUDE_DIR / "skills"),
        ("Codex", HOME_CODEX_DIR / "skills"),
    )


def _link_resolves_to(link_path: Path, target: Path) -> bool:
    """判断符号链接解析后是否精确指向目标目录。"""
    try:
        return link_path.resolve(strict=False) == target.resolve(strict=False)
    except OSError:
        return False


def install_skill_symlinks(
    skills: list[tuple[str, Path]],
    skills_dir: Path,
) -> LinkInstallResult:
    """在指定运行时目录为每个 skill 创建目录级符号链接（绝对路径）。

    <skills_dir>/<name> → /abs/path/to/my_dev_skills/<name>

    Args:
        skills: [(skill_name, source_path), ...]

    Returns:
        LinkInstallResult
    """
    created = 0
    skipped = 0
    replaced = 0
    warnings = 0

    for name, source_path in skills:
        link_path = skills_dir / name
        source_dir = source_path.parent.resolve()
        absolute_target = str(source_dir)
        was_replaced = False

        if link_path.is_symlink():
            if _link_resolves_to(link_path, source_dir):
                skipped += 1
                continue
            try:
                link_path.unlink()
                was_replaced = True
            except OSError as exc:
                print(f"  Warning: cannot replace {link_path}: {exc}")
                warnings += 1
                continue
        elif link_path.exists():
            print(
                f"  Warning: {link_path} exists as a regular directory/file, "
                f"skipping symlink creation"
            )
            warnings += 1
            continue

        try:
            skills_dir.mkdir(parents=True, exist_ok=True)
            os.symlink(absolute_target, str(link_path))
            if was_replaced:
                replaced += 1
            else:
                created += 1
        except OSError as exc:
            print(f"  Warning: cannot create {link_path}: {exc}")
            warnings += 1

    return LinkInstallResult(created, skipped, replaced, warnings)


def uninstall_skill_symlinks(
    skills: list[tuple[str, Path]],
    skills_dir: Path,
) -> LinkUninstallResult:
    """移除指定运行时目录中由本脚本管理的目录级符号链接。

    Returns:
        LinkUninstallResult
    """
    removed = 0
    not_found = 0
    warnings = 0

    for name, source_path in skills:
        link_path = skills_dir / name
        source_dir = source_path.parent.resolve()

        if link_path.is_symlink():
            current_target = os.readlink(str(link_path))
            if _link_resolves_to(link_path, source_dir):
                link_path.unlink()
                removed += 1
            else:
                print(
                    f"  Warning: {link_path} points to {current_target}, "
                    f"not ours — skipping"
                )
                warnings += 1
        elif link_path.exists():
            print(
                f"  Warning: {link_path} is a regular directory/file, "
                f"not our symlink — skipping"
            )
            warnings += 1
        else:
            not_found += 1

    return LinkUninstallResult(removed, not_found, warnings)


def install_runtime_skill_links(
    skills: list[tuple[str, Path]],
    runtime_dirs: Optional[tuple[tuple[str, Path], ...]] = None,
) -> dict[str, LinkInstallResult]:
    """独立安装所有运行时链接，使单端冲突不阻断其他运行时。"""
    results: dict[str, LinkInstallResult] = {}
    for runtime_name, skills_dir in runtime_dirs or runtime_skill_dirs():
        try:
            results[runtime_name] = install_skill_symlinks(skills, skills_dir)
        except OSError as exc:
            print(f"  Warning: {runtime_name} skill installation failed: {exc}")
            results[runtime_name] = LinkInstallResult(0, 0, 0, 1)
    return results


def uninstall_runtime_skill_links(
    skills: list[tuple[str, Path]],
    runtime_dirs: Optional[tuple[tuple[str, Path], ...]] = None,
) -> dict[str, LinkUninstallResult]:
    """独立卸载所有运行时中精确归属于本仓库的链接。"""
    results: dict[str, LinkUninstallResult] = {}
    for runtime_name, skills_dir in runtime_dirs or runtime_skill_dirs():
        try:
            results[runtime_name] = uninstall_skill_symlinks(skills, skills_dir)
        except OSError as exc:
            print(f"  Warning: {runtime_name} skill uninstallation failed: {exc}")
            results[runtime_name] = LinkUninstallResult(0, 0, 1)
    return results


# ─── 3. 全局权限配置 ─────────────────────────────────────────────────────────


def merge_global_settings(permissions: list[str]) -> tuple[int, int]:
    """合并权限白名单到 ~/.claude/settings.json。

    幂等逻辑：读取已有 settings，合并标准权限，保留用户原有配置，去重后写入。

    Returns:
        (configured_count, custom_preserved_count)
    """
    HOME_CLAUDE_DIR.mkdir(parents=True, exist_ok=True)

    standard_set = set(permissions)
    custom_entries: list[str] = []
    existing_settings: dict = {}

    if GLOBAL_SETTINGS_PATH.exists():
        try:
            with open(GLOBAL_SETTINGS_PATH, "r", encoding="utf-8") as f:
                existing_settings = json.load(f)
            existing_allow = existing_settings.get("permissions", {}).get("allow", [])
            for entry in existing_allow:
                if entry not in standard_set:
                    custom_entries.append(entry)
        except (json.JSONDecodeError, KeyError):
            pass

    merged = list(permissions) + custom_entries

    existing_settings.setdefault("permissions", {})["allow"] = merged

    with open(GLOBAL_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_settings, f, indent=2)
        f.write("\n")

    return len(permissions), len(custom_entries)


def remove_global_permissions(permissions: list[str]) -> tuple[int, int]:
    """从 ~/.claude/settings.json 中移除本脚本添加的权限。

    Returns:
        (removed_count, remaining_count)
    """
    if not GLOBAL_SETTINGS_PATH.exists():
        return 0, 0

    try:
        with open(GLOBAL_SETTINGS_PATH, "r", encoding="utf-8") as f:
            existing_settings = json.load(f)
    except (json.JSONDecodeError, KeyError):
        return 0, 0

    standard_set = set(permissions)
    current_allow = existing_settings.get("permissions", {}).get("allow", [])
    new_allow = [p for p in current_allow if p not in standard_set]

    existing_settings.setdefault("permissions", {})["allow"] = new_allow

    with open(GLOBAL_SETTINGS_PATH, "w", encoding="utf-8") as f:
        json.dump(existing_settings, f, indent=2)
        f.write("\n")

    return len(current_allow) - len(new_allow), len(new_allow)


# ─── 4. SKILL.md 解析 ────────────────────────────────────────────────────────


def parse_skill_frontmatter(
    skill_path: Path,
) -> tuple[list[str], bool]:
    """解析 SKILL.md 的 frontmatter，提取 allowed-tools 和 disable-model-invocation。

    Returns:
        (bash_prefixes, is_disabled)
    """
    content = skill_path.read_text(encoding="utf-8")

    match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return [], False

    frontmatter = match.group(1)

    is_disabled = bool(
        re.search(r"disable-model-invocation:\s*true", frontmatter, re.IGNORECASE)
    )

    tools_match = re.search(r"allowed-tools:\s*(.+)", frontmatter)
    if not tools_match:
        return [], is_disabled

    tools_line = tools_match.group(1)

    bash_prefixes: list[str] = []
    for m in re.finditer(r"Bash\(\s*([^\s:)]+)", tools_line):
        bash_prefixes.append(m.group(1))

    return bash_prefixes, is_disabled


# ─── 5. 交叉校验 ──────────────────────────────────────────────────────────────


def extract_standard_bash_prefixes(permissions: list[str]) -> set[str]:
    """从标准权限列表提取 bash 命令前缀集合。"""
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
    """交叉校验 SKILL.md 与标准权限列表的一致性。"""
    warnings = 0
    standard_prefixes = extract_standard_bash_prefixes(standard_permissions)

    for name, source_path in skills:
        bash_prefixes, _is_disabled = parse_skill_frontmatter(source_path)

        for prefix in bash_prefixes:
            if prefix not in standard_prefixes:
                print(
                    f"  Warning: skill '{name}' uses Bash({prefix} *) "
                    f"but no matching permission in standard list"
                )
                warnings += 1

    return warnings


# ─── 6. 主入口 ────────────────────────────────────────────────────────────────


def install() -> None:
    """全局安装 skills 和权限。"""
    print("=" * 60)
    print("  Skills 全局环境配置工具")
    print("=" * 60)
    print()

    # Step 1: 扫描 skills
    print("📦 扫描自定义 skills...")
    skills = scan_custom_skills()
    print(f"   发现 {len(skills)} 个自定义 skill: {[s[0] for s in skills]}")

    # Step 2: 独立安装 Claude Code 与 Codex 符号链接
    print("🔗 安装 Claude Code 与 Codex skill 符号链接...")
    link_results = install_runtime_skill_links(skills)
    for runtime_name, result in link_results.items():
        print(
            f"   {runtime_name}: {result.created} created, "
            f"{result.skipped} skipped, {result.replaced} replaced, "
            f"{result.warnings} warning(s)"
        )

    # Step 3: 一致性校验
    print()
    print("🔍 交叉校验 allowed-tools...")
    check_warnings = check_skill_consistency(skills, STANDARD_PERMISSIONS)

    # Step 4: 合并权限到 ~/.claude/settings.json
    print()
    print("⚙️  合并权限到 ~/.claude/settings.json...")
    configured, custom_preserved = merge_global_settings(STANDARD_PERMISSIONS)
    print(
        f"   Done. {configured} permissions configured, "
        f"{custom_preserved} custom entries preserved."
    )

    # Step 5: 摘要
    print()
    print("=" * 60)
    print("  执行摘要")
    print("=" * 60)
    for runtime_name, result in link_results.items():
        print(
            f"  {runtime_name} 符号链接: {result.created} created, "
            f"{result.skipped} skipped, {result.replaced} replaced, "
            f"{result.warnings} warning(s)"
        )
    print(f"  权限配置: {configured} standard, {custom_preserved} custom preserved")
    total_warnings = sum(result.warnings for result in link_results.values()) + check_warnings
    print(f"  校验警告: {total_warnings}")
    if total_warnings == 0:
        print("  ✓ 一切正常")
    print()
    print("  ⚠️  注意: Skills 通过符号链接安装在 ~/.claude/skills/ 与 ~/.codex/skills/")
    print("      指向本仓库的实际文件。请勿删除或移动本仓库目录，")
    print("      否则所有项目中已安装的 Skills 将失效。")
    print(f"      仓库路径: {PROJECT_ROOT}")
    print()


def uninstall() -> None:
    """卸载全局 skills 和权限。"""
    print("=" * 60)
    print("  Skills 全局卸载工具")
    print("=" * 60)
    print()

    # Step 1: 扫描 skills
    print("📦 扫描已安装的 skills...")
    skills = scan_custom_skills()
    print(f"   发现 {len(skills)} 个 skill: {[s[0] for s in skills]}")

    # Step 2: 独立移除两个运行时中的受管符号链接
    print("🔗 移除 Claude Code 与 Codex 中的受管 skill 符号链接...")
    link_results = uninstall_runtime_skill_links(skills)
    for runtime_name, result in link_results.items():
        print(
            f"   {runtime_name}: {result.removed} removed, "
            f"{result.not_found} not found, {result.warnings} warning(s)"
        )

    # Step 3: 移除权限
    print()
    print("⚙️  从 ~/.claude/settings.json 移除权限...")
    perms_removed, perms_remaining = remove_global_permissions(STANDARD_PERMISSIONS)
    print(f"   Removed: {perms_removed} permissions, {perms_remaining} remaining")

    # Step 4: 摘要
    print()
    print("=" * 60)
    print("  卸载摘要")
    print("=" * 60)
    for runtime_name, result in link_results.items():
        print(
            f"  {runtime_name} 符号链接: {result.removed} removed, "
            f"{result.not_found} not found, {result.warnings} warning(s)"
        )
    print(f"  权限: {perms_removed} removed, {perms_remaining} remaining")
    print()
    print("  ✓ 卸载完成。本仓库目录未受影响，可随时重新安装。")
    print()


def main() -> None:
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()


if __name__ == "__main__":
    main()
