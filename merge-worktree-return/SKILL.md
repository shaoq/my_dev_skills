---
name: merge-worktree-return
description: Use when returning one OpenSpec change from its canonical linked worktree to a selected target branch.
argument-hint: "[proposal-name] [--target <target-branch>]"
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(awk *) Bash(sed *) Bash(test *) Bash(pwd *) Read Write Edit Glob Grep AskUserQuestion
---

将规范 proposal worktree 合并回已授权目标；先自动提交目标的普通未跟踪文件，明确调用本技能时允许未完成提案返回并清理来源。未完成状态与 Git 交付安全分别核对。

## 核心不变量

- Step 0–6 只读；在适用授权路径完成且最终复检稳定前，不得 commit、rebase、merge、remove 或调用其他写流程。
- 来源身份必须精确满足：
  ```text
  SOURCE_BRANCH=worktree-<proposal-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
  ```
- 只从当前分支删除一个开头的 `worktree-` 得到 proposal；不得按目录、相似名称或 artifact 内容猜测。
- 目标分支必须由唯一注册 worktree 持有。目标的普通未跟踪文件可按冻结清单自动提交；merge 前必须严格 clean。不得切换其他 worktree，也不自动带入未授权的 tracked 改动。
- 已注册来源 worktree 在目标中呈现为未跟踪目录时，只使用精确本机 Git exclude，不提交其 `.git` 指针、内容副本或 mode 160000 gitlink。
- 明确调用允许任务未完成时 merge + cleanup，但保持所有未完成 checkbox，不自动补勾、加延期标签或归档。
- rebase 后冻结 `POST_REBASE_SOURCE_HEAD`，merge 只接受该 commit hash：
  ```bash
  git merge <POST_REBASE_SOURCE_HEAD>
  ```
- `CLEANUP_READY` 的每个条件都必须由刚刚成功的显式检查产生；false、unknown、解析失败或命令错误一律保留来源。
- merge 成功后任何验证失败都不自动 reset/revert，也不自动重试 merge。

## Step 0：确认当前请求确实要求执行 return（只读）

只从当前请求的明确意图设置 `LIMITED_RETURN_AUTHORIZED`：

- 用户直接调用本 Skill、明确说要执行合并返回，或提供精确的 Team/subagent/其他 Skill return handoff 时为 true。
- 只要求 `status、review、discussion`、可行性分析或其他只读工作时为 false；立即保持只读并停止，不通过追问把它升级成 return。
- 调用方身份、模型、Runtime、任务平台或工具权限都不是授权证据。授权只覆盖本 Skill 展示并复检稳定的 commit/rebase/exact-hash merge/verification/conditional cleanup 计划。

请求意图不清楚时保持 false 并结束当前执行。不得由 Skill 自行补出 return 意图。

另外记录 `EXPLICIT_RETURN_REQUEST`：人类直接使用 `$merge-worktree-return`、`/merge-worktree-return` 或明确要求使用本技能执行 return 时为 true；携带同一人类明确授权的精确 handoff 可保留该值。只有技能名被提及、status/review/discussion 或无明确调用证据时为 false。只读意图优先，即使请求中带有技能名也不得写入。

```text
ALLOW_INCOMPLETE_RETURN = LIMITED_RETURN_AUTHORIZED AND EXPLICIT_RETURN_REQUEST
```

此授权包含已展示并稳定复检的目标未跟踪文件准备提交和本机来源目录排除。不因调用方身份或工具权限扩大范围；inferred target 与 dirty source 的完整计划确认规则仍保留。

## Step 1：解析参数和来源环境（只读）

仅接受零或一个 proposal 位置参数及至多一个 `--target <target-branch>`。参数错误立即停止。

所有只读 Git 查询均使用 `git --no-optional-locks` 或 `GIT_OPTIONAL_LOCKS=0`，避免预检刷新 index。

检查当前目录确实是 linked worktree：

```bash
git rev-parse --is-inside-work-tree
git rev-parse --git-dir
git rev-parse --git-common-dir
git rev-parse --show-toplevel
git branch --show-current
git worktree list --porcelain
```

要求 Git dir 与 common dir 不同，且当前分支非空。

记录当前真实来源：

```text
SOURCE_WORKTREE_DIR=<git rev-parse --show-toplevel 的规范绝对路径>
SOURCE_BRANCH=<git branch --show-current>
```

解析规则：

```text
SOURCE_BRANCH 必须以一个精确的 worktree- 开头
DERIVED_PROPOSAL = 删除该开头一次后的剩余字符串
```

`DERIVED_PROPOSAL` 必须是非空的小写 kebab-case，`SOURCE_BRANCH` 长度不超过 64 且通过 `git check-ref-format --branch <SOURCE_BRANCH>`。若显式提供 proposal，它必须与 `DERIVED_PROPOSAL` 完全相等；否则停止，不自动迁移旧的无前缀分支。

## Step 2：验证规范来源映射（只读）

从 `git worktree list --porcelain` 取得 `PRIMARY_WORKTREE_DIR` 并定义 `REPO_ROOT=<PRIMARY_WORKTREE_DIR>`。计算：

```text
PROPOSAL=<DERIVED_PROPOSAL>
EXPECTED_SOURCE_BRANCH=worktree-<proposal-name>
EXPECTED_SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
```

要求：

- `SOURCE_BRANCH == EXPECTED_SOURCE_BRANCH`。
- `SOURCE_WORKTREE_DIR == EXPECTED_SOURCE_WORKTREE_DIR`，使用规范绝对路径比较，不接受前缀/子串匹配。
- 注册表中该 exact path 的 branch 是 `refs/heads/<SOURCE_BRANCH>`，注册 HEAD 等于 worktree HEAD。
- `refs/heads/<SOURCE_BRANCH>` 存在且等于 source worktree HEAD。
- `openspec/changes/<PROPOSAL>`、`.openspec.yaml`、proposal/design/tasks 和递归 delta specs 存在。

任一不一致都禁止 commit、rebase、merge 和 cleanup。

## Step 3：选择并验证目标（只读）

按以下顺序选择 `TARGET_BRANCH`：显式 `--target`、主工作树 porcelain 记录中的命名分支（对应本地 ref 存在）、`origin/HEAD` 本地同名分支（对应本地 ref 存在）、`main/master/trunk` 首个存在的本地分支。显式目标无效时不回退。候选资格只由分支来源和本地 ref 存在性决定；worktree holder、identity、HEAD/ref、cleanliness 等都在选中后验证，不能用来跳过高优先级候选。记录：

```text
TARGET_SOURCE=explicit
# 或
TARGET_SOURCE=inferred:<primary-worktree|origin-head|fallback-name>
```

`TARGET_SOURCE=inferred` 表示 target 仍需进入 interactive path；proposal 参数是否省略不影响这个分类。

从 worktree 注册表查找持有目标分支的唯一 `TARGET_WORKTREE_DIR`。要求：

- 目标必须已被一个注册 worktree 持有；未持有时要求用户自行准备后重试。
- `TARGET_BRANCH != SOURCE_BRANCH`。
- `TARGET_WORKTREE_DIR != SOURCE_WORKTREE_DIR`。
- 目标当前分支为 `TARGET_BRANCH`，非 detached HEAD。
- `TARGET_INPUT_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)`，目标准备前的不可变基线。
- `git -C <TARGET_WORKTREE_DIR> rev-parse HEAD == TARGET_INPUT_HEAD`。
- 成功读取 `git -C <TARGET_WORKTREE_DIR> status --porcelain --untracked-files=all`，逐项分类：
  - 普通未跟踪文件：递归枚举精确路径、类型和内容摘要，冻结 `TARGET_AUTO_COMMIT_PATHS`；在 Step 7 自动提交。
  - 精确来源 worktree 目录：必须与注册 path/branch/HEAD 一致且物理位于目标目录内，冻结其 target-relative 根路径到 `TARGET_LOCAL_EXCLUDES`；在 Step 7 写本机 Git exclude，不 stage 目录。
  - staged/unstaged tracked 改动、冲突、未注册嵌套 Git 仓库、其他 worktree 目录或不可读内容：当前请求没有额外明确授权时为 blocker，不自动纳入普通未跟踪文件清单。
  - 准备清单还须冻结本机 exclude 文件的规范路径、是否存在、当前完整内容及 index 状态；读取失败即停止。

空 status 表示无准备动作；仅含上述可准备项时不作为目标 dirty blocker。预检只读取清单，不提前 stage、commit 或写 exclude。禁止 checkout/switch、stash、reset、强制 add 或提交嵌套仓库来满足条件。
选中候选后，任一 worktree holder、topology、identity、HEAD/ref 或 clean 检查失败都报告该候选的 blocker 并停止，不尝试较低优先级 target。

## Step 4：读取来源、OpenSpec 和验证计划（只读）

记录：

```bash
SOURCE_HEAD=$(git rev-parse refs/heads/<SOURCE_BRANCH>)
git status --porcelain --untracked-files=all
openspec status --change "<PROPOSAL>" --json
```

读取 source status，命令成功且输出严格为空时记录 `SOURCE_CLEAN=true`；命令失败则预检失败；其余情况记录 `SOURCE_CLEAN=false`，并冻结、逐项显示全部 pending 文件及每项文件类型、内容摘要/删除标记和 index 状态。pending changes 只能在 interactive plan 明确确认并稳定复检后提交。读取 `tasks.md` 后只按标准 checkbox 行分类：

```text
TOTAL=<所有 - [ ] / - [x] 行数>
DEFERRED_REMAINING=<未勾选且同一行含精确标签 [post-merge-verification] 的任务>
BLOCKING_REMAINING=<其余未勾选任务>
```

`tasks.md` 缺失、不可读、`TOTAL == 0` 或任一未勾选行无法确定分类时，设置 `TASK_CLEANUP_POLICY_PASSED=unknown`，不能以明确调用绕过解析失败。有效分类后：

```text
TASK_CLEANUP_POLICY_PASSED =
  ALLOW_INCOMPLETE_RETURN OR BLOCKING_REMAINING is empty
```

`BLOCKING_REMAINING` 保留原名用于兼容，但在 `ALLOW_INCOMPLETE_RETURN=true` 时只是普通未完成清单，不阻止 merge 或 cleanup。没有明确调用证据时，普通未完成任务仍阻止 cleanup。不得依据近似标签、任务语义或模型推断延期状态。

精确标签 `[post-merge-verification]` 表示任务由用户后续在 target worktree 执行。Skill 必须保留这些 checkbox，且不得执行、勾选、stage 或 commit 对应任务的自动完成更新。

明确调用且存在任意未完成任务时，同样保留原有普通/延期分类和 checkbox；不要求追加标签，提案文件随已合并提交保留在 target。输出 `incomplete / non-archivable`，后续实施或验证由用户另行发起。允许返回不等于完成提案，也不豁免下列必要 Git/项目验证。

在冻结 audit plan 前确定 `PROJECT_VERIFY_COMMANDS`：

- 读取适用的 AGENTS.md/CLAUDE.md 和项目清单，收集明确要求的测试、lint、build 或一致性命令。
- 始终包含 OpenSpec strict validation、上述任务清理分类、artifact 状态和 `git diff --check`。不得把 `DEFERRED_REMAINING` 中描述的测试加入由 Skill 执行的命令。
- 没有项目专用命令时记录 `N/A: no project-specific verification command discovered`，不得虚构命令。
- 将每条命令原样显示在 audit plan，并映射到 Step 10 固定 gate 或补充项目命令。相同命令去重，固定 gate 执行后标记已执行；验证清单每条执行一次，不因失败换参数重试。Step 12 的身份、containment 与任务安全复检可以重复，但不得以此重跑项目测试/build、strict validation 或 diff check，也不能把清单验证失败转为重试。

## Step 5：冻结计划并选择授权路径（只读）

进入本步时设置 `WRITE_AUTHORIZATION_GATE=closed`。只有 Step 0–4 全部可读、无 blocker 且当前请求满足 `LIMITED_RETURN_AUTHORIZED=true`，才设置 `PREFLIGHT_PASSED=true` 并展示完整 audit plan；否则零写停止。

完整计划必须显示并冻结到不可覆盖的 `PREFLIGHT_SNAPSHOT`：

- 当前请求的 limited return 判定、`PROPOSAL` 的 explicit/derived 来源，以及 `SOURCE_BRANCH`、`SOURCE_WORKTREE_DIR` 的规范映射。
- `SOURCE_HEAD`、`SOURCE_CLEAN` 和全部 pending 文件的精确路径、类型、内容摘要/删除标记及 index 状态；clean 时明确写 `pending-file policy=none`，dirty 时显示逐文件 commit plan。
- `TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_INPUT_HEAD` 和 HEAD-ref 结果；全部 `TARGET_AUTO_COMMIT_PATHS` 内容摘要、`TARGET_LOCAL_EXCLUDES` 身份和精确准备动作；无准备动作时明确写 none。
- source/target 分支和路径不同。
- planned writes：先在目标写精确本机 exclude、自动提交冻结的普通未跟踪清单，检查 clean 后冻结准备后的 `TARGET_HEAD`；仅 interactive dirty-source path 包含来源 commit；随后来源 rebase 到该准备后 hash、冻结 post-rebase hash、目标 merge 该 hash、post-merge 验证、条件式普通 cleanup。
- 全部 `PROJECT_VERIFY_COMMANDS`。
- `EXPLICIT_RETURN_REQUEST`、`ALLOW_INCOMPLETE_RETURN`、`TASK_CLEANUP_POLICY_PASSED`、完整 `BLOCKING_REMAINING` 与 `DEFERRED_REMAINING`；明确调用且有未完成任务时显示“将 merge + cleanup，未完成任务不补勾，proposal 保持 incomplete / non-archivable，由用户后续在 target worktree 执行”。
- 普通 incomplete task 风险、冲突策略，以及“merge 后验证失败时不回滚且不清理”的行为。

计算：

```text
DETERMINISTIC_RETURN_READY =
  LIMITED_RETURN_AUTHORIZED
  AND TARGET_SOURCE == explicit
  AND SOURCE_CLEAN
  AND PREFLIGHT_PASSED
```

### Deterministic path

`DETERMINISTIC_RETURN_READY=true` 时记录 `AUTHORIZATION_PATH=deterministic`。完整 audit plan 本身就是当前明确 return 请求的受限执行计划；展示后不请求第二次确认。该路径的 source pending-file policy 固定为 none，后续不得 stage 或 commit source 文件；已冻结的目标未跟踪准备提交可执行，无需额外确认。

### Interactive compatibility path

当 `LIMITED_RETURN_AUTHORIZED=true` 且 `TARGET_SOURCE=inferred`、`SOURCE_CLEAN=false` 或两者同时成立时，记录 `AUTHORIZATION_PATH=interactive`。展示同一完整计划；dirty source 必须列出全部 pending 文件、精确 source commit 计划和其他 planned writes；目标准备清单同时展示，inferred target 必须显示 fallback 来源及冻结输入 hash。

使用交互工具请求无默认值、无超时同意的明确确认。拒绝、取消、缺失、模糊或无交互能力时保持 Git 不变。只有肯定答复才冻结该 interactive `PREFLIGHT_SNAPSHOT` 并进入 Step 6。

proposal 省略但能从唯一规范 branch 精确派生，不单独触发 interactive path。任何参数、映射、任务分类或命令不确定都属于 blocker，不得用确认绕过。

## Step 6：独立最终复检（只读）

完整重跑 Step 0–4，把结果写入独立 `REVALIDATION_SNAPSHOT`，不得覆盖、刷新或就地修改 `PREFLIGHT_SNAPSHOT`。逐字段比较请求意图、原始参数、proposal 来源、source/target 映射和身份、refs/HEAD、`SOURCE_CLEAN`、全部 pending 文件路径/类型/内容摘要或删除标记/index、target exclude 文件路径/存在性/完整内容、OpenSpec/task 分类、验证命令、planned writes 与冲突/cleanup 策略。

- deterministic path 任一变化都关闭 gate、执行零写、报告 `fresh invocation`，且不得自动转入 interactive path 或请求确认绕过漂移。
- interactive path 任一变化都使旧确认失效；保持零写并回到 Step 5 展示新计划，不能沿用旧确认。
- 两个快照逐字段完全一致时，才统一设置一次 `WRITE_AUTHORIZATION_GATE=open` 并开始 Step 7。

## Step 7：自动准备目标、处理来源并 rebase（写入开始）

先核对目标 branch/path/HEAD/ref、status、普通未跟踪文件字节、index、来源注册目录和 exclude 文件当前内容均与 `PREFLIGHT_SNAPSHOT` 一致；漂移时不开始准备，也不把并发新增文件纳入清单。

### 7.1 自动准备目标

仅在选中的 `TARGET_WORKTREE_DIR` 执行计划内动作：

1. `TARGET_LOCAL_EXCLUDES` 非空时，通过 `git rev-parse --git-path info/exclude` 找到本机排除文件，保留已有内容，追加缺少的精确 target-relative `/.../` 目录模式。再次证明每个目录仍是已注册规范来源，不影响 tracked 文件；记录排除修改。不得提交这些目录为 gitlink，也不为它们创建空提交。
2. `TARGET_AUTO_COMMIT_PATHS` 非空时，使用 literal pathspec 精确 stage 冻结文件，不使用无范围 `git add -A`：
   ```bash
   git --literal-pathspecs add -- <TARGET_AUTO_COMMIT_PATHS...>
   git diff --cached --check
   git commit -m "chore: prepare <PROPOSAL> target before verified merge"
   ```
   提交前复核 staged 文件与冻结清单/内容一致、没有 mode 160000 或来源目录内容，执行适用的提交前检查。提交失败停止，不改作者、不绕过 hook、不 amend。
3. 若没有普通未跟踪文件，跳过 commit。无论是否提交，目标 status 此时必须严格为空，目标 HEAD/ref/branch/path 必须一致；否则停止并保留已经完成的准备。
4. 有准备提交时，先证明该提交唯一 parent 等于 `TARGET_INPUT_HEAD`，目标 HEAD/ref 都等于该准备提交，提交路径及内容仅为冻结清单。无提交时目标 HEAD/ref 必须仍等于 `TARGET_INPUT_HEAD`。外部推进一律停止，不以“准备后重新读取”吸收漂移。随后冻结 `TARGET_HEAD` 为准备后的目标 HEAD，记录 `TARGET_PREPARATION_COMMIT`（无提交为 none）和独立 `PREPARED_TARGET_SNAPSHOT`。原 `TARGET_INPUT_HEAD` 与 `PREFLIGHT_SNAPSHOT` 不覆盖；后续 rebase/merge 只使用准备后的基线，不采纳外部推进的新 tip。

### 7.2 来源提交与 rebase

目标准备后再次复检来源注册、HEAD/ref、status、pending 集合及字节仍等于原冻结来源快照；不得带入准备期间并发出现的来源改动。

仅当 `AUTHORIZATION_PATH=interactive`、确认计划包含来源 pending changes，且 Step 6 证明 pending 集合与完整计划不变时执行：

```bash
git --literal-pathspecs add -A -- <CONFIRMED_SOURCE_PENDING_PATHS...>
git commit -m "chore: finalize <PROPOSAL> before verified merge"
```

deterministic path 必须再次证明 `SOURCE_CLEAN=true`，不得在来源执行任何 stage/commit；interactive clean-source path 也不创建空 commit。记录 `PRE_REBASE_SOURCE_HEAD`。

紧接着再次验证来源规范 path/branch/HEAD/ref/clean，以及目标 ref 和目标 worktree HEAD 仍都等于授权并冻结的 `TARGET_HEAD`。然后在来源 worktree执行：

```bash
git rebase <TARGET_HEAD>
```

interactive path 的冲突只允许在这一次 rebase 内按已确认计划解决并 continue；无法可靠解决时 abort 尚未完成的 rebase，报告并停止。deterministic path 遇到冲突时不得发明或提交解决方案，安全执行 `git rebase --abort` 后保留规范来源并停止，要求 fresh invocation；不得自动转入 interactive path、改用新目标或重试。

成功后立即冻结：

```bash
POST_REBASE_SOURCE_HEAD=$(git rev-parse HEAD)
```

并验证：

- source 注册 path/branch 未变。
- source worktree HEAD 和 `refs/heads/<SOURCE_BRANCH>` 都等于 `POST_REBASE_SOURCE_HEAD`。
- source status 严格为空。
- `git rev-list <TARGET_HEAD>..<POST_REBASE_SOURCE_HEAD>` 返回非空 delivery commit 集合；记录每个 hash 和 subject。
- target ref、target worktree HEAD 仍等于 `TARGET_HEAD`，target 仍 clean。

任一失败都停止在来源 worktree，不进入 merge。

## Step 8：进入目标并在 merge 前冻结复检

把控制器真实执行上下文绑定到 `TARGET_WORKTREE_DIR`。以下检查必须全部成功：

```bash
test "$(pwd -P)" = "<TARGET_WORKTREE_DIR>"
test "$(git rev-parse --show-toplevel)" = "<TARGET_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<TARGET_BRANCH>"
test "$(git rev-parse HEAD)" = "<TARGET_HEAD>"
test "$(git rev-parse refs/heads/<TARGET_BRANCH>)" = "<TARGET_HEAD>"
test -z "$(git status --porcelain --untracked-files=all)"
```

再通过 `git -C <SOURCE_WORKTREE_DIR>` 重跑 source 注册、branch、HEAD/ref、clean、delivery commit 检查，要求仍等于 `POST_REBASE_SOURCE_HEAD`。

这一步禁止恢复性 checkout、二次 rebase 或采用 source branch 的新 tip。任一漂移都停止并保留来源。

## Step 9：只 merge 冻结 commit

记录 `PRE_MERGE_TARGET_HEAD=<TARGET_HEAD>`，然后从目标真实 CWD 执行一次：

```bash
git merge <POST_REBASE_SOURCE_HEAD>
```

若 merge 未成功完成，interactive path 可按已确认计划处理当前冲突，无法可靠解决时中止；deterministic path 不解决或提交冲突，安全执行 `git merge --abort` 后保留规范来源并停止，要求 fresh invocation，且不得自动转入 interactive path。两个路径都不得用其他参数或新 source/target hash 自动重试。成功后立即记录：

```bash
MERGE_SUCCEEDED_ONCE=true
POST_MERGE_TARGET_HEAD=$(git rev-parse HEAD)
```

merge 成功后禁止自动 reset/revert，即使后续验证失败。

## Step 10：执行 `POST_MERGE_VERIFICATION`

按顺序执行且每项只执行一次：

1. 真实 CWD/top-level/current branch 仍是授权目标。
2. `refs/heads/<TARGET_BRANCH>` 等于 target worktree HEAD 和 `POST_MERGE_TARGET_HEAD`。
3. target status 严格为空。
4. `git merge-base --is-ancestor <POST_REBASE_SOURCE_HEAD> refs/heads/<TARGET_BRANCH>` 成功。
5. source worktree 仍按规范路径注册、clean，source HEAD/ref 仍等于 `POST_REBASE_SOURCE_HEAD`。
6. `git rev-list refs/heads/<TARGET_BRANCH>..refs/heads/<SOURCE_BRANCH>` 严格为空。
7. delivery commit 集合仍非空。
8. `openspec validate <PROPOSAL> --type change --strict` 成功，artifacts 完成。
9. 从 target 中的 `tasks.md` 重新执行 Step 4 的精确分类与授权谓词，要求清单、checkbox 和 `ALLOW_INCOMPLETE_RETURN` 与冻结 audit plan 一致且 `TASK_CLEANUP_POLICY_PASSED=true`。明确调用时普通未完成任务不阻止 cleanup；无明确调用时沿用严格任务策略。unknown、分类漂移或自动补勾均阻止 cleanup。
10. `git diff <PRE_MERGE_TARGET_HEAD>..<POST_MERGE_TARGET_HEAD> --check` 成功。
11. 逐条执行冻结 audit plan 中尚未在第 8～10 项执行的补充项目验证命令；固定 gate 已覆盖的相同命令不再执行。全部声明命令必须都有一次成功结果。

任一项 false、unknown、无法解析或命令失败：报告失败 gate、相关 hashes、已完成 merge 和保留的来源；不回滚、不重试、不 cleanup。

## Step 11：计算 `CLEANUP_READY`

只有以下条件刚刚全部显式为 true：

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

才可进入 Step 12。不要从“已经离开来源目录”、历史检查或单个空 log 推导 readiness。

## Step 12：普通清理，失败即保留

仍在目标真实 CWD，立即重复 source mapping/ref/HEAD/clean、target ref/HEAD、精确 containment、无 source-only commits、任务清理分类和 post-merge 结果。全部仍为 true 后执行：

```bash
git worktree remove <SOURCE_WORKTREE_DIR>
```

普通删除失败（包括 dirty、路径锁、进程占用、平台锁或解析错误）时停止，来源 worktree 和 branch 均保留，不升级为强制删除。

删除成功后精确确认 `SOURCE_WORKTREE_DIR` 已从 `git worktree list --porcelain` 消失。随后要求 `refs/heads/<SOURCE_BRANCH>` 仍存在且仍指向 `POST_REBASE_SOURCE_HEAD`，再次验证 target 包含该 hash，再执行：

```bash
git branch -d -- <SOURCE_BRANCH>
```

安全分支删除拒绝时保留 branch，不使用更强的 ref 删除方式。若 branch 在授权删除前意外消失，视为 identity drift 失败，不当作幂等成功，也不删除任何其他 ref。

## 成功输出

```text
## Worktree Merged & Safely Cleaned

Proposal: <PROPOSAL>
Authorization path: <deterministic | interactive>
Proposal source: <explicit | derived from SOURCE_BRANCH>
Source: <SOURCE_BRANCH> at <POST_REBASE_SOURCE_HEAD>
Source pending-file policy: <none | confirmed exact file set and commit>
Target preparation: <ordinary untracked commit hash | none>; local excludes: <exact paths | none>
Target input/prepared heads: <TARGET_INPUT_HEAD> -> <TARGET_HEAD>
Target: <TARGET_BRANCH> at <POST_MERGE_TARGET_HEAD> (<TARGET_SOURCE>)
Preflight/revalidation snapshots: <stable identifiers and equality result>
Merge count: 1
Post-merge verification: passed
Task cleanup policy: passed (ALLOW_INCOMPLETE_RETURN=<true | false>)
Ordinary unfinished tasks: <none | exact unchecked task lines>
Deferred post-merge tasks: <none | exact unchecked task lines>
Proposal status: <complete | incomplete / non-archivable; user-owned verification remains in target worktree>
CLEANUP_READY: true (all gates listed)
Source worktree: removed by ordinary git worktree remove
Source branch: removed by safe git branch -d
```

## Guardrails

- source/target branch 与 path 必须不同，且完整 mapping 始终精确。
- 目标必须预先由注册 worktree 持有；只自动提交冻结的普通未跟踪文件，merge 前严格 clean；来源目录仅本机排除，不切换、不提交嵌套仓库。
- 明确 return 请求、显式 target、clean source 和稳定预检选择 deterministic path；inferred target 或 dirty source 选择一次完整 interactive confirmation。
- deterministic path 不请求第二次确认，不 stage/commit source pending 文件；目标准备仅按冻结清单执行。任何未计划的漂移或冲突都要求 fresh invocation，且不得自动转入 interactive path。
- rebase 使用授权并冻结的 target hash，merge 使用冻结的 post-rebase source hash。
- merge 最多执行一次；失败或未验证时不换参数重试。
- merge 成功后不自动 reset/revert。
- 明确调用本技能时，已解析的普通/延期未完成任务均允许 merge + cleanup，保留 checkbox 和 incomplete / non-archivable 状态；无明确调用证据时普通未完成任务仍阻止 cleanup。
- cleanup 的任何失败或 unknown 都保留所有仍存在的来源对象。
- 只允许普通 worktree removal 和安全 local branch deletion；不删除远程 ref。
- 失败报告始终列出授权路径、proposal/target 来源、不可变输入/复检/准备快照、已完成目标准备提交与本机排除、source pending-file policy、普通/延期任务和仍保留的精确 worktree/branch/hash；准备后失败不撤销已完成准备，merge 后失败不回滚。
