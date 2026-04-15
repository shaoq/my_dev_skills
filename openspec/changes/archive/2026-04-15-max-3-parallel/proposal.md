## Why

当前 `parall-new-proposal` 和 `parall-new-worktree-apply` 对并发数量没有上限控制。Wave 内的 changes 数量决定了并行 Agent 数量，过多并发会导致：资源竞争（CPU/内存/API rate limit）、合并冲突概率激增、串行合并阶段耗时过长。实际测试表明，3 个并行 Agent 是效率与稳定性的最佳平衡点。

## What Changes

- `parall-new-proposal` 颗粒度阈值从 `3-8 正常 / >8 警告` 调整为 `2-6 正常 / >6 警告`
- `parall-new-proposal` 新增 Step 3.4 Wave 内批次划分（每批最多 3 个），在规划阶段即预览 Batch 划分
- `parall-new-proposal` 展示方案和总结报告增加 Batch 列和执行计划
- `parall-new-worktree-apply` Step 4 重构为 Wave → Batch 两层循环，每 Batch 最多 3 个并行 Agent
- `parall-new-worktree-apply` 采用方案 A：每个 Batch 完成后立即合并回主干，再执行下一个 Batch
- `parall-new-worktree-apply` Step 5 合并时机从"每 Wave 完成后"改为"每 Batch 完成后"
- `README.md` 同步更新注意事项描述

## Capabilities

### New Capabilities

- `batch-concurrency-control`: 并发上限控制与批次划分。Wave 内按字母序切分为每批最多 3 个的 Batch，同 Batch 并行执行，不同 Batch 串行执行，每 Batch 完成后立即合并

### Modified Capabilities

（无已有 spec 需要修改）

## Impact

- 修改文件：`parall-new-proposal/SKILL.md`、`parall-new-worktree-apply/SKILL.md`、`README.md`
- 不影响其他 skill（new-worktree-apply、merge-worktree-return、check-changes-completed、verify-impl-consistency）
- `dependencies.yaml` 格式不变，向后兼容
- 对用户工作流无破坏性变更，仅影响并行策略的内部行为
