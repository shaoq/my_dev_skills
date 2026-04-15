## Context

Claude Code 提供 `EnterWorktree` 工具用于在隔离环境中工作，但用户需要手动完成前置（提交未保存文件）和后置（同步验证、调用 apply）操作。OpenSpec 的 apply 流程在 worktree 中执行效果最佳，因为可以将提案实施完全隔离于主分支。

当前工作流是手动的：
1. `git status` → `git add -A && git commit`
2. `EnterWorktree` 或 `git worktree add`
3. 验证 HEAD 一致性
4. `/opsx:apply <name>`

本 skill 将上述流程封装为一条命令。

## Goals / Non-Goals

**Goals:**
- 一条命令完成"提交 → 创建 worktree → 验证 → apply"全流程
- 自动检测主分支名称，支持自定义覆盖
- 使用 Claude Code 内置 `EnterWorktree` 工具确保 session CWD 正确切换
- 健壮的错误处理：分支已存在、git 状态异常、HEAD 不一致等

**Non-Goals:**
- 不处理 worktree 的合并与退出（由 `merge-worktree-return` 负责）
- 不处理 OpenSpec 提案的创建（由 `/opsx:propose` 负责）
- 不支持同时操作多个提案

## Decisions

### 1. 使用 EnterWorktree 工具而非原始 git 命令

**选择**: 使用 Claude Code 内置 `EnterWorktree` 工具
**备选**: 使用 `git worktree add` + `cd`

**理由**: `EnterWorktree` 自动管理 session 的工作目录（CWD），无需手动 `cd`。原始 git 命令只能在每个 Bash 调用内切换目录，无法更新 session 级别的工作目录。

### 2. 主分支检测策略

**选择**: 按优先级尝试 `main` → `master` → `trunk` → `git remote show origin` 自动检测
**备选**: 硬编码 `main`，或要求用户每次指定

**理由**: 大多数项目使用 `main` 或 `master`，按优先级尝试即可覆盖绝大多数场景。同时支持用户通过参数自定义。

### 3. 未提交文件自动提交策略

**选择**: `git add -A && git commit -m "chore: auto-commit before worktree for <name>"`
**备选**: 拒绝创建 worktree，要求用户手动提交

**理由**: 自动提交减少用户操作步骤。commit message 中包含提案名称便于追踪。如果用户不想提交，可以在调用 skill 前手动处理。

### 4. HEAD 一致性验证与修复

**选择**: 比较 worktree HEAD 与主分支 HEAD，不一致时执行 `git merge <main-branch>`
**备选**: 不验证，依赖 `EnterWorktree` 基于 HEAD 创建

**理由**: `EnterWorktree` 基于 HEAD 创建新分支，通常与主分支一致。但如果在主分支有未推送的本地提交（已 commit 但尚未反映在新分支中），需要确保 worktree 基于最新的主分支状态。

## Risks / Trade-offs

- **[分支名冲突]** → 提交前检查分支是否已存在，已存在则报错并提示用户选择其他名称或删除已有分支
- **[自动提交可能包含敏感文件]** → 遵循 `.gitignore` 规则，`git add -A` 不会添加已忽略的文件。提示用户确认
- **[EnterWorktree 名称限制]** → 名称仅支持字母、数字、点、下划线、连字符，最多 64 字符。提案名需符合此规范
- **[OpenSpec CLI 不可用]** → 前置检查，如果 `openspec` 命令不存在则报错
