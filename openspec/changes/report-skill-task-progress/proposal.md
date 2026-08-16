## Why

`new-worktree-apply` 和 `parall-new-proposal` 的最终总结不能一致地回答提案任务完成了多少、剩余任务为何未完成，用户需要额外打开各提案的 `tasks.md` 才能判断实施状态。

## What Changes

- 为两个 skill 的最终总结增加只包含数量的任务进度：已完成任务数、总任务数、剩余任务数及可计算时的完成百分比。
- 为未完成任务增加基于执行证据的原因归类和概要说明，不输出逐条 task 明细。
- 明确未知状态处理：`tasks.md` 缺失、不可读或没有可识别 checkbox 时不得误报为完成。
- `parall-new-proposal` 同时输出各成功提案与全部成功提案的聚合进度；创建失败或进度未知的提案单独说明。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `worktree-targeting`: 规范 `new-worktree-apply` 在 apply 后的任务数量进度与未完成原因概要输出。
- `batch-concurrency-control`: 规范 `parall-new-proposal` 批量创建后的逐提案及聚合任务进度输出。

## Impact

- 修改 `new-worktree-apply/SKILL.md` 的任务核对和成功总结契约。
- 修改 `parall-new-proposal/SKILL.md` 的总结报告和错误状态契约。
- 不改变 Git/worktree 操作、OpenSpec artifact 生成、Wave/Batch 规划或实施逻辑。
