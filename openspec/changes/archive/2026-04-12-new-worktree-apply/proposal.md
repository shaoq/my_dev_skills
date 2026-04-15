## Why

日常研发中，每次基于 OpenSpec 提案开始实施功能时，需要手动执行一系列重复的 git 操作：检查工作区状态、提交未提交文件、创建 worktree 隔离分支、验证分支与主分支同步、最后执行提案实施。将这些步骤自动化为一个 skill，可以减少操作失误、提高研发效率，并确保每次功能开发都在干净的隔离环境中进行。

## What Changes

- 新建 `new-worktree-apply` skill，将完整的 worktree 创建 + OpenSpec apply 流程封装为一条命令
- 支持自动检测当前 git 状态并提交未提交的文件
- 支持自动检测主分支名称（main/master/trunk），同时支持用户自定义
- 使用 Claude Code 内置 `EnterWorktree` 工具创建 worktree（自动管理 session CWD）
- 创建 worktree 后自动验证 HEAD 与主分支一致，不一致时自动合并主分支最新代码
- worktree 创建并验证完成后，自动调用 `/opsx:apply` 执行提案实施

## Capabilities

### New Capabilities
- `worktree-creation`: 自动化的 git worktree 创建流程，包括未提交文件处理、主分支检测、worktree 创建、HEAD 一致性验证
- `worktree-apply-integration`: worktree 创建完成后自动调用 OpenSpec apply 流程的集成能力

### Modified Capabilities
（无）

## Impact

- 新增 skill 文件：`new-worktree-apply/SKILL.md`
- 依赖：Claude Code 的 `EnterWorktree` 工具、OpenSpec CLI、git
- 影响：用户工作流从手动多步操作变为一键式 `/new-worktree-apply <proposal-name>`
