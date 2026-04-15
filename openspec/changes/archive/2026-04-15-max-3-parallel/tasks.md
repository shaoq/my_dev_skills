## 1. parall-new-proposal — 颗粒度阈值调整

- [x] 1.1 修改 `parall-new-proposal/SKILL.md` Step 2.3 颗粒度检测：将 `≤2 建议 / 3-8 正常 / >8 警告` 改为 `≤1 建议 / 2-6 正常 / >6 警告`

## 2. parall-new-proposal — 新增批次划分

- [x] 2.1 在 `parall-new-proposal/SKILL.md` Step 3.3 之后新增 Step 3.4 Wave 内批次划分：按字母序排列，每批最多 3 个切分，标注执行策略（同批并行、不同批串行、每批完成后立即合并）
- [x] 2.2 修改 `parall-new-proposal/SKILL.md` Step 4.1 展示示例：子方案列表表格增加 Batch 列，依赖图改为含 Batch 栄注的执行计划格式
- [x] 2.3 修改 `parall-new-proposal/SKILL.md` Step 7.1 总结报告模板：表格增加 Batch 列，依赖图标注 Batch 边界

## 3. parall-new-proposal — Guardrails 更新

- [x] 3.1 修改 `parall-new-proposal/SKILL.md` Guardrails：将 `≤2 建议` 改为 `≤1 建议`，将 `超过 8 个警告` 改为 `超过 6 个警告`，新增"每 Wave 并行上限为 3"和"每 Batch 完成后立即合并"约束

## 4. parall-new-worktree-apply — 展示计划含 Batch

- [x] 4.1 修改 `parall-new-worktree-apply/SKILL.md` Step 2.5 展示执行计划：从 `Wave (并行: N)` 改为 `Wave → Batch (并行: ≤3)` 格式

## 5. parall-new-worktree-apply — Step 4 重构为批次循环

- [x] 5.1 重写 `parall-new-worktree-apply/SKILL.md` Step 4：新增 Step 4.1 批次划分（MAX_PARALLEL=3），原 Step 4.1 并行 Spawn 改为 Step 4.2 Batch 执行循环内的 Step 4.2.1
- [x] 5.2 在 Step 4 Batch 执行循环中新增 Step 4.2.4 合并当前 Batch：每个 Batch 所有 Agent 完成后立即调用 Step 5 合并流程
- [x] 5.3 新增 Step 4.3 Wave 完成：当前 Wave 所有 Batch 执行并合并完毕后进入下一个 Wave

## 6. parall-new-worktree-apply — Step 5 合并时机调整

- [x] 6.1 修改 `parall-new-worktree-apply/SKILL.md` Step 5 开头描述：从"每个 Wave 完成后"改为"由 Step 4.2.4 调用，每个 Batch 完成后"

## 7. parall-new-worktree-apply — Guardrails 更新

- [x] 7.1 修改 `parall-new-worktree-apply/SKILL.md` Guardrails：将"Agent spawn 必须在同一消息中并行"改为"同一 Batch 内的 Agent spawn 必须在同一消息中并行"，新增"每 Wave 并行上限为 3"和"每个 Batch 完成后立即合并"

## 8. README.md 文档同步

- [x] 8.1 修改 `README.md` parall-new-proposal 注意事项：`超过 8 个警告` → `超过 6 个警告`，新增"每 Wave 并行上限为 3"
- [x] 8.2 修改 `README.md` parall-new-worktree-apply 注意事项：新增"每 Wave 最多 3 个并行 Agent，超出自动分 Batch"，将"合并必须串行"改为"每个 Batch 完成后立即合并"
