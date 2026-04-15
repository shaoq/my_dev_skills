## Why

`openspec/` 目录被 `.gitignore` 排除，导致 worktree 中 `opsx:apply` 执行时对 `tasks.md` 的 `[ ]→[x]` 标记无法通过 `git merge` 回到主分支。每次 worktree 退出后，main 上的 tasks.md 永远是全 `[ ]` 状态，使得 `/check-changes-completed` 等验证 skill 报告"0/N 完成"，即使代码实际已交付。此外，`new-worktree-apply` 在执行 apply 前未校验 OpenSpec artifacts 是否齐全，apply 后也未验证 task 标记是否准确。

## What Changes

- 修改 `new-worktree-apply/SKILL.md`：新增 pre-apply artifact 校验步骤、post-apply task 验证与补标记步骤、`git add -f` 强制跟踪 tasks.md
- 修改 `parall-new-worktree-apply/SKILL.md`：Agent prompt 增加 force-add + post-verify 指令、合并后增强 task 验证

## Capabilities

### New Capabilities
- `pre-apply-validation`: apply 执行前的 OpenSpec artifact 完整性校验，确保 proposal/design/specs/tasks 齐全且 status 为 done
- `post-apply-task-verification`: apply 执行后的 task 状态验证与补标记，对比 task 描述与实际产出文件，将漏标任务强制标记为 [x]
- `force-add-tasks-md`: 通过 `git add -f` 强制将 tasks.md 纳入 git 跟踪，绕过 .gitignore 限制，确保 worktree 中的 task 状态变更能随 git merge 回到 main

### Modified Capabilities

（无）

## Impact

- 修改文件：`new-worktree-apply/SKILL.md`、`parall-new-worktree-apply/SKILL.md`
- 依赖：`openspec` CLI（status 指令）、git（add -f）
- 影响：task 状态标记将准确反映实施进度，`/check-changes-completed` 报告将显示正确的完成度
