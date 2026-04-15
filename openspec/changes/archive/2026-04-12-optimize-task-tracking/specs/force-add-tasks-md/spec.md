## ADDED Requirements

### Requirement: Force-add tasks.md after apply

`new-worktree-apply` 在 post-apply 验证完成后 SHALL 执行 `git add -f openspec/changes/<name>/tasks.md`，将 tasks.md 强制纳入 git 暂存区，绕过 `.gitignore` 规则。

#### Scenario: tasks.md modified by apply
- **WHEN** `opsx:apply` 或 post-apply 补标记修改了 tasks.md
- **THEN** 执行 `git add -f openspec/changes/<name>/tasks.md` 确保变更被暂存

#### Scenario: tasks.md unchanged
- **WHEN** tasks.md 无变更（apply 未修改任何 task 状态）
- **THEN** 跳过 force-add，不影响 git 状态

### Requirement: Commit includes force-added tasks.md

最终 git commit SHALL 包含 force-add 的 tasks.md，commit message 中体现任务完成度。

#### Scenario: Successful apply with tasks marked
- **WHEN** apply 完成，tasks.md 有 N/M 个 [x] 标记
- **THEN** commit message 格式: `feat: implement <name> (N/M tasks)`

#### Scenario: Partial completion
- **WHEN** apply 部分完成，tasks.md 有 X/M 个 [x] 标记（X < M）
- **THEN** commit message 格式: `feat: implement <name> (X/M tasks, partial)`

### Requirement: Parallel agent force-add in worktree

`parall-new-worktree-apply` 的 Agent prompt SHALL 明确指示 Agent 在 `opsx:apply` 完成后执行 `git add -f openspec/changes/<name>/tasks.md` 和 `git add -A`，确保 tasks.md 变更被 commit 到 worktree 分支。

#### Scenario: Agent follows force-add instruction
- **WHEN** Agent 执行 apply 后按照 prompt 指示执行 force-add
- **THEN** tasks.md 变更被 commit 到 worktree 分支，后续 merge 能传播到 main

#### Scenario: Agent skips force-add
- **WHEN** Agent 未能执行 force-add（如执行错误）
- **THEN** worktree 分支中 tasks.md 变更未被 commit，合并后主进程的验证步骤检测并补标记

### Requirement: Post-merge verification as safety net

`parall-new-worktree-apply` 合并每个分支后 SHALL 检查 main 上的 `tasks.md` 是否包含预期的 `[x]` 标记。若发现标记丢失，直接在 main 目录中重新执行补标记。

#### Scenario: tasks.md merged successfully
- **WHEN** merge 后 main 上的 tasks.md 包含正确的 [x] 标记
- **THEN** 验证通过，继续处理下一个分支

#### Scenario: tasks.md marks lost in merge
- **WHEN** merge 后 main 上的 tasks.md 仍为全 [ ]（标记丢失）
- **THEN** 在 main 目录中执行补标记流程，然后 `git add -f` 并 commit
