---
name: multica-architecture-approval-adapter
description: "Use to project a current portable architecture workflow mandate and review packet onto an existing Multica Issue, automatically delivering non-review operations while preserving exact human architecture decisions."
---

# Multica Architecture Approval Adapter

## Purpose and independence boundary

本 skill 是 `architecture-design-workflow` 的 optional sibling adapter。它消费 portable artifacts、`architecture_workflow_mandate_v2`、`execution_continuation_v2`、`architecture_blocker_action_v3`、`requires_human_review` 和 action state，把它们投影到一个明确存在的 Multica workspace/Issue；`architecture_blocker_action_v1|architecture_blocker_action_v2` 只读审计，新副作用必须先生成 superseding v3。adapter 不改变 core stage、Review conclusion、recommendation、packet bytes 或 legal human decision，也不向 core 注入 workspace、Issue、member、comment、attachment、status、URL 或 CLI required fields。

只安装 core 时，standalone local/shared-artifact profile 必须完整可用。adapter 不安装 core、不创建缺失资源、不替代 core 状态机。

## Trigger routes

1. **A0 — Decision Brief material route**：current portable action 绑定完整 standalone Design、Research、Control、唯一 Decision Owner，且 current mandate 允许在准确既有 Issue 内完成准备、交付、可访问性验证和状态投影。
2. **A — packet delivery route**：current compatible delivered `ARCH-APPROVAL-PACKET vN`、准确 Design/Review 和 current mandate 均存在，目标 workspace/Issue/member 唯一。
3. **B — decision consumption route**：current Human Action Request 或 packet readiness、target-human binding 和 exact Review reply 可重读；具名 `current_action_reference_v1` 可来自同一 Issue 最新位置，packet token-only 路径保留原绑定。读取本身无平台写入；current Action task/control evidence、packet decision sidecar 和 `in_progress` projection 作为 current mandate 内的自动操作。
4. **C — execution continuation route**：current portable `execution_continuation_v2` 的 actor/authority/responsibility 可唯一映射到现有 Agent，且 mandate 允许在同一 Issue 内自动发布一次独立 handoff、触发并回读下一 task。
5. **D — actionable blocker route**：current portable `architecture_blocker_action_v3` 可将 instruction owner 唯一映射到既有 Member，并将 resume/discovery actor 与 responsibility 唯一映射到既有 Agent；按 [actionable blocker projection and reply](references/actionable-blocker-projection-and-reply.md)执行 discovery-first、投影一个普通业务问题、消费 `provide_input|request_discovery`、恢复 task 或 blocked rollback。

任一路由的 identity、digest、Owner、stage、attempt 或 target 不唯一时 fail closed。不得从 Issue status、最近评论、显示名、Agent recommendation、旧 authorization token 或模糊肯定构造 core state。

## Human Review boundary

只接受 core 派生的：

```text
action_type=design_input|architecture_review|architecture_approval
requires_human_review=true
```

方案 Review 评论必须使用 [Multica Human Action Request template](templates/multica-human-action-request.md)，首行以 canonical member UUID 渲染 `[@<display-name>](mention://member/<member-id>)`。首屏按固定顺序呈现：方案摘要、简化架构图、Architecture recommendation/理由/置信度、已确定/未确定、关键备选后果、当前读者唯一决定、回复后行为、完整 Design/Research/Control（以及 gate 所需 Review/Packet）入口、准确回复与最小审计绑定。完整设计作为 canonical Markdown attachment，不复制正文。

preparation、delivery、attachment/access verification、task-result、status projection、relay、retry、sidecar、reconciliation、execution handoff 和 postcondition check 的 `requires_human_review` 必须为 `false`。它们在 current mandate 内自动执行，不发布或等待 `AUTHORIZE OPERATION`、relay authorization、access confirmation 或逐状态授权。

## Workflow mandate and derived manifest

开始平台操作前先读取 core [workflow mandate contract](../architecture-design-workflow/references/workflow-mandate-and-review-gates.md)，再读取 [architecture operation manifest](references/architecture-operation-manifest.md)。Adapter 从 current mandate 和只读平台事实确定性生成 `architecture_operation_manifest_v1`，冻结：

- mandate ref、workspace/Issue/Agent、stage、attempt；
- core/adapter package identity 与输入/输出 raw-byte digests；
- target member、action/version、candidate/task selectors；具名 Action profile 的 parent chain 只作审计，packet/delivery selector 保持原约束；
- ordered writes、status transitions、postconditions、retained objects、retry limit 与 supersession。

manifest 完全匹配后立即自动单次消费；它是 machine audit evidence，不是 Human Action，不要求用户签署。任一漂移则保留对象、停止后续写入，并把 manifest、digest、命令结果和 timeline 放入 task evidence；不得生成“授权修复”评论。

## Allowed automatic operations

current mandate 和 manifest 可以覆盖：

- 只读 capability/identity/preflight、材料准备与 raw-byte validation；
- 一条 Decision Brief comment 与其准确 attachments；
- desktop/mobile 的 actual UI activation、browser-rendered preview、identity/complete-content evidence 或明确 evidence gap；raw-byte fetch、HTTP 200 与 `download-only` 不计为 opened；对于有显式 Owner policy 的 `design_input|architecture_review`，可投影 `access_verification_mode=owner_manual` 与逐 scope `manual_check_required`，但不得声称 `opened`；
- platform-managed task-result evidence；
- `multica issue status <issue> in_progress --no-start` 与 `in_review --no-start` 的准确投影和 readback；
- packet route 的既有 `arch.packet.current` bounded projection；
- 已确认既有 shared scope 中的 no-clobber evidence sidecar；
- bounded reconciliation/retry 和旧 request supersession；
- 有效 current Review 回复的读取、sidecar 和后续处理启动。
- 按 [execution handoff and task readback](references/execution-handoff-and-task-readback.md)发布一个独立的 `multica_execution_handoff_v1`、精确 mention 下一 Agent，并回读准确 task ID/status。
- 按 [actionable blocker projection and reply](references/actionable-blocker-projection-and-reply.md)先自动 discovery，再投影必要的 `blocked`、发布唯一 instruction-owner 简明 blocker comment、消费准确 `provide_input|request_discovery` 并在 task 接收后恢复 `in_progress`。

禁止：创建 workspace/Project/Team/Agent/Issue/Skill/shared scope，跨 Issue/workspace 写入，私有 API，overwrite/delete/edit 历史对象，replace-all binding，业务实现、部署、采购或未列入 manifest 的写入。范围扩大时停止并说明需要新的任务指令，不生成 operational token。

## Status projection

Issue status 只是 portable intent 的平台投影：

- Agent 准备、交付、自动验证、retry 或处理有效回复，且当前 task 尚未结束：`in_progress`；
- current Decision Brief/完整材料/mention/access postconditions 成功，且 `requires_human_review=true`：自动 `in_review --no-start`；其中 `automatic` 要求 requested scopes=`opened`，显式 `owner_manual` 要求准确 attachment identity/digest、stable same-Issue entry、唯一 Owner 与 policy evidence，并记录 `manual_check_required`；
- discovery-first 没有唯一 verified binding 且 current actionable blocker 已向唯一 instruction owner 交付：自动 `blocked --no-start`；该动作 `requires_human_review=false`，不是方案审核；
- 唯一 Owner 的具名 current Action 回复通过 actor/work item/Action ID/继承的 version-digest/created-after-request/revision/supersession/task attribution 后：自动 `in_progress --no-start`，再处理决定；其 Multica parent/thread 只作审计；
- 非 Review 步骤成功：自动进入下一合法 stage；当前 task 若将结束，必须先由独立 handoff 回读下一 task 为 `queued|running`，或证明其 `waiting_local_directory` 仅等待当前前序 task 持有的同一 `in_place` 目录锁；否则不得保留 `in_progress + WAIT_REASON=none`；
- blocker 的 `provide_input|request_discovery` 回复验证成功但 resume/discovery task 尚未回读为 `queued|running`：保持或回滚 `blocked`；只有 task accepted/active 后才 `in_progress --no-start`；
- 不存在 current actionable blocker、Agent 或 human 可执行路径时：`blocked` 且说明需要新的任务指令；`critical_evidence_gaps` 与可执行方案 Review 共存时仍为 `in_review`。

无效、编辑、错误 Owner、错误/重复/superseded Action、未授权 mention 规范化或错误 task attribution 的回复不改变 status。packet token-only reply 的错误 parent/identity 仍无效。

## Route A0 — material delivery

1. 验证 current mandate、single action/Owner/scope、standalone Design/Research/Control identities 和 target member；Owner 不唯一时停止并请求新的任务指令。
2. 自动生成 manifest；必要时先投影 `in_progress --no-start` 并 read back。
3. 读取 [human action material bundle](references/human-action-material-bundle.md)与 [human-accessible evidence links](references/human-accessible-evidence-links.md)，执行一次 comment+attachments write。
4. 重读 exact comment/parent/author/mention/attachments并重算 raw-byte digests。`automatic` 分别在 desktop/mobile 执行 actual UI activation；已知 Markdown attachment link 必须打开 browser-rendered preview并呈现完整正文。仅当唯一 Owner 已明确选择自行检查时，`design_input|architecture_review` 可用 `owner_manual`：验证 stable same-Issue entry 后把 requested scopes 记为 `manual_check_required`，不伪造客户端打开证据。
5. 只有 `requires_human_review=true` 且当前模式全部 Review 前提通过时自动投影 `in_review --no-start`。`automatic` 的必要预览失败按 evidence gap 处理；`owner_manual` 的 identity、digest、稳定入口或 policy evidence 失败仍 unavailable。owner-manual 决策卡必须提供 `ACTION <action-id>: 材料打不开`。
6. 后续具名 Action 回复按 `current_action_reference_v1` + `valid_human_action_response_v1` 验证；用户可在同一 Issue 最新位置回复，允许规范化一个首尾 current Architecture Agent canonical mention，验证后自动恢复 `in_progress`。准确 Owner 回复“材料打不开”时不消费任何内容选项，记录 `content_decision=none`，投影 `preparing/in_progress` 并由 coordination 自动执行 `repair_or_republish_material_entry`。

## Route A — packet delivery and readiness

1. 按 [core compatibility](references/core-contract-compatibility.md) 验证 current delivered packet、Design/Review raw bytes 和 package aggregate。
2. 按 [target human mapping](references/target-human-mapping.md) 唯一解析 current member；禁止显示名、邮箱、assignee 或最近作者推断。
3. 自动派生 manifest 并执行 [capability preflight](references/capability-preflight-and-write-authorization.md) 的只读 fence。
4. 按 [delivery mapping](references/delivery-mapping-and-marker.md) 创建或 reconciliation 复用唯一 canonical packet comment；验证三份 attachments。
5. 按 [reconciliation and readiness](references/reconciliation-projection-and-readiness.md) 执行 bounded projection、final scan 和 no-clobber readiness sidecar。
6. current approval brief 成功交付后自动进入 `in_review`；readiness/recommendation/status 都不构成人工批准。

## Route B — decision consumption

1. 具名 Action route 重读 current Human Action Request/material readiness/target-human binding；packet route 重读 current readiness sidecar、packet comment/attachments 与 mapping；两者都按 ID 重读 exact decision comment。
2. 按 [human decision binding](references/human-decision-binding.md) 选择 `current_action_reference_v1` 或 packet profile，验证 actor、work item、Action/packet identity、revision、digest 与 supersession；不得用 parent 修复错误 Action，也不得用 Action ID 绕过 token-only packet binding。
3. `design_input|architecture_review` 把 decision evidence 写入 manifest-bound platform task/ARCH-CONTROL 并回读；正式 packet approval 继续使用既有 shared-scope no-clobber sidecar。证据通过后恢复 `in_progress` 处理 portable decision。
4. 具名 Action 的错误/重复/过期 identity、edited、wrong actor、非法 mention/附加正文，以及 packet route 的 token+prose、wrong parent/旧 packet/mapping drift，只保留审计，不改变 gate/status。

## Route C — execution continuation

1. 读取 core [execution continuation](../architecture-design-workflow/references/execution-continuation.md)，确认 work item/stage/attempt、next actor/authority/responsibility、action、输入 refs、关闭条件和 continuation identity current 且唯一。
2. 动态读取既有 Team member/Agent 目录，按显式 responsibility mapping 与稳定 identity 唯一映射下一执行者；不得用显示名、Team assignee、最近作者、旧部署角色或空闲状态猜测。
3. 按 [execution handoff and task readback](references/execution-handoff-and-task-readback.md)派生 `multica_execution_handoff_v1`。handoff 必须是独立评论；不得在普通 `ARCH-CONTROL` 中嵌入可触发的下一成员或 self mention。
4. 写入后按准确 Issue、Agent、handoff ID 和 attempt 回读 task。`queued` 或满足 runtime online、准确 attribution、current `predecessor_task_id` 和同一 `in_place` 目录锁证据的 `waiting_local_directory` 映射为 `accepted`；`running` 映射为 `active`。其他状态不得允许当前 task 完成。
5. 重复 handoff 回读既有 consumption/task 后 reconciliation no-op；未入队、目标漂移或 evidence 不可重读时失败关闭，不重复触发、不伪造执行者。

## Route D — actionable blocker

1. 读取 current blocker v3 与 mandate，确认 instruction owner、单项 missing input、`automatic_before_human`、一个普通 `business_question`、discovery scope/actor、`provide_input|request_discovery`、closing condition 和 resume actor 全部 current；v1/v2 只能作为 superseded audit evidence。
2. 唯一解析 instruction owner Member、resume Agent 与既有 `coordination|research` discovery Agent；无法解析时在任何写入前返回 `needs_new_mandate_v1`。
3. 在授权 scope 内只读 discovery：唯一 verified binding 自动派生 resume handoff；多个候选或有证据的 unavailable 才使用 [Multica blocker comment](templates/multica-blocker-comment.md)。评论按“为什么暂停→团队建议/理由/置信度→一个业务问题→三个可直接回复→回复后行为→可选依据”渲染；默认不得显示 RACI、组织/服务目录、策略批准记录或 machine binding 字段。投影 `blocked --no-start` 后回读唯一 mention/action。
4. 准确 Owner 的 created-after-request、未编辑、single-action 回复通过后：`ACTION <id>: 由我负责` 与 `ACTION <id>: 负责人是 <可识别对象>` 规范化为 `provide_input/human_declaration`，从 comment author、Action 冻结范围、ref/revision/time 与 readback 派生 machine evidence，再映射 resume Agent 验证；`ACTION <id>: 我不确定，请团队给出建议` 规范化为 `request_discovery` 并映射 discovery Agent。正式来源只在用户明确表示存在或 deployment policy 要求时追问。只有对应 task 回读 queued/running 才投影 `in_progress --no-start`。
5. task 未入队、authority 越界或 mapping/readback 漂移时 blocked rollback；保留历史对象，new attempt supersede 旧 action，不留下 orphaned in_progress，不请求 operational authorization。

## Failure, retry, and legacy migration

失败时不编辑、删除、relabel、append 或覆盖已创建对象。仍有确定性恢复路径且未耗尽上限时，自动生成 new attempt/new manifest 并把 retained set 和 supersedes 冻结进去；同一 current identity 不得重复 delivery。没有可执行路径时才投影 `blocked` 并给出自然语言恢复条件。

[Operational authorization protocol](references/operational-authorization.md) 与 [legacy template](templates/multica-operational-authorization.md) 仅用于解析历史审计记录。新契约不得生成、relay 或消费 `multica_operational_scope_v1` / `AUTHORIZE OPERATION`。激活后，未消费的 delivery/retry/relay/status request 保留原样并由新 manifest 的 `supersedes` 标记为 audit-only；晚到回复 no-op。

## Activation boundary

Skill package/import/binding 本身不是 Issue Review。只有明确的实施并激活任务指令建立 activation mandate 后，才按 [activation runbook](references/activation-runbook.md) 对用户指定的既有 workspace/Agent 自动执行 conflict-safe import/additive binding/readback；不再拆分 activation/conflict authorization。目标缺失、需要 overwrite/delete/创建资源或范围变化时停止并请求新的任务指令。

## Progressive disclosure

- 始终先读 workflow mandate 与 operation manifest。
- A0 再读 material bundle、human-accessible links、target-human mapping 和 human-action template。
- A 再读 compatibility、preflight、delivery mapping、reconciliation/readiness、durable evidence 和 approval template。
- B 再读 human-decision binding、durable evidence 和 decision template。
- C 再读 execution handoff and task readback。
- D 再读 actionable blocker projection/reply 与 blocker comment template。
- activation/sandbox 只在明确任务指令覆盖该阶段时读取对应 runbook/checklist。
