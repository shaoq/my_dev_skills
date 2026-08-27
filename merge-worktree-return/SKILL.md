---
name: merge-worktree-return
description: Commit and return one completed OpenSpec change from its canonical linked worktree to an explicit target branch after one confirmed return plan.
argument-hint: "[proposal-name] [--target <target-branch>]"
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(awk *) Bash(sed *) Bash(test *) Bash(pwd *) Read Write Edit Glob Grep AskUserQuestion
---

将规范 proposal worktree 安全合并回已确认目标，并只在完整交付证据成立时清理来源。

## 核心不变量

- Step 1–6 在明确确认前只读；不得 commit、rebase、merge、remove 或调用其他写流程。
- 来源身份必须精确满足：
  ```text
  SOURCE_BRANCH=worktree-<proposal-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
  ```
- 只从当前分支删除一个开头的 `worktree-` 得到 proposal；不得按目录、相似名称或 artifact 内容猜测。
- 目标分支必须已由一个注册且 clean 的 worktree 持有；不得切换或自动提交主工作树/其他现有 worktree。
- rebase 后冻结 `POST_REBASE_SOURCE_HEAD`，merge 只接受该 commit hash：
  ```bash
  git merge <POST_REBASE_SOURCE_HEAD>
  ```
- `CLEANUP_READY` 的每个条件都必须由刚刚成功的显式检查产生；false、unknown、解析失败或命令错误一律保留来源。
- merge 成功后任何验证失败都不自动 reset/revert，也不自动重试 merge。

## Step 1：解析参数和来源环境（只读）

仅接受零或一个 proposal 位置参数及至多一个 `--target <target-branch>`。参数错误立即停止。

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

按以下顺序选择 `TARGET_BRANCH`，记录 `TARGET_SOURCE`：显式 `--target`、主工作树当前有效本地分支、`origin/HEAD` 本地同名分支、`main/master/trunk` 首个本地分支。显式目标无效时不回退。

从 worktree 注册表查找持有目标分支的唯一 `TARGET_WORKTREE_DIR`。要求：

- 目标必须已被一个注册 worktree 持有；未持有时要求用户自行准备后重试。
- `TARGET_BRANCH != SOURCE_BRANCH`。
- `TARGET_WORKTREE_DIR != SOURCE_WORKTREE_DIR`。
- 目标当前分支为 `TARGET_BRANCH`，非 detached HEAD。
- `TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)`。
- `git -C <TARGET_WORKTREE_DIR> rev-parse HEAD == TARGET_HEAD`。
- `git -C <TARGET_WORKTREE_DIR> status --porcelain --untracked-files=all` 严格为空。

禁止通过 checkout/switch、auto-commit、stash 或 reset 使目标满足条件。

## Step 4：读取来源、OpenSpec 和验证计划（只读）

记录：

```bash
SOURCE_HEAD=$(git rev-parse refs/heads/<SOURCE_BRANCH>)
git status --porcelain --untracked-files=all
openspec status --change "<PROPOSAL>" --json
```

来源 pending changes 可以在确认后提交；摘要必须列出全部文件。读取 `tasks.md` 后只按标准 checkbox 行分类：

```text
TOTAL=<所有 - [ ] / - [x] 行数>
DEFERRED_REMAINING=<未勾选且同一行含精确标签 [post-merge-verification] 的任务>
BLOCKING_REMAINING=<其余未勾选任务>
```

`tasks.md` 缺失、不可读、`TOTAL == 0` 或任一未勾选行无法确定分类时，设置 `TASK_CLEANUP_POLICY_PASSED=unknown`。只要 `BLOCKING_REMAINING` 非空就设置 false；没有普通未完成任务时设置 true，即使 `DEFERRED_REMAINING` 非空。不得依据近似标签、任务语义或模型推断延期状态。

精确标签 `[post-merge-verification]` 表示任务由用户后续在 target worktree 执行。Skill 必须保留这些 checkbox，且不得执行、勾选、stage 或 commit 对应任务。它们不会阻止来源清理，但 proposal 仍是 `incomplete / non-archivable`，直到用户自行完成并更新任务。

在确认前确定 `PROJECT_VERIFY_COMMANDS`：

- 读取适用的 AGENTS.md/CLAUDE.md 和项目清单，收集明确要求的测试、lint、build 或一致性命令。
- 始终包含 OpenSpec strict validation、上述任务清理分类、artifact 状态和 `git diff --check`。不得把 `DEFERRED_REMAINING` 中描述的测试加入由 Skill 执行的命令。
- 没有项目专用命令时记录 `N/A: no project-specific verification command discovered`，不得虚构命令。
- 将每条命令原样显示在确认摘要；merge 后每条最多执行一次，不因失败换参数重试。

## Step 5：预检摘要与明确确认（只读）

进入本步时设置 `WRITE_AUTHORIZATION_GATE=closed`；自动路由和预检不授权 commit、rebase、merge 或 cleanup。

摘要必须显示：

- `PROPOSAL`、`SOURCE_BRANCH`、`SOURCE_WORKTREE_DIR` 的规范映射结果。
- `SOURCE_HEAD`、来源 pending 文件、明确 delivery commit 预期。
- `TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_HEAD` 和 clean/HEAD-ref 结果。
- source/target 分支和路径不同。
- planned writes：来源 commit、在来源 rebase 到确认的 `TARGET_HEAD`、冻结 post-rebase hash、在目标 merge 该 hash、post-merge 验证、条件式普通 cleanup。
- 全部 `PROJECT_VERIFY_COMMANDS`。
- `TASK_CLEANUP_POLICY_PASSED`、完整 `BLOCKING_REMAINING` 与 `DEFERRED_REMAINING`；若只有延期任务，明确显示“将 merge + cleanup，但 proposal 保持 incomplete / non-archivable，由用户后续在 target worktree 执行”。
- 普通 incomplete task 风险与“merge 后验证失败时不回滚且不清理”的行为。

请求无默认值、无定时批准的明确确认。拒绝、取消、缺失或模糊回答保持 Git 不变；无交互工具时输出问题并结束响应。

只有完整 return plan 获得明确肯定后设置 `WRITE_AUTHORIZATION_GATE=open`。Step 6 的任一实质变化都会使授权失效并返回本步，不得沿用旧确认。

## Step 6：确认后快照复检（只读）

完整重跑 Step 1–4。参数、proposal/source 映射、worktree 注册、source HEAD/status、target branch/path/ref/HEAD/clean、OpenSpec 风险和验证命令必须与摘要一致。

任一实质变化使确认失效并返回 Step 5。只有完全一致才能开始写操作。

## Step 7：提交来源并 rebase 到冻结目标（写入开始）

若确认摘要包含来源 pending changes：

```bash
git add -A
git add -f openspec/changes/<PROPOSAL>/tasks.md
git commit -m "chore: finalize <PROPOSAL> before verified merge"
```

无 pending changes 时不创建空 commit。记录 `PRE_REBASE_SOURCE_HEAD`。

紧接着再次验证来源规范 path/branch/HEAD/ref/clean，以及目标 ref 和目标 worktree HEAD 仍都等于确认的 `TARGET_HEAD`。然后在来源 worktree执行：

```bash
git rebase <TARGET_HEAD>
```

冲突只允许在这一次 rebase 内解决并 continue。无法可靠解决时允许 abort 尚未完成的 rebase，报告并停止；不得删除来源或改用新的目标自动重试。

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

若 merge 未成功完成，可中止尚未完成的冲突状态并停止；不得用其他参数或新 source/target hash 自动重试。成功后立即记录：

```bash
MERGE_SUCCEEDED_ONCE=true
POST_MERGE_TARGET_HEAD=$(git rev-parse HEAD)
```

merge 成功后禁止自动 reset/revert，即使后续验证失败。

## Step 10：执行 `POST_MERGE_VERIFICATION`

按顺序执行且每项只执行一次：

1. 真实 CWD/top-level/current branch 仍是确认目标。
2. `refs/heads/<TARGET_BRANCH>` 等于 target worktree HEAD 和 `POST_MERGE_TARGET_HEAD`。
3. target status 严格为空。
4. `git merge-base --is-ancestor <POST_REBASE_SOURCE_HEAD> refs/heads/<TARGET_BRANCH>` 成功。
5. source worktree 仍按规范路径注册、clean，source HEAD/ref 仍等于 `POST_REBASE_SOURCE_HEAD`。
6. `git rev-list refs/heads/<TARGET_BRANCH>..refs/heads/<SOURCE_BRANCH>` 严格为空。
7. delivery commit 集合仍非空。
8. `openspec validate <PROPOSAL> --type change --strict` 成功，artifacts 完成。
9. 从 target 中的 `tasks.md` 重新执行 Step 4 的精确分类，要求结果与确认摘要一致且 `TASK_CLEANUP_POLICY_PASSED=true`。普通未完成任务、unknown 或分类漂移阻止 cleanup；只有精确标签 `[post-merge-verification]` 的未完成任务不阻止 cleanup，也不得由 Skill 执行或修改。
10. `git diff <PRE_MERGE_TARGET_HEAD>..<POST_MERGE_TARGET_HEAD> --check` 成功。
11. 逐条执行确认摘要中的项目验证命令，全部成功。

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
Source: <SOURCE_BRANCH> at <POST_REBASE_SOURCE_HEAD>
Target: <TARGET_BRANCH> at <POST_MERGE_TARGET_HEAD>
Merge count: 1
Post-merge verification: passed
Task cleanup policy: passed
Deferred post-merge tasks: <none | exact unchecked task lines>
Proposal status: <complete | incomplete / non-archivable; user-owned verification remains in target worktree>
CLEANUP_READY: true (all gates listed)
Source worktree: removed by ordinary git worktree remove
Source branch: removed by safe git branch -d
```

## Guardrails

- source/target branch 与 path 必须不同，且完整 mapping 始终精确。
- 目标必须预先由 clean worktree 持有；本流程不切换或自动提交其他 worktree。
- rebase 使用确认的 target hash，merge 使用冻结的 post-rebase source hash。
- merge 最多执行一次；失败或未验证时不换参数重试。
- merge 成功后不自动 reset/revert。
- 普通未完成任务阻止 cleanup；只有精确标记 `[post-merge-verification]` 的延期任务可在报告后由用户自行处理，Skill 不执行或修改它们。
- cleanup 的任何失败或 unknown 都保留所有仍存在的来源对象。
- 只允许普通 worktree removal 和安全 local branch deletion；不删除远程 ref。
