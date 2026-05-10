## 1. 修改 new-worktree-apply/SKILL.md

- [x] 1.1 在 Step 5（创建 worktree）中加入平台分支指令：Claude Code 环境必须使用 `EnterWorktree` 工具，禁止 `git worktree add`；其他环境使用 `git worktree add <path> -b <branch-name>` + `cd <worktree-path>`
- [x] 1.2 在 Step 5 后新增 CWD 验证步骤：执行 `pwd` 和 `git branch --show-current`，验证 worktree 目录和分支正确，失败则报错停止
- [x] 1.3 在 Guardrails 中增加"在 Claude Code 环境下禁止使用 `git worktree add` 替代 `EnterWorktree`"条目

## 2. 修改 merge-worktree-return/SKILL.md

- [x] 2.1 在 Step 7（退出 worktree）中加入 fallback：Claude Code 环境使用 `ExitWorktree` 工具；其他环境使用 `git worktree remove <worktree-path>`（Step 6 已通过 `cd <MAIN_DIR>` 切回主目录，无需额外 CWD 切换）
- [x] 2.2 更新 Guardrails 中 ExitWorktree 相关说明，覆盖非 Claude Code 环境的 fallback 路径

## 3. 修改 parall-new-worktree-apply/SKILL.md

- [x] 3.1 在 Step 4.2.1 Agent spawn prompt 的步骤 1 中加入平台适配指引：说明如何判断当前环境、两条路径分别的操作方式、以及 CWD 验证要求
- [x] 3.2 在 Agent prompt 的 post-apply 后处理步骤中加入 CWD 验证，确保 commit 在正确目录中执行

## 4. 验证

- [x] 4.1 审阅三个修改后的 SKILL.md，确认平台分支逻辑正确且不破坏 Claude Code 环境下原有行为
- [x] 4.2 确认所有 CWD 验证步骤的报错信息清晰，包含恢复建议
