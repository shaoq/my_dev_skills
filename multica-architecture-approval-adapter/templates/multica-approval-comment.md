【需要你确认】 [@{{decision_owner_display_name}}](mention://member/{{decision_owner_member_id}})，请决定是否批准 `{{design_version}}` 进入 {{design_only_or_spec_stage_zh}}。

团队推荐：{{recommendation_zh}}。最关键后果：{{principal_consequence_zh}}。

- 【需要阅读并确认】`{{design_filename}}` — {{stable_design_entry}}
- 【供人参考，无需单独确认】{{light_1440x900_preview_or_archify_link_or_omit}}

回复后立即发生：{{immediate_next_stage_owner_writes_and_blockers_zh}}。

```text
ACTION {{action_id}}: decision={{legal_decision}}
```

Owner-attested：`ACTION {{action_id}}: materials_opened; decision={{legal_decision}}`

打不开：`ACTION {{action_id}}: 材料打不开`；可打开但无法决策：`ACTION {{action_id}}: 材料不可决策; reason=<原因>`。二者均 `content_decision=none`。

<!-- human_review_surface_v2; visible prose <= 600 Unicode code points by default excluding stable links, attachment filenames and the sole Action block. Review/Packet/Control/Research/receipts are agent_internal. Recommendation, access and readiness are not approval. -->
<!-- multica-architecture-approval-adapter:v3 action_id={{action_id_escaped}} design_ref={{design_ref_escaped}} design_version={{design_version}} design_digest={{design_digest}} -->
