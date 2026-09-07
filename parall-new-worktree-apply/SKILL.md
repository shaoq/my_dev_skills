---
name: parall-new-worktree-apply
description: Implement multiple selected pending OpenSpec changes in dependency-aware isolated worktrees after one confirmed batch plan.
argument-hint: "[--target <target-branch>]"
---

按依赖 Wave/Batch 并行实施所有待执行 OpenSpec changes。

## 核心不变量

- Step 0–4 只读：确认前不产生 Git 写操作、不 spawn Worker、不调用 apply。
- 目标分支必须已经由唯一、注册、clean 的 `TARGET_WORKTREE_DIR` 持有；不 checkout/switch 或 auto-commit 任何现有 worktree。
- 控制器维护 `EXPECTED_TARGET_HEAD`；只有本控制器一次成功且完整验证的 serial merge 才能推进它。
- 每个 Batch 冻结一个 `BATCH_TARGET_HEAD`；同 Batch 所有 child 从该 commit hash 创建。
- 每个 change 的规范身份：
  ```text
  SOURCE_BRANCH=worktree-<change-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<change-name>
  ```
- 每个 Worker rebase 后冻结独立 `POST_REBASE_SOURCE_HEAD`；Controller 只 merge 该 commit hash，不 merge 活跃 source branch name。
- 每个 child 独立计算完整 `CLEANUP_READY`；false/unknown/命令错误时保留该 child worktree 和 branch。
- 每个 child 在 apply 后独立计算 `TASK_CLEANUP_POLICY_PASSED`：普通未完成任务阻止交付与 cleanup；只有精确标签 `[post-merge-verification]` 的延期任务不阻止结构性交付、cleanup 或依赖 Wave。
- 不自动 reset/revert 已完成 merge，不自动重试失败或未验证 merge，不使用强制 cleanup。

## Step 0：参数、仓库、目标与控制器上下文（只读）

仅接受至多一个 `--target <target-branch>`；任何位置参数、未知选项、缺值或重复选项都报错并零写退出。

读取：

```bash
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
git worktree list --porcelain
```

按显式 `--target`、主工作树 porcelain 记录中的命名分支（对应本地 ref 存在）、`origin/HEAD` 本地同名分支（对应本地 ref 存在）、`main/master/trunk` 首个存在的本地分支选择 `TARGET_BRANCH`；显式目标不存在时不回退。候选资格只由分支来源和本地 ref 存在性决定；worktree holder、identity、HEAD/ref 和 cleanliness 都在选中后验证，不能用来跳过高优先级候选。记录：

```text
TARGET_SOURCE=explicit
# 或
TARGET_SOURCE=inferred:<primary-worktree|origin-head|fallback-name>
```

从注册表解析唯一 `TARGET_WORKTREE_DIR`。要求：

- 目标分支已经由该 worktree 持有；未持有时停止并要求用户自行准备。
- target current branch 是 `TARGET_BRANCH`，非 detached HEAD。
- `TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)`。
- target worktree HEAD 等于 `TARGET_HEAD`。
- `git -C <TARGET_WORKTREE_DIR> status --porcelain --untracked-files=all` 严格为空。

选中候选后，任一 worktree holder、topology、identity、HEAD/ref 或 clean 检查失败都报告该候选的 blocker 并停止，不尝试较低优先级 target。

定义 `REPO_ROOT=<PRIMARY_WORKTREE_DIR>`。记录控制器能否把后续 spawn、merge 和 cleanup 的真实 CWD 持久绑定到 `TARGET_WORKTREE_DIR`；如果不能，在预检停止。不得用一条 `git -C` 假装控制器上下文已切换，也不得用 checkout 修复错误分支。

## Step 1：Discovery 与 artifact manifest（只读）

枚举 `openspec/changes/*/`（排除 archive），对每个 change：

1. 读取 `tasks.md`；存在未完成任务时才是候选。
2. 要求 `openspec status --change "<change-name>" --json` 的全部 artifacts done 且 `isComplete=true`。
3. 要求 `change-name` 是小写 kebab-case；计算规范 `SOURCE_BRANCH=worktree-<change-name>` 和绝对 `SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<change-name>`，要求最终 branch 长度不超过 64 且通过 `git check-ref-format --branch`。
4. 要求 source branch 不存在、source path 不存在且未注册；不复用、不接管、不追加后缀。
5. 针对当前确认的 `TARGET_HEAD` 构建该 change 的 `ARTIFACT_MANIFEST`：固定包含 `.openspec.yaml`、proposal/design/tasks，递归包含 `specs/` 全部文件且至少一个 `spec.md`。
6. 当前工作区或 `TARGET_HEAD` 任一侧存在 `dependencies.yaml` 时必须加入 manifest；两侧均缺省才记录无依赖。
7. 用当前 `find ... -type f | LC_ALL=C sort` 与 `git ls-tree -r --name-only <TARGET_HEAD>` 比较路径集合；逐项以 `git hash-object` 对 frozen commit blob 比较字节内容。
8. 记录每个 `ARTIFACT_MANIFEST_DIGEST`。未提交、ignored、新增、删除、内容不同、空 specs、读取错误或 dependency 单侧缺失均跳过该 change，并显示精确原因。

待执行列表为空则零写退出。

## Step 2：依赖图与 Batch 计划（只读）

只使用已经通过 manifest 验证的 `dependencies.yaml` 构图。缺失引用、引用未通过 artifact 验证或循环依赖都停止整个计划。

Kahn 算法生成 Wave；每 Wave 按 change 名字母序分 Batch，每 Batch 最多 3 个。即使只有一个 change，也使用一个规范隔离 worktree，不直接在目标调用 apply。

后续 Wave 必须等待依赖 Wave 的每个所需 change 完成 merge、post-merge 验证并按策略可供目标使用；依赖 change 未交付时，不调度依赖者。

## Step 3：确认摘要（只读）

进入本步时设置 `WRITE_AUTHORIZATION_GATE=closed`；自动路由和只读规划不授权 spawn、worktree、apply、merge 或 cleanup。

摘要必须显示：

- `TARGET_BRANCH`、标准化 `TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_HEAD`、clean/HEAD-ref 结果。
- `EXPECTED_TARGET_HEAD` 初值等于确认的 `TARGET_HEAD`。
- 每个 Wave/Batch、canonical source branch/path 和 `ARTIFACT_MANIFEST_DIGEST`。
- 每个 Batch 共享冻结 hash、每个 Worker apply/commit、来源内 rebase、冻结 source hash、目标内 exact-hash merge、验证和条件式普通 cleanup。
- 确认后不会 checkout/switch 或 auto-commit 目标；漂移和 cleanup 失败的 child 会保留。
- 确定的 `PROJECT_VERIFY_COMMANDS`；至少含 change strict validation、任务完成度、artifacts、目标 identity/clean、containment、source-only commits 和 `git diff --check`。
- 每个 change 已声明的精确 `[post-merge-verification]` 任务；明确这些任务由用户后续在 target worktree 执行，Controller/Worker 不执行或修改，且 child 会保持 `incomplete / non-archivable`。
- merge 每个 child 最多一次，失败不换参数重试；成功后验证失败不自动回滚。

使用交互工具请求无默认值、无超时同意的明确确认。拒绝、取消、缺失、模糊或无交互能力时不写、不 spawn、不 apply。

只有完整批次计划获得明确肯定后设置 `WRITE_AUTHORIZATION_GATE=open`。Step 4 复检出现任何漂移都会使授权失效并返回本步，不得沿用旧确认。

## Step 4：确认后完整复检（只读）

重跑 Step 0–2，并要求参数、`TARGET_SOURCE`、目标注册/ref/HEAD/clean、控制器上下文能力、change 集合、manifest、依赖图、Wave/Batch、canonical collision 和验证命令全部与摘要一致。

任一变化使确认失效，返回 Step 3。全部一致后设置：

```text
EXPECTED_TARGET_HEAD=<TARGET_HEAD>
```

## Step 5：持久进入目标控制器上下文

将主控后续命令和 Worker 创建的父上下文绑定到 `TARGET_WORKTREE_DIR`，验证：

```bash
test "$(pwd -P)" = "<TARGET_WORKTREE_DIR>"
test "$(git rev-parse --show-toplevel)" = "<TARGET_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<TARGET_BRANCH>"
test "$(git rev-parse HEAD)" = "<EXPECTED_TARGET_HEAD>"
test "$(git rev-parse refs/heads/<TARGET_BRANCH>)" = "<EXPECTED_TARGET_HEAD>"
test -z "$(git status --porcelain --untracked-files=all)"
```

失败时不 spawn。禁止执行恢复性 checkout/switch。

## Step 6：Wave/Batch 创建与 apply

按 Wave、Batch 顺序执行。每个 Batch spawn 前验证 target ref 和 target worktree HEAD 都等于 `EXPECTED_TARGET_HEAD`，target clean、真实 CWD 正确。外部或无法归因的推进使流程停止，不接受新 HEAD、不重新确认后偷偷继续。

然后冻结：

```bash
BATCH_TARGET_HEAD=<EXPECTED_TARGET_HEAD>
```

重新验证 Batch 内每个 change 的 manifest 对 `BATCH_TARGET_HEAD` 完全一致。后续 Wave 因 `EXPECTED_TARGET_HEAD` 已由本控制器的验证 merge 推进，可以在新 commit 上重新得到一致 manifest；若 change artifacts 不在该 commit 或内容变化则不 spawn。

### 6.1 显式创建每个规范 child

对每个 change 同时并行创建/执行，但每个创建命令必须是：

```bash
git worktree add <SOURCE_WORKTREE_DIR> -b worktree-<change-name> <BATCH_TARGET_HEAD>
```

不得使用 ambient HEAD、`TARGET_BRANCH` 或平台隐式 isolation 代替 start-point。创建后验证注册路径、branch、branch ref、worktree HEAD 均等于期望，且 Worker 真实 CWD 是该 source path；失败时保留已创建现场，不换名字或机制重试。

### 6.2 Worker apply 与来源提交

每个 Worker 在自己的 verified source CWD 调用 `openspec-apply-change <change-name>`，但明确跳过同一未勾选行含精确标签 `[post-merge-verification]` 的任务；这些任务由用户后续在 target worktree 执行。Worker 不得执行、勾选、stage 或 commit 延期任务。

apply 后只按标准 checkbox 行分类：

```text
TOTAL=<所有 - [ ] / - [x] 行数>
DEFERRED_REMAINING=<未勾选且同一行含精确标签 [post-merge-verification] 的任务>
BLOCKING_REMAINING=<其余未勾选任务>
```

`tasks.md` 缺失、不可读、`TOTAL == 0` 或无法确定分类时，`TASK_CLEANUP_POLICY_PASSED=unknown`；`BLOCKING_REMAINING` 非空时为 false；否则为 true。只有 true 才把 Worker 视为成功 delivery candidate。Worker 返回必须包含 source path、`SOURCE_BRANCH`、source HEAD、clean 状态、DONE/TOTAL、`TASK_CLEANUP_POLICY_PASSED`、两类 remaining 清单与错误。只有延期任务时明确报告 `incomplete / non-archivable`，但不是 Worker failure。

Worker 失败不清理且不合并。Batch 内其他 Worker 可完成；Controller 等待全部返回后才串行处理成功者。

## Step 7：每个成功 child 的 rebase 与冻结

按 change 名字母序串行处理。对一个 child，在其规范 source worktree 中验证：注册 path/branch、worktree HEAD 与 branch ref 相等、source clean、tasks/artifacts 状态可读，且重新分类结果与 Worker 返回完全一致并满足 `TASK_CLEANUP_POLICY_PASSED=true`；target ref 和 target worktree HEAD 等于当前 `EXPECTED_TARGET_HEAD`。

从来源真实 CWD执行一次：

```bash
git rebase <EXPECTED_TARGET_HEAD>
```

无法解决的冲突允许 abort 这次未完成 rebase，然后保留 child 并跳过；不得换目标重试。

成功立即记录：

```bash
POST_REBASE_SOURCE_HEAD=$(git rev-parse HEAD)
```

要求 source worktree HEAD 和 branch ref 都等于该 hash、source clean，且 `git rev-list <EXPECTED_TARGET_HEAD>..<POST_REBASE_SOURCE_HEAD>` 是非空 delivery commits。再次验证 target ref/HEAD/clean 仍等于 `EXPECTED_TARGET_HEAD`。

## Step 8：目标内 exact-hash merge

返回 `TARGET_WORKTREE_DIR` 的真实控制器 CWD，验证 top-level/current branch/ref/HEAD/clean 全部仍等于 `EXPECTED_TARGET_HEAD`。通过 `git -C <SOURCE_WORKTREE_DIR>` 重新验证 source registration、branch、HEAD/ref、clean、delivery commits 仍对应 `POST_REBASE_SOURCE_HEAD`。

只执行一次：

```bash
PRE_MERGE_TARGET_HEAD=<EXPECTED_TARGET_HEAD>
git merge <POST_REBASE_SOURCE_HEAD>
```

失败时可中止未完成冲突并保留 child；不换参数、不使用 source branch 新 tip、不自动重试。成功后记录：

```text
MERGE_SUCCEEDED_ONCE=true
POST_MERGE_TARGET_HEAD=<git rev-parse HEAD>
```

成功 merge 后不自动 reset/revert。

## Step 9：每 child 的 post-merge 验证与 cleanup

逐项验证且每条命令最多一次：

- 控制器真实 CWD/top-level/current branch 是目标。
- target ref、target worktree HEAD 和 `POST_MERGE_TARGET_HEAD` 相等，target clean。
- target 包含精确 `POST_REBASE_SOURCE_HEAD`。
- source canonical mapping 仍精确，source clean，source HEAD/ref 仍等于冻结 hash。
- source 有 delivery commits，且 `git rev-list target..source` 为空。
- change strict validation 与 artifacts 完成；target 中的 task 分类与冻结 child 结果一致且 `TASK_CLEANUP_POLICY_PASSED=true`。普通未完成任务或 unknown 阻止 cleanup，只有延期任务时保持 checkbox 不变。
- `git diff <PRE_MERGE_TARGET_HEAD>..<POST_MERGE_TARGET_HEAD> --check` 和确认的项目命令全部成功；不得把 `DEFERRED_REMAINING` 描述的测试当作 Controller/Worker 项目命令执行。

只有全部显式成功：

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
  AND TASK_CLEANUP_POLICY_PASSED
  AND POST_MERGE_VERIFICATION_PASSED
```

才立即重复关键 checks，并执行：

```bash
git worktree remove <SOURCE_WORKTREE_DIR>
git branch -d -- <SOURCE_BRANCH>
```

普通 worktree 删除失败时保留 branch；安全 branch deletion 拒绝时保留 branch。branch 在授权删除前意外消失视为 drift。任何失败都不升级为强制 cleanup。

若 post-merge/cleanup 任一 gate 失败，target 上已成功 merge 保留，child source 现场保留，不自动回滚或重试 merge。

只有 child merge、task cleanup policy 与结构性 post-merge verification 全部通过，才更新：

```text
EXPECTED_TARGET_HEAD=<POST_MERGE_TARGET_HEAD>
```

cleanup 因锁失败不否认代码已经验证进入目标，但报告为“已交付、未清理”；依赖调度可基于已验证 target 继续。post-merge verification 失败则不得推进依赖 Wave。

若 child 只有 `DEFERRED_REMAINING`，成功更新 `EXPECTED_TARGET_HEAD` 后可推进依赖 Wave；这仅表示代码已结构性交付，不表示 proposal 已完成或可归档。最终报告必须列出延期任务，保留其未勾选状态并交给用户执行。

## Step 10：Batch/Wave 推进规则

- 同 Batch children 都基于相同 `BATCH_TARGET_HEAD`；串行 rebase 到每个前序已验证 merge 后的最新 `EXPECTED_TARGET_HEAD`。
- 下个 Batch spawn 前重新执行目标 equality/clean/CWD 和每个 manifest 检查。
- Wave 的依赖 change 必须已成功 merge 且 post-merge verification 通过；cleanup 是否因普通路径锁失败单独报告，不阻止已经验证的依赖代码可见性。
- 只有延期任务的依赖 change 在 `TASK_CLEANUP_POLICY_PASSED=true` 且结构性 post-merge verification 通过后可推进依赖 Wave；普通未完成任务、unknown 或验证失败仍阻止依赖者。
- 外部 target 漂移、target dirty 或控制器上下文漂移停止后续 Batch/Wave，不执行修复性 checkout。

## Step 11：最终报告

逐 change 输出：

| 字段 | 内容 |
|---|---|
| Proposal | `<change-name>` |
| Source identity | `worktree-<change-name>` + exact path |
| Artifact manifest | digest / failure |
| Batch target | `BATCH_TARGET_HEAD` |
| Post-rebase source | `POST_REBASE_SOURCE_HEAD` |
| Post-merge target | `POST_MERGE_TARGET_HEAD` |
| Merge count | 0 或 1 |
| Verification | 每个 gate 的 true/false/unknown |
| CLEANUP_READY | true/false |
| Task cleanup policy | true/false/unknown |
| Deferred tasks | none / exact unchecked lines; user-owned in target |
| Proposal status | complete / incomplete / non-archivable |
| Preserved recovery objects | exact worktree/branch |

最终摘要显示 `EXPECTED_TARGET_HEAD`、成功/失败/已交付未清理数量、未执行的依赖 changes 和人工恢复上下文。

## Guardrails

- 确认前零写、零 spawn、零 apply。
- 目标必须由已有 clean worktree 持有，但本流程不切换或自动提交它。
- 每个 child 使用 canonical branch/path 与显式 commit-hash start-point。
- 每个 source/target 快照在 rebase、merge 和 cleanup 前重新验证。
- merge 冻结 hash 且每 child 最多一次；验证失败不自动重试或回滚。
- cleanup 只使用普通 worktree removal 和安全 local branch deletion。
- 每 Batch 最多 3 个 Worker；依赖排序和单 change 隔离语义保持不变。
