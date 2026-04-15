## Why

当前 OpenSpec 工作流中，判断一个 change 是否可以存档需要在 `openspec-archive-change` 中逐个检查，缺乏全局视角。当多个 changes 并行推进时，无法一目了然地看到所有 changes 的整体健康状态，也缺少对"tasks 勾了但代码没落地"这类虚假完成情况的检测。需要一个独立的全局检查 skill，通过四维检查模型全面评估每个 change 的完成情况，并为可存档的 changes 提供批量存档引导。

## What Changes

- 新建 `check-changes-completed` skill，提供全局 OpenSpec changes 完成度检查
- 支持四维检查模型：
  - 维度 1 — Tasks 完成度：解析 tasks.md，统计 `[x]` / `[ ]` 计数和比例
  - 维度 2 — Artifacts 齐全性：通过 `openspec status --json` 检查所有 artifacts 是否 done
  - 维度 3 — Code 落地验证：检查设计中提及的产出文件是否存在 + git log 中是否有实质提交
  - 维度 4 — 依赖完整性：解析 proposal.md 的 `## Dependencies` 段，验证依赖链中所有 change 的完成状态
- 支持汇总表格输出，每个 change 标记"可存档 / 不可存档"及阻塞原因
- 支持检查完毕后对可存档 changes 提供批量存档引导（调用 `openspec-archive-change` skill）
- 与 `parall-new-worktree-apply` 互补：parall 是执行后验证，本 skill 是独立全局检查

## Capabilities

### New Capabilities
- `completion-scanner`: 扫描所有 active changes，逐个执行四维检查，汇总为结构化报告
- `archive-guidance`: 基于检查结果，识别可存档的 changes 并引导用户逐个或批量存档

### Modified Capabilities
（无）

## Impact

- 新增 skill 文件：`check-changes-completed/SKILL.md`
- 依赖：`openspec` CLI（status 指令）、git（log 验证）、`openspec-archive-change` skill（存档引导）
- 影响：为用户提供一条命令 `/check-changes-completed` 即可全局掌握所有 changes 健康状态
