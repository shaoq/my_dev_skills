---
name: new-worktree-apply
description: Use when starting implementation of an OpenSpec change in a new isolated git worktree.
argument-hint: <proposal-name> [--target <target-branch>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(find *) Bash(sort *) Bash(grep *) Bash(test *) Bash(pwd *) Bash(awk *) Bash(sed *) Read Write Edit Glob Grep Skill AskUserQuestion
---

为一个 OpenSpec proposal 创建规范化 worktree，并在其中实施。

**输入**：一个 proposal 名称和可选的 `--target <target-branch>`。

```text
/new-worktree-apply add-user-auth
/new-worktree-apply add-user-auth --target develop
```

## 核心不变量

- Step 1–6 只读：确认和快照复检完成前，不执行 Git 写操作、不创建 worktree、不调用 apply。
- 不 checkout/switch、stage、commit、stash、reset 或以其他方式修改主工作树或任何现有目标 worktree。
- 目标分支必须已经由一个注册 worktree 精确持有，且该 worktree clean、HEAD 与 branch ref 一致。
- 规范身份固定为：
  ```text
  PROPOSAL=<proposal-name>
  SOURCE_BRANCH=worktree-<proposal-name>
  SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>
  ```
- 创建只使用用户确认的不可变 commit hash：
  ```bash
  git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
  ```
- 不能接受明确 branch、path 和 commit hash 的平台 worktree 创建能力不得替代上面的 Git 命令。
- 任一检查失败或结果 unknown 时失败关闭；已创建的现场保留，不自动删除、改名、换参数或换机制重试。

## Step 1：解析参数与检查前置条件（只读）

仅接受一个 proposal 位置参数及至多一个 `--target <target-branch>`。缺少 proposal、多余位置参数、`--target` 缺值/重复或未知选项均报错并停止。

旧 `--branch` 不是别名。检测到后只显示等价 `--target` 用法并停止，不产生 Git 写操作。

检查：

```bash
git rev-parse --is-inside-work-tree
git rev-parse --show-toplevel
git worktree list --porcelain
which openspec
test -d openspec/changes/<proposal-name>
```

proposal 名称必须是小写 kebab-case（只含小写字母、数字和单个连字符分隔）。最终 `SOURCE_BRANCH=worktree-<proposal-name>` 长度不超过 64，且必须通过 `git check-ref-format --branch <SOURCE_BRANCH>`；不得包含 `/`、`..`、空白或连续连字符。

## Step 2：选择目标分支（只读）

按以下顺序选择 `TARGET_BRANCH` 并记录 `TARGET_SOURCE`：

1. 显式 `--target`，必须精确存在于 `refs/heads/`；不存在时不 fetch、不创建、不回退。
2. 主工作树当前检出的有效本地分支。
3. `origin/HEAD` 指向的本地同名分支。
4. `main`、`master`、`trunk` 中首个存在的本地分支。

所有 ref 检查都使用完整本地 ref，例如：

```bash
git rev-parse --verify --quiet refs/heads/<TARGET_BRANCH>
```

无可用候选时停止并要求显式指定目标。

## Step 3：解析 worktree 拓扑和规范身份（只读）

从 `git worktree list --porcelain` 精确记录：

- `PRIMARY_WORKTREE_DIR`：列表中的主工作树；同时定义 `REPO_ROOT=<PRIMARY_WORKTREE_DIR>`。
- `INVOCATION_WORKTREE_DIR`：当前 `git rev-parse --show-toplevel`。
- `TARGET_WORKTREE_DIR`：注册为持有 `refs/heads/<TARGET_BRANCH>` 的唯一 worktree。
- `SOURCE_BRANCH=worktree-<proposal-name>`。
- `SOURCE_WORKTREE_DIR=<REPO_ROOT>/.claude/worktrees/<proposal-name>`，转换为绝对规范路径。

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

读取 `openspec status --change "<proposal-name>" --json`，要求所有 artifacts 为 `done` 且 `isComplete=true`。

## Step 5：构建 `ARTIFACT_MANIFEST`（只读）

定义：

```text
CHANGE_PREFIX=openspec/changes/<proposal-name>
```

manifest 必须包含：

- `<CHANGE_PREFIX>/.openspec.yaml`
- `<CHANGE_PREFIX>/proposal.md`
- `<CHANGE_PREFIX>/design.md`
- `<CHANGE_PREFIX>/tasks.md`
- 递归枚举 `<CHANGE_PREFIX>/specs/` 下的全部文件；至少存在一个 `spec.md`
- 当前工作区或 `TARGET_HEAD` 任一侧存在 `dependencies.yaml` 时包含该文件

验证算法必须按以下顺序执行：

1. 在当前确认工作区检查四个固定文件和 `specs/` 目录。
2. 用 `find <CHANGE_PREFIX>/specs -type f | LC_ALL=C sort` 枚举当前 spec 路径集合；禁止使用单层 `specs/*.md` glob。
3. 用 `git ls-tree -r --name-only <TARGET_HEAD> -- <CHANGE_PREFIX>/specs` 独立枚举 commit tree 路径集合。
4. 两侧路径集合必须完全相等且非空。
5. 对四个固定文件和可选 `dependencies.yaml`，两侧存在性必须完全一致；固定文件必须两侧都存在。
6. 对 manifest 每个路径比较当前内容 blob 与冻结提交 blob：
   ```bash
   CURRENT_BLOB=$(git hash-object -- <path>)
   TARGET_BLOB=$(git rev-parse <TARGET_HEAD>:<path>)
   test "$CURRENT_BLOB" = "$TARGET_BLOB"
   ```
7. 将排序后的 `<path> <blob>` 行记录为 `ARTIFACT_MANIFEST`，并用 `git hash-object --stdin` 生成 `ARTIFACT_MANIFEST_DIGEST`。

untracked、ignored、新增、删除、重命名、内容差异、路径读取错误、空 delta spec 集合或 `dependencies.yaml` 单侧缺失都阻止创建。不得为通过检查而自动提交 artifacts。

## Step 6：展示摘要并取得明确确认（只读）

摘要必须显示：

- 命令范围与 proposal。
- `TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`、`TARGET_HEAD`。
- 目标 clean、HEAD/ref 一致的检查结果。
- `SOURCE_BRANCH` 和 `SOURCE_WORKTREE_DIR` 的精确映射及无冲突结果。
- 完整 `ARTIFACT_MANIFEST` 路径列表和 `ARTIFACT_MANIFEST_DIGEST`。
- 确认后唯一的创建命令、进入新 worktree、apply、任务回填与来源提交。
- 风险说明：不会修改目标 worktree；任何创建后上下文失败都会保留来源 branch/worktree。

使用交互工具请求无默认值、无超时自动同意的明确确认。拒绝、取消、缺失或模糊回答均保持 Git 不变；没有交互工具时输出问题并结束本次响应等待用户。

## Step 7：确认后快照复检（只读）

在首次写操作前完整重跑 Step 1–5，要求下列值与确认摘要逐字一致：

- 参数、`TARGET_BRANCH`、`TARGET_SOURCE`、`TARGET_WORKTREE_DIR`。
- `TARGET_HEAD`、目标 worktree HEAD、目标 clean 状态。
- `SOURCE_BRANCH`、`SOURCE_WORKTREE_DIR` 及 branch/path/注册表无冲突状态。
- `ARTIFACT_MANIFEST` 和 `ARTIFACT_MANIFEST_DIGEST`。
- OpenSpec artifact 完成状态和全部风险说明。

任何变化使原确认失效，返回 Step 6 请求新确认。即使 ref 在最后复检后再次推进，实际创建仍使用已确认的 `<TARGET_HEAD>` hash，不能重新解析分支名。

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

## Step 9：在来源 worktree 中再次验证 artifacts

在新 worktree 中重跑 OpenSpec status，并根据 `ARTIFACT_MANIFEST` 逐项确认路径和 blob 与 `TARGET_HEAD` 一致。任何丢失或不同都停止，不进入 apply。

## Step 10：执行 OpenSpec apply

在已验证的 `SOURCE_WORKTREE_DIR` 中调用：

```text
Skill("openspec-apply-change", args="<proposal-name>")
```

不得从目标或 invocation worktree 调用 apply。

## Step 11：任务核对、回填和来源提交

读取 `tasks.md`，统计 `- [x]` 与 `- [ ]`。保留现有四类回填规则，但只能在来源 worktree 中按实际交付证据标记；仅有文件名或模糊关键词而没有任务要求的实现证据时不得标记完成。

```bash
git add -A
git add -f openspec/changes/<proposal-name>/tasks.md
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
Target: <TARGET_BRANCH> at <TARGET_HEAD>
Target worktree: <TARGET_WORKTREE_DIR> (unchanged)
Artifact manifest: <ARTIFACT_MANIFEST_DIGEST> verified
Tasks: DONE/TOTAL

下一步：从来源 worktree 运行
/merge-worktree-return <proposal-name> --target <TARGET_BRANCH>
```

## Guardrails

- 确认前零 Git 写入；确认后也不得修改目标 worktree。
- 创建 start-point 必须是确认的 commit hash，禁止使用可变 branch name 或 ambient HEAD。
- canonical branch/path 任一冲突都失败，不覆盖、不复用、不改名。
- artifacts 必须已经存在于 `TARGET_HEAD` 且与确认内容逐字节一致。
- 禁止强制 worktree/ref 清理；错误和 recovery 文本也不得建议强制删除。
- 禁止自动 reset/revert、自动 merge、自动重试创建或切换目标工作树。
- 所有命令错误、解析失败和 unknown 状态都按失败处理，并报告保留现场。
