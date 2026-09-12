[@{{decision_owner_display_name}}](mention://member/{{decision_owner_member_id}})，请处理下面唯一一项当前动作。

# Multica Human Action Request

## Architecture Decision Brief

## 当前方案摘要

{{one_paragraph_solution_summary_zh}}

- Design maturity：`{{directional_or_spec_ready_or_implementation_ready}}`
- Reviewer conclusion / concise findings：`{{review_conclusion_or_not_applicable}}` / {{concise_findings_or_none_zh}}
- 关键风险 / accepted warnings：{{critical_risks_or_none_zh}}
- Recommendation / rationale / confidence：`{{recommendation}}` / {{rationale_zh}} / `{{confidence}}`

## 简化架构图

{{inline_or_linked_light_1440x900_preview_or_not_applicable}}

图是 `derived_non_authoritative`；Design 正文解释图的结论。交互 HTML 不是必读入口。

## 最重要的备选及后果

| Option | 含义 | 收益 | 代价 / material risks | 不可逆影响 |
|---|---|---|---|---|
| {{option}} | {{meaning_zh}} | {{benefits_zh}} | {{costs_and_risks_zh}} | {{irreversible_effect_or_none}} |

## 当前读者的一项决定

- Action ID / type：`{{action_id}}` / `design_input|architecture_review|architecture_approval`
- `requires_human_review=true`
- Human Action State：`{{none_preparing_awaiting_response_received_unavailable_superseded}}`
- Why now：{{why_now_zh}}
- Decision Owner / authority scope：`{{decision_owner_member_id}}` / {{authority_scope_zh}}
- Current reader binding：`{{unique_unbound_ambiguous}}`
- Access verification mode / state：`{{automatic_owner_manual_owner_attested}}` / `opened|manual_check_required|unavailable|not_run`
- 一句话决定：{{atomic_decision_zh}}

## 回复后会发生什么

| Response | Next stage / blockers / Next Owner / planned writes | 新对象或版本 | 不可逆影响 |
|---|---|---|---|
| {{response}} | {{projection}} | {{new_object_or_version}} | {{irreversible_effect_or_none}} |

## 一份完整材料入口

- 恰好一份 canonical Design Markdown attachment：`{{design_filename}}` / `{{design_digest}}`
- Stable Design entry：{{stable_design_entry}}
- Required preview：{{preview_ref_or_not_applicable}}；capture=`light/1440x900`
- Requested scopes：`desktop|mobile`
- Access evidence：{{per_scope_access_evidence}}

Research、Control、完整 Review、machine-only Packet、digests、task result、continuation/handoff 和 reconciliation 属于 `architecture_internal_evidence_v1`，无需当前读者打开。

## Exact response

只有 current Action、唯一 Owner 和 selected access gate 均 ready 时展示。新 writer 使用 `current_action_reference_v1`，不要求定位 parent/thread 或复制 packet digest。

```text
ACTION {{action_id}}: {{type_specific_decision}}
```

Owner-attested architecture approval：

```text
ACTION {{action_id}}: materials_opened; decision={{approved_design_only_or_approved_for_spec_or_revision_requested_or_rejected}}
```

材料打不开时：

```text
ACTION {{action_id}}: 材料打不开
```

该回复仅触发 material repair，`content_decision=none`。

## Authority boundary

- Authorizes：{{authorized_effect_zh}}
- Does not authorize：资源创建、Skill activation、OpenSpec、branch、commit、代码、部署或其他 Owner 的决定。
- Recommendation、Review conclusion、access evidence、status 和内部 readiness 均不构成批准。

## Minimal audit binding

- Human surface：`human_review_surface_v1`
- Internal surface：`architecture_internal_evidence_v1`
- Current / superseded：`{{current_or_superseded}}`
- Action / Design snapshot：`{{action_id}}` / `{{design_ref_and_version}}`
