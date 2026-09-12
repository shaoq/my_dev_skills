# Multica architecture readiness evidence

```text
evidence_type=review_packet_ready|review_packet_unavailable
human_surface_contract=human_review_surface_v1
internal_evidence_contract=architecture_internal_evidence_v1
bundle_contract=multica_human_action_material_bundle_v2
evidence_profile=shared_workspace_sidecar_v1|multica_issue_task_evidence_v1
access_verification_mode=automatic|owner_attested
delivery_state=absent|delivering|delivered_unverified|ready|unavailable
attempt_id={{attempt_id}}
action_id={{current_action_id}}
design_maturity=directional|spec_ready|implementation_ready
review_conclusion={{review_conclusion}}
verifier={{verifier}}
verified_at={{rfc3339_utc}}
```

## Canonical human material — exactly one block

```text
artifact_kind=design
authority=human_canonical
attachment_ref={{design_attachment_ref}}
stable_access_ref={{stable_design_entry}}
expected_digest={{design_digest}}
verified_digest={{verified_design_digest}}
target_member={{canonical_member_uuid}}
desktop_access=opened|manual_check_required|unavailable|not_run
mobile_access=opened|manual_check_required|unavailable|not_run
```

## Required visual projection

```text
diagram_requirement=required|diagram_not_applicable
visual_manifest_ref={{architecture_visual_manifest_v1_ref_or_none}}
deliver=passed|failed|skipped|not_applicable
browser_evidence=passed|failed|skipped|not_applicable
visual_review=passed|failed|skipped|not_applicable
semantic_findings=closed|open|not_applicable
preview_capture=light/1440x900|none
preview_ref={{stable_platform_preview_ref_or_none}}
preview_expected_digest={{digest_or_none}}
preview_verified_digest={{digest_or_none}}
preview_desktop_access=opened|manual_check_required|unavailable|not_run
preview_mobile_access=opened|manual_check_required|unavailable|not_run
authority=derived_non_authoritative
```

Required visual 只有 deliver、browser、visual review 全部 `passed`、semantic findings=`closed`、preview 来自同一 current receipt 且 digest/client readability 通过时才 ready。`failed|skipped`、stale 或 mismatch 一律 unavailable。

## Internal evidence

```text
review_ref/digest={{internal_review_identity}}
packet_ref/digest={{machine_only_manifest_identity}}
research_ref/digest={{internal_research_identity}}
control_ref/digest={{internal_control_identity}}
task_result_ref={{task_result_ref}}
continuation_handoff_ref={{internal_handoff_ref}}
projection_reconciliation_ref={{projection_reconciliation_ref}}
supersession_state=current|superseded
```

Internal artifacts 不要求 human rendering。ready 还要求唯一 Owner/current Action、comment marker、exactly one Design attachment、selected access mode、status/projection 和 supersession 全部回读一致。`directional + approved_for_spec` 必须 fail closed。

## Legacy

旧 readiness 的 design/review/packet 三 block 只读审计，不可被 v2 writer 复用或改写。
