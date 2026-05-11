## MODIFIED Requirements

### Requirement: 每 Batch 完成后立即合并

`parall-new-worktree-apply` SHALL 在每个 Batch 的所有 Agent 完成后，立即执行串行合并流程，再开始下一个 Batch。串行合并流程 SHALL 使用检测出的 `<MAIN_BRANCH>` 执行 rebase、checkout、merge 和合并验证，并 SHALL 在合并前后验证主控 CWD 与当前分支。

#### Scenario: 两个 Batch 的 Wave 执行顺序

- **WHEN** Wave 1 有 Batch 1（3 个 change）和 Batch 2（2 个 change）
- **THEN** 先并行执行 Batch 1 的 3 个 Agent → 等待完成 → 使用 `<MAIN_BRANCH>` 串行合并 Batch 1 成功分支 → 再并行执行 Batch 2 的 2 个 Agent → 等待完成 → 使用 `<MAIN_BRANCH>` 串行合并 Batch 2 成功分支

#### Scenario: Batch 1 有 Agent 失败

- **WHEN** Batch 1 中有 1 个 Agent 失败
- **THEN** 仍然执行 Batch 1 的合并（仅合并成功的分支），然后继续执行 Batch 2

#### Scenario: 合并前主控状态验证

- **WHEN** Batch 内某个成功分支准备合并
- **THEN** `parall-new-worktree-apply` SHALL 验证主控在主工作树且当前分支为 `<MAIN_BRANCH>`
- **THEN** 验证通过后才执行该分支的 rebase 和 merge

#### Scenario: 合并后分支完整性验证

- **WHEN** 成功分支已执行 merge 到 `<MAIN_BRANCH>`
- **THEN** `parall-new-worktree-apply` SHALL 检查 `git log <MAIN_BRANCH>..<branch>` 是否为空
- **THEN** 仅当输出为空时，将该分支记录为已合并
