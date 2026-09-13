【需要你确认】 [@{{decision_owner_display_name}}](mention://member/{{decision_owner_member_id}})，请决定：{{atomic_decision_zh}}

团队推荐：{{recommendation_zh_or_no_recommendation}}。最关键后果：{{principal_consequence_zh}}。

- 【需要阅读并确认】{{required_material_filename}} — {{stable_required_material_entry}}
- 【供人参考，无需单独确认】{{optional_archify_or_pdf_resource_or_omit}} — {{stable_reference_entry_or_omit}}

回复后立即发生：{{immediate_next_stage_owner_writes_and_blockers_zh}}。

```text
ACTION {{action_id}}: {{type_specific_decision}}
```

Owner-attested 正式批准使用：`ACTION {{action_id}}: materials_opened; decision={{approved_design_only_or_approved_for_spec_or_revision_requested_or_rejected}}`

打不开：`ACTION {{action_id}}: 材料打不开`

可打开但无法决策：`ACTION {{action_id}}: 材料不可决策; reason=<原因>`

<!-- human_review_surface_v2; visible prose default <= 600 Unicode code points excluding stable links, attachment filenames and the sole Action code block. Exactly one required entry. Entry fields: audience=human|agent; review_requirement=required|reference_only|none; bound_action={{action_id}}|none. Formal approval requires canonical ARCH-DESIGN-vN.md; pre-Design uses one explicitly non-canonical action-bound decision-detail attachment. Research/Control/complete Review/Packet/receipt/continuation/handoff are architecture_internal_evidence_v1 and must not be copied here. -->
