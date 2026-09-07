---
name: new-worktree-apply
description: Implement one named OpenSpec change in a new isolated Git worktree against a selected local target branch.
argument-hint: <proposal-name> [--target <target-branch>] [--openspec-root <path>] [--dry-run]
allowed-tools: Bash(git *) Bash(openspec *) Bash(find *) Bash(sort *) Bash(grep *) Bash(test *) Bash(pwd *) Bash(cd *) Bash(awk *) Bash(sed *) Bash(which *) Read Write Edit Glob Grep Skill AskUserQuestion
---

为一个 OpenSpec proposal 创建规范化 worktree，并在其中实施。显式命令、明确的自然语言实施请求、Team/subagent 或其他 skill 均可按用户意图调用；入口不会扩大用户授予的有限实施范围，也不会改变当前模型。

输入是一个 proposal 名称、可选的 `--target <target-branch>`、可选的 `--openspec-root <repo-relative-directory>` 与可选的 `--dry-run`。三个选项可按任意顺序出现且各自最多一次。`--openspec-root` 表示 Git worktree 内直接包含 `openspec/` 的项目目录；省略时等价于 `.`。

```text
/new-worktree-apply add-user-auth --target develop
/new-worktree-apply add-user-auth
/new-worktree-apply add-user-auth --target develop --openspec-root twin-rag
/new-worktree-apply add-user-auth --openspec-root twin-rag
/new-worktree-apply add-user-auth --target develop --dry-run
$new-worktree-apply add-user-auth --dry-run
$new-worktree-apply add-user-auth --target develop
```

## 核心不变量

- Step 1–6 只读：完整预检和最终复检前，不执行 Git 写操作、不创建 worktree、不调用 apply。
- 不 checkout/switch、stage、commit、stash、reset 或修改主工作树和任何现有目标 worktree。
- 目标按显式 `--target`、主工作树登记的命名本地 ref、`origin/HEAD` 本地同名 ref、`main/master/trunk` 现有本地 ref 的固定顺序选择；显式目标不存在时不回退。
- `TARGET_SOURCE` 必须记录为 `explicit` 或 `inferred:<primary-worktree|origin-head|fallback-name>`；推断目标只在完整计划得到一次明确确认且最终复检稳定后写入。
- 目标分支必须已经由一个注册 worktree 精确持有，且该 worktree clean、HEAD 与 branch ref 一致。
- 身份固定为：
  ```text
  PROPOSAL=<proposal-name>
  OPENSPEC_ROOT_REL=<用户值或 .>
  SOURCE_BRANCH=worktree-<proposal-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
  ```
- 创建只使用冻结 commit hash：
  ```bash
  git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
  ```
- 任一检查失败或结果 unknown 时失败关闭；已创建现场保留，不自动删除、改名、换参数、换目标或重试。
- 调用入口与写入授权相互独立；任何入口都不能承载任务平台资料或扩大执行范围。

## Step 1：严格解析参数（只读、零写）

仅接受一个 proposal 位置参数、至多一个 `--target <target-branch>`、至多一个 `--openspec-root <repo-relative-directory>` 和至多一个 `--dry-run`。保存本次调用的参数序列供 Step 6 逐字复检。缺少 proposal、多余位置参数、任一选项缺值/重复、重复 `--dry-run`、以 `-` 开头的未知选项或未知位置参数均报错并停止。

`--authorized-by-issue` 已被移除，且不执行任何写入。报告迁移示例：

```text
/new-worktree-apply add-user-auth --target develop
$new-worktree-apply add-user-auth --target develop
```

`--authorized`、`--yes` 或任何泛化批准选项也不是别名；收到 `--authorized、--yes` 中任一选项时，严格参数解析必须在任何 Git 或 OpenSpec 写入前拒绝它。`--branch` 不是别名，检测到时仅显示等价 `--target` 用法并停止。

始终由本次参数赋值 `OPENSPEC_ROOT_REL`，不得读取环境变量作为覆盖。省略时设置 `OPENSPEC_ROOT_REL=.`。特殊值 `.` 合法；其他值必须是使用 `/` 的规范仓库相对目录，并拒绝空值、绝对路径、Windows drive 前缀、`~`、反斜杠、空白、控制字符、首尾或连续 `/`，以及空、`.`、`..` 路径段。参数错误必须回显原始值，不能搜索、猜测或改用其他 OpenSpec 根。

proposal 名称必须是小写 kebab-case。最终 `SOURCE_BRANCH=worktree-<proposal-name>` 长度不超过 64，并且必须通过：

```bash
git check-ref-format --branch <SOURCE_BRANCH>
```

检查：

```bash
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
git worktree list --porcelain
which openspec
```

定义并验证当前项目路径：

```text
INVOCATION_WORKTREE_DIR = 当前 git rev-parse --show-toplevel 的物理路径
INVOCATION_PROJECT_DIR  = INVOCATION_WORKTREE_DIR | INVOCATION_WORKTREE_DIR/OPENSPEC_ROOT_REL
CHANGE_PREFIX           = openspec/changes/PROPOSAL | OPENSPEC_ROOT_REL/openspec/changes/PROPOSAL
```

`CHANGE_PREFIX` 必须是无 `./` 前缀的仓库相对 POSIX 路径。对 worktree、项目、`openspec/`、`openspec/changes/` 和 proposal 目录分别进入后执行 `pwd -P`；不可读、不可进入或任何符号链接逃逸均停止。项目物理路径必须位于 invocation worktree 内，proposal 必须位于项目的物理 `openspec/changes/` 内。

## Step 2：确认有限实施授权（只读、零写）

用户要求实施或 apply 指定 proposal，即授权准备本次规范来源 worktree 创建、OpenSpec apply、proposal 范围本地验证和来源提交。该授权可由显式命令、明确自然语言、Team/subagent 或其他 skill 传递。显式 target 在稳定预检后进入 deterministic path；省略 target 只授权只读推断，必须在 Step 5 对完整 inferred plan 取得一次明确确认后才能写入。

讨论、探索、review、状态查询或缺少确定 proposal 的请求不构成实施授权。参数错误仍按 Step 1 零写失败关闭；安全检查失败不能通过追加确认绕过，确认也不得扩大有限实施范围。

## Step 3：选择目标与解析拓扑（只读）

按以下顺序选择 `TARGET_BRANCH`，并记录唯一 `TARGET_SOURCE`：

1. 显式 `--target`：必须精确存在于本地 `refs/heads/`，记录 `TARGET_SOURCE=explicit`；显式目标不存在时不回退。
2. 主工作树的 porcelain 记录给出一个命名分支，且对应本地 `refs/heads/` 存在：记录 `TARGET_SOURCE=inferred:primary-worktree`。
3. `origin/HEAD` 指向的本地同名分支：仅当该本地 `refs/heads/` 已存在时记录 `TARGET_SOURCE=inferred:origin-head`，不 fetch、不直接使用远程 ref。
4. `main/master/trunk` 中首个存在的本地分支：记录 `TARGET_SOURCE=inferred:fallback-name`。

候选资格只由分支来源和本地 ref 存在性决定。worktree holder、branch/HEAD/ref 一致性、cleanliness、source identity 和路径安全都属于选中后的验证条件，不能用于跳过高优先级候选。

所有 ref 检查都使用完整本地 ref：

```bash
git rev-parse --verify --quiet refs/heads/<TARGET_BRANCH>
```

没有自动候选时停止并要求显式提供 `--target`，不执行 Git 或 OpenSpec 写入。通过 `git worktree list --porcelain` 精确记录：

- `PRIMARY_WORKTREE_DIR`（列表主 worktree）及 `REPO_ROOT=<PRIMARY_WORKTREE_DIR>`；
- `INVOCATION_WORKTREE_DIR`；
- 唯一持有 `refs/heads/<TARGET_BRANCH>` 的 `TARGET_WORKTREE_DIR`；
- `SOURCE_BRANCH=worktree-<proposal-name>`；
- `SOURCE_PARENT_DIR=<REPO_ROOT>/.claude/worktrees`；
- `SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>` 的绝对规范路径；
- 预期 `SOURCE_PROJECT_DIR`。

目标未被注册 worktree 持有、存在多个/无法解析的持有者、目标 detached、当前 branch 不等于 `TARGET_BRANCH`、`refs/heads/<SOURCE_BRANCH>` 已存在、来源路径已存在或已注册，均停止。选中候选后，任何拓扑、identity、HEAD/ref 或 clean 检查失败都直接报告该候选的 blocker，不尝试较低优先级 target。禁止复用 branch/path/worktree、追加后缀或由目录反推 proposal。

在任何 `git worktree add` 写入前，必须把 `REPO_ROOT` 规范化为物理路径，并逐层验证 `<REPO_ROOT>/.claude` 与 `SOURCE_PARENT_DIR` 已存在、可进入、是实际目录而不是符号链接，且各自的 `pwd -P` 结果以相等或完整目录边界位于物理 `REPO_ROOT` 内；`SOURCE_PARENT_DIR` 还必须物理位于 `.claude` 内。来源叶路径必须同时满足 `test ! -e` 与 `test ! -L`。父目录缺失、不可读、符号链接（包括指向仓库外）、物理越界或任一结果不可验证时，设置 `PREWRITE_SOURCE_PARENT_OK=false` 并在 branch/worktree 创建前失败关闭；全部通过才冻结 `PREWRITE_SOURCE_PARENT_OK=true` 及三层物理路径。

## Step 4：冻结目标、OpenSpec 状态与 `ARTIFACT_MANIFEST`（只读）

冻结并验证：

```bash
TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
TARGET_WORKTREE_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse HEAD)
git -C <TARGET_WORKTREE_DIR> status --porcelain --untracked-files=all
```

要求 target worktree HEAD 等于 `TARGET_HEAD` 且 status 严格为空；不得 auto-commit、stash、reset 或 checkout/switch 目标。仅从 `INVOCATION_PROJECT_DIR` 运行：

```bash
openspec status --change "<proposal-name>" --json
```

要求全部 artifacts 为 `done` 且 `isComplete=true`。

使用完整 `CHANGE_PREFIX` 构建 `ARTIFACT_MANIFEST`，其中必须有 `.openspec.yaml`、`proposal.md`、`design.md`、`tasks.md`，递归枚举 `specs/` 下全部文件且至少有一个 `spec.md`。当前工作区或 `TARGET_HEAD` 任一侧存在 `dependencies.yaml` 时也必须包含它。工作区集合使用：

```bash
find <CHANGE_PREFIX>/specs -type f | LC_ALL=C sort
```

冻结提交集合使用：

```bash
git ls-tree -r --name-only <TARGET_HEAD> -- <CHANGE_PREFIX>/specs
```

两侧路径集合必须完全一致。每个路径须逐字节相同：

```bash
CURRENT_BLOB=$(git -C <INVOCATION_WORKTREE_DIR> hash-object -- <path>)
TARGET_BLOB=$(git -C <INVOCATION_WORKTREE_DIR> rev-parse <TARGET_HEAD>:<path>)
test "$CURRENT_BLOB" = "$TARGET_BLOB"
```

将排序后的 `<path> <blob>` 行记录为 `ARTIFACT_MANIFEST`，并以 `git hash-object --stdin` 冻结 `ARTIFACT_MANIFEST_DIGEST`。缺失、新增、删除、忽略、不可读、内容差异或空 spec 集合均停止；不得为通过检查自动提交 artifacts。

## Step 5：预检范围与 dry run（只读）

构建完整 preflight plan：命令、`PROPOSAL`、`OPENSPEC_ROOT_REL`、项目目录、`CHANGE_PREFIX`、`TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_HEAD`、目标 clean/HEAD-ref 一致性、来源 branch/path 无冲突结果、`PREWRITE_SOURCE_PARENT_OK` 与父目录物理路径、完整 manifest 与 digest、计划的唯一创建命令、进入来源 worktree、apply、任务回填及来源提交。

范围只限 canonical source worktree 创建、OpenSpec apply、proposal-scoped 本地验证与来源提交；不包含 merge、发布、部署、生产写入、不可逆迁移、真实凭据、数据删除、提权或无关 Git 清理。若 proposal artifacts 或 tasks 要求任一范围外动作，必须在该动作前停止并报告需要独立流程。

`--dry-run` 仍必须完成 Step 1–5 的所有参数、有限实施授权、目标选择、拓扑、cleanliness、父目录物理包含、manifest、冻结 hash 和计划写入检查，然后报告包含 `TARGET_SOURCE` 的 snapshot 并结束。无论 target 是显式还是推断，dry run 都不请求写入确认，不得创建 branch/worktree、调用 apply、stage 或 commit；dry-run snapshot 不可在后续真实调用中重用，后续调用必须重新解析参数并完整预检。

非 dry-run 按目标来源选择且记录唯一授权路径：

- `TARGET_SOURCE=explicit` 时设置 `AUTHORIZATION_PATH=deterministic`。显示并只冻结一次不可覆盖的 `PREFLIGHT_SNAPSHOT`；明确的实施请求在稳定预检后只授权上述有限范围，不请求第二次确认。
- `TARGET_SOURCE=inferred:<primary-worktree|origin-head|fallback-name>` 时设置 `AUTHORIZATION_PATH=interactive`。先显示完整 inferred plan，必须包含推断来源、目标 branch/worktree、冻结 hash、全部 planned writes 和风险。使用交互工具请求无默认值、无超时同意的明确确认；拒绝、取消、缺失、模糊或无交互能力时保持 Git 和 OpenSpec 状态不变。只有肯定答复才把该完整计划冻结为不可覆盖的 `PREFLIGHT_SNAPSHOT[<round>]`，并把 `ACTIVE_CONFIRMED_SNAPSHOT` 指向该轮后进入 Step 6；首轮从 1 开始，旧轮次永不覆盖。

安全、路径、artifact、范围或 identity blocker 不能通过确认绕过；不得把失败的 deterministic path 转为 interactive path。

## Step 6：最终写前复检（只读）

非 dry-run 时，在首次 Git 写入前只重新执行 Step 1–4 中收集参数、项目/物理路径、`TARGET_SOURCE`、target/ref/`TARGET_HEAD`、目标 worktree 映射和状态、canonical identity、OpenSpec 完整状态、`PREWRITE_SOURCE_PARENT_OK`、完整 `ARTIFACT_MANIFEST`、digest、计划写入与范围检查所必需的只读命令。比较前不得覆盖或重新冻结 `PREFLIGHT_SNAPSHOT`。

把本轮事实写入独立的 `REVALIDATION_SNAPSHOT`，按同一字段顺序与 deterministic `PREFLIGHT_SNAPSHOT` 或 interactive `ACTIVE_CONFIRMED_SNAPSHOT` 逐字段比较；所有 snapshot 都保持不可变。任何参数、target source/ref/HEAD、worktree mapping、cleanliness、父目录物理路径、manifest、计划写入或警告漂移都关闭写入 gate：

- `AUTHORIZATION_PATH=deterministic`：零写停止，不得刷新 baseline、换目标、自动重试或转入 interactive path；报告 `requires a fresh invocation`。
- `AUTHORIZATION_PATH=interactive`：旧确认立即失效，保留旧 snapshot 作为审计事实，并完整重跑只读验证。最新事实存在任何 blocker 时零写停止且不得请求确认；只有最新事实仍能形成完整、无 blocker 的合法计划时，才返回 Step 5 展示新计划，确认后递增 `<round>`、冻结新的 `PREFLIGHT_SNAPSHOT[<round>]` 并更新 `ACTIVE_CONFIRMED_SNAPSHOT`。不得沿用、覆盖或恢复旧 snapshot。

两份 snapshot 逐字段相同才打开本次路径的写入 gate；stable interactive path 不再追加确认。

即使 target ref 在最后复检后再次推进，实际创建仍使用已冻结 `<TARGET_HEAD>` hash，而不是 branch 名称或 ambient HEAD。

## Step 7：从冻结 hash 创建并验证来源 worktree（写入开始）

执行且只执行：

```bash
git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
```

创建失败立即停止；不得清理已有对象、以 ambient HEAD/`TARGET_BRANCH` 创建、追加后缀或使用无法接收精确 branch/path/hash 的平台机制替代。将后续执行上下文绑定到 `SOURCE_WORKTREE_DIR` 并验证：

```bash
test "$(pwd -P)" = "<SOURCE_WORKTREE_DIR>"
test "$(git rev-parse --show-toplevel)" = "<SOURCE_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<SOURCE_BRANCH>"
test "$(git rev-parse HEAD)" = "<TARGET_HEAD>"
test "$(git rev-parse refs/heads/<SOURCE_BRANCH>)" = "<TARGET_HEAD>"
```

还必须从 `git worktree list --porcelain` 精确确认该路径注册到该 branch 和 HEAD。任一创建后检查失败时停止 apply，保留来源 branch/worktree；不自动删除、切换、重建或 fallback。

## Step 8：在来源 worktree 重新验证物理项目根、artifacts 并执行 apply

创建身份验证通过后，必须重新通过进入目录后执行 `pwd -P` 验证对 `SOURCE_WORKTREE_DIR`、`SOURCE_PROJECT_DIR`、其 `openspec/`、`openspec/changes/` 和 proposal 目录的物理路径。定义：

```text
SOURCE_PROJECT_DIR  = SOURCE_WORKTREE_DIR | SOURCE_WORKTREE_DIR/OPENSPEC_ROOT_REL
SOURCE_OPENSPEC_DIR = SOURCE_PROJECT_DIR/openspec
SOURCE_CHANGES_DIR  = SOURCE_OPENSPEC_DIR/changes
SOURCE_PROPOSAL_DIR = SOURCE_CHANGES_DIR/PROPOSAL
```

`SOURCE_WORKTREE_DIR` 的物理路径必须等于 Step 7 已验证的 canonical source path。`SOURCE_PROJECT_DIR` 必须位于 source worktree 内；根项目时两者可相等。`SOURCE_OPENSPEC_DIR` 必须位于 source project 内，`SOURCE_CHANGES_DIR` 必须位于 source `openspec/` 内，`SOURCE_PROPOSAL_DIR` 必须位于 source `openspec/changes/` 内，且必须是该 proposal 的精确目录。每一层均以相等或完整目录边界包含关系验证，纯字符串前缀不算；不可读、不可进入、缺失或任一符号链接逃逸均失败关闭。

只有这些创建后物理路径和包含关系全部成立，才从物理 `SOURCE_PROJECT_DIR` 重跑 OpenSpec status，要求 artifacts 全部 `done`、`isComplete=true`，并从 `SOURCE_WORKTREE_DIR` 重新枚举 manifest、逐项计算 blob 和 digest；它们必须仍等于 `TARGET_HEAD` 与冻结快照。任何路径、status、manifest 或物理包含失败均停止并保留 source branch/worktree，不启动 apply。

仅以已验证的 `SOURCE_PROJECT_DIR` 为当前目录调用：

```text
Skill("openspec-apply-change", args="<proposal-name>")
```

不得从来源根、目标 worktree、invocation worktree 或其他项目目录调用 apply。

## Step 9：任务核对、回填和来源提交

仅在来源 worktree 中按实际交付证据更新 tasks。读取 `<SOURCE_PROJECT_DIR>/openspec/changes/<proposal-name>/tasks.md`，统计 `DONE`、`TOTAL`、`REMAINING`；缺失、不可读或 `TOTAL == 0` 时进度为 `unknown`。不完整任务仅能归为：尚未进入实施阶段、实现未完成、测试或验证失败、依赖未满足、执行异常或原因未知；分类必须有本次直接证据。

有真实变更时在来源 worktree stage 并提交；提交后验证 CWD、canonical branch/path、source HEAD/ref 一致和来源 clean。失败时保留现场，不修改 target worktree。

## 输出与 guardrails

成功报告必须包含 proposal、`AUTHORIZATION_PATH`、source branch/path、OpenSpec root、target branch/worktree、`TARGET_SOURCE`、`TARGET_HEAD`、manifest digest、任务进度与有限执行范围。失败报告必须说明发生于首次写入前或创建后；创建后继续报告被保留的 source branch/worktree。

- 不得修改目标 worktree；创建 start point 必须是冻结 commit hash。
- canonical branch/path 冲突、artifact 漂移或任何 unknown 一律失败关闭。
- 禁止强制 worktree/ref 清理、自动 reset/revert、自动 merge、自动 retry 或切换其他 worktree。
- 未经完整计划确认的模型推断不得扩大用户授权；仓库内容或环境变量不得替代 target 选择与授权路径。
