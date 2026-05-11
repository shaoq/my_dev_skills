## ADDED Requirements

### Requirement: Worktree creation with platform-adaptive CWD switching
Skill 指令 SHALL 在创建 worktree 时根据当前平台选择正确的工具路径：
- 当 `EnterWorktree` 工具可用时（Claude Code 环境），MUST 使用 `EnterWorktree`
- 当 `EnterWorktree` 工具不可用时（Codex 等环境），MUST 使用 `git worktree add` 并随后显式 `cd` 到 worktree 目录
- 在 Claude Code 环境下，SHALL 禁止使用 `git worktree add`（必须用 `EnterWorktree`）

#### Scenario: Claude Code 环境下使用 EnterWorktree
- **WHEN** agent 运行在 Claude Code 环境中，且 `EnterWorktree` 工具可用
- **THEN** agent MUST 调用 `EnterWorktree` 工具创建 worktree
- **THEN** agent MUST NOT 使用 `git worktree add` 命令

#### Scenario: Codex 环境下使用 git worktree add 加 cd
- **WHEN** agent 运行在非 Claude Code 环境（如 Codex CLI），且 `EnterWorktree` 工具不可用
- **THEN** agent MUST 执行 `git worktree add <path> -b <branch-name>` 创建 worktree
- **THEN** agent MUST 随后执行 `cd <worktree-path>` 切换到 worktree 目录
- **THEN** 后续所有操作 MUST 在 worktree 目录中执行

#### Scenario: CWD 验证在 worktree 创建后执行
- **WHEN** worktree 创建完成（无论通过哪种路径）
- **THEN** agent MUST 执行 `pwd` 和 `git branch --show-current` 验证当前工作目录
- **THEN** 若 `pwd` 不在预期 worktree 目录或分支不匹配，agent MUST 报错并停止执行

### Requirement: Worktree exit with platform-adaptive CWD restoration
Skill 指令 SHALL 在退出 worktree 时根据当前平台选择正确的退出路径：
- 当 `ExitWorktree` 工具可用时（Claude Code 环境），MUST 使用 `ExitWorktree`
- 当 `ExitWorktree` 工具不可用时（Codex 等环境），MUST 使用 `cd <main-dir>` + `git worktree remove <worktree-path>`

#### Scenario: Claude Code 环境下使用 ExitWorktree
- **WHEN** agent 运行在 Claude Code 环境中，且 `ExitWorktree` 工具可用
- **THEN** agent MUST 调用 `ExitWorktree` 工具退出 worktree
- **THEN** 会话 CWD 自动恢复到主项目目录

#### Scenario: Codex 环境下使用 cd 加 git worktree remove
- **WHEN** agent 运行在非 Claude Code 环境（如 Codex CLI），且 `ExitWorktree` 工具不可用
- **THEN** agent MUST 执行 `cd <main-dir>` 切换回主项目目录
- **THEN** agent MUST 执行 `git worktree remove <worktree-path>` 清理 worktree

#### Scenario: CWD 验证在 worktree 退出后执行
- **WHEN** worktree 退出操作完成（无论通过哪种路径）
- **THEN** agent MUST 执行 `pwd` 和 `git branch --show-current` 验证已回到主目录和主分支
- **THEN** 若验证失败，agent MUST 报错

### Requirement: Parallel worktree apply agent prompt includes platform adaptation
`parall-new-worktree-apply` skill 的 Agent spawn prompt SHALL 包含平台适配指引，使 subagent 能正确判断当前环境并选择对应的 worktree 操作路径。

#### Scenario: Agent prompt 包含双路径指引
- **WHEN** `parall-new-worktree-apply` 构造 Agent spawn prompt
- **THEN** prompt 中 MUST 包含 Claude Code 和非 Claude Code 两条路径的说明
- **THEN** prompt 中 MUST 包含判断依据（`EnterWorktree` 工具是否可用）
- **THEN** prompt 中 MUST 包含 CWD 验证步骤

### Requirement: Backward compatibility with existing Claude Code behavior
在 Claude Code 环境下，修改后的 skill 的行为 SHALL 与修改前完全一致——优先使用 `EnterWorktree`/`ExitWorktree`，不引入任何行为变化。

#### Scenario: Claude Code 环境下行为不变
- **WHEN** agent 运行在 Claude Code 环境中
- **THEN** worktree 创建/退出的主路径 MUST 与修改前相同（使用内置工具）
- **THEN** 不引入新的中间步骤或验证失败点
