## 1. new-worktree-apply: Pre-Apply 校验

- [x] 1.1 在 `new-worktree-apply/SKILL.md` 中新增 Step 7（在 worktree 创建后、apply 前）：调用 `openspec status --change "<name>" --json` 检查所有 artifacts 的 status 是否为 "done"
- [x] 1.2 实现关键文件存在性验证：检查 `proposal.md`、`design.md`、`tasks.md`、`specs/` 目录下至少一个 spec 文件
- [x] 1.3 实现 artifacts 不完整时的错误输出与终止逻辑

## 2. new-worktree-apply: Post-Apply 验证与补标记

- [x] 2.1 在 `new-worktree-apply/SKILL.md` 中新增 Step 9（在 opsx:apply 完成后）：读取 `tasks.md`，收集仍为 `[ ]` 的 task 项
- [x] 2.2 实现 task 描述解析器：从 task 文本中提取反引号内的文件路径、目录路径等模式
- [x] 2.3 实现文件存在性检测：对每个未标记 task 的提取路径检查文件/目录是否存在
- [x] 2.4 实现自动补标记：将文件存在的 task 从 `- [ ]` 改为 `- [x]`
- [x] 2.5 实现补标记报告输出：显示自动标记数、仍缺失数、总完成度

## 3. new-worktree-apply: Force-add 与 Commit 增强

- [x] 3.1 在 `new-worktree-apply/SKILL.md` 的最终提交步骤中加入 `git add -f openspec/changes/<name>/tasks.md`
- [x] 3.2 修改 commit message 格式为 `feat: implement <name> (N/M tasks)` 或 `feat: implement <name> (X/M tasks, partial)`
- [x] 3.3 实现成功输出中增加 task 完成度汇总

## 4. parall-new-worktree-apply: Agent Prompt 修改

- [x] 4.1 修改 `parall-new-worktree-apply/SKILL.md` Step 4.1 的 Agent prompt：在 `opsx:apply` 指令后增加 post-apply 验证和 `git add -f openspec/changes/<name>/tasks.md` 指令
- [x] 4.2 Agent prompt 中增加补标记逻辑描述：解析 tasks.md 检查 [ ] 项，对比产出文件，自动标记
- [x] 4.3 Agent prompt 中确保 force-add 和 `git add -A` 一起执行，commit message 包含任务完成度

## 5. parall-new-worktree-apply: 合并后验证增强

- [x] 5.1 修改 `parall-new-worktree-apply/SKILL.md` Step 5 串行合并流程：每个分支合并后检查 main 上的 tasks.md 标记状态
- [x] 5.2 实现标记丢失时的兜底逻辑：直接在 main 目录中执行补标记 + `git add -f` + commit
- [x] 5.3 修改 Step 7 验证：重新扫描 tasks.md 时结合文件存在性检测，输出准确的完成度

## 6. parall-new-worktree-apply: Pre-Apply 校验

- [x] 6.1 修改 `parall-new-worktree-apply/SKILL.md` Step 1 Discovery：对每个待执行 change 增加 artifact 完整性检查
- [x] 6.2 实现 artifacts 不完整的 change 自动跳过并在执行计划中标注
