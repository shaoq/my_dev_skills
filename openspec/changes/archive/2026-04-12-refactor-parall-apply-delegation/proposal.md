## Why

`parall-new-worktree-apply` 的 Agent prompt 中重复了 `new-worktree-apply` 步骤 7-10 的全部逻辑（Artifact 校验、Task Backfill、Force-add commit），两处维护同一套命令，容易因只改一边而造成行为不一致。

## What Changes

- 修改 `parall-new-worktree-apply` SKILL.md 中 Agent prompt 的步骤 2-3，将内联的 Artifact 校验、Task Backfill、Force-add commit 逻辑替换为：指示 Agent 用 Read 工具读取 `new-worktree-apply/SKILL.md`，然后按其中的步骤 7-10 执行后处理
- `new-worktree-apply` SKILL.md 本身无需修改（它作为被引用的权威源）

## Capabilities

### New Capabilities
（无）

### Modified Capabilities
- `apply-postprocessing-delegation`: parall Agent prompt 中 apply 后处理逻辑改为委托读取 new-worktree-apply SKILL.md 执行，消除重复指令

## Impact

- 修改文件：`parall-new-worktree-apply/SKILL.md`（Agent prompt 部分）
- 依赖关系：parall-new-worktree-apply 运行时依赖 `new-worktree-apply/SKILL.md` 文件可被 Read 工具读取
- 无 API / 依赖变更
