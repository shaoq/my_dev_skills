## Context

本仓库的 skill 以 Markdown 指令描述跨 Runtime 的执行协议。R&D Team 的目标流程会把一个 Issue 绑定到一个 OpenSpec change、一个 canonical worktree branch 和一个明确的集成目标分支。Issue 被分配并进入执行状态后，团队已获得在隔离 worktree 内实施的授权；真正改变共享状态的边界仍是后续 merge。

现有实现有两类不一致：

1. `new-worktree-apply` 对所有调用都执行即时人工确认，无法消费上游 Issue 的执行授权。
2. `verify-impl-consistency` 和 `check-changes-completed` 分别在 OpenSpec 增量验证、D3 交付验证和 D5 合规验证中使用 `main..HEAD`，与工作流中显式选择的 `TARGET_BRANCH` 脱节。

对所有非归档 `SKILL.md` 的审计还确认：`new-worktree-apply`、`merge-worktree-return` 和 `parall-new-worktree-apply` 中出现的 `main/master/trunk` 只是没有显式 `--target` 时的候选顺序，实际写入和验证已经绑定冻结的 `TARGET_HEAD`；`openspec-review-change` 不使用分支差异来判定 proposal readiness。它们不属于固定比较基线缺陷。

## Goals / Non-Goals

**Goals:**

- 让已获得明确 Issue 授权的 `new-worktree-apply` 在安全条件满足时无需逐次人工确认。
- 保留交互式模式为默认行为，并保持所有现有 Git/OpenSpec 安全不变量。
- 为 repository verification skills 建立显式、不可变、可报告的目标分支基线。
- 让实现、测试、任务交付和配套合规检查对同一目标 branch/commit 归因。
- 让每次 change-level 验证的 change 选择集、目标基线、当前 commit 与允许写回范围都可确定、可复检。
- 通过回归扫描阻止新的非归档 skill 引入 `main..HEAD`、`refs/heads/main` 等固定比较基线。

**Non-Goals:**

- 不取消 `merge-worktree-return` 或并行集成的人工确认。
- 不让自治模式执行 merge、发布、生产操作、不可逆数据变更或外部副作用。
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

冻结后必须先执行 `git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>`。失败表示调用方选择的目标 tip 不是当前交付历史的祖先；不得改用 merge-base、当前分支、旧 target commit 或其他推断值。`verify-impl-consistency` 可以继续项目级诊断，但把 OpenSpec 增量维度标记为未执行；`check-changes-completed` 输出阻塞结果且不得回填、stage 或 commit 任何 `tasks.md`。

后续 Git 命令全部使用两个冻结 commit hash，不重复解析可移动的 branch name，也不使用字面 `HEAD`。结束时同时复检 `refs/heads/<BASE_BRANCH>` 与当前 `HEAD`：

- `verify-impl-consistency` 若发现任一漂移，保留基于冻结快照得出的诊断，但必须标记为 stale evidence，不能暗示覆盖了新 tip。
- `check-changes-completed` 若发现任一漂移，可以显示冻结快照的诊断结果，但必须把可存档结论置为 unknown/blocked，并保持零回填、零 stage、零 commit。

选择显式本地分支而非任意 rev，是因为 R&D Team 的授权对象就是目标 checkout branch；限制到 `refs/heads/` 还能避免 tag、远程追踪 ref、路径或模糊 revision 被误当作目标。

### 2. 增量验证使用显式 change 选择，不自动绑定多个 active changes

- `verify-impl-consistency <change-name> --base <target-branch>`：提供 change 名称时必须同时提供唯一 `--base`，change 必须精确匹配 active change。省略 change 名称时只执行项目级 D1/D2/D3，不自动发现或循环 active changes，且拒绝孤立的 `--base`。
- `check-changes-completed --target <target-branch> --change <name> [--change <name> ...]`：要求一个目标和一个或多个显式 active change。`--change` 可重复但不得重复同名，所有名字必须精确匹配 active changes。

二者都拒绝重复的单值选项、重复 change、缺值、未知 flag、多余位置参数和不存在的本地分支。不得以 `main`、当前分支、`origin/HEAD`、conventional branch 或 active-change 自动发现替代缺失输入。

选择显式 change 而不是从目录或 `openspec list` 自动绑定，是因为 target 属于调用授权，不是 OpenSpec artifact 的固有字段。自动发现无法证明多个 active changes 面向同一个目标。

### 3. `check-changes-completed` 的选择集、D3、D5 与写回边界共用同一快照

D3 的提交证据改为：

```text
git log --oneline <BASE_HEAD>..<CURRENT_HEAD> -- <expected-file-paths>
```

D5 的配套产出范围改为：

```text
git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only
```

只有显式 `--change` 选择集参与五维扫描、blocking reasons、任务矛盾检测和 Level-1/Level-2 回填。未选择的 active changes 不得读取为本次结论的证据，也不得修改。选择集中的 changes 共用本次调用冻结的目标基线；若它们面向不同目标，调用方必须拆分为多次显式调用。

该设计不在仓库中持久化 change→target 映射，因为目标是每次交付调用的外部上下文。代价是调用方必须显式列出分组，但不会把同一个 `--target` 静默应用到全部 active changes。

### 4. `new-worktree-apply` 只接受 Runtime 控制面的 `issue-authorization/v1`

默认调用保持现状：

```text
/new-worktree-apply <change> --target <branch>
```

自治调用增加：

```text
/new-worktree-apply <change> --target <branch> --authorized-by-issue <issue-id>
```

`--authorized-by-issue` 不是通用 `--yes`，也不携带授权本身。调用 Runtime 必须通过 agent 无法从用户消息、仓库文件、环境变量或模型推断中构造的控制面元数据通道，注入一个 schema 为 `issue-authorization/v1` 的结构化 envelope。该元数据必须具有 system/developer 等价权限与可信 provenance；普通 user content 即使包含相同 JSON 也不构成授权。

envelope 必须包含：

```text
schema=issue-authorization/v1
authorization_id
issuer_id
issued_at
expires_at
issue_id
issue_state=ready|in_progress
assigned_team_id
executing_team_id
execution_scope=isolated-worktree-apply
repository_physical_root
openspec_root_rel
change_name
target_branch
risk_class=standard
external_side_effects=[]
```

Runtime 负责认证并 allowlist `issuer_id`、把外部 tracker 状态归一化为 `ready|in_progress`、提供实际执行 Team identity，并把 `authorization_id` 绑定到当前 invocation，防止被其他 invocation 重放。`issued_at` 与 `expires_at` 使用 RFC3339 UTC，授权窗口必须大于 0 且不超过 30 分钟；Runtime 使用可信时钟保证 Step 7 完成前仍满足 `issued_at <= now < expires_at`。同一 invocation 的 Step 6–7 MUST 复检同一个 authorization id 和 envelope digest，而不是把正常复检误判为重放。skill 仍必须逐字段验证：参数 issue ID 与 `issue_id` 完全一致，`assigned_team_id == executing_team_id`，scope 精确匹配，预检得到的物理仓库/OpenSpec root/change/target 与 envelope 完全一致，风险为 standard 且外部副作用列表为空。

任何缺字段、未知 schema、非可信 provenance、过期、重放、issuer 未认证、状态不允许、Team 不匹配或字段无法比较都在首次写入前 `BLOCKED`。skill 不得从用户文本补字段，不得请求模型判断 envelope 是否“看起来可信”，也不得降级到交互模式继续同一次调用。

选择 Runtime 控制面元数据而不是仓库内授权文件，是为了避免把流程授权写入业务仓库、提交临时控制文件、信任环境变量或引入凭据。没有该可信通道的 Runtime 只能使用默认交互模式，这是有意的能力降级。

### 5. 自治模式记录快照但不自动接受漂移

Step 1–5 保持只读。Step 6 在交互模式展示摘要并请求确认；在自治模式则生成 `AUTONOMOUS_AUTHORIZATION_SNAPSHOT`，包含 schema、authorization/issuer/Issue/Team 标识、签发与过期时间、scope、风险字段、目标 hash、canonical source identity、artifact manifest 和计划写入。该快照只输出审计字段，不输出 connector token、签名材料或其他凭据，并作为结构化 Handoff 交回提供 envelope 的 Runtime。

Step 7 仍完整复检。交互模式发现变化时返回 Step 6 获取新确认；自治模式发现任何变化时直接 `BLOCKED`，必须由上游基于新快照重新发起，禁止自动更新授权、自动转为人工模式或继续使用旧 Issue 标识。

### 6. 高风险行为不由模型自行豁免

自治授权只覆盖本地隔离 worktree 的创建、OpenSpec apply、来源提交和允许的本地验证。proposal/design/tasks 中存在生产发布、外部系统写入、真实凭据使用、不可逆迁移、数据删除、权限提升或其他超出 `isolated-worktree-apply` 的行为时，skill 必须停止并要求独立人工授权。

风险分类来自 Issue envelope 与 OpenSpec artifacts 的共同证据；任一侧缺失、冲突或不确定均按高风险处理。不能因为目标 worktree 不被修改就忽略 apply 可能执行的外部副作用。

### 7. 采用协议测试与固定基线回归扫描

扩展现有 shell safety test，构造临时 Git 仓库和本地 `main/develop` 分支，验证：

- 默认模式仍等待明确确认。
- 可信、未过期且字段一致的 `issue-authorization/v1` 可在显式 target 上自治创建。
- user message 伪造、未知 schema、未认证 issuer、过期/重放、Issue/Team/scope/目标不匹配、风险不明或快照漂移均零写失败。
- 两个验证 skill 的命令和报告使用冻结的非 `main` commit，并在目标不是当前 commit 祖先时失败关闭。
- 两个 active changes 面向不同目标时，`check-changes-completed` 只扫描显式分组，且未选择 change 永不被回填。
- 非归档 source `SKILL.md` 不再包含用于变更归因的固定 `main..HEAD`/`refs/heads/main`，但允许文档中描述已禁止的反例及 conventional fallback 文本。

## Risks / Trade-offs

- [skill 本身不验证 tracker 凭据或密码学签名] → 认证、可信时钟和单次 invocation 防重放由 Runtime 控制面保证；skill 只接受带可信 provenance 的 `issue-authorization/v1`，其他 Runtime 默认交互。
- [模型难以可靠识别所有外部副作用] → 要求 Issue 与 OpenSpec 双重声明；任何缺失或不确定都阻止自治，不允许模型自行接受风险。
- [显式基线参数带来调用迁移成本] → 这是有意的失败关闭行为；更新 Team Prompt 和调用示例，确保同一个 target 从 worktree 创建一路传递到 Review/完成度验证。
- [目标或当前分支在长时间诊断中移动] → 所有 Git 查询使用冻结 commits；结束时复检两侧，完成度检查禁止在漂移后写回。
- [目标 tip 不是当前 commit 的祖先] → 失败关闭，不用 tree-to-tree diff 冒充交付范围，也不静默改用 merge-base。
- [一次 completion 检查包含多个目标不同的 changes] → 要求调用方用重复 `--change` 显式分组；未选择 change 完全排除，不引入猜测性的 per-change target 推断。

## Migration Plan

1. 先更新 delta specs 和协议测试，确认现有默认交互式 worktree 流程仍被覆盖。
2. 更新 `new-worktree-apply` 参数解析、授权 envelope、Step 6–7 和报告。
3. 更新 `verify-impl-consistency` 的显式 change + `--base` 解析、祖先门禁、冻结范围及报告。
4. 更新 `check-changes-completed` 的 `--target` + 重复 `--change` 解析，让选择集、D3/D5 与写回边界共享冻结基线。
5. 扫描所有非归档 skill，验证没有遗漏用于变更归因的固定 `main`。
6. 更新调用示例与 README（若现有文档包含旧命令）。
7. 回滚时恢复三个 skill 的旧参数契约及对应 specs/tests；不涉及数据迁移或外部状态回滚。

## Open Questions

无。Issue envelope 的可信来源和最小字段、自治范围、change 选择、祖先关系、漂移写入门禁、两个验证参数契约及失败关闭行为已在本提案中确定。
