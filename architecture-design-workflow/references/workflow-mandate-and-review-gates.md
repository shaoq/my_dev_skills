# Workflow mandate and architecture review gates

## Purpose

`architecture_workflow_mandate_v1` 表示人类已经明确要求开始、继续或重试一个有界的架构工作阶段。它不是架构内容批准，也不是永久权限；它只允许当前工作项在同一 stage/attempt 内自动完成确定性的准备、校验、材料发布、可访问性验证、状态投影、结果记录和有界重试。

portable core 只定义语义，不规定 Issue、comment、attachment、member、URL、CLI 或任何平台字段。standalone Runtime 可以用 local/shared artifact ref 和当前会话触发证据实现相同契约；optional adapter 负责把它投影到平台。

## Portable mandate envelope

每个 current mandate 至少冻结：

```text
mandate_profile=architecture_workflow_mandate_v1
mandate_ref=<stable portable evidence ref>
work_item_ref=<single current architecture work item>
subject_project_ref=<existing project or none>
stage=<current canonical stage>
attempt=<opaque single-attempt identity>
architecture_agent=<current responsible role/identity>
trigger_evidence_ref=<explicit start|continue|retry instruction>
allowed_operations=<ordered portable operation categories>
forbidden_scope=<resource creation, cross-work-item writes, implementation, deployment, procurement>
retry_limit=<bounded non-negative integer>
preconditions=<frozen checks>
postconditions=<frozen checks>
invalidates_on=<identity, stage, version, digest, owner, target or scope drift>
```

允许操作只能来自：`read`、`prepare_materials`、`validate_materials`、`deliver_review_materials`、`verify_access`、`project_status`、`record_task_evidence`、`consume_valid_review_response`、`continue_agent_work`、`bounded_retry`。这组名称是 portable category，不代表任何平台命令。

以下情况使 mandate 失效：work item/stage/attempt/Agent 改变；输入、artifact version/digest 或 Decision Owner 漂移；目标不再唯一；重试耗尽；需要创建资源、跨 work item 写入或进入实现/部署/采购；人类发出替代或取消指令。失效后停止并用自然语言说明需要什么新的任务指令，不生成 operational authorization token。

## `requires_human_review` derivation

只有以下 `action_type` 可以派生 `requires_human_review=true`：

- `design_input`：由准确 Design Decision Owner 接受、修改或拒绝会改变方案的输入；
- `architecture_review`：由准确 Review/Risk Owner 对方案 finding 或明确风险作内容判断；
- `architecture_approval`：由准确 Approval Owner 对 current ready packet 作正式决定。

还必须同时满足：

1. action、Owner 与 authority scope 唯一且 current；
2. Design、Research、Control 以及当前 gate 所需 Review/Packet 具备经 actual activation 验证的 human-readable rendering；`download-only`、raw bytes 或 digest 校验不满足该条件；
3. brief 给出一段式摘要、简图、Team 建议/理由/置信度、已确定/未确定、关键备选后果；
4. 只请求一个原子决定，并给出准确回复与回复后的状态/写入边界；
5. 回复会改变方案内容、Review 结论/风险状态或正式批准状态。

任何条件缺失时 `requires_human_review=false`，不得渲染内容回复表单。准备、交付、附件、可访问性检查、status projection、task-result、relay、retry、verification、sidecar/审计记录和 supersession 都是自动操作，不是 Human Review。

`routing`、Owner binding 或目标范围缺失表示 current mandate 无法唯一执行，应报告新的任务指令边界；它们不伪装成方案 Review。访问能力由 Runtime/adapter 自动验证并记录 evidence gap，`access_confirmation` 不再是可生成的 Review action。

## Portable action and status semantics

```text
HUMAN_ACTION_STATE=none|preparing|awaiting_response|received|unavailable|superseded
requires_human_review=true|false
platform_status_intent=agent_working|human_review|hard_blocked|terminal
```

- Agent 正在准备、交付、自动验证、重试或处理有效回复：`agent_working`。
- `requires_human_review=true` 且完整 current request 已交付给唯一 Owner：`awaiting_response + human_review`。
- 有效 current 回复通过 actor/action/version/digest/supersession 验证后：先记 `received + agent_working`，再处理决定。
- 只有不存在 Agent 自动路径、可执行方案 Review 或明确的新任务关闭路径时才是 `hard_blocked`。

### `execution_continuation_v1`

`agent_working` 只描述意图，不能单独证明 Agent 正在执行。任何非终结 current task 结束前都必须按 [portable execution continuation](execution-continuation.md)生成 `execution_continuation_v1`，绑定唯一下一执行者、单项 action、输入 artifact/version 和 completion condition，并从执行环境回读 `state=accepted|active` 与准确 evidence ref。只有 Next Owner、角色名、任务建议或 planned trigger 时不得报告完成。

无法取得 `accepted|active` evidence 时，当前执行者必须继续可用的确定性恢复；若下一步是真实方案决定则使用 `waiting_human`，若没有 Agent/human 执行路径则使用 `blocked`，已终结则使用 `terminal`。continuation handoff 为 `requires_human_review=false`，不生成 operational authorization。

### `current_action_reference_v1`

`design_input|architecture_review` 的具名回复可以使用 `current_action_reference_v1`。portable authority 由以下事实共同构成：同一 work item、准确 Decision Owner、request 之后产生且未编辑的独立回复、唯一 current Action ID、从 current request 重读并继承的 Action version/digest、一个符合该 action type 的合法决定，以及 current supersession 状态。用户不需要重复机械 version/digest。

平台评论位置、direct parent、thread chain 或自动 mention 都不能进入 portable required fields。回复只要携带准确 current Action ID，就可以从 work item 的最新交互位置提交；adapter 负责在不改变决定语义的前提下处理平台 envelope。Action 缺失、错误、重复、已 supersede，Owner 不匹配，回复早于 request、被编辑、含多个 Action/决定或无法唯一继承 version/digest 时保持 `awaiting_response`，不得按最近时间猜测。

`architecture_approval` 的 packet-bound token/explicit identity 兼容规则保持不变；没有携带 Action ID 的 token-only 回复不能使用本 profile 绕过 packet binding。

platform adapter 可以把这些 intent 映射为本平台状态，但不得把平台状态反向当作 core approval evidence。

## Audit and compatibility

自动操作必须形成 immutable derived execution evidence，绑定 mandate、输入/输出 digests、ordered operations、postconditions、retained objects 和 supersession。该 evidence 由 Runtime 自动生成和重验，不向人请求签署。

历史 `routing|risk_acceptance|design_approval|access_confirmation` 记录继续可读：`risk_acceptance` 解释为 `architecture_review` legacy subtype，`design_approval` 解释为 `architecture_approval` legacy subtype；`routing` 与 `access_confirmation` 仅作历史审计，不得作为新 Review action 生成。历史 operational authorization 也不构成方案决定。
