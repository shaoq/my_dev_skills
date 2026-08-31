---
name: multica-architecture-approval-adapter
description: "Use to project a current portable architecture workflow mandate and review packet onto an existing Multica Issue, automatically delivering non-review operations while preserving exact human architecture decisions."
---

# Multica Architecture Approval Adapter

## Purpose and independence boundary

本 skill 是 `architecture-design-workflow` 的 optional sibling adapter。它消费 portable artifacts、`architecture_workflow_mandate_v1`、`requires_human_review` 和 action state，把它们投影到一个明确存在的 Multica workspace/Issue；它不改变 core stage、Review conclusion、recommendation、packet bytes 或 legal human decision，也不向 core 注入 workspace、Issue、member、comment、attachment、status、URL 或 CLI required fields。

只安装 core 时，standalone local/shared-artifact profile 必须完整可用。adapter 不安装 core、不创建缺失资源、不替代 core 状态机。

## Trigger routes

1. **A0 — Decision Brief material route**：current portable action 绑定完整 standalone Design、Research、Control、唯一 Decision Owner，且 current mandate 允许在准确既有 Issue 内完成准备、交付、可访问性验证和状态投影。
2. **A — packet delivery route**：current compatible delivered `ARCH-APPROVAL-PACKET vN`、准确 Design/Review 和 current mandate 均存在，目标 workspace/Issue/member 唯一。
3. **B — decision consumption route**：current Human Action Request 或 packet readiness、target-human binding 和 exact Review reply 可重读；具名 `current_action_reference_v1` 可来自同一 Issue 最新位置，packet token-only 路径保留原绑定。读取本身无平台写入，决定 sidecar 和 `in_progress` projection 作为 current mandate 内的自动操作。

任一路由的 identity、digest、Owner、stage、attempt 或 target 不唯一时 fail closed。不得从 Issue status、最近评论、显示名、Agent recommendation、旧 authorization token 或模糊肯定构造 core state。

## Human Review boundary

只接受 core 派生的：

```text
action_type=design_input|architecture_review|architecture_approval
requires_human_review=true
```

方案 Review 评论必须使用 [Multica Human Action Request template](templates/multica-human-action-request.md)，首行以 canonical member UUID 渲染 `[@<display-name>](mention://member/<member-id>)`。首屏按固定顺序呈现：方案摘要、简化架构图、Team 建议/理由/置信度、已确定/未确定、关键备选后果、当前读者唯一决定、回复后行为、完整 Design/Research/Control（以及 gate 所需 Review/Packet）入口、准确回复与最小审计绑定。完整设计作为 canonical Markdown attachment，不复制正文。

preparation、delivery、attachment/access verification、task-result、status projection、relay、retry、sidecar、reconciliation 和 postcondition check 的 `requires_human_review` 必须为 `false`。它们在 current mandate 内自动执行，不发布或等待 `AUTHORIZE OPERATION`、relay authorization、access confirmation 或逐状态授权。

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
- desktop/mobile 的 actual UI activation、browser-rendered preview、identity/complete-content evidence 或明确 evidence gap；raw-byte fetch、HTTP 200 与 `download-only` 不计为 opened；
- platform-managed task-result evidence；
- `multica issue status <issue> in_progress --no-start` 与 `in_review --no-start` 的准确投影和 readback；
- packet route 的既有 `arch.packet.current` bounded projection；
- 已确认既有 shared scope 中的 no-clobber evidence sidecar；
- bounded reconciliation/retry 和旧 request supersession；
- 有效 current Review 回复的读取、sidecar 和后续处理启动。

禁止：创建 workspace/Project/Team/Agent/Issue/Skill/shared scope，跨 Issue/workspace 写入，私有 API，overwrite/delete/edit 历史对象，replace-all binding，业务实现、部署、采购或未列入 manifest 的写入。范围扩大时停止并说明需要新的任务指令，不生成 operational token。

## Status projection

Issue status 只是 portable intent 的平台投影：

- Agent 准备、交付、自动验证、retry 或处理有效回复：`in_progress`；
- current Decision Brief/完整材料/mention/access postconditions 成功，且 `requires_human_review=true`：自动 `in_review --no-start`；
- 唯一 Owner 的具名 current Action 回复通过 actor/work item/Action ID/继承的 version-digest/created-after-request/revision/supersession/task attribution 后：自动 `in_progress --no-start`，再处理决定；其 Multica parent/thread 只作审计；
- 非 Review 步骤成功：自动进入下一合法 stage 或完成当前步骤；
- 仅在没有 Agent 或 human 可执行路径时：`blocked`；`critical_evidence_gaps` 与可执行方案 Review 共存时仍为 `in_review`。

无效、编辑、错误 Owner、错误/重复/superseded Action、未授权 mention 规范化或错误 task attribution 的回复不改变 status。packet token-only reply 的错误 parent/identity 仍无效。

## Route A0 — material delivery

1. 验证 current mandate、single action/Owner/scope、standalone Design/Research/Control identities 和 target member；Owner 不唯一时停止并请求新的任务指令。
2. 自动生成 manifest；必要时先投影 `in_progress --no-start` 并 read back。
3. 读取 [human action material bundle](references/human-action-material-bundle.md)与 [human-accessible evidence links](references/human-accessible-evidence-links.md)，执行一次 comment+attachments write。
4. 重读 exact comment/parent/author/mention/attachments，重算 raw-byte digests，并分别在 desktop/mobile 执行 actual UI activation；已知 Markdown attachment link 必须打开 browser-rendered preview 并呈现完整正文，不能只 fetch 或触发下载。
5. 只有 `requires_human_review=true` 且全部 Review 前提通过时自动投影 `in_review --no-start`。任一必要材料只有 `download-only`、preview 未呈现或无法验证时保留对象并记录 evidence gap/恢复路径，保持 `in_progress` 或在无恢复路径时 `blocked`，不生成 access-confirmation action。
6. 后续具名 Action 回复按 `current_action_reference_v1` + `valid_human_action_response_v1` 验证；用户可在同一 Issue 最新位置回复，允许规范化一个首尾 current Architecture Agent canonical mention，验证后自动恢复 `in_progress`。

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
3. 自动 no-clobber 写入 decision evidence，并在 readback 通过后恢复 `in_progress` 处理 portable decision。
4. 具名 Action 的错误/重复/过期 identity、edited、wrong actor、非法 mention/附加正文，以及 packet route 的 token+prose、wrong parent/旧 packet/mapping drift，只保留审计，不改变 gate/status。

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
- activation/sandbox 只在明确任务指令覆盖该阶段时读取对应 runbook/checklist。
