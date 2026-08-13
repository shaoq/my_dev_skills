## Context

`new-worktree-apply` 目前把 `CHANGE_PREFIX` 固定为
`openspec/changes/<proposal>`，并从 Git 仓库根调用 OpenSpec CLI。该假设适用于
`my_dev_skills`，但不适用于同一 Git 仓库中包含一个或多个子项目的布局，例如：

```text
<git-worktree>/twin-rag/openspec/changes/<proposal>
```

现有 worktree 安全合同要求确认前零 Git 写入、artifact 必须存在于冻结
`TARGET_HEAD`、创建必须使用不可变 hash、来源 branch/path 必须规范且唯一。新增项目
根选择不能削弱这些条件，也不能通过递归搜索在 monorepo 中猜测用户意图。

## Goals / Non-Goals

**Goals:**

- 用显式 `--openspec-root` 安全支持 Git 仓库内嵌套的 OpenSpec 项目。
- 保持省略参数时仓库根 OpenSpec 项目的现有行为。
- 把所选项目根绑定到确认快照、artifact manifest、创建后复验、apply 和任务回填。
- 对路径越界、歧义、漂移或读取错误失败关闭。

**Non-Goals:**

- 不自动发现或选择 OpenSpec 项目。
- 不移动、复制、创建或自动提交 proposal artifacts。
- 不修改来源 branch/worktree 的规范身份或目标分支选择顺序。
- 不给 `merge-worktree-return` 或 `parall-new-worktree-apply` 新增同名参数。
- 不新增脚本、运行时依赖或平台专用 worktree 创建机制。

## Decisions

### 1. 使用显式仓库相对目录，不自动发现

命令新增可选参数：

```text
new-worktree-apply <proposal> [--target <branch>] [--openspec-root <directory>]
```

`--target` 与 `--openspec-root` 可按任意顺序出现，但各自最多一次且必须有值。
`OPENSPEC_ROOT=.` 为默认值；非 `.` 值表示“Git 仓库内直接包含
`openspec/` 的目录”。例如 `--openspec-root twin-rag` 对应
`twin-rag/openspec/changes/<proposal>`。

拒绝自动递归发现，因为一个仓库可能同时包含多个 OpenSpec 项目；“唯一搜索结果”也不
作为回退，以免仓库新增第二个项目后改变既有命令语义。也不把 OpenSpec 根编码进
proposal 名称，因为 proposal 身份必须继续只表达 change 名称。

### 2. 分离逻辑路径、当前项目物理路径和来源项目路径

定义：

```text
OPENSPEC_ROOT_REL          = 用户值或 .
CHANGE_PREFIX              = openspec/changes/P
                             （OPENSPEC_ROOT_REL=.）
                           | OPENSPEC_ROOT_REL/openspec/changes/P
INVOCATION_PROJECT_DIR     = <INVOCATION_WORKTREE_DIR>/<OPENSPEC_ROOT_REL>
SOURCE_PROJECT_DIR         = <SOURCE_WORKTREE_DIR>/<OPENSPEC_ROOT_REL>
```

`CHANGE_PREFIX` 始终是从 Git 仓库根开始、无 `./` 前缀的 POSIX 风格相对路径，
用于 `git ls-tree`、`git rev-parse <hash>:<path>`、blob 比较、manifest 和
`git add -f`。OpenSpec CLI 则从对应的 `*_PROJECT_DIR` 运行，使 CLI 仍看到本
项目自己的 `openspec/config.yaml` 与 `openspec/changes/`。

不把 `REPO_ROOT` 与 `INVOCATION_WORKTREE_DIR` 混用：前者继续表示主
worktree，并决定规范来源 worktree 路径；后者表示用户正在确认 artifacts 的当前
worktree，并决定当前 OpenSpec 项目物理路径。

### 3. 路径先做词法校验，再做物理包含校验

除特殊值 `.` 外，参数必须是规范化的仓库相对目录。解析器拒绝：

- host 平台绝对路径、`~` 前缀和反斜杠路径；
- 开头/结尾 `/`、连续 `/`；
- 空路径段、`.` 或 `..` 路径段；
- 空白或控制字符；
- 重复参数、缺值和未知选项。

随后解析 `INVOCATION_PROJECT_DIR` 的物理路径并证明它位于
`INVOCATION_WORKTREE_DIR` 的物理路径内；`openspec/` 和目标 change 目录也
必须存在且解析后仍在该项目目录内。符号链接可以存在，但只要导致任何物理路径逃出
相应 worktree/项目边界就失败。路径检查或规范化命令失败均视为 unknown 并停止。

备选方案是仅拒绝 `..`。这无法阻止符号链接逃逸，因此不足。另一方案是拒绝所有
符号链接，虽更简单但会无必要排除仍严格位于仓库内的合法布局，因此采用物理包含判断。

### 4. 所选项目根成为确认快照的一部分

Step 6 除现有信息外必须显示：

- 原始 `--openspec-root` 是否显式提供及规范化 `OPENSPEC_ROOT_REL`；
- `INVOCATION_PROJECT_DIR`；
- 创建后的预期 `SOURCE_PROJECT_DIR`；
- 仓库相对 `CHANGE_PREFIX`。

Step 7 从参数解析开始完整重跑，并要求这些值、物理包含结论、OpenSpec status、
manifest 路径/内容/digest 与原摘要逐字一致。变化时原确认失效；不能切换到自动发现
的项目或用新路径继续旧确认。

### 5. Manifest 保持仓库相对且与冻结提交逐 blob 一致

四个固定 artifact、递归 specs 和可选 `dependencies.yaml` 均以
`CHANGE_PREFIX` 为前缀。当前路径集合从 invocation worktree 枚举，目标集合从
`TARGET_HEAD` tree 独立枚举；两侧集合和逐文件 blob 必须完全相同。digest 输入继续
使用排序后的 `<repo-relative-path> <blob>` 行，因此同名 proposal 位于不同
OpenSpec 根时会得到不同且无歧义的 manifest。

不把 manifest 改为相对 OpenSpec 项目根，因为 Git tree 查询和后续
`git add -f` 都需要仓库相对路径；省略项目前缀会让 monorepo 中同名 change 无法
区分。

### 6. 创建后重新建立来源项目上下文

`git worktree add` 和来源 Git 身份检查仍从
`SOURCE_WORKTREE_DIR` 执行，不改变规范创建命令。创建验证通过后再验证
`SOURCE_PROJECT_DIR` 的物理包含关系、OpenSpec status 和 manifest blobs；只有全部
匹配 `TARGET_HEAD` 才从该目录调用 `openspec-apply-change`。

任务核对读取 `<SOURCE_PROJECT_DIR>/openspec/changes/P/tasks.md`，暂存仍从来源
worktree 根执行，并用仓库相对 `<CHANGE_PREFIX>/tasks.md` 进行 `git add -f`。
如果创建后的项目目录缺失、逃逸或与确认快照不同，停止 apply 并保留已创建的规范
branch/worktree，不自动清理、重建或换根重试。

### 7. 保留运行时 frontmatter，并隔离通用 validator 的已知边界

`new-worktree-apply` 继续保留 Claude 运行时需要的顶层 `argument-hint` 和
`disable-model-invocation`。当前 skill-creator `quick_validate.py` 只接受通用 Agent
Skills 字段，会对这两个变更前已存在的扩展字段返回固定的 unknown-key 诊断；不得为了让
通用 validator 返回零退出码而删除、移动或弱化运行时字段。

交付验证仍须实际运行 `quick_validate.py`。只有当当前文件与 `HEAD` 基线都仅返回相同的
`argument-hint, disable-model-invocation` unknown-key 诊断时，才将其记录为已知工具边界；
任何新增字段、不同诊断或其他结构错误仍阻止完成。同时独立解析真实 `SKILL.md` 的 YAML，
验证 `name`、`description`、`argument-hint`、`disable-model-invocation` 和 `allowed-tools`
的类型与预期值，再运行 OpenSpec strict、Markdown/diff 和隔离场景验证。

## Risks / Trade-offs

- **[参数增加认知成本]** → 默认仍为 `.`；只有嵌套项目需要显式传参，并在摘要中
  展示完整解析结果。
- **[物理路径判断存在跨平台差异]** → 使用现有 Bash/Git 可用的真实路径检查并对
  命令失败统一失败关闭；验证覆盖根目录、嵌套目录和逃逸路径。
- **[同一 proposal 名可能存在于多个项目]** → 绝不按名称搜索；用户必须显式选择，
  manifest 使用完整仓库相对路径。
- **[确认等待期间目录或符号链接变化]** → Step 7 重跑词法、物理和 artifact 全量
  检查，任一变化要求重新确认。
- **[只修改单 apply 技能造成参数不对称]** → 这是有意范围；返回流程从规范来源
  branch/worktree 工作且不需要重新选择 proposal 项目。并行技能的多项目发现策略另行
  设计，不在本 change 中隐式扩展。
- **[通用 skill validator 不识别 Claude 扩展 frontmatter]** → 保留运行时字段；要求
  当前与变更前基线产生完全相同且仅限两个既有字段的诊断，并用独立 YAML/runtime 字段
  校验覆盖该工具盲区。其他诊断仍失败关闭。

## Migration Plan

1. 更新 `worktree-targeting` delta requirement，冻结参数、路径、快照和执行上下文。
2. 修改 `new-worktree-apply/SKILL.md` 的参数解析与 Step 1、4～11。
3. 更新 README 示例。
4. 先复现当前技能对嵌套项目的 RED 失败，再在隔离场景中验证 GREEN、根目录回归与
   非法路径失败。
5. 运行 OpenSpec strict、skill 结构检查、Markdown/diff 检查和 GitNexus
   `detect_changes`；对 quick validator 的两个既有 Claude 扩展字段诊断按 Decision 7
   处理，并独立验证真实 frontmatter。

回滚时同时回滚 skill、README 和现行 spec。已创建的用户 worktree 不由回滚流程自动
删除或改名。

## Open Questions

无。参数名称、默认值、仓库相对语义、嵌套目录示例及禁止自动发现均已由用户确认。
