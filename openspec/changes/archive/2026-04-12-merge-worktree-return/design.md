## Context

`merge-worktree-return` 是 `new-worktree-apply` 的配对 skill，用于在 worktree 中完成提案实施后，将成果安全合并回主分支并退出 worktree。

核心挑战：
1. 确保代码安全合并，不丢失任何更改
2. rebase 过程中可能出现冲突，需要自动解决
3. 合并前可能需要验证 OpenSpec 提案的实施状态
4. 退出 worktree 前必须确认合并成功

Claude Code 提供 `ExitWorktree` 工具用于安全退出 worktree，但前置的提交、rebase、合并操作需要精确编排。

## Goals / Non-Goals

**Goals:**
- 一条命令完成"提交 → rebase → 合并 → 退出"全流程
- 自动解决 rebase 和 merge 冲突
- 支持传入提案名称参数，合并前验证 OpenSpec 提案已 apply 完成
- 使用 `ExitWorktree` 安全退出，合并失败时拒绝退出

**Non-Goals:**
- 不负责创建 worktree（由 `new-worktree-apply` 负责）
- 不负责 OpenSpec 提案的 apply 实施（由 `/opsx:apply` 负责）
- 不处理 worktree 的归档（由 `/opsx:archive` 负责）

## Decisions

### 1. 使用 ExitWorktree 工具而非手动 git 操作

**选择**: 使用 Claude Code 内置 `ExitWorktree` 工具
**备选**: 使用 `git checkout main` + `git worktree remove`

**理由**: `ExitWorktree` 自动恢复 session CWD 到原始目录，并处理 worktree 清理。手动操作需要多步且容易遗漏。

### 2. Rebase vs Merge 策略

**选择**: 在 worktree 分支上 `git rebase <main-branch>`，然后在主分支上 `git merge <branch-name>`
**备选**: 直接 `git merge <main-branch>` 到 worktree 分支

**理由**: rebase 保持线性提交历史，更干净。rebase 后再 merge 到主分支时是 fast-forward，无额外合并提交。

### 3. 冲突自动解决策略

**选择**: Claude 自动分析冲突文件内容并尝试解决
**备选**: 遇到冲突即暂停，要求用户手动解决

**理由**: 用户明确要求自行解决（即 Claude 解决），而非暂停。Claude 可以读取冲突标记并做出合理判断。

### 4. 合并前 OpenSpec 状态验证

**选择**: 如果用户传入提案名称参数，检查 `openspec status --change <name> --json` 确认所有 tasks 已完成
**备选**: 不验证，信任用户判断

**理由**: 作为安全保障，避免用户在提案未完成时意外合并不完整的代码。如果未传参数则跳过验证。

### 5. 退出 worktree 的安全策略

**选择**: 仅在以下条件全部满足时才执行 `ExitWorktree`：
1. 当前分支所有文件已提交
2. rebase 完成（无冲突）
3. 主分支合并成功
4. 如果有提案参数，提案状态为已完成

**备选**: 合并后立即退出

**理由**: 宁可多验证一步，不可丢失代码。退出后代码不可回退。

## Risks / Trade-offs

- **[Rebase 冲突复杂无法自动解决]** → 如果自动解决失败，使用 `git rebase --abort` 回退，暂停并报告给用户
- **[合并后代码丢失]** → 在合并前确认所有文件已提交，合并后验证主分支包含所有变更
- **[ExitWorktree 清理失败]** → ExitWorktree 会检查未提交的变更，有保护机制
- **[OpenSpec 提案部分完成]** → 如果用户传入提案名但未全部完成，暂停并报告进度，由用户决定是否继续
