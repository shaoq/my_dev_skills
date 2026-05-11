## Why

当前 `new-worktree-apply` 和 `merge-worktree-return` 两个 skill 依赖 Claude Code 内置的 `EnterWorktree`/`ExitWorktree` 工具来切换 CWD，但这些工具在 Codex CLI 等其他平台中不存在。Agent 在非 Claude Code 环境下会退而使用 `git worktree add`（通过 Bash），而 Bash 不会切换会话 CWD，导致后续所有操作在错误的工作目录执行，statusline 也无法正确显示分支信息。需要让这些 skill 在所有支持的平台上都能正确创建 worktree 并切换工作目录。

## What Changes

- 在 `new-worktree-apply` 和 `merge-worktree-return` 的 Step 指令中加入平台分支逻辑：检测当前环境是否有 `EnterWorktree`/`ExitWorktree` 工具，有则优先使用，没有则用 `git worktree add` + 显式 `cd` 切换
- 在 `parall-new-worktree-apply` 的 Agent spawn prompt 中加入平台适配指引，确保 subagent 也能正确处理 CWD
- 在 `new-worktree-apply` Step 5 中增加硬性禁令：Claude Code 环境下禁止使用 `git worktree add`，必须用 `EnterWorktree`
- 在 `merge-worktree-return` Step 7 中增加平台分支：有 `ExitWorktree` 则用之，否则用 `cd` 回主目录 + `git worktree remove`
- 在各 skill 中增加 CWD 验证步骤，确保切换后确实位于正确目录

## Capabilities

### New Capabilities

- `worktree-platform-adaptation`: 定义 worktree 操作的跨平台适配策略，包括平台检测、CWD 切换验证、以及 fallback 路径

### Modified Capabilities

（无既有 spec 需要修改）

## Impact

- **受影响的 skill 文件**: `new-worktree-apply/SKILL.md`、`merge-worktree-return/SKILL.md`、`parall-new-worktree-apply/SKILL.md`
- **兼容性**: 纯增量修改，不影响现有 Claude Code 用户的行为（优先路径不变），仅增加 fallback 支持
- **依赖**: 无新增外部依赖，仅使用各平台已有的 git 命令
