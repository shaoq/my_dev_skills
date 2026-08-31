[@{{decision_owner_display_name}}](mention://member/{{decision_owner_member_id}})，请处理下面唯一一项当前动作。

# Multica Human Action Request

该 mention 必须由已验证的 canonical member UUID 渲染。

## Architecture Decision Brief

## 当前方案摘要

{{one_paragraph_solution_summary_zh}}

## 简化架构图

```text
{{simplified_architecture_diagram}}
```

## Architecture Team 总体建议

- 总体建议：`{{team_recommendation_or_no_recommendation}}`
- 推荐理由：{{team_recommendation_rationale_zh}}
- 置信度：`{{confidence_high_medium_low}}`；依据与可能改变建议的证据：{{confidence_basis_zh}}

## 已确定与尚未确定

- 已确定：{{determined_zh}}
- 尚未确定：{{undetermined_zh}}
- Other-owner dependencies (non-actionable)：

| Action / dependency | Owner / authority scope | 对当前方案的影响 | Closure condition |
|---|---|---|---|
| {{dependency_action}} | {{dependency_owner_scope}} | {{dependency_impact_zh}} | {{dependency_closure_zh}} |

这些依赖没有当前读者可执行的回复表单，不能通过本评论代替其他 Owner 关闭。

## 最重要的备选及后果

| Option | 含义 | 收益 | 代价 / material risks | 不可逆影响 |
|---|---|---|---|---|
| {{option}} | {{meaning_zh}} | {{benefits_zh}} | {{costs_and_risks_zh}} | {{irreversible_effect_or_none}} |

## 当前读者的一项决定

- Action ID：`{{action_id}}`
- `action_type={{action_type}}`；只允许 `design_input|architecture_review|architecture_approval`。
- `requires_human_review=true`
- Human Action State：`{{none_preparing_awaiting_response_received_unavailable_superseded}}`
- Issue status：交付验证通过并等待你回复时为 `in_review`；你的准确 current 回复启动后续 Agent 工作时为 `in_progress`。这两个状态不改变 architecture stage。
- Current / superseded：`{{current_or_superseded}}`
- Why now：{{why_now_zh}}
- Decision Owner：`{{decision_owner_member_id}}`（{{decision_owner_display_name}}）
- Authority scope：{{authority_scope_zh}}
- Current reader / authority binding：`{{unique_unbound_ambiguous}}` / `{{binding_evidence_ref}}`
- Content-decision activation gate：`{{ready_or_not_ready}}`；未全部验证时不发布本评论的可执行版本，由 workflow mandate 自动补齐验证或记录 evidence gap。
- 一句话决定：{{atomic_decision_zh}}
- Candidate recommendation：`{{candidate_recommendation_or_no_recommendation}}`
- Bounded alternatives / Option consequences：见上一节。

## 回复后会发生什么

| Response | Next stage / remaining blockers / Next Owner / planned writes | 新对象或版本 | 不可逆影响 |
|---|---|---|---|
| {{response}} | {{after_response_projection}} | {{new_object_or_version}} | {{irreversible_effect_or_none}} |

## 完整材料入口

- Stable human-accessible evidence refs：
  - Design canonical attachment：`{{design_attachment_filename}}` / `{{design_attachment_digest}}` / {{design_attachment_card_or_stable_entry}}
  - Design reading copy：{{design_pdf_or_na}}；`derived_non_authoritative={{true_or_na}}`
  - Research：{{research_human_access_entry}}
  - Control：{{control_human_access_entry}}
  - Review / Packet（仅当前 gate 需要时）：{{review_packet_entries_or_na}}
- Requested client scopes：`desktop`（Web）/ `mobile`
- Access status by scope：`opened|unavailable|not_run`
- Primary action：每个材料入口必须打开 browser-rendered preview；`download-only`、raw-byte fetch、HTTP 200 或文件已保存不等于 `opened`。下载仅作为预览框内的次要动作。

| Material | Scope | Status | Exact identity / complete content | Verifier / verification time | Evidence / closure condition |
|---|---|---|---|---|---|
| {{material}} | {{desktop_or_mobile}} | {{access_status}} | {{identity_and_content_status}} | {{verifier_and_time}} | {{evidence_or_closure}} |

- Missing evidence / Owner / closure condition：{{missing_evidence_owner_closure_zh}}

## Exact response

仅当 Current reader binding=`unique`、`requires_human_review=true` 且 Content-decision activation gate=`ready` 时渲染内容决定回复。否则不得生成 actionable Review comment；只在 task evidence 记录缺失证据与恢复路径，不生成 operational、access confirmation 或 routing token。

请复制一种合法回复，不要把解释文字混入要求 token-only 的回复：

```text
{{type_specific_exact_response}}
```

Revision context 使用 `context_profile=multica_revision_context_v1` 的固定 7 行语法，必须从 current refs 生成，不得自由改写字段顺序。材料访问由 Adapter 自动验证，不要求用户提交 access-confirmation payload。

## 权限边界

- Authorizes：{{authorized_effect_zh}}
- Does not authorize：{{excluded_effects_zh}}
- 非权威上下文：recommendation、访问 evidence、说明文字和 revision brief 不替代正式决定或其他 canonical evidence。

## 最小审计绑定

- Bound packet / routing / risk：`{{bound_identity}}`
- Multica Issue / comment ref：`{{issue_ref}}` / `{{comment_ref_or_pending}}`
- Current / superseded：`{{current_or_superseded}}`
- Human Action Request ref / version：`{{human_action_request_ref}}` / `{{human_action_request_version}}`
