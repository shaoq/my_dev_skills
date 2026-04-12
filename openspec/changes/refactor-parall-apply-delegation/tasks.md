## 1. 修改 parall Agent prompt

- [x] 1.1 修改 `parall-new-worktree-apply/SKILL.md` 中 Agent prompt 的步骤 2（Post-apply task 验证与补标记），删除内联的 Task Backfill 逻辑（解析 task 描述、检查文件存在性、自动标记 `[x]`、输出补标记报告）
- [x] 1.2 修改 Agent prompt 的步骤 3（提交所有变更），删除内联的 Force-add tasks.md 和 commit 逻辑
- [x] 1.3 在 Agent prompt 步骤 2 的位置新增委托指令：指示 Agent 用 Read 工具读取 `new-worktree-apply/SKILL.md`，按其中的步骤 7-10（功能描述：Artifact 校验 → Task Backfill → Force-add commit）执行后处理，包含步骤编号和功能描述以防编号变更
- [x] 1.4 调整 Agent prompt 步骤编号，确保引用 new-worktree-apply 步骤后的整体流程连贯

## 2. 验证

- [x] 2.1 确认修改后的 parall-new-worktree-apply SKILL.md 中不再包含与 new-worktree-apply 步骤 7-10 重复的内联命令
- [x] 2.2 确认 Agent prompt 中的委托指令同时包含步骤编号（7-10）和功能描述（Artifact 校验、Task Backfill、Force-add commit）
