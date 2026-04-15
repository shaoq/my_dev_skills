## MODIFIED Requirements

### Requirement: Agent prompt delegates post-apply logic to new-worktree-apply skill
parall-new-worktree-apply 的 Agent prompt SHALL 不再内联 Artifact 校验、Task Backfill、Force-add commit 的具体命令，而是指示 Agent 通过 Read 工具读取 `new-worktree-apply/SKILL.md` 文件，然后按照其中的步骤 7-10（Artifact 校验 → Task Backfill → Force-add commit）执行后处理。prompt 中 SHALL 同时包含步骤编号和功能描述，以防止单纯编号引用失效。

#### Scenario: Agent successfully reads and executes delegated steps
- **WHEN** parall Agent 执行完 `opsx:apply <change-name>` 后
- **THEN** Agent 使用 Read 工具读取 `new-worktree-apply/SKILL.md`，找到步骤 7-10（Pre-apply OpenSpec artifact validation、Execute OpenSpec apply、Post-apply task verification and backfill、Force-add tasks.md and commit），并按照其中的具体命令执行后处理

#### Scenario: new-worktree-apply SKILL.md not found
- **WHEN** Agent 尝试 Read `new-worktree-apply/SKILL.md` 但文件不存在
- **THEN** Agent 报错："new-worktree-apply/SKILL.md 未找到，无法执行后处理"并在返回结果中标注失败原因

#### Scenario: Steps 7-10 are modified in new-worktree-apply
- **WHEN** 用户修改了 new-worktree-apply/SKILL.md 中步骤 7-10 的内容
- **THEN** 下次 parall Agent 执行时会读到最新版本的后处理逻辑，自动获得更新，无需手动同步 parall-new-worktree-apply
