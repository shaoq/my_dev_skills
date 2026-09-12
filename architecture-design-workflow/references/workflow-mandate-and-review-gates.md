# Workflow mandate and architecture review gates

Current writer freezes `human_surface_contract=human_review_surface_v1` and `internal_evidence_contract=architecture_internal_evidence_v1` in every mandate. Only the canonical Design, concise Review/risk/recommendation and one current Action enter the human surface. Research、Control、complete Review、machine-only Packet、continuation/handoff/readback、retry and reconciliation remain internal and do not create ordinary human comments.

## Purpose

`architecture_workflow_mandate_v2` 表示可识别的 trigger actor 已明确要求开始、继续或重试一个有界架构阶段。它不是内容批准或永久权限；它只允许 current work item/stage/attempt 在冻结 actor、responsibility、输入和 scope 内自动完成非 Review 操作。

portable core 只定义语义，不规定 workspace、Issue、comment、attachment、member、Agent、URL、CLI 或 task。standalone Runtime 使用 local/shared artifact ref、当前会话 actor 与 portable evidence；optional adapter 才负责平台投影。默认 `access_verification_mode=automatic` 时，`download-only`、raw-byte fetch 或传输成功不能替代 actual human-readable rendering。唯一 Decision Owner 已明确选择自行检查材料时可使用 `access_verification_mode=owner_manual`；它不把机器证据伪装为 actual rendering。

## Actor identity and responsibility

`actor_ref` 是 work item 内稳定、不可由显示名猜测的 opaque identity；`authority_identity_ref` 用于权限与职责分离。current responsibility 只允许：

```text
coordination|research|solution_design|independent_review|dependency_input|human_decision|downstream_delivery
```

每个 current action 恰有一个 responsibility；每条 binding 恰有一个 actor 与 authority。一个 actor 可以承担多项 responsibility。`independent_review` actor 的 authority 必须与 current design author 不同；无法证明时 fail closed。`dependency_input` 只补充 routing、Owner、scope 或 evidence，不具有 `human_decision` 权限。

### v2 canonical fields

```text
mandate_profile=architecture_workflow_mandate_v2
mandate_ref=<stable portable evidence ref>
work_item_ref=<single local, shared or runtime work item>
stage=<current canonical stage>
attempt=<opaque single-attempt identity>
workflow_actor_ref=<current actor ref>
workflow_actor_authority_ref=<current authority identity>
current_responsibility=<one responsibility value>
responsibility_bindings=<one or more responsibility@actor@authority bindings>
trigger_actor_ref=<unique human or upstream authority ref>
trigger_actor_authority_ref=<trigger authority identity>
trigger_evidence_ref=<explicit start|continue|retry evidence>
allowed_operations=<one or more portable operation categories>
forbidden_scope=<one or more explicit exclusions>
retry_limit=<bounded non-negative integer>
preconditions=<one or more frozen checks>
completion_condition=<one observable condition>
input_digest=<canonical input digest>
state=active|completed|superseded|invalid
evidence_refs=<one or more portable refs>
supersedes=<older mandate refs or none>
```

单值字段恰有一个值；列表字段至少一个去重值，`supersedes` 为 0..n。允许操作只能来自：`read`、`prepare_materials`、`validate_materials`、`deliver_review_materials`、`verify_access`、`project_status`、`record_task_evidence`、`consume_valid_review_response`、`consume_valid_blocker_response`、`continue_actor_work`、`bounded_retry`。

work item/stage/attempt/actor/authority 改变、输入或 digest 漂移、target 不唯一、重试耗尽、scope 越界或替代/取消指令都会使 mandate 失效。失效后返回准确结果，不生成 operational authorization token。

### v1 compatibility

reader 与 optional adapter 执行 v1 dual-read；writer 执行 v2-only write。历史 `architecture_workflow_mandate_v1` 不编辑，只作 audit/reconciliation。任何需要新副作用的 v1 attempt 都先创建 v2 superseding attempt。

v1 `architecture_agent` 仅在 identity 可精确回读时映射为 `workflow_actor_ref`；legacy deployment role 只通过外部 profile 映射为 responsibility。映射未知、冲突或多值时 fail closed，不用 assignee、最近 actor 或显示名猜测。

## `requires_human_review` derivation

只有 `design_input|architecture_review|architecture_approval` 可以派生 `requires_human_review=true`，且必须同时满足：

1. action、Decision Owner 与 authority scope 唯一且 current；
2. 所需完整材料满足当前 access verification mode：`automatic` 已通过 actual reader activation 验证 human-readable rendering；或 `owner_manual` 已有 Owner 的显式 policy evidence、准确 identity/digest 回读、稳定的同一 work item 导航入口，并将逐 scope 状态标记为 `manual_check_required`；
3. brief 给出摘要、简图、Architecture recommendation/理由/置信度、已确定/未确定和备选后果；
4. 只请求一个原子内容决定，并给出准确回复和 After-response；
5. 回复会改变方案内容、Review/风险状态或正式批准状态。

准备、交付、附件、访问检查、status、task-result、relay、retry、verification、sidecar、supersession 和 continuation 都是自动操作。routing、Owner binding、scope 或 evidence reference 使用 `dependency_input` blocker，固定 `requires_human_review=false`，不得伪装成方案 Review。

## Portable action and status semantics

```text
HUMAN_ACTION_STATE=none|preparing|awaiting_response|received|unavailable|superseded
BLOCKER_ACTION_STATE=none|discovering|awaiting_input|received|discovery_needed|unavailable|superseded
requires_human_review=true|false
platform_status_intent=actor_working|human_review|hard_blocked|terminal
```

- actor 正在执行或处理有效回复：`actor_working`，但只有 execution evidence 才能证明真实连续性。
- current 内容请求已交付给唯一 Owner：`awaiting_response + human_review`。
- current dependency input 已交付给唯一 instruction owner：`awaiting_input + hard_blocked`，但该 blocker 是可行动的。
- 有效 blocker 回复必须先产生 accepted/active resume continuation，才恢复 actor working。

### `execution_continuation_v2`

任何非终结 current action 结束前都按 [portable execution continuation](execution-continuation.md)生成 v2 continuation。`accepted|active` 必须有准确 evidence；planned、Next Owner 或普通消息不够。blocked continuation 必须绑定 current actionable blocker，terminal 之外禁止空 actor。

### `architecture_blocker_action_v3`

依赖输入阻塞读取 [actionable architecture blocker](architecture-blocker-action.md)。`architecture_blocker_action_v1|architecture_blocker_action_v2` 仅双读审计，新写只使用 v3。只有 discovery-first 已执行，instruction owner、一个普通业务问题、基于 current evidence 的单一 `recommendation_intent` 及理由/置信度/边界/有序备选、`provide_input|request_discovery`、closing condition、resume/discovery actor 和 evidence 都 current 时，才可报告 blocker delivery 成功。唯一 verified binding 自动继续；证据无法排序、low/unknown 或 unavailable 时推荐 `request_discovery`，不得从平台角色推断领域责任。人类声明的机器字段必须从准确回复上下文派生，正式来源只按明确条件追问。

instruction owner 是有权提供下一任务绑定的人，不等于缺失的 domain Owner。若无法从 mandate trigger 或既有显式 binding 唯一解析，必须在任何外部写入前返回 `needs_new_mandate_v1`；Issue effect 为 unchanged、current Runtime task 结果为 completed-with-non-success、downstream task 为 none。

### `current_action_reference_v1`

`design_input|architecture_review` 的具名内容回复继续使用 `current_action_reference_v1`。authority 由同一 work item、准确 Owner、request 后未编辑回复、唯一 current Action ID、继承的 version/digest、合法决定与 supersession 共同构成，不来自平台评论位置。

Action 缺失、错误、重复、superseded，Owner 不匹配，回复早于 request、被编辑、含多个 Action/决定或无法继承 version/digest 时保持 awaiting_response。`architecture_approval` 的 packet-bound 规则不变。

## Audit and compatibility

自动操作形成 immutable derived evidence，绑定 mandate、输入/输出 digest、ordered operations、postconditions、retained objects 和 supersession，不向人请求签署。历史 `routing|risk_acceptance|design_approval|access_confirmation` 继续可读；routing/access confirmation 只作审计，不得作为新内容 Review action。
