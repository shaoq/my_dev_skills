## Why

在 worktree 中完成 OpenSpec 提案实施后，需要手动执行一系列 git 操作将成果合并回主分支：提交当前分支文件、rebase 主分支代码、解决可能的冲突、合并回主分支、退出 worktree。这个过程容易出错，特别是冲突处理和分支合并的顺序。将这些步骤自动化为一个 skill，确保代码安全合并、worktree 正确退出，是 `new-worktree-apply` 的配对流程。

## What Changes

- 新建 `merge-worktree-return` skill，将完整的 worktree 合并 + 退出流程封装为一条命令
- 支持自动提交当前 worktree 分支的所有未提交文件
- 支持从 worktree 分支 rebase 主分支最新代码，自动解决冲突
- 合并回主分支后，验证合并成功才退出 worktree
- 支持传入提案名称参数，在合并前验证 OpenSpec 提案已 apply 完成
- 使用 Claude Code 内置 `ExitWorktree` 工具退出 worktree（自动管理 session CWD）

## Capabilities

### New Capabilities
- `worktree-merge`: 自动化的 worktree 合并流程，包括文件提交、rebase、冲突解决、主分支合并
- `worktree-exit`: 合并验证通过后安全退出 worktree 并返回主目录
- `openspec-verify`: 合并前验证 OpenSpec 提案实施完成状态

### Modified Capabilities
（无）

## Impact

- 新增 skill 文件：`merge-worktree-return/SKILL.md`
- 依赖：Claude Code 的 `ExitWorktree` 工具、OpenSpec CLI（可选，仅当传入提案名称时需要）、git
- 影响：与 `new-worktree-apply` 配对，形成完整的 worktree 开发闭环
