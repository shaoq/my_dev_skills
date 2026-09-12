# Human Action Request

Current requests render `human_review_surface_v1`: one canonical `ARCH-DESIGN-vN.md`, Design maturity, concise Reviewer findings/conclusion, critical risks, recommendation/consequences and one atomic current Action. Research、Control、complete Review and machine-only Packet remain `architecture_internal_evidence_v1`; they are not mandatory human entries. The Owner never copies packet digest because the current Action inherits the verified manifest snapshot.

## Purpose

只有需要人类改变方案内容、作出架构 Review/风险判断或批准 current packet 的下一动作，才用这份平台无关请求表达。请求必须让 Decision Owner 在不先阅读完整审计记录的情况下，快速理解“为什么现在需要我、我能决定什么、有哪些真实选项、每个选项会发生什么、如何准确回复”。详细证据仍保留并通过稳定引用打开。

该请求是决策界面，不是新的 stage、Review conclusion 或批准协议。它不得把 recommendation、风险接受、路由确认、访问确认或修订说明提升为正式架构批准。

## Orthogonal action state and platform intent

每个 current action 必须记录：

```text
HUMAN_ACTION_STATE=none|preparing|awaiting_response|received|unavailable|superseded
HUMAN_ACTION_TYPE=<action_type|none>
HUMAN_ACTION_OWNER=<unique human or role|none>
HUMAN_ACTION_REF=<stable current request ref|none>
WAIT_REASON=none|target_project|design_approval|awaiting_human_confirmation
platform_status_intent=agent_working|human_review|hard_blocked|terminal
access_verification_mode=automatic|owner_manual
material_access_state=opened|manual_check_required|unavailable|not_run
```

这些字段与 architecture stage、Review conclusion、gate 和 `BLOCKED_REASON` 分开计算。`preparing` 表示 Agent 仍在准备材料；准确请求已经交付给唯一 Owner 后使用 `awaiting_response` 与 `WAIT_REASON=awaiting_human_confirmation`，即使 stage 仍是 `designing|reviewing`。正式 packet 批准仍使用 `stage=waiting_human`、`WAIT_REASON=design_approval`，同时 action state 为 `awaiting_response`。

`platform_status_intent=human_review` 只表示平台应让人看见当前请求处于待其处理的审核态；平台 adapter 决定具体状态名与写入方式。`critical_evidence_gaps` 本身不是 hard blocker：只要存在已交付、Owner 唯一、回复可执行的 current Human Action Request，就仍有明确推进路径。只有 Owner 无法绑定、请求无法交付或依赖确实不存在且没有任何可执行关闭动作时，才使用 `HUMAN_ACTION_STATE=unavailable` 与 `platform_status_intent=hard_blocked`。

routing、Owner binding、scope 或 evidence reference 属于 `dependency_input`，使用独立 actionable blocker，固定 `requires_human_review=false`。提供这些字段的 actor 不因此获得 `human_decision`、设计接受、风险接受或批准权限，也不创建 Decision Brief。

## Action types

新生成的 `action_type` 只能是：

- `design_input`：确认或修改会影响方案的设计输入，也用于补齐缺失的 revision brief；
- `architecture_review`：由准确 Review/Risk Owner 对方案 finding 或非阻断风险作内容判断；
- `architecture_approval`：针对 current ready packet 作正式决定。

`risk_acceptance|design_approval|routing|access_confirmation` 只作为历史记录兼容读取；前两者分别映射为 `architecture_review|architecture_approval` legacy subtype，后两者不得生成新的 Review 请求。项目/Owner 范围不唯一时报告需要新的任务指令；材料访问由 Runtime 或 adapter 自动验证并记录 evidence gap。

## Atomicity and authority

- 每个 action item 只绑定一个原子决定和一个 authority scope。
- 两个 Owner、两个权限域或可以独立选择的两项风险，必须拆成两个 action item；不得提供“接受全部”来跨 Owner 决策。
- 同一时刻可以存在多个 current action items；`ARCH-CONTROL` 以可重复条目列出每个 action ref、Owner 和状态，不用单数摘要覆盖其他动作。
- `Decision Owner` 必须是可识别的人类或明确角色；未知时写明 Owner 缺口和关闭条件，不得让任意回复者代替。
- 请求必须写明该 Owner 有权决定什么，以及明确无权授权什么。

## Architecture Decision Brief

面向一个当前读者的请求按以下固定顺序呈现：

1. 当前方案的一段式摘要；
2. 简化架构图；
3. Architecture recommendation、理由和置信度；
4. 已确定与尚未确定的内容；
5. 最重要的备选及后果；
6. 当前读者真正有权决定的一项内容；
7. 回复后会发生什么；
8. 可点击的完整 Design、Research、Control（以及当前 gate 必需的 Review/Packet）入口；
9. Exact response、authority boundary 与最小 current/superseded audit binding。

不要用“请确认”“等待审核”、只列 token、多 Owner 问卷或完整设计正文代替上述 brief。完整方案必须是独立版本化 artifact，通过目标人类可重读的稳定入口打开；仅 Agent 可读的路径不算 human-accessible evidence。

## Current reader and authority

- 一个 brief 只绑定一个 current action、一个 Decision Owner 和一个 authority scope。
- renderer 必须记录 Current reader / authority binding、`requires_human_review`、`access_verification_mode` 和 `Content-decision activation gate`。`automatic` 只有全部 requested client scopes 为 `opened` 时展示内容回复；`owner_manual` 只有显式 policy evidence、唯一 Owner、准确材料 identity/digest 和稳定入口均通过时展示内容回复，并把逐 scope 状态保留为 `manual_check_required`。
- 其他 Owner 的未决 action 只能列在 `Other-owner dependencies (non-actionable)`，包含 action ID、Owner、依赖影响和关闭条件，不得显示可执行回复表单。
- Decision Owner 为未知角色、零匹配或多匹配时，当前 action 只能是 routing/owner-binding；不能要求当前读者代替该角色决定内容。

## Human-accessible evidence contract

每个完整材料入口分别记录 exact artifact identity/type/version/digest、可导航 ref、Requested client scopes、Access status by scope（`opened|unavailable|not_run`）、Verifier / verification time，以及失败时的 Owner/closure condition。

某个 scope 只有在具名 verifier 执行 actual reader activation，并在目标人类界面内看到准确、完整、可阅读的 artifact rendering、核对 identity 后才能记录 `opened`。一个 scope 的成功不能推出另一个 scope；Agent 进程、CLI、raw-byte fetch、HTTP 200、digest 一致、`download-only` 入口或“文件已经保存”不能替代人的客户端证据。下载后的本地文件还可能受宿主系统来源标记、隔离策略、应用关联或设备不可达影响，除非目标 reader 实际打开并呈现正文，否则仍为 `unavailable|not_run`。若新发布入口必须在发布后才能验证，先在同一 mandate 内自动交付并执行客户端验证；验证完成后才可生成 current Human Action Request 请求内容决定。无法自动证明时记录 evidence gap 和可观察恢复路径，不把访问确认当成人工授权或内容批准。

core 不规定平台 URL、附件或预览语法。没有经验证入口时，brief 保留建议和 unavailable 报告，但不得请求正式内容决定；需要正式批准且 packet 不可访问时继续适用既有 `review_packet_unavailable`。

### Owner 手动检查模式

`access_verification_mode=owner_manual` 只在唯一 Decision Owner 已通过 current mandate 或部署 policy 明确表示“由我在网页/手机端手动检查材料”时使用。Runtime 仍须自动完成 artifact type/version/digest、完整 raw bytes、current/superseded identity、同一 work item 稳定导航入口和 Decision Brief 的回读。未完成这些机器检查时仍为 `unavailable`；不得用 owner-manual policy 绕过 identity 或 digest 失败。

通过后，各 requested scope 记录 `manual_check_required`、Owner 和 policy evidence ref，不得声称 `opened`，但 content-decision activation gate 可为 `ready`，`HUMAN_ACTION_STATE=awaiting_response`。决策卡必须明确提示“请先打开完整材料；若打不开，不要选择方案”，并提供：

```text
ACTION <action_id>: 材料打不开
```

该回复只报告 delivery/access failure，`content_decision=none`；系统把 action 置回 `preparing`，由 `coordination` responsibility 自动执行 `repair_or_republish_material_entry`，投影为 actor working，不要求 operational authorization。修复并重新交付后生成新 attempt；不得把“材料打不开”解释为拒绝、修订、批准或风险接受。

## Recommendation and alternatives

- 有足够依据时给出一个具体 `Candidate recommendation`，并明确它是建议而非决定。
- 没有可靠建议时写 `no_recommendation`，仍需提供有限备选或确定的补证路径。
- 每个备选分别写明即时状态变化、后续写入、主要收益、代价、风险和不可逆影响；没有不可逆影响也明确写 `none known`。
- Basis 必须分为 facts、inferences、principles；不得把推断写成事实。

## Exact responses by type

携带具名 Action ID 的 `design_input|architecture_review` 回复使用 `current_action_reference_v1`：同一 work item 中准确 Owner 可以在当前最新交互位置提交，平台评论 parent/thread 不是 authority。Action ID 必须唯一 current；Action version/digest 从 current Human Action Request 继承并在消费前重读。普通 `OK|确认|继续`、多个 Action/决定、编辑或 superseded 回复仍无效。

### Design input

提供可复制格式：

```text
ACTION <action_id>: accept <candidate_id>
ACTION <action_id>: modify <field>=<value>; reason=<reason>
ACTION <action_id>: reject; reason=<reason>
```

有效 `revision_requested` 即使缺少 revision brief，仍按其 packet-bound 决定进入新版本 `designing`。同时生成新的 `design_input` 请求，标记 `revision_scope=missing`，要求人类补充可执行范围；revision brief ref 独立记录且属于非授权上下文。旧 packet 保持不变。

### Architecture review / risk acceptance subtype

每个 Risk ID 单独提供：

```text
ACTION <action_id>: accept risk=<risk_id>; conditions=<conditions>
ACTION <action_id>: modify risk=<risk_id>; conditions=<conditions>
ACTION <action_id>: reject risk=<risk_id>; reason=<reason>
```

接受只绑定该 Risk ID、Owner、条件和 evidence ref。所有要求的风险接受齐备前，不得形成依赖这些接受的 approvable conclusion 或创建 packet。

### Architecture approval

决定值保持为：`approved_design_only|approved_for_spec|revision_requested|rejected`。准确回复必须同时绑定 current packet ref/version/digest；不得修改 token 语法，也不得让解释文字替代 token。

对四种选项分别说明：

- `approved_design_only`：只发布批准的 ADR/详细设计，完成 design-only 流程，不产生研发授权；
- `approved_for_spec`：发布批准文档，并在目标项目存在时形成 R&D handoff；目标 Team 之后独立分析，不自动创建 OpenSpec 或实现；
- `revision_requested`：进入新设计迭代；附带的 revision brief 是非授权上下文，缺失时另行请求；
- `rejected`：current work item 进入 `rejected` 终态，后续如需继续必须由明确的新工作重新进入流程。

## After-response projection

每个选项必须在回复前就说明：

- Next stage；
- remaining blockers；
- Next Owner；
- 当前动作直接产生的 planned writes；
- 是否会生成新 artifact/version；
- 不会被该回复授权的动作。

只投影当前合法转换的直接结果，不提前声称未来 Review、packet、发布、OpenSpec 或实现已经发生。

收到回复后先验证 actor、同一 work item、current Action ID、继承的 version/digest、准确回复格式、created-after-request、未编辑和 supersession。对 `current_action_reference_v1`，平台评论位置不是必填身份。有效回复将 `HUMAN_ACTION_STATE` 记为 `received`、清除 `WAIT_REASON=awaiting_human_confirmation`，并把 `platform_status_intent` 恢复为 `agent_working`，然后才开始该回复授权范围内的 Agent 工作；无效或过期回复保持 current request，不得假装已恢复执行。

Human Action Request 是现有控制或 artifact 的人类决策入口，不新增 canonical artifact type。core normalized `planned_writes` 只使用既有目标；请求随 `ARCH-CONTROL` 评论呈现时写 `issue:ARCH-CONTROL`，不得临时创造 `issue:HUMAN-ACTION-REQUEST/...` 等目标。平台 renderer 可以记录自己的 delivery evidence，但不能改写 core normalized 字段。

## Stable evidence and audit binding

- 每个关键材料使用稳定、经对应 client scope 验证的可导航 ref；记录 artifact type、version/digest、requested scopes、逐 scope status、access evidence、verifier 和 verification time。
- 内部对象 identity、可导航入口和 target-human access confirmation 分开记录；任一项不能替代另一项。
- 审计区绑定当前 routing version、design/review/packet version 或 Risk ID；明确 `current|superseded`。
- superseded 请求与回复保留审计，但不得驱动 current action。
- 请求本身的 context ref 可以补充决策说明，但只有各自 canonical evidence 或正式批准 token 能改变对应 gate。

## Compatibility

历史有效决定继续按原规则生效。`current_action_reference_v1` 可在明确的新 continue/retry mandate 中重读此前因平台位置/envelope 被判 no-op 的独立评论，但只能在 Action 仍唯一 current、全部 identity 未漂移时生效；不得自动扫描或重放任意历史评论。新契约不创造 canonical stage、Review conclusion、blocker、recommendation 或 human decision 值。
