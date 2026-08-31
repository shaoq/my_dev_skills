# 架构审批材料已交付

## Architecture Decision Brief

## 当前方案摘要

{{one_paragraph_solution_summary_zh}}

## 简化架构图

```text
{{simplified_architecture_diagram}}
```

## Architecture Team 总体建议

- 总体建议：`{{architecture_recommendation}}`
- 推荐理由：{{recommendation_rationale_zh}}
- 置信度：`{{confidence_high_medium_low}}`；依据与可能改变建议的证据：{{confidence_basis_zh}}
- 适用条件：{{applicable_conditions_zh}}
- 关键风险 / accepted warnings：{{key_risks_and_acceptance_zh}}

> 推荐不是批准。Recommendation、Review conclusion、readiness、访问 evidence、metadata、reaction、Issue status 或 Agent/system 评论均不得驱动 core gate。

## 已确定与尚未确定

- 已确定：{{determined_zh}}
- 尚未确定：{{undetermined_zh}}
- Other-owner dependencies (non-actionable)：

| Action / dependency | Owner / authority scope | 对当前方案的影响 | Closure condition |
|---|---|---|---|
| {{dependency_action}} | {{dependency_owner_scope}} | {{dependency_impact_zh}} | {{dependency_closure_zh}} |

这些依赖没有当前读者可执行的回复表单，不能通过本评论代替其他 Owner 关闭。

## 最重要的备选及后果

| 准确 token | 中文后果 | 收益 | 代价 / material risks | 不可逆影响 |
|---|---|---|---|---|
| `approved_design_only` | 只发布批准文档 | {{design_only_benefits_zh}} | 不生成 R&D handoff | 正式历史通过 supersede/revoke 演进 |
| `approved_for_spec` | 发布批准文档，并在目标存在时形成 R&D handoff | {{for_spec_benefits_zh}} | 目标缺失时仍等待 routing | R&D Team 独立分析；不自动创建 OpenSpec、Issue、branch、commit 或代码 |
| `revision_requested` | 进入新设计迭代 | 可按新证据修订方案 | 当前 packet 不再推进 | 旧 packet 不改写；生成新设计版本 |
| `rejected` | 拒绝 current work item | 明确终止当前方案 | 继续需要新的明确工作 | 当前 work item 进入终态 |

## 当前读者的一项决定

- Action ID / type：`{{human_action_id}}` / `architecture_approval`
- `requires_human_review=true`
- Decision Owner：`{{canonical_target_member_uuid}}`
- Current reader / authority binding：`{{unique_binding_evidence_ref}}`
- Content-decision activation gate：`ready`；Design/Review/Packet 已按 requested client scopes 自动验证，否则不得渲染本审批表单。
- 审核对象：`{{review_subject_zh}}`
- 为什么现在可决定：`{{packet_ref}} {{packet_version}}` 已完成 current delivery/readiness，Review conclusion=`{{review_conclusion}}`
- Candidate recommendation：`{{architecture_recommendation}}`
- Bounded alternatives / Option consequences：仅限上一节四个 token；当前评论只请求这一项审批决定。

## 回复后会发生什么

| Response | Next stage | Remaining blockers | Next Owner | 直接 planned writes | 权限边界与不可逆影响 |
|---|---|---|---|---|---|
| `approved_design_only` | `publishing` | `none|approved_artifact_unavailable` | Architecture Lead | 控制记录、ADR、详细设计 | 不生成 R&D handoff；历史通过 supersede/revoke 演进 |
| `approved_for_spec` | `publishing`；目标缺失时 `waiting_human` | `none|missing_target_project|approved_artifact_unavailable` | Architecture Lead；目标缺失时 Routing Owner | 控制记录、ADR、详细设计、目标存在时 handoff | 不自动创建研发资源或实现产物 |
| `revision_requested` | `designing` | `none`；说明缺失时 `revision_scope=missing` context | Solution Architect / Design Decision Owner | 控制记录、新设计版本 | revision brief 另行提供；旧 packet 不改写 |
| `rejected` | `rejected` | `none` | Architecture Lead 记录终态 | 控制记录 | 终态；继续需要新的明确工作 |

## 完整材料入口

- Stable human-accessible evidence refs：
  - Stable Design ref：{{stable_design_attachment_ref}}（`{{design_ref}} {{design_version}}`）
  - Research：{{research_human_access_entry}}
  - Control：{{control_human_access_entry}}
  - Stable Review ref：{{stable_review_attachment_ref}}（`{{review_ref}} {{review_version}}`）
  - Stable Packet ref：{{stable_packet_attachment_ref}}（`{{packet_ref}} {{packet_version}}`）
- Requested client scopes：`desktop`（Web）/ `mobile`
- Access status by scope：`opened|unavailable|not_run`
- Verifier / verification time：{{verifier_and_time}}

请逐项打开完整 Design、Research、Control、Review 和 Packet；附件卡片名称、摘要、Agent 下载、内部对象 identity 和可选预览均不能替代完整材料或 target-member access confirmation。

## 准确回复

在本评论的 descendant chain 中，由准确 Decision Owner 新建一条评论，去除首尾空白后只包含一个 token。不要把原因或 revision prose 写在同一条 token 评论中：

```text
{{one_legal_token_only}}
```

如果选择修订，把具体修改内容另发为绑定本 packet/comment 的 revision brief；它只形成 `decision_context_ref`，不是决定 authority。token 缺失或 token 与说明混写时，需要 fresh token-only comment。

## 最小审计绑定

- Human Action Request ref / version：`{{human_action_request_ref}}` / `{{human_action_request_version}}`
- Packet digest：`{{packet_digest}}`
- Design / Review identity：`{{design_ref}} {{design_version}}` / `{{review_ref}} {{review_version}}`
- Current / superseded：`current`
- Does not authorize：Skill import、Agent binding、资源创建、OpenSpec、branch、commit、代码实施或未列出的 shared-scope write。
- 权威材料：冻结 Markdown 原始字节和 SHA-256；可选预览为 `derived_non_authoritative`

<!-- multica-architecture-approval-adapter:v1 packet_ref={{packet_ref_marker_escaped}} packet_version={{packet_version}} packet_digest={{packet_digest}} -->
