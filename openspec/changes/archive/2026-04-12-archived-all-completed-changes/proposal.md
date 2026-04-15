## Why

项目在持续迭代中积累了多个已完成实施的 OpenSpec changes，但归档操作仍需逐个手动执行。需要一个批量归档工具：自动扫描所有 active changes，识别代码已交付的 changes，一次性完成归档，减少重复操作。

## What Changes

- 新增 `archived-all-completed-changes` skill，实现批量归档流程
- 三维完成判定：tasks.md 全部完成 + 代码文件落地且已 commit 到当前分支 + 依赖完整
- 复用已有 `opsx:archive` skill 执行实际归档操作
- 提供三种确认策略：全部归档 / 逐个确认 / 仅查看

## Capabilities

### New Capabilities
- `completion-scanner`: 扫描所有 active changes 并通过三维模型判定可归档性（tasks 完成 + 代码落地且已提交 + 依赖完整）
- `batch-archive`: 批量调用 opsx:archive 归档已通过判定的 changes，支持全部归档 / 逐个确认 / 仅查看三种策略

### Modified Capabilities
（无）

## Impact

- 新增文件：`archived-all-completed-changes/SKILL.md`（skill 定义）
- 依赖已有 skill：`opsx:archive`（执行实际归档）、`check-changes-completed`（参考其检查逻辑）
- 纯增量变更，不修改任何现有 skill
