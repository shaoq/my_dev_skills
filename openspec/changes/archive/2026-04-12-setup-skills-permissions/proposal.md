## Why

新环境 clone 后需要手动配置两个东西：(1) `.claude/settings.local.json` 是 gitignored 的权限白名单，需手动创建；(2) 根目录下的自定义 skill（如 `new-worktree-apply/SKILL.md`）虽然 git tracked 且被 Claude Code 自动发现，但在 `.claude/skills/` 中没有统一入口。同时 5 个 skill 的 `allowed-tools` 与 settings 的 `permissions.allow` 是两套独立声明，无交叉校验。需要一个一键脚本解决初始化、安装和一致性问题。

## What Changes

- 新增 `setup-skills-env.py` 脚本，内含标准权限列表，一键生成 `.claude/settings.local.json`
- 脚本扫描根目录 `*/SKILL.md`，为每个自定义 skill 在 `.claude/skills/<name>/` 创建指向源文件的符号链接
- 脚本扫描 `allowed-tools` 字段，与标准权限列表做交叉校验，输出不一致警告
- 幂等执行：已有 settings 合并更新，已有 symlink 检查有效性

## Capabilities

### New Capabilities
- `permission-generation`: 从内置标准权限列表生成 `.claude/settings.local.json`，支持幂等执行和合并更新
- `skill-symlink-install`: 扫描根目录 `*/SKILL.md`，在 `.claude/skills/<name>/SKILL.md` 创建相对路径符号链接
- `skill-consistency-check`: 扫描 SKILL.md 的 allowed-tools，与 settings 交叉校验，输出不一致警告

### Modified Capabilities
（无）

## Impact

- 新增 1 个 Python 脚本文件：`setup-skills-env.py`
- 不修改任何现有 SKILL.md 文件
- 在 `.claude/skills/` 下创建符号链接（不影响已有 openspec 核心技能）
- `.claude/settings.local.json` 会被生成/更新（幂等合并）
- 脚本需要 Python 3.6+，无第三方依赖
- 和项目已有的 `setup-iterm2-claude-notify.py` 风格一致
