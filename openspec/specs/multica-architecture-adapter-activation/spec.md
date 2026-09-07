# multica-architecture-adapter-activation Specification

## Purpose
TBD - created by archiving change add-multica-architecture-approval-adapter. Update Purpose after archive.
## Requirements
### Requirement: Adapter remains an independently installable sibling skill
The repository SHALL maintain `multica-architecture-approval-adapter/` as its own valid skill source with independent frontmatter, references, templates and Runtime metadata. `architecture-design-workflow` MUST remain usable without the adapter, while the adapter MUST refuse platform delivery without a compatible core packet.

#### Scenario: Both skills are installed locally
- **WHEN** the repository installer scans the two root skill directories in an isolated HOME
- **THEN** Claude Code and Codex receive separate links for core and adapter, each pointing to its repository source

#### Scenario: Adapter is absent
- **WHEN** only `architecture-design-workflow` is installed
- **THEN** core standalone profiles continue to work and no Multica field becomes a required core dependency

### Requirement: Automated validation never activates real Multica resources
Repository validation and packaging verification MUST use temporary Runtime homes, local archives and static/local contract checks. They MUST NOT import a real workspace Skill, bind a real Agent, create an Issue or mutate Team/Project/configuration as a completion prerequisite. This change does not require a fake `multica` CLI or dual-Runtime behavior suite.

#### Scenario: Apply validates packaging and local installation
- **WHEN** implementation validates the package and repository skill links in isolated temporary directories
- **THEN** it verifies local contents and leaves every real Multica profile and workspace untouched without simulating import or Agent binding

#### Scenario: No authenticated Multica profile exists
- **WHEN** automated validation runs on a machine without Multica credentials
- **THEN** all required local validation still runs deterministically without network access

### Requirement: Workspace activation requires explicit human authorization
Delivery SHALL provide a runbook that packages the adapter, imports it with safe conflict handling, additively binds it to the selected existing Architecture Agent and verifies the final skill list. The runbook MUST NOT use replace-all binding by default or create missing resources.

#### Scenario: Human authorizes activation
- **WHEN** a human names the target workspace and existing Agent and explicitly requests activation
- **THEN** the operator imports the adapter, uses additive `agent skills add`, and confirms both core and adapter IDs through a final read-only list

#### Scenario: Skill import reports a conflict
- **WHEN** workspace import returns a same-name conflict
- **THEN** activation stops and reports existing identity and supported choices without overwriting unless the human separately authorizes an overwrite strategy

#### Scenario: Target Agent does not exist
- **WHEN** activation cannot resolve the selected Architecture Agent
- **THEN** it stops without creating an Agent, Team, Project or fallback binding

### Requirement: Activation verifies a sandbox review flow before production use
After authorized import/binding, the runbook MUST require a dedicated sandbox Issue acceptance that covers comment delivery, attachment opening on mobile, digest re-verification, short-token human reply, supersession and failure closing. Production Architecture Team activation MUST NOT be claimed from static installation alone.

#### Scenario: Sandbox acceptance passes
- **WHEN** desktop and mobile target members can open exact attachments and a valid reply produces current-packet decision evidence while stale replies remain no-op
- **THEN** the adapter may be reported ready for the explicitly selected Architecture Agent

#### Scenario: Mobile material cannot be opened
- **WHEN** attachment cards exist but the target member cannot retrieve the material from the mobile client
- **THEN** acceptance fails, the adapter remains inactive for production use, and a separate platform capability proposal is recommended if configuration cannot close the gap

### Requirement: Adapter version evidence is recorded for operations
Implementation and activation evidence MUST record implementation revision evidence: when a commit is separately authorized, the adapter repository commit; in a no-commit run, `not_committed` plus baseline HEAD and working-tree scope. It MUST also record consumed core contract revision, observed Multica/CLI version or commit, validation matrix, target workspace/Agent only when explicitly activated, and known tool limitations.

#### Scenario: Implementation is ready for review
- **WHEN** repository work is complete but no real activation was authorized
- **THEN** evidence records implementation revision evidence, consumed core and observed platform-contract versions while marking workspace, Agent and sandbox acceptance as `n/a|not_run`

#### Scenario: Platform capability later changes
- **WHEN** a newer Multica version changes a required comment, attachment or metadata contract
- **THEN** the adapter must re-run capability preflight and record the new observed version before claiming compatibility

### Requirement: Activation and conflict choices use operational action requests
Workspace Skill import, additive Agent binding, same-name conflict strategy and sandbox execution SHALL each require a current operational Human Action Request when a new human choice or authorization is needed. The request MUST name exact existing identities, proposed commands/writes, alternatives, overwrite or availability risks, excluded resource creation, verification and rollback/stop behavior, and an exact authorize/deny response.

#### Scenario: Human authorizes initial activation
- **WHEN** a human names an existing workspace and Architecture Agent but has not yet authorized the exact import/binding scope
- **THEN** the runbook presents the operational request and performs no import or binding until its explicit response covers both skill identities and planned additive writes

#### Scenario: Import conflict requires a new choice
- **WHEN** import discovers an existing same-name Skill
- **THEN** the prior activation authority is insufficient, a new conflict-strategy request explains fail/overwrite consequences, and no overwrite occurs without that exact authorization

### Requirement: Sandbox acceptance presents a human checklist
The sandbox run SHALL present the target member with a concise checklist for opening exact Design, Review and Packet materials on desktop and mobile, submitting a separate legal token, observing supersession and confirming failure retention. Each human-observed result MUST be recorded per check; a generic `OK` MUST NOT mark sandbox acceptance passed.

#### Scenario: Human completes only desktop checks
- **WHEN** desktop materials open but mobile or supersession checks are not individually confirmed
- **THEN** sandbox acceptance remains `not_run|failed` and production readiness is not claimed

### Requirement: Multica blocker 必须投影为普通用户可直接回答的业务问题

adapter SHALL 将 portable blocker 的唯一 requested input 渲染为一个简体中文业务问题，并提供至多三个完整、可复制且包含 current Action ID 的回复：当前用户负责、指定其他负责人、不确定并请团队建议。默认评论 MUST NOT 要求用户提供 `RACI`、组织目录、服务目录、策略批准记录或 machine binding 字段。

#### Scenario: 自然语言负责人声明
- **WHEN** current instruction owner 回复 `ACTION <current-id>: 由我负责` 或 `ACTION <current-id>: 负责人是 <可识别的人或团队>`
- **THEN** adapter 从 comment author、current Action scope、comment ref/revision/time 和 readback 派生 evidence，创建验证 handoff；不得把声明直接解释为领域接受、方案批准或实现授权

#### Scenario: 不确定并请求建议
- **WHEN** current instruction owner 回复 `ACTION <current-id>: 我不确定，请团队给出建议`
- **THEN** adapter 规范化为 `request_discovery` 并创建既有 discovery actor task，回读 accepted/active 后才投影 `in_progress`

#### Scenario: 条件性来源追问
- **WHEN** 用户未声称存在正式记录且 deployment policy 未要求外部 authority record
- **THEN** adapter 不显示来源链接必填项；只有上述条件成立时才追加一个普通语言的来源问题

### Requirement: Adapter 必须兼容 portable 历史版本并只投影 current 新操作

adapter SHALL 读取 mandate/continuation v1 与 v2，以及 blocker v1/v2/v3，用于审计和 reconciliation。任何新 mandate/continuation/handoff 或状态副作用 MUST 绑定 v2，任何新 blocker/retry MUST 绑定 v3。v1 actor/role 只有在 identity 与 deployment mapping 唯一时才可确定性迁移；历史 blocker v1/v2 只读，歧义时 fail closed。

#### Scenario: v1 live attempt 需要新写入
- **WHEN** current portable evidence 为 v1，且请求需要 comment、status 或 task 副作用
- **THEN** adapter 保留 v1 audit-only，创建并验证 superseding v2 mandate/continuation；需要 blocker 时生成 superseding v3 action 后才执行

#### Scenario: v1 role mapping 冲突
- **WHEN** legacy role 对应多个 Member/Agent 或 authority identity 不一致
- **THEN** adapter 不选择最近 actor、assignee 或显示名，并返回准确 compatibility failure

### Requirement: Adapter 必须把 Actionable Blocker 投影给唯一 Member

adapter SHALL 从 current `architecture_blocker_action_v3` 与外部 deployment profile 唯一映射既有 Member/Agent，并在发布人类 blocker 前执行 `automatic_before_human` discovery。comment MUST 按 Member mention、为什么暂停、一个普通业务问题、标为推荐的完整 current Action、普通语言理由/置信度/适用边界、有序备选及适用条件、回复后行为、可选依据入口的顺序呈现；machine binding schema 和企业治理记录类型不得成为默认人类表单。推荐 Action MUST 位于 mention 后前 800 个 Unicode code points 内，并早于 evidence link、digest、control 或 machine field。reader 保留 blocker v1/v2 audit-only；新写只使用 v3。

#### Scenario: 唯一 instruction owner 可映射
- **WHEN** action、work item、attempt、owner authority、Member 和 Issue 均 current 且唯一
- **THEN** adapter 先运行 discovery；唯一 verified binding 自动恢复，多个候选按 core recommendation 发布简单选择，零候选才发布一次含单一推荐的 comment 并记录 `BLOCKER_ACTION_STATE=awaiting_input`

#### Scenario: 手机端首屏可复制推荐
- **WHEN** adapter 为 current blocker 生成 Multica comment
- **THEN** 推荐完整 Action、理由和置信度出现在 mention 后 800 个 Unicode code points 内，且所有审计字段后置

#### Scenario: Owner 不能唯一映射
- **WHEN** owner 缺失、冲突或只能从 creator/assignee/recent commenter 猜测
- **THEN** adapter 在首笔写入前返回 `needs_new_mandate_v1` 或 mapping failure，不写 status/comment/task

### Requirement: Adapter 必须消费 Current Blocker 回复并恢复真实任务

adapter SHALL 仅消费准确 instruction owner 在 current request 后提交的 current canonical Action reply，并 SHALL 验证 work item、Action ID、created-after、未编辑 revision、`provide_input|request_discovery` response mode、single action、supersession 和 task attribution；`provide_input` 还验证 required fields。格式无效但意图唯一的回复只能进入 `reply_correction_candidate_v1`，不得被消费。有效 provide-input 记录 received 并映射 resume actor；有效 request-discovery 记录 discovery_needed 并映射既有 coordination/research actor。两者都创建 single-consumption handoff、回读 task accepted/active 后才写 `in_progress --no-start`。

#### Scenario: 最新位置的有效回复
- **WHEN** 唯一 instruction owner 在同一 Issue 最新位置提交 current Action ID 的有效 provide-input 或本地化 request-discovery
- **THEN** adapter 不依赖 direct parent，回读 resume/discovery task accepted/active 后自动投影 in_progress

#### Scenario: 中文 request-discovery
- **WHEN** 用户提交 current Action 定义的准确本地化 request-discovery，且仅存在一个可规范化的边缘 Agent mention、Markdown mention 转义或无语义空白
- **THEN** adapter 规范化并消费 request-discovery；其他附加自然语言不得通过宽松匹配消费

#### Scenario: 无效但意图唯一的回复
- **WHEN** 准确 Owner 的回复唯一表达一个允许意图，但缺少 current Action ID 或不符合 canonical grammar
- **THEN** adapter 不消费回复、不创建 handoff，最多进入一次友好纠错，Issue 继续 blocked

#### Scenario: 无效或过期回复
- **WHEN** actor、Action、时间、revision、字段、single action 或 supersession 任一无法唯一通过
- **THEN** adapter audit-only/no-op；除满足严格 correction candidate 的当前 Owner 单意图回复外，不发布纠错，不创建 task、不改变 Review gate

#### Scenario: Resume task 未入队
- **WHEN** canonical reply 内容有效但 mapped handoff 没有 accepted/active task evidence
- **THEN** adapter 不遗留 orphaned in_progress，保留 response evidence并保持/恢复 blocked

### Requirement: Blocker 回复不得扩大架构或实施权限

adapter MUST 把 blocker reply 仅作为 dependency input；它 MUST NOT 将 instruction owner 视为 domain Owner，也 MUST NOT 据此接受设计、风险、Review、approval、PoC、实现、部署、采购或资源创建。

#### Scenario: 回复包含额外批准措辞
- **WHEN** current blocker 回复除 required fields 外包含设计接受或实施授权文字
- **THEN** adapter 只消费合法 dependency-input fields，额外文字仅作审计且不得改变 gate 或 planned writes

### Requirement: Adapter 必须支持显式 Owner 手动材料检查

adapter SHALL 在 `design_input|architecture_review` 的唯一 Decision Owner 已明确选择自行检查时，把准确 attachment identity/digest、stable same-Issue entry 和 policy evidence 投影为 `access_verification_mode=owner_manual`、`material_access_state=manual_check_required`。这些 postcondition 通过后 SHALL 自动写入 `in_review --no-start`；未经认证的 Agent 浏览器失败不得单独产生 hard blocker。

#### Scenario: Owner-manual Decision Brief 交付
- **WHEN** comment、mention、attachment、digest、稳定入口和 policy evidence 全部回读成功
- **THEN** adapter 发布可执行决策卡和 `ACTION <action-id>: 材料打不开`，并将 Issue 投影为 in_review

#### Scenario: 材料打不开回复
- **WHEN** 准确 Owner 对 current Action 提交“材料打不开”
- **THEN** adapter 不记录候选选择，自动触发 coordination repair task 并在 task accepted/active 后投影 in_progress

### Requirement: Adapter 必须友好纠正单一明确但格式无效的 Blocker 回复

当准确 instruction owner 在同一 Issue、current request 之后提交未编辑且只对应一个 current blocker 的回复，文本能唯一映射到一个允许业务意图但缺少 Action ID、使用非 canonical 措辞或包含额外正文时，adapter SHALL 标记 `reply_correction_candidate_v1`，MUST NOT 消费该回复，并 MAY 为同一 `action_id + request_revision` 自动发布至多一次 `reply_correction_v1`。

纠错 SHALL 说明原回复尚未生效、一个普通语言失败原因、唯一完整 canonical Action 和再次回复后的行为。纠错 MUST 绑定 invalid comment ref、revision、raw digest 与 current Action，MUST 保持 `BLOCKER_ACTION_STATE=awaiting_input` 和 Issue `blocked`，不得 mention Architecture Agent、创建 task、恢复 Issue 或改变任何架构 gate。重复事件 MUST reconciliation no-op；wrong actor、多意图、占位值、旧/superseded Action 或意图不明 MUST 静默 fail closed。

#### Scenario: 明确自荐但缺少 Action ID
- **WHEN** 准确 instruction owner 在 current request 后回复“我负责提供”，且回复未编辑、只表达 `provide_self` 并唯一绑定 current blocker
- **THEN** adapter 不消费回复，最多发布一次说明“缺少当前处理编号”的纠错，并给出完整 `ACTION <current-id>: 由我负责`

#### Scenario: 重复事件不重复纠错
- **WHEN** 同一 invalid comment ref/revision/raw digest 与 `action_id + request_revision` 再次被观察
- **THEN** adapter reconciliation no-op，不重复评论、不创建 task、不改变状态

#### Scenario: 纠错证据无法安全写入
- **WHEN** mandatory correction identity 无法通过容量门禁或写后回读
- **THEN** adapter 保持 blocked 并报告恢复条件，不重试同一纠错、不消费原回复

#### Scenario: 错误 actor 或多个意图
- **WHEN** 回复来自非 instruction owner、对应多个 current action、含占位值或表达多个互斥意图
- **THEN** adapter 不发布纠错、不消费回复、不改变状态或 gate
