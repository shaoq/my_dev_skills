## Why

当多个 OpenSpec 提案同时处于待实施状态时，逐个串行执行效率低下。需要一个编排层 skill，自动发现所有待执行的 changes，解析它们的依赖关系，将无依赖的 changes 并行在隔离 worktree 中实施，有依赖的按序执行，最终将所有成果合并回主干并验证完成状态。

## What Changes

- 新建 `parall-new-worktree-apply` skill，作为编排层封装多提案并行执行流程
- 支持自动扫描 `openspec/changes/*/tasks.md`，通过检测 `[ ]` 未完成项识别待执行 changes
- 支持解析 `proposal.md` 中的 `## Dependencies` 段构建依赖图
- 支持拓扑排序生成分波次执行计划（Wave），无依赖的 changes 在同一 Wave 内并行
- 支持 Wave 内通过 `Agent` 工具 + `isolation: "worktree"` 并行 spawn 子代理执行 `/opsx:apply`
- 支持 Wave 间串行合并：每个 Wave 完成后将所有分支 rebase + merge 回 main
- 支持 rebase 冲突时 Claude 智能分析和自动解决
- 支持单个 change 时的简化路径：直接委托 `new-worktree-apply` skill 执行
- 支持全部完成后重新扫描 tasks.md 验证所有 changes 已完成

## Dependencies

- new-worktree-apply
- merge-worktree-return

## Capabilities

### New Capabilities
- `change-discovery`: 扫描 OpenSpec changes 目录，识别待执行提案（含未完成任务的 changes），解析依赖关系并构建依赖图
- `wave-execution`: 基于依赖图进行拓扑排序，按 Wave 分组并行执行，每个 Wave 完成后串行合并回主干
- `conflict-resolution`: rebase 冲突时智能分析冲突标记，自动解决可合并的冲突
- `completion-verification`: 全部实施完成后重新扫描 tasks.md 验证所有 changes 状态

### Modified Capabilities
（无）

## Impact

- 新增 skill 文件：`parall-new-worktree-apply/SKILL.md`
- 依赖：`new-worktree-apply` skill（单个 change 时委托执行）、`Agent` 工具（并行执行）、`openspec-apply-change` skill（子代理调用）、git
- 影响：用户工作流从手动逐个执行变为一条命令 `/parall-new-worktree-apply` 自动编排全部待执行提案
