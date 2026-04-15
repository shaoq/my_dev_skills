## ADDED Requirements

### Requirement: Auto-commit before execution
系统 SHALL 在开始执行前检查当前工作区状态（`git status --porcelain`），若有未提交文件则自动 commit，确保 HEAD 是干净的。commit 消息格式为 `chore: auto-commit before parallel worktree apply`。

#### Scenario: Dirty working directory
- **WHEN** 工作区有未提交的修改文件
- **THEN** 系统执行 `git add -A && git commit` 提交所有变更

#### Scenario: Clean working directory
- **WHEN** 工作区无未提交文件
- **THEN** 系统跳过 auto-commit 步骤

### Requirement: Single change delegates to opsx:apply
当待执行 changes 数量为 1 时，系统 SHALL 直接在主会话中通过 Skill 工具调用 `opsx:apply <change-name>`，然后执行合并回主干和退出 worktree 的流程（与 new-worktree-apply 一致）。

#### Scenario: Exactly one pending change
- **WHEN** 发现只有 1 个待执行 change
- **THEN** 系统调用 Skill "opsx:apply" 并传入该 change 名称，走完整的 worktree 隔离 + apply + merge + exit 流程

### Requirement: Spawn parallel agents per wave
对于每个 Wave，系统 SHALL 为该 Wave 内的每个 change 通过 `Agent` 工具 spawn 一个子代理，使用 `isolation: "worktree"` 参数创建独立 worktree。所有子代理在同一消息中并行 spawn。

#### Scenario: Wave with 3 independent changes
- **WHEN** Wave 1 包含 change-a, change-b, change-c
- **THEN** 系统并行 spawn 3 个 Agent，每个使用 `isolation: "worktree"`，prompt 指示执行 `/opsx:apply <change-name>`

#### Scenario: Wave with 1 change
- **WHEN** Wave 2 仅包含 change-b
- **THEN** 系统仅 spawn 1 个 Agent

### Requirement: Agent prompt specifies apply and commit
每个子代理的 prompt SHALL 明确指示：执行 Skill `opsx:apply <change-name>` 实施所有任务，完成后使用 `git add -A && git commit` 提交所有变更。

#### Scenario: Agent completes successfully
- **WHEN** 子代理成功执行完 `/opsx:apply` 并 commit
- **THEN** Agent 返回结果包含 branch 名称和成功状态

#### Scenario: Agent fails during apply
- **WHEN** 子代理在执行 `/opsx:apply` 过程中失败
- **THEN** Agent 返回失败状态和错误信息，主会话记录该失败

### Requirement: Wait for all agents in wave to complete
系统 SHALL 等待当前 Wave 内所有子代理完成后再进入合并阶段。失败的 Agent 不阻塞其他 Agent 的等待。

#### Scenario: One agent fails in wave
- **WHEN** Wave 内有 3 个 Agent，其中 1 个失败
- **THEN** 系统等待其余 2 个完成，记录失败的那个，继续合并成功的分支

### Requirement: Sequential merge after each wave
每个 Wave 内所有 Agent 完成后，系统 SHALL 按目录名字母序逐个将分支合并回 main：先 `git rebase main <branch>`，再 `git checkout main && git merge <branch>`。

#### Scenario: Merge two branches from wave
- **WHEN** Wave 1 的 Agent 返回 branch-a 和 branch-b
- **THEN** 系统按字母序先 rebase + merge branch-a，再 rebase + merge branch-b

### Requirement: Ensure latest code in worktree
系统 SHALL 确保每个子代理的 worktree 基于当前最新 HEAD。由于 Agent 的 `isolation: "worktree"` 基于 spawn 时的 HEAD 创建，Wave 间串行执行保证了后续 Wave 的代码是最新的。

#### Scenario: Second wave gets updated code
- **WHEN** Wave 1 完成合并后，HEAD 已包含 Wave 1 的变更
- **THEN** Wave 2 的 Agent 基于新的 HEAD 创建 worktree，自然包含 Wave 1 的代码
