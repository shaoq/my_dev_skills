## Context

本仓库的 skill 以 Markdown 指令描述跨 Runtime 的执行协议。`new-worktree-apply` 具有明确的命令名称和有限的本地隔离作用域。默认非交互写入依赖各 Runtime 自身强制执行的显式调用门禁：Claude 使用 frontmatter 的 `disable-model-invocation: true`，Codex 使用 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false`；其他 Runtime 只有具备等价策略时才受支持。

现有实现有两类不一致：

1. `new-worktree-apply` 把这次显式调用之后的第二次人工确认设为默认，并额外引入 Issue/Team/Runtime 授权协议；这让没有 Issue 的本地 proposal 无法自治执行，也把通用 Git/OpenSpec skill 与特定任务平台耦合。
2. `verify-impl-consistency` 和 `check-changes-completed` 分别曾在 OpenSpec 增量验证、D3 交付验证和 D5 合规验证中使用 `main..HEAD`，与工作流中显式选择的目标分支脱节。

安全目标不是证明某个外部 Issue 是否授权，而是保证调用参数、目标 checkout、OpenSpec artifacts 和首次写入使用同一个经过复检的不可变快照。真正改变共享分支的边界仍是后续 merge。

## Goals / Non-Goals

**Goals:**

- 让显式调用的 `new-worktree-apply` 在预检通过后默认直接实施，不再重复请求人工确认。
- 只在 Runtime 原生策略保证当前 skill 无法被模型隐式激活时允许默认非交互写入；自动选择、嵌套转调或无法执行等价门禁时失败关闭。
- 让该 skill 与 Issue、Team 和具体 Runtime 解耦，支持任何来源的 OpenSpec proposal。
- 要求 `new-worktree-apply` 显式提供目标分支，避免非交互执行时猜测写入基线。
- 提供严格只读的 `--dry-run`，供调用方在需要时主动查看完整计划。
- 保留所有 Git/OpenSpec 安全不变量，并在首次写入前对完整快照做最终漂移复检。
- 为 repository verification skills 建立显式、不可变、可报告的目标分支基线。
- 让实现、测试、任务交付和配套合规检查对同一目标 branch/commit 归因。
- 通过回归扫描阻止新的非归档 skill 引入 `main..HEAD`、`refs/heads/main` 等固定比较基线。

**Non-Goals:**

- 不取消 `merge-worktree-return` 或并行集成的人工确认。
- 不让 `new-worktree-apply` 执行 merge、发布、生产操作、不可逆数据变更或外部副作用。
- 不从 Issue、Team、tracker、环境变量或任务平台授权 envelope 推导高风险或外部权限。
- 不把用户消息正文、仓库文件、环境变量或模型对意图的解释当作 Runtime 显式调用门禁的替代证据。
- 不修改 OpenSpec CLI、Git 配置、默认分支或用户目录下已安装的 skill。
- 不把诊断 skill 改造成自动修复器或最终 pass/fail 裁决器。
- 不抽取新的可执行共享库；各 skill 继续以自包含的 Markdown 协议运行。

## Decisions

### 1. 使用一个跨 skill 的冻结目标基线契约

所有需要计算“目标分支到当前 HEAD 的变更”的验证必须先解析一个显式本地目标分支，再冻结：

```text
BASE_BRANCH=<调用方显式提供的本地目标分支>
BASE_HEAD=$(git rev-parse refs/heads/<BASE_BRANCH>^{commit})
CURRENT_HEAD=$(git rev-parse HEAD^{commit})
COMPARISON_RANGE=<BASE_HEAD>..<CURRENT_HEAD>
```

冻结后必须执行 `git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>`。失败时不得改用 merge-base、当前分支、旧 target commit 或其他推断值。`verify-impl-consistency` 可以继续项目级诊断，但把 OpenSpec 增量维度标记为未执行；`check-changes-completed` 输出阻塞结果且不得回填、stage 或 commit 任何 `tasks.md`。

后续 Git 命令全部使用两个冻结 commit hash，不重复解析可移动的 branch name，也不使用字面 `HEAD`。结束时同时复检 `refs/heads/<BASE_BRANCH>` 与当前 `HEAD`：

- `verify-impl-consistency` 发现任一漂移时保留冻结诊断，但标记为 stale evidence。
- `check-changes-completed` 发现任一漂移时把可存档结论置为 unknown/blocked，并保持零写。

### 2. 增量验证使用显式 change 选择

- `verify-impl-consistency <change-name> --base <target-branch>`：提供 change 时必须同时提供唯一 `--base`，change 必须精确匹配 active change。无参数时只执行项目级 D1/D2/D3。
- `check-changes-completed --target <target-branch> --change <name> [--change <name> ...]`：要求一个目标和一个或多个显式 active change，未选择的 changes 不参与扫描、结论或回填。

二者都拒绝重复选项、缺值、未知 flag、多余位置参数和不存在的本地分支。不得以 `main`、当前分支、`origin/HEAD`、conventional branch 或 active-change 自动发现替代缺失输入。

### 3. 完成度检查的选择集、D3、D5 与写回边界共用同一快照

D3 的提交证据使用：

```text
git log --oneline <BASE_HEAD>..<CURRENT_HEAD> -- <expected-file-paths>
```

D5 的配套产出范围使用：

```text
git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only
```

只有显式 `--change` 选择集参与五维扫描、blocking reasons、任务矛盾检测和 Level-1/Level-2 回填。选择集中的 changes 共用本次调用冻结的目标基线；若它们面向不同目标，调用方必须拆分调用。

### 4. Runtime 原生门禁证明用户显式调用

默认写入前，实际承载调用的 Runtime 必须已强制执行禁止隐式激活的原生控制面策略：

- Claude Code：本 skill frontmatter 设置 `disable-model-invocation: true`，用户通过 `/new-worktree-apply ...` 直接激活；
- Codex：本 skill 的 `agents/openai.yaml` 设置 `policy.allow_implicit_invocation: false`，用户通过 `$new-worktree-apply ...` 直接激活；
- 其他 Runtime：只有提供等价、由 Runtime 自身强制的原生显式调用策略时才支持默认写入。

在这些门禁下发生的 skill 激活就是可信的用户显式调用断言，无需 Markdown skill 无法访问的 dispatcher 字段。用户消息正文、仓库文件、环境变量、模型推断或另一个 skill 构造的参数不能创建或替换该断言。自然语言任务匹配导致的模型自动选择和 `Skill("new-worktree-apply", ...)` 嵌套转调都被 Runtime 策略挡在 skill 激活之前；Runtime 无法提供等价策略时在仓库写入前停止，且不得降级为人工确认。

### 5. 可信显式调用构成有限 Worktree Apply 授权

`new-worktree-apply` 的唯一执行语法为：

```text
/new-worktree-apply <change> --target <branch> [--openspec-root <path>]
```

Runtime 证明的用户显式调用授权以下有限操作：

- 从冻结的 `TARGET_HEAD` 创建 canonical source branch/worktree；
- 在该来源 worktree 中执行 OpenSpec apply；
- 执行 proposal 范围内的本地验证；
- 提交来源变更。

skill 不再区分交互与自治模式，不接受 `--authorized` 或 `--authorized-by-issue`，也不读取 Issue、Team 或任务平台授权数据。Runtime 原生门禁只证明用户如何激活本 skill，不携带 Issue 权限、外部系统身份、凭据或高风险授权。检测到旧 `--authorized-by-issue` 时在任何写入前停止，并显示移除该参数后的等价命令。

`--target` 对 `new-worktree-apply` 为必填项。默认非交互执行不能通过主工作树、`origin/HEAD` 或 conventional branch fallback 猜测目标。该要求只改变单 change apply，不改变另外两个 worktree skill 的目标选择规则。

### 6. dry-run 与默认执行共享同一只读预检

可选调用：

```text
/new-worktree-apply <change> --target <branch> [--openspec-root <path>] --dry-run
```

`--dry-run` 执行完整的参数、repository/OpenSpec root、目标 worktree、cleanliness、canonical identity、创建父目录物理包含、artifact manifest、`TARGET_HEAD` 和计划写入检查，只创建并输出一次 `PREFLIGHT_SNAPSHOT` 后结束。它不得创建 branch/worktree、调用 apply、stage、commit、stash、checkout、switch、reset 或执行其他写操作。

默认模式执行同一预检，随后直接进入最终复检，不等待确认。dry-run 的输出不构成未来调用可复用的授权或快照；后续真实执行必须重新完成全部检查。

Runtime 原生显式调用门禁是两个模式共同的调用入口。Runtime 无法强制等价门禁时，即使请求 dry-run 也停止；停止本身保持零写。

### 7. 写前漂移复检取代重复人工确认

首次写入前重新解析并比较：

- 本次调用参数；
- repository 与 OpenSpec root；
- target branch/ref/HEAD；
- target worktree 注册、CWD 和 clean 状态；
- canonical source branch/path 不存在性；
- canonical source 父目录的物理包含与非符号链接状态；
- 完整 artifact path set、blob identity 和 digest；
- 计划写入范围。

`PREFLIGHT_SNAPSHOT` 只在预检时创建一次且不可覆盖。最终复检仅重跑收集上述只读事实所需的检查，把结果写入独立不可变的 `REVALIDATION_SNAPSHOT`，再逐字段比较。任何变化、未知值或命令错误都直接零写停止。skill 不自动刷新基线、自动接受新状态、切换目标、交互询问或使用新快照继续；调用方在处理漂移后重新发起命令。

通过复检后，创建命令仍以冻结 hash 为起点：

```text
git worktree add <SOURCE_WORKTREE_DIR> -b <SOURCE_BRANCH> <TARGET_HEAD>
```

因此 target ref 在最终复检之后移动，也不会改变本次来源 worktree 的实际基线。

### 8. 默认执行不扩大到共享或外部副作用

默认非交互只覆盖本地隔离来源交付。proposal/design/tasks 若要求 merge、release、deploy、生产系统写入、不可逆迁移、数据删除、权限提升、真实凭据或其他外部副作用，skill 必须在相关动作前停止并报告超出作用域。它不得因为调用本身已授权 worktree apply 而推导这些额外权限。

`merge-worktree-return` 和 `parall-new-worktree-apply` 的人工确认保持不变，因为它们会改变共享目标分支或串行集成多个来源。

### 9. 采用协议测试与固定基线回归扫描

测试必须验证：

- 默认调用在稳定预检后不询问确认并创建 canonical worktree。
- Claude `disable-model-invocation: true` 与 Codex `policy.allow_implicit_invocation: false` 可被结构化测试验证；模型自动选择、嵌套转调或缺少等价 Runtime 门禁时均零写失败。
- `--dry-run` 在成功和失败场景都保持零写。
- 缺失显式 `--target`、旧授权参数、未知参数和重复参数在首次写入前停止。
- target/artifact/worktree 快照漂移直接失败关闭，不覆盖预检基线或进入交互确认。
- `.claude` 或 `.claude/worktrees` 缺失、不可验证或通过符号链接逃逸时，在创建 branch/worktree 前失败关闭。
- merge 与并行 apply 仍要求人工确认。
- 两个验证 skill 使用冻结的非 `main` commit，并在目标不是当前 commit 祖先时失败关闭。
- 未选择 change 永不被 completion check 回填。
- 非归档 source `SKILL.md` 不包含用于变更归因的固定 `main..HEAD`/`refs/heads/main`。

## Risks / Trade-offs

- [不同 Runtime 对 skill 自动触发的支持不同] → 为 Claude 与 Codex 分别配置其原生禁止隐式调用策略；其他 Runtime 缺少等价门禁时失败关闭。
- [错误的上游自动化尝试转调] → Runtime 原生策略禁止 nested/model-selected activation，不能由 Markdown 内容绕过。
- [默认执行会创建 branch、worktree 和来源 commit] → 所有写入限定在 canonical source identity，目标 worktree保持不变；失败现场保留，不自动清理或扩大操作范围。
- [dry-run 结果可能在真实执行前过期] → dry-run 不可复用；真实执行重新冻结并复检全部事实。
- [显式基线参数带来调用迁移成本] → 这是有意的确定性输入，避免自动化流程把错误目标当作基线。
- [目标或当前分支在长时间诊断中移动] → 所有 Git 查询使用冻结 commits；结束时复检两侧，完成度检查禁止在漂移后写回。
- [目标 tip 不是当前 commit 的祖先] → 失败关闭，不用 tree-to-tree diff 冒充交付范围，也不静默改用 merge-base。

## Migration Plan

1. 更新 delta specs 和任务清单，明确 Runtime 原生显式调用门禁、默认非交互、必填 target、dry-run 和确认边界。
2. 为 Claude 保留 `disable-model-invocation: true`，为 Codex 增加 `policy.allow_implicit_invocation: false`，其他 Runtime 缺少等价门禁时失败关闭。
3. 删除 `new-worktree-apply` 的 `--authorized-by-issue`、任务平台 envelope、双模式和人工确认实现。
4. 增加 `--dry-run`，并让默认与 dry-run 共用同一只读 preflight。
5. 把 Step 6–7 重构为不可变 preflight baseline 与独立零写 revalidation snapshot，并在创建前增加 source parent 物理包含门禁；通过后默认直接创建。
6. 更新 `verify-impl-consistency` 与 `check-changes-completed` 的显式冻结基线实现和文档。
7. 扫描所有非归档 skill，确认没有固定 `main` 比较或遗留 Issue 授权文本。
8. 运行 worktree lifecycle、target-aware、安装环境、OpenSpec strict validation 和 diff 检查。
9. 回滚时可恢复 `new-worktree-apply` 的人工确认，但不恢复 Issue/Team/task-platform 授权耦合；不涉及数据迁移。

## Open Questions

无。Runtime 原生门禁下的用户显式调用即有限授权、显式 target、dry-run、漂移失败关闭、父目录物理包含、外部副作用边界和验证 skill 的目标基线契约均已确定。
