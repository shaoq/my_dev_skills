## Context

项目通过三个 Markdown skill 管理同一条 worktree 生命周期：`new-worktree-apply` 创建并实施单个 OpenSpec change，`merge-worktree-return` rebase、merge 并回收单个来源 worktree，`parall-new-worktree-apply` 按依赖 Wave/Batch 创建多个来源 worktree并串行合并。它们共享 Git refs、worktree 注册表、OpenSpec artifacts 和目标工作树，因此局部修补任何一个阶段都可能在相邻阶段留下不兼容或破坏性行为。

当前契约有七类安全缺口：会为目标分支切换或自动提交既有 worktree；确认后仍按可变分支名创建；只验证当前文件系统中的部分 artifacts；proposal、来源分支和路径没有规范映射；清理只依赖较弱的 containment；错误提示仍建议强制删除；rebase 后没有冻结和重新验证来源快照。Git 的 ref、worktree HEAD、工作区状态和真实 CWD 可被并发会话独立改变，任何只检查其中一项的流程都不足以证明交付完成。

本变更修改既有 `worktree-targeting` capability，并要求三个 skill 原子迁移。OpenSpec artifacts 是设计主文档；不额外创建 `docs/superpowers` 设计文件，也不在提案阶段提交 Git commit。

## Goals / Non-Goals

**Goals:**

- 禁止流程切换、自动提交或以其他方式改写目标分支所在的现有 worktree 来满足前置条件。
- 用不可变 commit hash 创建每个来源 worktree，并在写操作前后验证 ref、HEAD、路径和分支身份。
- 证明用户确认的全部 OpenSpec artifact 路径集合和内容已经存在于冻结的目标提交中。
- 为 proposal、来源分支、来源 worktree 建立可逆且唯一的规范映射。
- 在 rebase 后冻结精确来源提交，只 merge 该 commit，并阻止 rebase 后来源漂移进入目标。
- 将清理定义为显式 `CLEANUP_READY` 合取门槛；任何未知、失败或漂移均保留来源 worktree 和分支。
- 单 change 与并行流程采用同一套身份、快照、merge 和清理语义，并通过隔离临时仓库场景测试。

**Non-Goals:**

- 不设计或引入 Codex launcher、`codex exec` 参数探测、审批模式或失败重试逻辑。
- 不改变 OpenSpec change 拆分、任务回填的业务含义、Wave 依赖算法或每 Batch 最多 3 个并发的限制。
- 不 fetch、pull、push，不创建目标分支，不删除远程 ref。
- 不自动 reset/revert 已完成的 merge，不在验证失败后重试 merge。
- 不引入常驻 daemon、锁服务或新的外部运行时依赖。

## Decisions

### 1. 一个原子变更覆盖完整生命周期

本变更同时修改三个 skill、现有 `worktree-targeting` delta spec、README 和场景验证。创建端一旦采用 `worktree-<proposal>`，返回端和并行端必须在同一版本理解该映射；清理门槛也依赖创建与 rebase 阶段记录的同一组身份和快照概念。

备选方案一是按创建、返回、并行拆成三个提案。它能缩小每个 diff，但会产生无前缀/有前缀映射混用、旧返回流程删除新来源 worktree等危险中间状态，因此拒绝。备选方案二是新增共享 shell/Python runtime 集中执行全部 Git 操作；它可减少文本重复，但扩大运行时和跨平台测试范围。本次采用“一个规范契约 + 三个 skill 内相同的低自由度检查序列”，不新增 runtime。

### 2. 目标分支必须已由注册 worktree 持有，且流程不改写它来满足前置条件

目标选择仍保留显式 `--target`、主工作树当前分支、`origin/HEAD` 本地同名分支、`main/master/trunk` 的候选优先级，但选出的 `TARGET_BRANCH` 必须在 `git worktree list --porcelain` 中精确映射到一个 `TARGET_WORKTREE_DIR`。若没有持有者，流程停止并要求用户自行准备目标 worktree；不得 checkout/switch 主工作树、不得创建临时目标 checkout、不得选择其他候选来掩盖显式目标失败。

三个 skill 对目标 worktree 只进行契约允许的动作：创建流程只读目标状态并从目标 ref 的冻结 hash 创建新 worktree；返回/并行流程仅在控制器真实 CWD 已进入已确认目标 worktree、目标 clean 且身份复检通过后执行明确授权的 merge。所有目标 auto-commit 路径删除，避免提交其他会话的文件。

目标 worktree dirty、路径映射变化、当前分支/HEAD 与 ref 不一致或无法建立真实 CWD 时都失败关闭。无法可靠判断“另一个人是否正在使用”某个 clean worktree，因此本设计用“不切换、不自动提交、合并前真实进入并重复验证”作为可执行的所有权边界。

### 3. proposal、分支和路径采用唯一规范映射

对合法 proposal `P` 定义：

```text
PROPOSAL          = P
SOURCE_BRANCH     = worktree-P
SOURCE_WORKTREE   = <REPO_ROOT>/.claude/worktrees/P
```

创建前必须同时证明 `refs/heads/worktree-P` 不存在、规范路径不存在且未注册为 worktree。任一冲突都停止；不添加数字/随机后缀，不复用或接管现有 ref/path。

返回流程从当前来源分支只允许精确移除一次开头的 `worktree-` 得到候选 proposal，再验证：候选符合命名规则、artifact 目录存在、当前 worktree 的真实路径等于规范路径、分支 ref/HEAD 与 worktree 注册记录一致。若命令显式传入 proposal，它还必须与候选完全相等。没有精确前缀或任一映射不一致都不得 merge 或 cleanup。

保留返回命令 proposal 参数可选，是为了不破坏无参数用法；这不是目录近似推断，因为唯一来源是精确分支前缀，并且之后必须完成全映射验证。

### 4. 用 artifact manifest 证明确认内容已提交到冻结基线

每个 change 建立 `ARTIFACT_MANIFEST`，至少包含：

- `openspec/changes/P/.openspec.yaml`
- `proposal.md`
- `design.md`
- `tasks.md`
- `specs/` 下递归发现的全部 delta spec 文件，并至少包含一个 `spec.md`
- 并行计划实际读取 `dependencies.yaml` 时的该文件；无依赖且当前工作区与目标提交均不存在该文件时，明确记录为“双方均缺省”，不能把单侧缺失解释为无依赖

预检从当前确认内容和 `TARGET_HEAD` 两侧独立枚举路径，要求集合完全相等，再逐文件做字节级内容比较。目标侧通过 commit tree（例如 `git ls-tree`/`git show`/`git cat-file`）读取，不能依赖目标工作区；当前侧即使是 untracked 或 ignored 文件也会进入枚举，因此只要未存在于 `TARGET_HEAD` 就会阻止创建。新增、删除、重命名、内容差异、读取错误或空 delta spec 集合均为硬失败。

确认摘要展示 `TARGET_HEAD`、manifest 路径和稳定摘要值。确认后、首次写操作前再次生成并比较同一 manifest；写操作开始后不再刷新为新的用户基线。

备选方案是继续 auto-commit artifacts 后刷新 `TARGET_HEAD`。这会在确认后制造新 commit，并可能连带提交其他会话文件，因此拒绝。

### 5. 所有创建都使用不可变 commit hash

单 change 在确认和复检后执行等价命令：

```bash
git worktree add <absolute-source-path> -b worktree-<proposal> <TARGET_HEAD>
```

并行流程为每个 Batch 在目标身份验证通过后冻结 `BATCH_TARGET_HEAD`，对 Batch 内每个 child 使用相同 hash：

```bash
git worktree add <absolute-child-path> -b worktree-<change> <BATCH_TARGET_HEAD>
```

不得把 `<TARGET_BRANCH>` 传给实际创建命令。创建后要求 worktree 注册路径、当前分支、branch ref 和 worktree HEAD 全部精确匹配预期 hash，随后才可 apply。不能接受显式 start-point 的平台创建机制不得替代该命令；若平台不能把后续执行上下文可靠地放入新 worktree，则停止并保留已创建现场，不自动删除或换机制重试。

并行控制器维护 `EXPECTED_TARGET_HEAD`。每次自身成功 merge 后将其更新为已验证的 target HEAD；下一个 Batch 只在 target ref 和 target worktree HEAD 均等于该期望值时冻结新基线。这样允许控制器自身已验证的推进，同时拒绝外部并发提交。

### 6. rebase 和 merge 使用冻结的来源快照

来源提交完成后，在来源 worktree 内执行 rebase。成功后立即记录 `POST_REBASE_SOURCE_HEAD`，并验证：

- 来源 worktree 仍以规范路径注册；
- 当前真实 CWD、当前分支和规范映射一致；
- source worktree HEAD 与 `refs/heads/SOURCE_BRANCH` 都等于 `POST_REBASE_SOURCE_HEAD`；
- source clean；
- 相对目标存在非空的明确交付提交集合，并在确认/报告中列出 hash 与 subject；
- target ref 与 target worktree HEAD 仍等于预期的 pre-merge target snapshot。

控制器随后真实进入 `TARGET_WORKTREE_DIR`，再次验证目标路径、分支、HEAD/ref、clean 状态以及来源完整快照。merge 的输入是 `POST_REBASE_SOURCE_HEAD`，不是可继续移动的分支名：

```bash
git merge <POST_REBASE_SOURCE_HEAD>
```

merge 完成后记录 `POST_MERGE_TARGET_HEAD`。来源 ref 后续若被 Worker 推进，不会混入本次 merge，并会使清理门槛中的“来源 ref 仍等于冻结快照”和“无 source-only commits”失败，从而保留来源现场。

并行流程对每个成功 Worker 串行执行相同步骤。开始 rebase 前也要验证 child worktree 仍注册、在规范分支、HEAD/ref 一致且 clean，避免依赖平台自动清理或在目标 worktree 中操作仍被别处持有的来源分支。

### 7. `CLEANUP_READY` 是删除前的显式合取状态机

清理不得由“会话离开来源目录”或单独的 `git log target..source` 推导。对每个来源定义：

```text
CLEANUP_READY =
  REAL_CWD_IS_TARGET_WORKTREE
  AND SOURCE_MAPPING_EXACT
  AND SOURCE_CLEAN
  AND SOURCE_HAS_DELIVERY_COMMITS
  AND SOURCE_HEAD_REF_EQUAL_POST_REBASE_SOURCE_HEAD
  AND MERGE_SUCCEEDED_ONCE
  AND TARGET_REF_EQUALS_TARGET_WORKTREE_HEAD
  AND TARGET_CONTAINS_POST_REBASE_SOURCE_HEAD
  AND NO_SOURCE_ONLY_COMMITS
  AND POST_MERGE_VERIFICATION_PASSED
```

每个布尔量都由显式命令成功结果产生，不允许把命令错误、空输出解析失败或未知状态当作 true。任一条件为 false/unknown，立即停止该来源的 cleanup，保留 worktree 和分支，并输出失败条件、冻结 hashes 和恢复信息。

`POST_MERGE_VERIFICATION` 至少包括目标身份/clean 检查、精确 commit containment、artifact/OpenSpec 状态检查、`git diff --check`，以及在实施阶段确定并在 merge 前展示的项目级测试或验证命令。任何必需命令无法确定或无法执行时，cleanup 不就绪。

只有所有条件成立，才从目标真实 CWD 执行：

```bash
git worktree remove <exact-source-path>
git branch -d -- worktree-<proposal>
```

先普通移除 worktree；移除失败即保留分支。分支删除前再次验证目标包含冻结来源 commit。Windows 路径锁、进程占用、平台目录锁或普通删除拒绝都只报告并保留现场。

### 8. 失败处理不扩大破坏面

禁止 `git worktree remove --force`、`git branch -D`、`git update-ref -d` 以及等价强制清理；错误输出和 recovery 文本也不得建议这些命令。不能用不透明的强制平台清理替代普通 Git 删除。

rebase 尚未成功时允许 `git rebase --abort` 恢复未完成的 rebase；merge 冲突尚未形成完成提交时允许安全中止该未完成操作。merge 一旦成功，不自动 reset/revert；post-merge 验证失败时保留 target merge、来源 worktree 和分支，报告人工决策点。任何 merge 失败或验证失败都不得自动换参数或重试 merge。

这一区分保留了未完成 Git 操作的安全退出能力，同时避免把已完成集成在用户不知情时回滚。

### 9. 场景矩阵验证规范与 skill 一致性

实现阶段在 `mktemp -d` 创建隔离仓库和多个 worktree，验证至少以下场景：目标未被 worktree 持有；目标在其他路径持有；目标 dirty；确认后 target ref 漂移；artifact 未提交、ignored、新增、删除、内容差异和嵌套 delta specs；依赖文件单侧缺失；规范映射成功；旧无前缀分支、路径冲突和已有 branch 冲突；rebase 后 Worker 新增提交；target ref/HEAD 分叉；无交付提交；post-merge 验证失败；普通删除因锁失败；完整成功清理。

静态检查同时禁止危险命令和分支名模式，核对 README、现行 spec 与三个 skill 使用相同变量和状态门槛。测试不操作开发者真实 worktree。

## Risks / Trade-offs

- **[目标分支未检出时流程更严格]** → 明确失败并输出用户自行创建目标 worktree 的恢复步骤，不再牺牲其他会话上下文换取便利。
- **[未提交 proposal 无法直接创建实施 worktree]** → 这是有意的安全边界；先由用户在目标分支明确提交 artifacts，再重新确认其 commit hash。
- **[旧 worktree 命名不兼容]** → 标记 BREAKING；旧无前缀分支只报告人工迁移，不自动重命名、复用或删除。
- **[平台原生 worktree 工具可能无法接受 hash]** → 使用显式 Git CLI；平台无法维持后续 CWD 时停止并保留现场，不降级到隐式基线。
- **[检查与 skill 文本明显增加]** → 通过统一变量名、相同状态表达式、现行 spec 和场景矩阵降低漂移，不引入难以审计的隐式 helper。
- **[成功 merge 后验证失败会留下已合并 target 和来源现场]** → 明确报告 hashes 和失败条件，禁止自动回滚；由用户决定修复、继续验证或人工回退。
- **[无法彻底消除检查与删除之间的极短并发窗口]** → 删除前立即重复 ref/HEAD/clean/mapping 检查，所有命令绑定精确路径/hash；不声称提供跨进程事务锁。

## Migration Plan

1. 先更新 `worktree-targeting` delta requirements，确定目标持有、规范映射、artifact manifest、不可变创建、merge 快照和 `CLEANUP_READY` 契约。
2. 同步修改 `new-worktree-apply`：删除目标 checkout/auto-commit和无前缀命名，创建前验证 artifacts，并以 `TARGET_HEAD` hash 创建。
3. 修改 `merge-worktree-return`：严格反解/验证映射，在 source 内 rebase 并冻结 hash，只 merge 冻结 commit，最后通过完整清理门槛。
4. 修改 `parall-new-worktree-apply`：每 Batch 维护可归因的 `EXPECTED_TARGET_HEAD`，对每个 child 使用相同创建与返回状态机，移除 checkout 恢复和隐式平台 cleanup 假设。
5. 更新 README 和相关权限/命令说明，删除所有强制清理建议。
6. 在隔离临时仓库运行静态检查和完整场景矩阵；不得用当前开发 worktree 作为测试目标。

回滚必须同时回滚三个 skill、现行 spec 和文档。不得只恢复其中一个命名或清理阶段。若新流程已经创建 `worktree-` 分支，回滚本身不自动改名或删除这些 worktree。

## Open Questions

无。单一原子提案、排除 launcher、规范映射、commit-hash 创建、artifact 精确一致、post-rebase 快照和失败关闭清理边界均已确认。
