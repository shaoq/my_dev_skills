## 1. 安全契约与实施基线

- [x] 1.1 在修改三个 worktree skill 前，使用 GitNexus 分别检查相关文件/可解析符号的 upstream impact，并记录直接依赖、受影响流程和风险等级；HIGH/CRITICAL 时先向用户告警。
- [x] 1.2 将 delta spec 中的统一变量、规范映射、`ARTIFACT_MANIFEST`、`EXPECTED_TARGET_HEAD`、`POST_REBASE_SOURCE_HEAD`、`POST_MERGE_TARGET_HEAD` 和 `CLEANUP_READY` 条件整理成三个 skill 必须逐项复用的实施检查表。
- [x] 1.3 设计隔离临时 Git 仓库场景驱动方式，确保后续验证只操作 `mktemp -d` 下的仓库/worktree，不触碰开发者真实 worktree。

## 2. 加固单 worktree 创建流程

- [x] 2.1 更新 `new-worktree-apply/SKILL.md` 的参数、拓扑和预检：要求目标分支已由注册 worktree 持有且 clean，删除主工作树 checkout/switch、目标 auto-commit 及相关确认文案。
- [x] 2.2 实现并记录规范身份 `proposal=P`、`branch=worktree-P`、`path=<repo>/.claude/worktrees/P` 的精确冲突检查，禁止复用、近似推断、后缀回退和强制删除恢复建议。
- [x] 2.3 在创建前递归构建并复检 `ARTIFACT_MANIFEST`，从冻结 `TARGET_HEAD` 的 commit tree 验证 `.openspec.yaml`、proposal/design/tasks、全部 delta specs 的路径集合和字节内容完全一致。
- [x] 2.4 将实际创建统一为 `git worktree add <absolute-path> -b worktree-<proposal> <TARGET_HEAD>`，禁止使用分支名或不能接受显式 hash 的平台隐式创建机制，并在 apply 前验证注册路径、分支 ref、worktree HEAD 和真实 CWD。
- [x] 2.5 更新创建成功、失败和恢复输出，报告目标/来源精确身份、artifact manifest、冻结 hash 和保留现场，且不建议 `git branch -D`、强制 worktree 删除或换机制重试。

## 3. 加固单 worktree 返回与清理流程

- [x] 3.1 更新 `merge-worktree-return/SKILL.md` 的来源识别：只从当前分支精确移除一个 `worktree-` 前缀，验证可选 proposal 参数、规范路径、worktree 注册、source ref/HEAD 和 artifact 目录的完整映射，并拒绝 source/target 分支或路径相同。
- [x] 3.2 删除为目标分支切换主工作树的路径，要求目标已经由 clean worktree 持有，并在确认、rebase 前、merge 前和 cleanup 前重复验证目标路径、分支、ref、HEAD 与真实 CWD。
- [x] 3.3 在规范来源 worktree 中提交授权改动并 rebase；成功后冻结 `POST_REBASE_SOURCE_HEAD`，验证 source clean、HEAD/ref 相等且存在非空的明确 delivery commit 集合。
- [x] 3.4 将目标 merge 输入改为精确 `POST_REBASE_SOURCE_HEAD`，记录 `POST_MERGE_TARGET_HEAD`，禁止按活跃 source branch ref 合并、验证失败后自动重试以及成功 merge 后自动 reset/revert。
- [x] 3.5 实现完整 `POST_MERGE_VERIFICATION` 和 `CLEANUP_READY` 合取门槛，对每个 false/unknown/命令错误条件失败关闭并报告精确 hashes 与保留对象。
- [x] 3.6 仅在 cleanup 全部就绪时从目标真实 CWD 执行普通 `git worktree remove <exact-path>` 和安全 `git branch -d -- <exact-branch>`；路径锁、进程占用或普通删除失败时保留现场，不调用平台强制清理。

## 4. 加固并行 Wave/Batch 生命周期

- [x] 4.1 更新 `parall-new-worktree-apply/SKILL.md` 的 Discovery、目标拓扑和确认摘要：禁止 target checkout/auto-commit，并为每个待执行 change 递归验证含实际 `dependencies.yaml` 的 artifact manifest。
- [x] 4.2 为控制器引入 `EXPECTED_TARGET_HEAD`，仅在本控制器的串行 merge 通过完整验证后推进；每个 Batch 前要求 target ref 和 target worktree HEAD 精确等于该期望值。
- [x] 4.3 将每个 Worker 的身份统一为 `worktree-<change>` 与规范绝对路径，并从同一冻结 `BATCH_TARGET_HEAD` hash 显式创建；已有 ref/path/worktree 或平台无法维持正确 CWD 时保留现场并停止，不复用或降级。
- [x] 4.4 在每个成功 Worker 的规范 source worktree 内完成 rebase 和 `POST_REBASE_SOURCE_HEAD` 冻结，merge 前重新验证注册关系、分支、HEAD/ref、clean 状态和 target snapshot。
- [x] 4.5 串行 merge 每个冻结 source commit，并为每个 child 独立执行 post-merge 验证与 `CLEANUP_READY`；child 漂移、验证或普通删除失败时保留该 child，不影响已安全完成项但禁止对失败项自动重试 merge。
- [x] 4.6 更新 Wave/Batch 报告，逐项显示 canonical mapping、artifact manifest、target/source hashes、merge 次数、cleanup gate 和保留 worktree/branch，保持并发上限 3 与依赖排序不变。

## 5. 规范、文档与危险命令一致性

- [x] 5.1 更新 `README.md` 的创建、并行、返回示例和生命周期图，使用 `worktree-<proposal>`、commit-hash 创建、目标已持有要求和失败保留语义。
- [x] 5.2 检查权限/命令说明及相关文档，移除任何把 checkout/switch、目标 auto-commit、平台隐式 cleanup 或强制删除描述为正常恢复路径的内容。
- [x] 5.3 静态扫描三个 skill、README 和本 change delta spec（归档时合入现行 spec），确认不存在 `git worktree remove --force`、`git branch -D`、`git update-ref -d`、无前缀来源分支创建、按目标分支名创建、成功 merge 自动回滚或验证失败自动 merge 重试。
## 6. 隔离场景验证与交付检查

- [x] 6.1 在临时仓库验证目标分支未被 worktree 持有、目标由其他路径持有、目标 dirty、detached HEAD 和目标注册/HEAD/ref 漂移均失败关闭且不修改既有 worktree。
- [x] 6.2 验证规范映射成功路径，以及已有 `worktree-<proposal>`、已有规范目录、已注册路径、旧无前缀分支、显式 proposal 不匹配时均不复用、不加后缀、不清理。
- [x] 6.3 验证 artifact manifest 对未提交、ignored、新增、删除、内容不同、嵌套 delta specs、空 spec 集和 `dependencies.yaml` 单侧缺失/差异均给出预期结果。
- [x] 6.4 模拟确认后 target ref 推进，证明实际 child 仍只能从冻结 hash 创建；模拟未经控制器归因的 Batch target 推进，证明后续 spawn/merge 被阻止。
- [x] 6.5 模拟 rebase 后 Worker 新提交、source dirty、source ref/HEAD 分叉、worktree 注册漂移、target ref/HEAD 分叉和无 delivery commit，确认 merge 或 cleanup 被阻止且来源现场保留。
- [x] 6.6 验证完整成功 merge/cleanup、post-merge 验证失败、source-only 新提交、普通 worktree remove 因锁失败和安全 branch deletion 拒绝等路径，确认只有全部 `CLEANUP_READY` 为 true 才删除。
- [x] 6.7 运行 OpenSpec 严格校验、Markdown/命令静态检查及适用的项目验证；实施完成且提交前运行 `gitnexus_detect_changes()`，确认只影响预期 worktree lifecycle 文件与流程。
