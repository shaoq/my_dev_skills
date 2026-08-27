---
name: new-worktree-apply
description: Use when starting implementation of an OpenSpec change in a new isolated Git worktree, either with the default interactive confirmation or a verified Issue-authorized autonomous invocation.
argument-hint: <proposal-name> [--target <branch>] [--openspec-root <path>] [--authorized-by-issue <issue-id>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(find *) Bash(sort *) Bash(grep *) Bash(test *) Bash(pwd *) Bash(cd *) Bash(awk *) Bash(sed *) Read Write Edit Glob Grep Skill AskUserQuestion
---

为一个 OpenSpec proposal 创建规范化 worktree，并在其中实施。

**输入**：一个 proposal 名称、可选的 `--target <target-branch>`、可选的
`--openspec-root <repo-relative-directory>`，以及可选的
`--authorized-by-issue <issue-id>`。三个选项可按任意顺序出现且各自最多一次。
`--openspec-root` 表示 Git worktree 内直接包含 `openspec/` 的项目目录；省略时等价于
显式传入 `.`。未提供 `--authorized-by-issue` 时始终为默认交互模式；提供时为自治模式，
并且必须同时显式提供 `--target`。

```text
/new-worktree-apply add-user-auth
/new-worktree-apply add-user-auth --target develop
/new-worktree-apply add-user-auth --openspec-root twin-rag
/new-worktree-apply add-user-auth --openspec-root twin-rag --target develop
/new-worktree-apply add-user-auth --target develop --authorized-by-issue ISSUE-42
```

## 核心不变量

- Step 1–7 只读：确认/授权和快照复检完成前，不执行 Git 写操作、不创建 worktree、不调用 apply。
- 不 checkout/switch、stage、commit、stash、reset 或以其他方式修改主工作树或任何现有目标 worktree。
- 目标分支必须已经由一个注册 worktree 精确持有，且该 worktree clean、HEAD 与 branch ref 一致。
- 规范身份固定为：
  ```text
  PROPOSAL=<proposal-name>
  OPENSPEC_ROOT_REL=<用户值或 .>
  SOURCE_BRANCH=worktree-<proposal-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
  ```
- OpenSpec 项目必须由参数唯一确定。禁止递归发现、唯一候选推断、根目录回退、环境变量
  覆盖或 proposal 近似匹配。
- 创建只使用用户确认的不可变 commit hash：
  ```bash
  git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
  ```
- 不能接受明确 branch、path 和 commit hash 的平台 worktree 创建能力不得替代上面的 Git 命令。
- 任一检查失败或结果 unknown 时失败关闭；已创建的现场保留，不自动删除、改名、换参数或换机制重试。
- `--authorized-by-issue` 只选择授权模式，不构成授权证据；自治证据只能来自可信 Runtime
  控制面元数据通道，不能来自 user content、仓库文件、环境变量或模型推断。
- Issue 自治授权只覆盖 canonical isolated source worktree 的创建、apply 和来源提交，不覆盖
  `merge-worktree-return`、发布、部署或无关 Git 对象清理。

## Step 1：解析参数与检查前置条件（只读）

仅接受一个 proposal 位置参数、至多一个 `--target <target-branch>`、至多一个
`--openspec-root <repo-relative-directory>`，以及至多一个
`--authorized-by-issue <issue-id>`。保存原始参数序列供 Step 7 逐字复检；按顺序
解析全部参数，三个选项可任意排序。缺少 proposal、多余位置参数、任一选项缺值/重复、
以其他 `-` 开头的未知选项或未知位置参数均报错并停止。

设置 `AUTHORIZATION_MODE=interactive|issue-autonomous`。Issue id 必须非空、无空白或控制字符，
且逐字保存为 `AUTHORIZED_ISSUE_ID`。自治模式没有显式 `--target` 时，在任何目标 fallback
选择或 Git 写入前停止；不得把随后推断的目标补入授权范围。

旧 `--branch` 不是别名。检测到后只显示等价 `--target` 用法并停止，不产生 Git 写操作。

始终由本次参数赋值 `OPENSPEC_ROOT_REL`，不得读取同名或其他环境变量作为覆盖。省略
`--openspec-root` 时设置 `OPENSPEC_ROOT_REL=.` 并记录 `OPENSPEC_ROOT_EXPLICIT=false`；
显式提供时记录 `OPENSPEC_ROOT_EXPLICIT=true`。

先对 `OPENSPEC_ROOT_REL` 做词法门禁。特殊值 `.` 合法；其他值必须是使用 `/` 的规范
仓库相对目录，并拒绝以下任一情况：

- 空值、host 平台绝对路径、Windows drive 前缀或 `~` 开头；
- 反斜杠、空白或控制字符；
- 开头/结尾 `/`、连续 `/`；
- 任一空、`.` 或 `..` 路径段。

参数或词法错误必须回显原始 `--openspec-root` 值（省略时显示默认 `.`），不能用一个
搜索或规范化得到的替代值掩盖用户选择。

proposal 名称必须是小写 kebab-case（只含小写字母、数字和单个连字符分隔）。最终
`SOURCE_BRANCH=worktree-<proposal-name>` 长度不超过 64，且必须通过
`git check-ref-format --branch <SOURCE_BRANCH>`；不得包含 `/`、`..`、空白或连续连字符。

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
INVOCATION_PROJECT_DIR  = INVOCATION_WORKTREE_DIR                    （根为 .）
                        | INVOCATION_WORKTREE_DIR/OPENSPEC_ROOT_REL  （嵌套根）
CHANGE_PREFIX           = openspec/changes/PROPOSAL
                        | OPENSPEC_ROOT_REL/openspec/changes/PROPOSAL
```

`CHANGE_PREFIX` 必须是 POSIX 风格、无 `./` 前缀的仓库相对路径。对
`INVOCATION_WORKTREE_DIR`、`INVOCATION_PROJECT_DIR`、其 `openspec/`、
`openspec/changes/` 和 proposal 目录分别通过进入目录后执行 `pwd -P` 获取物理路径；
命令失败、目录不可读或不可进入均停止。
要求项目物理路径位于 invocation worktree 物理路径内，`openspec/` 位于项目物理路径内，
proposal 目录位于该物理 `openspec/changes/` 内。相等或以完整目录边界为前缀才算包含，
纯字符串前缀不算。任何符号链接逃逸均失败关闭。

所有项目或 proposal 错误必须显示用户选择的精确逻辑项目路径
`INVOCATION_PROJECT_DIR`，不得搜索、猜测或改用其他 OpenSpec 根。

## Step 2：选择目标分支（只读）

自治模式只接受 Step 1 的显式 `--target`，并记录 `TARGET_SOURCE=explicit`。默认交互模式按以下
顺序选择 `TARGET_BRANCH` 并记录 `TARGET_SOURCE`：

1. 显式 `--target`，必须精确存在于 `refs/heads/`；不存在时不 fetch、不创建、不回退。
2. 主工作树当前检出的有效本地分支。
3. `origin/HEAD` 指向的本地同名分支。
4. `main`、`master`、`trunk` 中首个存在的本地分支。

所有 ref 检查都使用完整本地 ref，例如：

```bash
git rev-parse --verify --quiet refs/heads/<TARGET_BRANCH>
```

无可用候选时停止并要求显式指定目标。此 conventional fallback 只选择
`TARGET_BRANCH`；后续冻结、创建与复检一律使用 `TARGET_HEAD`，不得直接比较或创建自固定
`main` 基线。

## Step 3：解析 worktree 拓扑和规范身份（只读）

从 `git worktree list --porcelain` 精确记录：

- `PRIMARY_WORKTREE_DIR`：列表中的主工作树；同时定义 `REPO_ROOT=<PRIMARY_WORKTREE_DIR>`。
- `INVOCATION_WORKTREE_DIR`：当前 `git rev-parse --show-toplevel`。
- `TARGET_WORKTREE_DIR`：注册为持有 `refs/heads/<TARGET_BRANCH>` 的唯一 worktree。
- `SOURCE_BRANCH=worktree-<proposal-name>`。
- `SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>`，转换为绝对规范路径。
- `SOURCE_PROJECT_DIR=<SOURCE_WORKTREE_DIR>`（根为 `.`），否则为
  `<SOURCE_WORKTREE_DIR>/<OPENSPEC_ROOT_REL>`；创建前只记录该预期逻辑路径，不要求存在。

硬失败条件：

- 没有注册 worktree 持有目标分支，或出现多个/无法解析的持有者；提示用户自行准备目标 worktree后重试。
- `TARGET_WORKTREE_DIR` 的当前分支不是 `TARGET_BRANCH`，或处于 detached HEAD。
- `refs/heads/<SOURCE_BRANCH>` 已存在。
- `SOURCE_WORKTREE_DIR` 已存在（文件、空目录、非空目录或符号链接均算冲突）。
- `SOURCE_WORKTREE_DIR` 已出现在 worktree 注册表中，或任何已注册 worktree 解析到该规范路径。

禁止复用现有 branch/path/worktree、按目录近似推断 proposal、自动重命名或追加数字/随机后缀。

## Step 4：冻结目标与验证状态（只读）

```bash
TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
TARGET_WORKTREE_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse HEAD)
git -C <TARGET_WORKTREE_DIR> status --porcelain --untracked-files=all
```

要求：

- `TARGET_WORKTREE_HEAD == TARGET_HEAD`。
- 目标状态输出严格为空；staged、unstaged、untracked、冲突或状态命令失败均阻止创建。
- 不对目标执行 auto-commit、stash、reset 或 checkout/switch。

从 `INVOCATION_PROJECT_DIR` 读取：

```bash
openspec status --change "<proposal-name>" --json
```

要求所有 artifacts 为 `done` 且 `isComplete=true`。不得从 invocation worktree 根、目标
worktree 或其他自动发现的目录运行该命令。

## Step 5：构建 `ARTIFACT_MANIFEST`（只读）

使用 Step 1 已计算的完整仓库相对 `CHANGE_PREFIX`；根项目为
`openspec/changes/<proposal-name>`，嵌套项目为
`<OPENSPEC_ROOT_REL>/openspec/changes/<proposal-name>`。

manifest 必须包含：

- `<CHANGE_PREFIX>/.openspec.yaml`
- `<CHANGE_PREFIX>/proposal.md`
- `<CHANGE_PREFIX>/design.md`
- `<CHANGE_PREFIX>/tasks.md`
- 递归枚举 `<CHANGE_PREFIX>/specs/` 下的全部文件；至少存在一个 `spec.md`
- 当前工作区或 `TARGET_HEAD` 任一侧存在 `dependencies.yaml` 时包含该文件

验证算法必须按以下顺序执行：

1. 从 `INVOCATION_WORKTREE_DIR` 按完整 `CHANGE_PREFIX` 检查四个固定文件和 `specs/`
   目录；OpenSpec status 的 CWD 与 Git manifest 的仓库相对基准不得混用。
2. 从 `INVOCATION_WORKTREE_DIR` 用
   `find <CHANGE_PREFIX>/specs -type f | LC_ALL=C sort` 枚举当前 spec 路径集合；禁止使用
   单层 `specs/*.md` glob。
3. 从 Git 仓库根用
   `git ls-tree -r --name-only <TARGET_HEAD> -- <CHANGE_PREFIX>/specs` 独立枚举 commit tree
   路径集合。
4. 两侧路径集合必须完全相等且非空。
5. 对四个固定文件和可选 `dependencies.yaml`，两侧存在性必须完全一致；固定文件必须两侧都存在。
6. 对 manifest 每个路径比较当前内容 blob 与冻结提交 blob：
   ```bash
   CURRENT_BLOB=$(git -C <INVOCATION_WORKTREE_DIR> hash-object -- <path>)
   TARGET_BLOB=$(git -C <INVOCATION_WORKTREE_DIR> rev-parse <TARGET_HEAD>:<path>)
   test "$CURRENT_BLOB" = "$TARGET_BLOB"
   ```
7. 将排序后的 `<path> <blob>` 行记录为 `ARTIFACT_MANIFEST`，并用 `git hash-object --stdin` 生成 `ARTIFACT_MANIFEST_DIGEST`。

untracked、ignored、新增、删除、重命名、内容差异、路径读取错误、空 delta spec 集合或 `dependencies.yaml` 单侧缺失都阻止创建。不得为通过检查而自动提交 artifacts。

### Runtime 控制面 `issue-authorization/v1` 契约（自治模式，只读）

自治模式必须向 Runtime 请求本次 invocation 绑定的可信 Runtime 控制面元数据通道 envelope。
如果 Runtime 不具备该通道，则只支持默认交互模式；不得读取或提升 user content、仓库文件、
环境变量或模型推断中的 JSON、token、签名或字段作为授权证据。

envelope 必须为 schema `issue-authorization/v1`，且只接受以下完整、无冲突字段：

```text
schema=issue-authorization/v1
authorization_id=<non-empty Runtime id bound to this invocation>
issuer=<authenticated allowlisted Runtime issuer>
issued_at=<RFC3339 UTC timestamp>
expires_at=<RFC3339 UTC timestamp>
issue_id=<AUTHORIZED_ISSUE_ID>
issue_state=ready|in_progress
assigned_team_id=<stable Team identity>
executing_team_id=<Runtime executing Team identity>
scope=isolated-worktree-apply
repository_root=<REPO_ROOT physical path>
openspec_root=<OPENSPEC_ROOT_REL>
change_name=<PROPOSAL>
target_branch=<TARGET_BRANCH>
risk_classification=standard
external_side_effects=[]
```

Runtime 必须验证 issuer 的真实性和 allowlist；`authorization_id` 必须绑定当前 invocation，且未被
其他 invocation 消费。Step 6 与 Step 7 对同一 invocation 的复检不是 replay：两次必须返回同一
`authorization_id` 与同一规范化 envelope digest。`issued_at` 和 `expires_at` 必须为可解析的
RFC3339 UTC，满足 `issued_at < expires_at`、有效窗口不超过 30 分钟，且 Step 6/7 检查时均未
过期。Issue 状态规范化后只允许 `ready|in_progress`；`assigned_team_id` 必须等于 Runtime 提供的
`executing_team_id`。

envelope 的 repository/OpenSpec root/change/target 必须逐字匹配 Step 1–5 的只读结果；scope、
风险或外部副作用不匹配均失败。OpenSpec artifacts 或 Issue 描述若声明生产写入、不可逆迁移、
数据删除、提权、真实凭据或任何外部副作用，也超出 `standard` 自治范围。未知字段、缺失字段、
多 envelope、多个 issuer 结论、冲突值、过期、跨 invocation 重放或真实性 unknown 均在首次
Git 写入前零写失败；不得由模型修正或补全。

## Step 6：展示统一摘要并取得确认或授权快照（只读）

摘要必须显示：

- 命令范围与 proposal。
- `--openspec-root` 是否显式、规范化 `OPENSPEC_ROOT_REL`。
- `INVOCATION_PROJECT_DIR`、预期 `SOURCE_PROJECT_DIR` 和完整仓库相对
  `CHANGE_PREFIX`。
- `TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_HEAD`。
- 目标 clean、HEAD/ref 一致的检查结果。
- `SOURCE_BRANCH` 和 `SOURCE_WORKTREE_DIR` 的精确映射及无冲突结果。
- 完整仓库相对 `ARTIFACT_MANIFEST` 路径列表、各 blob 和
  `ARTIFACT_MANIFEST_DIGEST`。
- 确认后唯一的创建命令、进入新 worktree、apply、任务回填与来源提交。
- 风险说明：不会修改目标 worktree；任何创建后上下文失败都会保留来源 branch/worktree。
- `AUTHORIZATION_MODE`；自治模式还显示授权来源、issuer、authorization id 的脱敏审计标识、
  Issue/Team、时效、scope、边界和 envelope digest，但不得输出 token、签名或其他密钥材料。

两种模式必须展示相同的 target、canonical identity、artifact manifest、planned writes 和风险证据：

- 默认交互模式：使用交互工具请求无默认值、无超时自动同意的明确确认。拒绝、取消、缺失或
  模糊回答均保持 Git 不变；没有交互工具时输出问题并结束本次响应等待用户。
- Issue 自治模式：按上述契约验证可信 envelope，将完整摘要、规范化 envelope digest 和验证
  结论冻结为 `AUTONOMOUS_AUTHORIZATION_SNAPSHOT`，不再请求第二次人工确认。任何字段验证
  失败都停止，不得回退到交互模式、自动更新授权、换目标或接受新快照继续。

## Step 7：确认后快照复检（只读）

在首次 Git 写入前完整重跑 Step 1–5，要求下列值与确认摘要或自治授权快照逐字一致：

- 原始参数及重解析结果、`OPENSPEC_ROOT_EXPLICIT`、`OPENSPEC_ROOT_REL`、
  `INVOCATION_PROJECT_DIR`、`SOURCE_PROJECT_DIR`、`CHANGE_PREFIX` 和全部物理包含结论。
- `TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`。
- `TARGET_HEAD`、目标 worktree HEAD、目标 clean 状态。
- `SOURCE_BRANCH`、`SOURCE_WORKTREE_DIR` 及 branch/path/注册表无冲突状态。
- `ARTIFACT_MANIFEST` 和 `ARTIFACT_MANIFEST_DIGEST`。
- 从相同 `INVOCATION_PROJECT_DIR` 得到的 OpenSpec artifact 完成状态和全部风险说明。
- `AUTHORIZATION_MODE`。自治模式必须由 Runtime 复验同一 invocation 的同一
  `authorization_id`、同一 envelope digest、issuer authenticity、未过期状态及全部字段；不得
  接受另一个 authorization id 或更新后的 envelope。

交互模式的任何变化使原确认失效，返回 Step 6 展示更新摘要并请求新确认。自治模式的任何参数、
授权、ref/HEAD、worktree、manifest、风险或警告变化都直接失败关闭；不得回退到交互模式、自动
更新授权、换目标或使用新快照继续，只能由调用方发起新的 Issue-authorized invocation。即使 ref
在最后复检后再次推进，实际创建仍使用已确认或授权的 `<TARGET_HEAD>` hash，不能重新解析分支名。

## Step 8：从冻结 hash 创建规范 worktree（写入开始）

执行且只执行：

```bash
git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
```

创建失败立即停止；不得清理已有对象、追加后缀或以 ambient HEAD/`TARGET_BRANCH`/平台隐式创建方式重试。

随后把控制器的后续执行上下文绑定到 `SOURCE_WORKTREE_DIR`，并验证：

```bash
test "$(pwd -P)" = "<SOURCE_WORKTREE_DIR>"
test "$(git rev-parse --show-toplevel)" = "<SOURCE_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<SOURCE_BRANCH>"
test "$(git rev-parse HEAD)" = "<TARGET_HEAD>"
test "$(git rev-parse refs/heads/<SOURCE_BRANCH>)" = "<TARGET_HEAD>"
```

还必须从 `git worktree list --porcelain` 精确确认该路径注册到该 branch 和 HEAD。任一检查失败时停止 apply，并明确报告已保留的 `SOURCE_WORKTREE_DIR` 与 `SOURCE_BRANCH`；不自动删除、切换、重建或 fallback。

## Step 9：在来源 worktree 中再次验证项目与 artifacts

创建身份验证通过后，重新建立来源项目上下文：

- 通过进入目录并执行 `pwd -P` 解析 `SOURCE_WORKTREE_DIR`、`SOURCE_PROJECT_DIR`、其
  `openspec/` 和 proposal 目录；要求来源项目位于来源 worktree 内，`openspec/` 位于
  来源项目内，proposal 位于其 `openspec/changes/` 内。
- 从验证后的 `SOURCE_PROJECT_DIR` 重跑 OpenSpec status，要求所有 artifacts 为 `done`
  且 `isComplete=true`。
- 从 `SOURCE_WORKTREE_DIR` 按确认的完整仓库相对 `ARTIFACT_MANIFEST` 重新枚举路径并
  逐项计算 blob，要求路径集合、每个 blob 和 digest 都与 `TARGET_HEAD` 及确认快照一致。

路径缺失、物理越界、status 不完整、manifest/blob 漂移或任何 unknown 都停止，不进入
apply。保留已经创建的 `SOURCE_BRANCH` 和 `SOURCE_WORKTREE_DIR`；不得清理、换根、重建、
回退到仓库根或使用其他 OpenSpec 项目重试。

## Step 10：执行 OpenSpec apply

仅以已验证的 `SOURCE_PROJECT_DIR` 为当前工作目录调用：

```text
Skill("openspec-apply-change", args="<proposal-name>")
```

不得从来源 worktree 根、目标 worktree、invocation worktree 或其他项目目录调用 apply。

## Step 11：任务核对、回填和来源提交

从 `<SOURCE_PROJECT_DIR>/openspec/changes/<proposal-name>/tasks.md` 读取最终任务状态，按
Markdown checkbox 统计：`- [x]` 为 `DONE`，`- [ ]` 为未完成，二者之和为 `TOTAL`，并
计算 `REMAINING=TOTAL-DONE`。保留现有四类回填规则，但只能在来源 worktree 中按实际
交付证据标记；仅有文件名或模糊关键词而没有任务要求的实现证据时不得标记完成。

任务进度和未完成原因必须遵守以下契约：

- `TOTAL > 0` 且 `DONE == TOTAL` 时进度为 `complete`；`DONE < TOTAL` 时为 `partial`。
- `tasks.md` 缺失、不可读或 `TOTAL == 0` 时进度为 `unknown`，不得把 `0/0` 报告为完成。
- 每个未完成 task 必须且只能归入一个类别：`尚未进入实施阶段`、`实现未完成`、
  `测试或验证失败`、`依赖未满足`、`执行异常`、`原因未知`。
- 分类只能依据本次 workflow 的直接证据，包括 apply 返回、测试或验证输出、依赖状态和
  已执行阶段。不得根据 task 编号、task 正文、文件名或关键词猜测原因；证据不足时计入
  `原因未知`。
- 各原因类别的数量之和必须等于 `REMAINING`。未完成原因概要只输出数量和一句归类说明；不得输出 task 编号、task 正文或逐项清单。数量为 0 的类别省略。

```bash
git -C <SOURCE_WORKTREE_DIR> add -A
git -C <SOURCE_WORKTREE_DIR> add -f <CHANGE_PREFIX>/tasks.md
```

有变更时提交到 `SOURCE_BRANCH`：

- 全部完成：`feat: implement <proposal-name> (DONE/TOTAL tasks)`
- 部分完成：`feat: implement <proposal-name> (DONE/TOTAL tasks, partial)`

提交后验证 CWD、规范 branch/path、source HEAD/ref 一致和 source clean。提交或验证失败时保留现场并停止。

## 成功输出

```text
## Worktree Created & Apply Complete

Proposal: <proposal-name>
Source branch: worktree-<proposal-name>
Source worktree: <REPO_ROOT>/.claude/worktrees/<proposal-name>
OpenSpec root: <OPENSPEC_ROOT_REL> (<explicit-or-default>)
Invocation project: <INVOCATION_PROJECT_DIR>
Source project: <SOURCE_PROJECT_DIR>
Change prefix: <CHANGE_PREFIX>
Target: <TARGET_BRANCH> at <TARGET_HEAD>
Target worktree: <TARGET_WORKTREE_DIR> (unchanged)
Artifact manifest: <ARTIFACT_MANIFEST_DIGEST> verified
Authorization: <interactive confirmation | issue-authorization/v1 authorization_id audit label>
Authorization validity: <not-applicable | issued_at..expires_at, valid at final pre-write check>
Authorized boundary: isolated source worktree apply and source commit only
Proposal progress: <complete|partial|unknown>
Tasks: <DONE>/<TOTAL> | unknown
Remaining: <REMAINING> | unknown
Unfinished reason summary: <category=count; ... | none | unknown: reason>

下一步：从来源 worktree 运行
/merge-worktree-return <proposal-name> --target <TARGET_BRANCH>
```

当进度为 `complete` 时，`Unfinished reason summary` 输出 `none`；当进度为 `partial` 时，
输出计数之和等于 `Remaining` 的原因类别及一句概要；当进度为 `unknown` 时，输出导致无法
读取或计算进度的概要原因，并使用 `Tasks: unknown` 和 `Remaining: unknown`。Step 10 或 Step 11 失败后的终态报告只要能够读取最终
`tasks.md`，也必须包含同一组数量字段和原因概要；无法读取时按 `unknown` 输出。

## 失败输出

所有失败都报告失败发生在首次写入前还是创建后，并记录 `AUTHORIZATION_MODE`。自治失败还要
记录可信 Runtime issuer、authorization id 的脱敏审计标识、`issued_at`/`expires_at`、失败时刻、
envelope digest、授权边界和精确失败字段；不得输出 token 或签名材料。创建后的失败继续报告
保留的 source branch/worktree，且不会扩大 Issue 授权边界。

## Guardrails

- 确认前零 Git 写入；确认后也不得修改目标 worktree。
- 创建 start-point 必须是确认的 commit hash，禁止使用可变 branch name 或 ambient HEAD。
- canonical branch/path 任一冲突都失败，不覆盖、不复用、不改名。
- artifacts 必须已经存在于 `TARGET_HEAD` 且与确认内容逐字节一致。
- OpenSpec 根只能来自显式参数或默认 `.`；禁止搜索、猜测、回退或环境变量覆盖。
- OpenSpec status/apply 只从验证后的项目目录运行；Git manifest/stage 只使用完整仓库相对
  `CHANGE_PREFIX`。
- 自治模式必须显式指定 target，并在首次写入前验证可信 `issue-authorization/v1`；Issue id、
  用户粘贴的 JSON 或仓库内 metadata 均不单独构成授权。
- 自治授权不包含 merge、release、deploy、生产/外部副作用或 elevated-risk 工作；授权或快照
  漂移一律零写失败，不切换模式。
- 禁止强制 worktree/ref 清理；错误和 recovery 文本也不得建议强制删除。
- 禁止自动 reset/revert、自动 merge、自动重试创建或切换目标工作树。
- 所有命令错误、解析失败和 unknown 状态都按失败处理，并报告保留现场。
