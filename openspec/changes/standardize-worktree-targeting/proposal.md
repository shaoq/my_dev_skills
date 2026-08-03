## Why

`new-worktree-apply`、`merge-worktree-return` 和 `parall-new-worktree-apply` 对开发主分支的参数、默认检测顺序和执行语义不一致，并普遍把 `main` 优先当作目标；在实际开发主分支为 `develop`、`dev-*` 等分支的仓库中，worktree 可能基于错误分支创建或被合并到错误分支。三个高风险 Git workflow 必须共享一个可配置、可解释、需用户确认的目标分支契约。

## What Changes

- 三个 worktree skill 统一使用可选参数 `--target <target-branch>`，并统一使用 `TARGET_BRANCH` 语义。
- **BREAKING**：`new-worktree-apply` 原有 `--branch` 参数由 `--target` 替代；使用旧参数时停止并显示迁移命令，不静默兼容。
- 三个 skill 统一按“显式 `--target` → 主工作树当前分支 → `origin/HEAD` 本地同名分支 → `main`/`master`/`trunk`”选择本地目标分支，并显示选择依据。
- 三个 skill 在任何 Git 写操作前完成只读预检，展示目标分支、工作树路径、风险和完整操作计划，等待用户明确确认；确认后、首次写操作前重新验证快照。
- 修复 `new-worktree-apply` 将当前 HEAD 错当成目标 HEAD、创建分支时未使用所选目标作为起点的问题，确保新 worktree 精确基于已确认目标。
- 将 `merge-worktree-return` 的 rebase、merge、验证和清理全部绑定到已确认目标，并正确定位目标分支所在 worktree。
- 将 `parall-new-worktree-apply` 的 Auto-commit、子 worktree 基线、串行合并与最终验证全部绑定到已确认目标；单 change 也必须在隔离 worktree 中实施。
- **BREAKING**：无人值守调用不再自动越过目标确认；未明确确认时保持 Git 状态不变并暂停或退出。

## Capabilities

### New Capabilities

- `worktree-targeting`: 定义三个 worktree skill 的统一目标参数、确定性选择算法、只读预检、确认门槛、状态复检以及目标驱动的创建和合并行为。

### Modified Capabilities

（无；当前 `openspec/specs/` 中没有已发布的 worktree 目标分支规格。）

## Impact

- 修改文件：`new-worktree-apply/SKILL.md`、`merge-worktree-return/SKILL.md`、`parall-new-worktree-apply/SKILL.md`
- 用户接口：三个命令的 `argument-hint`、输入示例、参数错误、确认提示及成功/错误输出
- Git 行为：目标分支检测、worktree 拓扑解析、创建起点、Auto-commit 时机、rebase、merge、验证与清理
- 运行环境：兼容 Claude Code 的 `EnterWorktree`/`ExitWorktree`/`AskUserQuestion` 与 Codex CLI 等环境中的等价流程
- 迁移影响：`new-worktree-apply --branch` 调用必须改为 `--target`；所有写操作流程新增强制交互确认
