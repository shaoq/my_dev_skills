# Actionable architecture blocker

## Purpose and compatibility

`architecture_blocker_action_v3` 用于缺少 routing、Owner binding、scope 或 evidence reference 等 `dependency_input`。它固定 `requires_human_review=false`，不得伪装成方案 Review、内容批准或操作授权。v3 在 v2 的 discovery-first 基础上增加普通业务问题、人类声明与后台证据派生。

reader 可读取 `architecture_blocker_action_v1|architecture_blocker_action_v2` 供审计；v1/v2 不得产生新副作用。新 blocker、retry 或 superseding attempt 只写 v3，并以 `supersedes` 指向旧 action。

## Canonical fields

```text
blocker_profile=architecture_blocker_action_v3
blocker_action_id=<single current identity>
work_item_ref=<current work item>
stage=<current canonical stage>
attempt=<current attempt>
blocker_reason=<stable current reason>
blocked_responsibility=<responsibility awaiting input>
resolution_instruction_owner_ref=<unique actor allowed to supply the instruction>
resolution_instruction_owner_authority_ref=<matching authority>
requested_input_kind=owner_binding|routing|scope|evidence_reference
requested_input=<one bounded input object>
discovery_policy=automatic_before_human
discovery_scope=<authorized read-only sources and forbidden scope>
discovery_actor_ref=<existing portable actor>
discovery_actor_authority_ref=<matching authority>
discovery_responsibility=coordination|research
discovery_completion_condition=unique_verified|multiple_verified|unavailable_with_evidence
response_modes=provide_input|request_discovery
provide_input_profiles=verified_binding|human_declaration
business_question=<one plain-language question with scope frozen by this Action>
provide_input_reply_contract=<verified binding or exact human declaration>
human_declaration_reply_contracts=ACTION <ACTION_ID>: I am responsible|ACTION <ACTION_ID>: the responsible party is <identifiable person or group>
request_discovery_reply_contract=ACTION <ACTION_ID>: I am not sure; provide a recommendation
required_reply_fields=<provide_input fields or none>
derive_machine_evidence_from_reply=actor identity|frozen business scope|comment ref/revision/time|reread
formal_source_policy=conditional
context_refs=<current evidence refs>
recommendation_intent=provide_self|provide_candidate|request_discovery
recommendation_reason=<plain-language facts and inference>
recommendation_confidence=high|medium|low|unknown
recommendation_boundary=<what the recommendation does and does not decide>
ordered_alternatives=<remaining intents in evidence order, each with condition and consequence>
closing_condition=<observable condition>
resume_actor_ref=<unique actor that validates a provided binding>
resume_actor_authority_ref=<matching authority>
resume_responsibility=<one responsibility>
resume_completion_condition=<observable bounded condition>
requires_human_review=false
BLOCKER_ACTION_STATE=discovering|awaiting_input|received|discovery_needed|superseded|unavailable
request_evidence_refs=<delivery evidence or none>
response_evidence_refs=<validated response evidence or none>
resume_continuation_ref=<accepted or active execution_continuation_v2 or none>
supersedes=<older blocker action or none>
```

## Discovery-first

在发布 `awaiting_input` 前，当前 actor 必须在 mandate 的 `allowed_operations` 与 `discovery_scope` 内只读查询 current artifacts、已有 evidence、ownership/config、可用 directory 和 work-item history，并记录来源、版本和观察时间：

1. `unique_verified`：authority 与 current evidence 都可回读时，不要求人类填写字段；创建 resume continuation，并在 `accepted|active` 后继续。
2. `multiple_verified`：只展示候选、Architecture recommendation、理由、置信度和各选项后果，请 instruction owner 作一项简单选择。
3. `unavailable_with_evidence`：把缺口改写成一个普通业务问题，给出 Architecture recommendation、理由与置信度，以及“由我负责 / 指定负责人 / 我不确定，请给出建议”三类完整回复。

未验证候选、显示名、Issue creator/assignee、最近评论者或 instruction owner 本身不能自动成为 domain Owner。

## Recommendation projection

只要仍需发布人类 blocker，core 必须从 current discovery evidence 生成一个明确的 portable recommendation，而不是把三种 response intent 作为平级清单：

1. `unique_verified` 不生成 recommendation；直接建立 continuation。
2. 多个 verified candidates 只有在 current evidence 能明确排序时，才可推荐 `provide_candidate`；若证据同时支持当前用户承担该冻结业务范围，才可推荐 `provide_self`。
3. 多候选不可排序、`unavailable_with_evidence`、`recommendation_confidence=low|unknown` 或证据只来自平台角色/最近交互时，必须推荐 `request_discovery`。
4. `recommendation_reason` 必须用普通语言区分已观察事实与推断；`recommendation_boundary` 必须明确这是待验证 dependency input，**not domain acceptance**、Architecture Review、risk acceptance、approval 或 implementation authorization。
5. `ordered_alternatives` 只列剩余允许 intent，并逐项说明它何时适用及回复后的主要行为；不得让用户自行从无差别列表猜测。

core 不生成 Action ID、本地化句子、mention、comment 顺序或任何平台状态。adapter 只可投影这些语义，不得改变推荐意图或权限边界。

## Reply rules

`provide_input` 有两种 profile：`verified_binding` 用于 instruction owner 已掌握完整 binding；`human_declaration` 用于用户只回答 v3 Action 已冻结的业务问题。内部 `owner_identity`、`authority_scope`、`evidence_ref`、`evidence_version`、`evidence_date`、`human_readable_access_evidence` 不得成为默认人类表单。

人类决策面必须采用正向 recipe：为什么暂停；一个 `business_question`；标为推荐的单一回复及理由、置信度和边界；有序备选及适用条件；回复后行为；可选审计入口。问题使用业务动作和结果描述责任范围，不使用治理记录类型代替问题。具体首屏预算和平台布局由 adapter 决定。

`human_declaration` 的 portable intents 为：当前用户声明负责，或指定一个可识别的人/群组负责。它们只形成待验证 dependency input。core 以 `derive_machine_evidence_from_reply` 规定 adapter 必须从准确 actor、Action 已冻结的 business scope、comment ref/revision/time 与 readback 派生机器字段，不要求人类重复输入，也不直接产生 domain acceptance。

用户不确定时，`request_discovery` 是完整有效回复。portable intent 为：

```text
ACTION <ACTION_ID>: I am not sure; provide a recommendation
```

adapter 可提供本地化等价表达，但只能在准确 actor、current Action ID、created-after-request、未编辑、single action、未 superseded 与 task attribution 都通过后消费。有效 `provide_input` 记为 `received` 并映射 resume actor；有效 `request_discovery` 记为 `discovery_needed` 并映射既有 discovery actor。只有 continuation 达到 `accepted|active` 才恢复 actor work；未入队或回读失败时 blocked rollback。

`formal_source_policy=conditional`：只有用户明确表示已有正式记录但未提供入口，或 deployment policy 明确要求外部正式记录，adapter 才追问一个可打开的来源；其他情况下不得把来源链接作为默认解除条件。

空值、示例占位符、多 action、宽松自然语言匹配或越出 discovery scope 的回复均 audit-only/no-op。无法唯一解析 instruction owner 时，在任何外部写入前返回 `needs_new_mandate_v1`，包含 `success=false`、缺失 binding、所需新顶层指令、unchanged state、no downstream task、resume condition 与 evidence refs。
