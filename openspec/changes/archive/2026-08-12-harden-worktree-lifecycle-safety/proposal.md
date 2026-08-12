## Why

现有 worktree 创建、并行实施和返回流程仍会切换或自动提交其他现有 worktree，按可变分支名创建基线，并在只验证分支包含关系后过早删除来源 worktree。并发会话下，这些行为可能从未经确认的 HEAD 创建分支、遗漏或错用 OpenSpec artifacts、合并 rebase 后漂移的提交，甚至删除尚未完成交付的工作现场。

## What Changes

- **BREAKING**：禁止为了满足目标分支条件对主工作树或其他现有 worktree 执行 `git checkout`/`git switch`；目标分支必须已经被一个已注册 worktree 精确持有，所有权或映射不满足时失败关闭。
- **BREAKING**：统一映射为 `proposal=<name>`、`branch=worktree-<name>`、`path=.claude/worktrees/<name>`；禁止无前缀分支、近似推断、冲突后追加后缀、复用既有分支或 worktree。返回流程只可精确移除一个 `worktree-` 前缀并重新验证完整映射。
- 创建前冻结 `TARGET_BRANCH` 到不可变的 `TARGET_HEAD`，并要求所有创建命令使用该 commit hash，而不是在确认后重新解析分支名。并行流程为每个 Batch 冻结 `BATCH_TARGET_HEAD`，同时拒绝无法归因于本控制器已验证 merge 的目标漂移。
- 在创建任何 worktree 前，验证 `.openspec.yaml`、`proposal.md`、`design.md`、`tasks.md`、完整 delta spec 文件集，以及并行流程使用的 `dependencies.yaml` 已存在于冻结的目标提交中，且路径集合与内容和用户确认时的工作区完全一致。
- rebase 后冻结 `POST_REBASE_SOURCE_HEAD`；merge 前重新验证来源/目标 worktree 注册关系、分支、HEAD、ref 和 clean 状态，并只合并冻结的 commit hash。
- 引入失败关闭的 `CLEANUP_READY` 门槛。仅当控制器真实 CWD 位于目标 worktree、来源干净且具有明确交付提交、merge 成功、目标 ref/HEAD 一致、目标包含精确的 post-rebase 来源快照、不存在额外 source-only commits、且 post-merge 验证全部通过时，才允许删除来源 worktree 和本地分支。
- 禁止强制 worktree/分支/ref 清理、自动 reset/revert 已完成 merge，以及验证失败后的自动 merge 重试。普通删除因路径锁、活跃进程或其他原因失败时保留现场。
- 为单 change 与并行 Wave/Batch 流程增加隔离临时仓库场景验证，覆盖并发 ref 漂移、artifact 差异、映射冲突、post-rebase 漂移和清理失败。
- 明确排除 Codex launcher、`codex exec` 参数探测及权限模式选择；该问题不属于本变更范围。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `worktree-targeting`：将目标选择、不可变创建基线、OpenSpec artifact 一致性、规范化 worktree 身份、rebase/merge 快照以及清理就绪条件升级为完整的失败关闭生命周期契约。

## Impact

- 受影响的 skill：`new-worktree-apply/SKILL.md`、`merge-worktree-return/SKILL.md`、`parall-new-worktree-apply/SKILL.md`。
- 受影响的规范与文档：`openspec/specs/worktree-targeting/spec.md`、`README.md`，以及与 worktree 命令权限说明直接相关的配置文档。
- 用户可见影响：旧的无前缀来源分支和不符合规范路径的既有 worktree 将不能自动复用或清理；目标分支未被 worktree 持有、artifacts 未提交或内容不同、以及任何验证不确定时，流程都会保留现场并要求人工处理。
- 不引入新运行时依赖，不修改 OpenSpec proposal 拆分、Codex launcher 或并行上限。
