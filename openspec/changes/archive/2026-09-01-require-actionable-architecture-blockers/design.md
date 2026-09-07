## Context

portable actor/continuation v2 已消除固定 Team topology，但 blocker v1 只允许 instruction owner 提交完整 binding。UNIDRAG-12 的真实验收表明，用户通常不知道 `owner_identity`、`authority_scope` 与 evidence 正式值：空值和照抄占位符均被正确 no-op，却让流程永久停在 blocked。contract 必须先安排既有 actor 调查，并让“不知道，请调查并给出建议”成为有效依赖输入。

`require-executable-architecture-continuations` 已实现 task readback，但其 delta 未同步并已用 `--skip-specs` 归档；本 change 以 topology-neutral v2 接续该保证。portable core 和 adapter 仍保持 sibling：core 不导入 Multica 概念，adapter 只消费 portable artifacts 与外部 deployment profile。

## Goals / Non-Goals

**Goals:**

- 精确定义 mandate/continuation v2、actor identity、responsibility、cardinality 与 standalone evidence。
- 保留 v1 live artifacts 的读取和审计，但禁止新写 v1。
- 让每个成功投影的 nonterminal blocker 具名、单项、可回复、可恢复。
- 让 adapter 只在恢复 task accepted/active 后投影 `in_progress`。
- 在询问人类前自动执行授权范围内的只读发现，内部 binding 字段留在 machine evidence。
- 支持 `provide_input|request_discovery`，让不掌握正式值的用户只需请求调查。

**Non-Goals:**

- 不修改 Multica core、平台 schema 或业务仓库。
- 不把 dependency input 变成方案 Review/approval。
- 不创建新 Runtime、Team、Agent、Issue、watchdog 或资源。
- 不要求用户猜测、编造或照抄其并不掌握的 Owner、authority 与 evidence。

## Decisions

### 1. v2 actor contract

`actor_ref` 是 work item 内稳定 opaque identity，不能从显示名猜测；`authority_identity_ref` 用于权限与 author/reviewer separation。responsibility 只允许：

```text
coordination | research | solution_design | independent_review |
dependency_input | human_decision | downstream_delivery
```

每个 current action 恰有一个 current responsibility；每条 responsibility binding 恰有一个 actor 与 authority。一个 actor 可以承担多项 responsibility，但 `independent_review` 的 authority 必须与 current design author 不同。`dependency_input` 仅补充 routing/Owner/scope/evidence，不具有 `human_decision` 权限。

`architecture_workflow_mandate_v2` required fields：

```text
mandate_profile=architecture_workflow_mandate_v2
mandate_ref
work_item_ref
stage
attempt
workflow_actor_ref
workflow_actor_authority_ref
current_responsibility
responsibility_bindings
trigger_actor_ref
trigger_actor_authority_ref
trigger_evidence_ref
allowed_operations
forbidden_scope
retry_limit
preconditions
completion_condition
input_digest
state=active|completed|superseded|invalid
evidence_refs
supersedes=none|<refs>
```

除 `supersedes` 为 0..n 外，单值字段恰有一个值，列表字段至少一个去重值。`work_item_ref` 可以是 local/shared artifact；core 不要求 workspace、Issue、Team、Member、Agent、comment、URL、CLI 或 task。

`execution_continuation_v2` required fields：

```text
continuation_profile=execution_continuation_v2
continuation_id
work_item_ref
stage
attempt
next_actor_ref
next_actor_authority_ref
next_responsibility
action
input_artifact_refs
completion_condition
state=planned|accepted|active|waiting_human|blocked|terminal
blocker_action_id=none|<current-id>
execution_evidence_mode=local_session|shared_artifact|runtime_task|human_response
evidence_refs
supersedes=none|<refs>
```

除 terminal 外 next actor/authority/responsibility/action/completion/evidence 均为必需；blocked 额外要求 current blocker ID，next actor 必须等于 instruction owner，responsibility 固定 `dependency_input`。waiting_human 绑定唯一 Decision Owner 与 `human_decision`。

### 2. Standalone evidence

同一 invocation 继续工作时使用 `local_session`，记录 session actor、attempt、input digest、output artifact ref/revision 和观察时间后才可为 active。共享 artifact 被另一 actor 显式 claim 时使用 `shared_artifact`，只有 actor/authority、revision、created-after-continuation 和 current/supersession evidence 全部存在才可为 accepted。跨会话只有计划文字而没有 claim 时保持 planned，不声称仍在执行。

### 3. v1 compatibility

reader/core adapter 双读 v1/v2，writer 只写 v2。历史 v1 不编辑；需要新副作用时创建 v2 superseding attempt。

确定性映射：

| v1 | v2 |
|---|---|
| `architecture_agent` | `workflow_actor_ref` |
| `next_executor_ref` | `next_actor_ref` |
| Architecture Lead | `coordination` |
| Architecture Analyst | `research` |
| Solution Architect | `solution_design` |
| Architecture Reviewer | `independent_review` |

identity、role 或 deployment mapping 不唯一时 fail closed；不得用字符串 alias 静默选择。fixtures 覆盖 exact mapping、unknown role、identity conflict、v1 replay、v2 standalone、v2 Runtime 和 supersession。

### 4. Discovery-first actionable blocker v2 与人类友好 v3

v1/v2 保留读取与审计；任何新 blocker/retry/superseding attempt 只写 `architecture_blocker_action_v3`。v3 继承 v2 的 discovery-first 语义，并增加第 7 节的人类友好字段。它与 Human Action Request 正交，required fields：

```text
blocker_action_profile=architecture_blocker_action_v3
action_id
work_item_ref
stage
attempt
blocker_reason
resolution_instruction_owner_ref
resolution_instruction_owner_authority_ref
requested_input_kind=owner_binding|routing|scope|evidence_reference
requested_input
discovery_policy=automatic_before_human
discovery_scope
discovery_actor_ref
discovery_actor_authority_ref
discovery_responsibility=coordination|research
discovery_completion_condition
response_modes=provide_input|request_discovery
provide_input_profiles=verified_binding|human_declaration
business_question
provide_input_reply_contract
human_declaration_reply_contracts
request_discovery_reply_contract
required_reply_fields=none|<fields used only by provide_input>
derive_machine_evidence_from_reply
formal_source_policy=conditional
context_refs
recommendation_state=recommendation|no_recommendation
recommendation
recommendation_reasons
completion_condition
resume_actor_ref
resume_actor_authority_ref
resume_responsibility
requires_human_review=false
state=discovering|awaiting_input|received|discovery_needed|superseded|unavailable
evidence_refs
supersedes_action_id=none|<id>
```

每个 action 只有一个 requested input object。人类输入前先读取 mandate 授权的 current artifacts、evidence、ownership/config、directory 与 Issue history，并返回三类结果：唯一 verified binding 自动继续；多个 verified candidates 展示建议、理由、置信度和后果供简单选择；零候选发布有证据的组织 blocker。未验证候选不能自动绑定。

`provide_input` 保留完整机器可验证 grammar：

```text
ACTION CURRENT-ACTION-ID: provide field=value; another_field=value
```

`request_discovery` portable intent 为：

```text
ACTION CURRENT-ACTION-ID: request discovery and recommendation
```

adapter 可本地化为 `ACTION CURRENT-ACTION-ID: 我不知道，请团队调查并给出建议`，并只规范化单个边缘 Agent mention、Markdown 转义和无语义空白。内部 fields 不得成为默认人类表单。instruction owner 不等于缺失的 domain Owner；两种回复都只是 dependency input。

### 5. Owner precondition 与非成功结果

adapter 在任何 status/comment/handoff 写入前唯一解析 instruction owner。无法解析时 core 返回：

```text
outcome_profile=needs_new_mandate_v1
work_item_ref
stage
attempt
outcome=needs_new_mandate
success=false
missing_binding=resolution_instruction_owner_ref
required_instruction
issue_state_effect=unchanged
current_task_effect=completed_with_non_success_result
downstream_task_effect=none
resume_condition
evidence_refs
```

adapter 不写 Issue、不发布 blocker、不创建 task；Runtime task 可结束为 platform completed，但 result 必须保留 success=false。新顶层指令必须具名 trigger actor、authority、work item 与单项任务，并创建新 v2 attempt。

### 6. Adapter projection 与回复消费

adapter 从 portable action 与 deployment profile 唯一映射既有 Member/Agent。写 blocker 前执行 discovery-first。blocker comment 固定顺序：准确 Member mention、停止原因、已确认事实、已调查内容、当前人真正能完成的唯一任务、Architecture recommendation/理由/置信边界或 no recommendation、简明回复、回复后行为、evidence links。成功写入并回读后 Issue 为 blocked，`BLOCKER_ACTION_STATE=awaiting_input`。

回复验证 actor、work item、current Action ID、created-after、未编辑 revision、response mode、single action、supersession 和 task attribution；`provide_input` 额外验证 required fields。有效 `provide_input` 先记 received 并映射 resume actor；有效 `request_discovery` 记 discovery_needed 并映射既有 coordination/research actor。两者都创建 single-consumption handoff、回读 accepted/active task 后才投影 `in_progress --no-start`。task 未入队或回读失败时不遗留 in_progress。无效回复 audit-only/no-op，不产生 operational authorization。

### 7. 人类首屏使用业务问题，机器证据从回复上下文派生

零候选或 `unique_unverified` 之后，默认评论不得继续要求用户“提供权威来源”、理解 `RACI`、组织目录、服务目录、策略批准记录或填写 binding schema。blocker action 必须先把待补充范围冻结为一个普通业务问题，例如：“谁负责决定 Chat 数据可以采集什么、保存多久、谁能查看，以及如何删除？”

首屏固定为六段：为什么暂停、团队建议及理由/置信度、你只需要回答的一个问题、最多三个可直接复制的回复、回复后会发生什么、可选审计入口。默认回复意图为：

```text
ACTION <ACTION_ID>: 由我负责
ACTION <ACTION_ID>: 负责人是 <可识别的人或团队>
ACTION <ACTION_ID>: 我不确定，请团队给出建议
```

前两种都规范化为 `provide_input` 的人类声明 profile，只提供“谁负责”这个业务输入，并进入现有 resume actor 的验证路径；它们不直接构成领域接受、架构批准或事实验证。系统从准确评论作者、current Action 中冻结的业务范围、comment ref/revision、created/updated time 和 readback 自动派生 actor、scope 与 evidence 字段，不要求用户重复填写。第三种规范化为 `request_discovery`。

若用户主动附上正式来源，adapter 可把它作为候选 evidence 验证；只有用户明确说明“已有正式记录但未提供入口”，或部署 policy 明确要求外部权威记录，系统才追加一个来源链接问题。不得把该条件性问题作为所有用户的默认前置条件。

### 8. Decision Owner 可显式选择自行检查完整材料

默认 `access_verification_mode=automatic` 继续要求 Agent 在 requested client scopes 完成 actual rendering。对于 `design_input|architecture_review`，若唯一 Decision Owner 已在 current mandate 或 deployment policy 中明确表示由自己在网页/手机端检查，使用 `access_verification_mode=owner_manual`：系统仍自动回读 attachment identity、media type、size、raw-byte digest、Decision Brief 和 stable same-Issue entry；逐 scope 只记录 `manual_check_required`，不得伪造 `opened`。

这些机器 postcondition 通过后，评论可展示唯一内容决定并投影 `in_review`。评论必须同时提供 `ACTION <action-id>: 材料打不开`；该回复固定不产生内容决定，而是自动恢复 coordination actor，修复或重新发布材料入口。identity/digest/入口/Owner/policy 任一失败仍为 unavailable。正式 `architecture_approval` 不使用 owner-manual 快捷路径，继续服从 packet readiness。

## Risks / Trade-offs

- v3 blocker upgrade → v1/v2 dual-read/audit-only、v3-only-write、superseding attempt 和 compatibility fixtures；不原地改变已交付的 v2 evidence。
- responsibility abstraction 可能弱化职责分离 → 使用 authority identity 强制 review separation。
- instruction owner 可能被误认作 domain Owner → contract/template 同时展示两者且限制回复权限。
- comment/task 不是事务 → single-consumption ID、写后回读、失败回滚 blocked。
- discovery 循环或误绑定 → 有界 scope/attempt/三类完成结果；只有唯一且 verified 的 binding 可自动继续。
- 自然语言声明可能被误当作正式授权 → Action 冻结问题范围，声明只生成待验证 dependency input；actor/ref/revision/time 由系统回读派生，正式来源仅在明确存在或 policy 要求时追问。

## Migration Plan

1. 新增 blocker v3、普通业务问题、人类声明、后台证据派生 fixtures 并看到 RED。
2. 更新 core SKILL/references/templates，保留 v1/v2 audit-only，以 v3-only-write 实施普通业务问题和条件性来源追问。
3. 更新 adapter SKILL/references/templates，实施中文 request-discovery、handoff/readback 与 rollback。
4. strict validate、quick validate、full tests、GitNexus detect-changes。
5. 输出可覆盖同步的两个既有 Skill package；live 资源更新由调用方 change 执行。

## Open Questions

无。具体 Architecture Team role mapping 只属于 deployment profile，不属于 portable core。
