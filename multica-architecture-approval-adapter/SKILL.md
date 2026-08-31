---
name: multica-architecture-approval-adapter
description: "Use for explicitly authorized Multica delivery of current architecture decision materials or a compatible packet, or for platform-read-only decision review of existing durable readiness; never create core state or implicit platform writes."
---

# Multica Architecture Approval Adapter

## Purpose and trigger boundary

本 skill 是 `architecture-design-workflow` 的独立、可单独安装的 sibling skill；它不是 core 的条件分支，也不替代或指令 core 状态机。它有三个互不隐含授权的路由：

1. **A0 — human-action material delivery**：current core Human Action Request 绑定完整 standalone `ARCH-DESIGN-vN.md`、准确 Research/Control 与一个唯一 Decision Owner；既有 Multica workspace/Issue 和 `operation_variant=delivery` 精确授权覆盖一次 Decision Brief+附件写入。该路由只交付决策材料，不创建 packet readiness 或 core state。
2. **A — packet delivery route**：当前 core packet 是 compatible/current/delivered 的 `ARCH-APPROVAL-PACKET vN`，已给出既有可访问的 Multica workspace/Issue，且当前任务明确授权对该 Issue 写入 delivery。该路由在首笔写入前还必须通过 write preflight。
3. **B — platform-read-only decision route**：已存在 current、可重读的 readiness sidecar，且已给出 exact Issue、packet 与 canonical target-human binding；当前任务明确要求读取/审计 decision。该路由不要求、也不取得新的 Multica delivery-write 授权，绝不隐含 Multica comment、attachment、metadata、workspace 或配置写入。若要把 audit candidate 变成有效 portable decision，当前任务还必须单独明确授权在已确认 shared scope 写入 immutable decision sidecar；没有该授权只能返回 audit candidate，不能生效。

compatibility 的 exact markers、frozen inputs 和 raw-byte digests 会在相关 I/O 前验证。任一路由条件缺失时，**不得**从 Issue、评论、metadata、Agent 或推荐中构造、补写或猜测 core 状态。

无 packet 或 packet 不兼容时，adapter 只在本地 `availability`/closing condition 表达不可用，保留 core 原有状态；它不得写出、建议或要求任何 core stage/blocker。只有 compatible current packet 已存在但 external readiness 未能验证时，adapter 才输出 portable unavailable evidence；是否维持 `reviewing` / `review_packet_unavailable` 完全由 core 自身 contract 计算。

本 adapter 的可交付 evidence 只映射回 portable core fields；不得改变 canonical stage、Review conclusion、`ARCHITECTURE_RECOMMENDATION` enum、packet bytes 或 legal human decision value。readiness 与 recommendation 都不构成人工批准。

当 compatible core 输出 current Human Action Request 时，先读取 [human action material bundle](references/human-action-material-bundle.md)与 [human-accessible evidence links](references/human-accessible-evidence-links.md)，再使用 [Multica Human Action Request template](templates/multica-human-action-request.md)忠实渲染。评论固定为 Architecture Decision Brief：方案摘要、简化架构图、Team 建议/理由/置信度、已确定/未确定、关键备选后果、当前读者的一项决定、回复后行为和完整 Design/Research/Control 入口；完整设计作为 canonical Markdown attachment，不复制正文。只有唯一绑定的当前 member 获得一个可执行回复表单，其他 Owner 只列 non-actionable dependencies。用户材料入口必须经过实际 attachment/link、准确 identity、完整内容与逐 desktop/mobile scope 验证；未经验证的 `multica://issues/...`、本地路径、文件名卡片或临时 URL 不能冒充 human-accessible ref。

所有可执行 Human Action 评论首行必须用 canonical member UUID 渲染 `[@<display-name>](mention://member/<member-id>)`，不能只写显示名、角色名或普通文本 `@name`。Issue status 是 core stage 的平台投影而非替代：Agent 正在准备或处理有效回复时为 `in_progress`；current actionable request 已成功交付、等待该 member 回复时为 `in_review`；只有没有可执行 Agent 或 human 路径时才是 `blocked`；正式发布或 handoff 完成后才可为 `done`。`critical_evidence_gaps` 与可行动请求可以同时存在，此时必须投影为 `in_review`，不能仅因 evidence gap 设为 `blocked`。

任何新的 delivery、target-human/shared-scope 写入、activation、conflict strategy、sandbox 或 retry 权限，都必须先读取 [operational authorization protocol](references/operational-authorization.md)并使用 [Multica Operational Authorization template](templates/multica-operational-authorization.md)。运维授权与架构内容决定是不同 authority：它只覆盖所列 existing identities、exact planned writes 和 path scope，不能被 recommendation、批准 comment 或模糊肯定推断，也不能成为 core human decision。

## Fixed core compatibility contract

packet route 继续只消费 `architecture-design-workflow` implementation revision `1d4b860b48e15f678d78a71bf2c38557ab9c2951` 的 immutable packet contract。A0 route 另外消费 portable `architecture_decision_brief_v1` / standalone Design markers，并在 activation 时记录实际 core package aggregate。开始任何 Multica I/O 前，按 [core compatibility](references/core-contract-compatibility.md) 验证对应 route 的 exact markers、required fields 和 immutable raw-byte digest contract。

版本不兼容、字段未知、字段缺失、输入不再是 current packet、或 digest 无法重读匹配时，输出：

```text
evidence_type=review_packet_unavailable
packet_ref=<supplied-or-none>
packet_version=<supplied-or-none>
packet_digest=<supplied-or-none>
review_conclusion=<real supplied conclusion or none>
failed_checks=core_contract_compatible
owner=Architecture Lead
closing_condition=provide a current delivered packet compatible with core revision 1d4b860b48e15f678d78a71bf2c38557ab9c2951
```

这不是把 Multica 字段加入 core required fields；core 继续只消费 portable ref/version/digest、actor、scope、verification time、verifier 和 evidence ref。

## Required preflight and allowed writes

在写入前读取 [capability preflight and write authorization](references/capability-preflight-and-write-authorization.md)。每个 check 必须记录 deterministic evidence（check、observed command/profile、result、owner、closing condition）。对 unknown、unsupported、错误输出或无法重读的行为一律失败关闭为 `review_packet_unavailable`，保留真实 Review conclusion，并且不写入。

只有同时满足 current `operational_authorization` 明确覆盖该 Issue delivery、所有 input/path scope 和完整 preflight 通过时，才可对该既有 Issue 执行最小必要的 comment、attachment 与 `arch.packet.current` metadata projection 写入。若准备任务的 task result 会由 Multica 自动投递为授权请求评论，scope 使用 `authorization_request=multica_task_result_authorization_request_v1`，冻结 preparation task、原 trigger、request Agent、授权身份、Issue/workspace、Owner、attempt 与材料 digest，并把 `comment:multica_task_result_authorization_request_v1` 列为受约束的预期 retained object。平台投递后必须以 `source_task_id`、parent、Agent、revision 1、准确授权内容和唯一性解析实际请求评论；缺失、重复、编辑或不匹配均失败关闭。

若随后的人类授权回复触发 delivery，scope 的 `planned_writes` 使用 `parent=multica_authorization_response_parent_v1`。执行时必须先解析上述 task-result 请求评论，再验证当前回复的 direct parent 等于该评论，并在 author/content/revision/Issue/workspace/task-attribution 全部精确匹配后，才把 response selector 解析为当前 `trigger_comment_id`，调用 `multica issue comment add <issue> --parent <trigger-comment-id> --attachment <path> --output json`。不得使用猜测 UUID、旧回复、最近评论或 thread root。

未列入 `planned_writes` 的 Agent 主动授权请求、诊断、修补评论和 Issue 状态变更一律不是隐含副作用；没有对应授权时只通过 task result 返回。Multica 把 task result 自动投递为 platform-managed task result comment 属于平台管理行为，不是 Agent 主动调用 Issue write；结果必须如实说明“未主动调用 Issue write；Multica 将 task result 自动投递为平台管理评论”，不得声称没有产生平台评论。A0 的授权必须把当前执行开始时的 `in_progress --no-start`（若当前状态不同）、交付评论及其附件、交付 postcondition 成功后的 `in_review --no-start`，以及由 `valid_human_action_response_v1` 延迟选择器约束的回复任务 `in_progress --no-start` 分别列为准确有序写入；任何一项未授权都不得执行或暗中补写。

以下操作不属于 Issue delivery，也不得作为本 skill 的隐式副作用：Skill import、Agent binding、Team/Project/Issue 创建、Runtime 配置、CLI install/upgrade、私有/未文档化 API、缺失 resource 创建。它们要求单独、明确的人类授权；没有该授权时停止并报告 owner 与 closing condition。不得以 preflight 失败为理由安装、升级、配置或绕过平台接口。

## Target human boundary

交付前读取 [target-human mapping](references/target-human-mapping.md)。使用 `multica_target_human_v1`：design/review 的 `Target human actor` 必须非空且相同，且唯一解析为 canonical Multica member UUID。只接受 packet 中的 `multica_member:<uuid>`（并生成 external, re-verifiable packet-bound binding evidence ref），或 packet-bound user-role-confirmed mapping evidence。两种分支都必须把 exact current packet ref/version/digest 与 design/review actor fields 绑定到 `human_actor_binding_ref`；禁止由显示名、邮箱片段、Issue assignee、评论作者、workspace membership 或 Agent 身份推断。

若 actor 不一致、为零或多个匹配、evidence 不可重验、Issue/workspace scope 不匹配，必须输出 `review_packet_unavailable`；不得发布 delivery 或消费 human decision。仅 Agent 可下载附件不是 target human access confirmation。

## Execution order

### A0 — human-action material delivery

1. 验证 current Human Action Request 的单 action/Owner/scope、standalone Design 结构/version/digest 以及 Research/Control identities；不要求不存在的 packet。Agent 开始执行已授权工作时，将 Issue 精确投影为 `in_progress --no-start` 并重读验证。
2. 唯一绑定当前 Multica member；Owner 未绑定/歧义时只允许 routing brief，不允许 content action。评论首行必须渲染该 member 的 canonical mention。
3. 验证 exact operational authorization、路径/digest、状态写入与一次 comment+attachment write preflight；若授权请求来自平台自动投递的准备任务结果，先唯一解析 `multica_task_result_authorization_request_v1`，再验证回复并解析 `multica_authorization_response_parent_v1`。
4. 若 exact 新入口尚无 requested-client 证据，本次唯一 action 必须是 `access_confirmation`；按 `multica_human_action_material_bundle_v1` 执行一次写入，重读 comment/attachment/parent/author，并验证 canonical Markdown raw bytes。
5. 分别记录 desktop/mobile attachment/link、exact identity 和 complete-content 结果；失败保留对象并 unavailable，不写 `arch.packet.current`。评论及所有交付 postconditions 成功后，执行 `multica issue status <issue> in_review --no-start` 并重读；这表示已明确 `@` 唯一 Owner 且等待其行动。
6. 当后续任务由准确 current 回复触发时，先按 `valid_human_action_response_v1` 验证 actor、direct parent、action ref、revision、exact response 与 task attribution，再执行已授权的 `multica issue status <issue> in_progress --no-start` 并重读，然后处理回复。无效、过期或错误 Owner 的回复不得改变状态。
7. 全部通过后，内容决定必须使用新的 core action 版本和新的独立授权交付，不编辑旧评论，访问确认本身不批准方案。状态 postcondition 失败时保留已有对象、失败关闭并在 task result 报告，不执行未授权 repair。

### A — delivery route

1. 验证 delivered current packet 与 pinned core contract；失败则只输出 adapter-local availability/closing condition。
2. 验证 `multica_target_human_v1`、已授权 durable shared scope 与 target member 的 Issue/workspace scope；失败则 unavailable，不写入。
3. 执行并记录 [two-phase capability preflight](references/capability-preflight-and-write-authorization.md) 的无副作用 pre-write gate；失败即停止。
4. 仅在当前显式写任务允许时，执行一次 packet-comment delivery；把 response/actual parent/bindings/redownload/metadata write-readback 当作 postconditions。随后按 reconciliation/readiness 流程生成 sidecar。

### B — read-only decision-consumption route

1. 从已存在的可重读 readiness sidecar 重读 exact current packet、target-human mapping、Issue 与 delivery identity；没有 durable current readiness 则不生效。
2. 只读重建 comment parent chain 或验证 explicit identity，并重新读取 decision comment。
3. 仅在 [human decision binding](references/human-decision-binding.md) 与 durable sidecar contract 都满足时记录/消费 decision；sidecar 写入需该任务的额外明确 shared-scope 授权，此路由不执行任何 Multica 平台写入。

后续流程必须保持 frozen Markdown 原始 bytes；不能用平台重排、评论摘要或 PDF 覆盖 canonical bytes/digest。任何 unavailable evidence 都须保留已有对象与真实 Review conclusion，不自动删除或“回滚”平台对象。

## Delivery, readiness, and decision routes

- 设计阶段 Decision Brief、完整 Design 附件、Research/Control 入口与客户端验证：读取 [human action material bundle](references/human-action-material-bundle.md)、[human-accessible evidence links](references/human-accessible-evidence-links.md)和 [Multica Human Action Request template](templates/multica-human-action-request.md)。
- packet 审核评论、单次三附件交付、stable marker、JSON durable refs 与 PDF 非权威边界：读取 [delivery mapping and marker](references/delivery-mapping-and-marker.md)、[Multica Human Action Request template](templates/multica-human-action-request.md) 和 [approval-comment template](templates/multica-approval-comment.md)。
- delivery states、reconciliation、`arch.packet.current` projection、raw-byte reread 和 readiness/unavailable envelope：读取 [reconciliation, projection, and readiness](references/reconciliation-projection-and-readiness.md)、[durable evidence records](references/durable-evidence-records.md) 和 [readiness-evidence template](templates/multica-readiness-evidence.md)。
- packet-comment reply / explicit-reference 人工决定、token/context 分离、reread、编辑失效、同 actor replacement 与跨 actor conflict：读取 [human decision binding](references/human-decision-binding.md) 和 [decision-evidence template](templates/multica-decision-evidence.md)。

## Activation and sandbox boundary

本 skill 的安装、workspace import 与 Agent binding 不属于 Issue delivery，也不是 apply 的副作用。仅在人类通过 current operational authorization 指定**既有**目标 workspace、Architecture Agent、两份 skill identity 和准确 planned writes 后，才可按 [activation runbook](references/activation-runbook.md) 操作；runbook 使用 safe conflict handling、additive `agent skills add` 与最终只读 `agent skills list`，绝不自动创建缺失资源。same-name conflict、sandbox 和 partial-failure retry 都需要绑定新事实的新授权，旧授权不自动扩展。

静态安装、临时 HOME 链接或本地 archive 检查都不等于生产可用。实际激活后仍须在专用 sandbox Issue 完成 [sandbox acceptance checklist](references/sandbox-acceptance-checklist.md) 的桌面/手机附件打开、raw-byte digest、短 token reply、supersession、retry 与失败关闭验收；未获单独授权或尚未执行时，activation 和 sandbox acceptance 必须记录为 `not_run`。
