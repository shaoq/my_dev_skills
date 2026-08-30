# Multica human decision evidence

## Record

```text
evidence_type=human_decision_evidence
evidence_profile=shared_workspace_sidecar_v1
evidence_ref={{shared_workspace_sidecar_ref_or_none}}
shared_scope_write_authorization={{explicit_current_task_authorization_or_none}}
decision_evidence_status=valid|invalid|noop|superseded
binding_profile=multica_packet_comment_reply_v1|multica_explicit_packet_reference_v1
decision={{approved_design_only|approved_for_spec|revision_requested|rejected}}
issue_ref=multica://issues/{{issue_id}}
decision_comment_id={{decision_comment_id}}
decision_comment_ref=multica://issues/{{issue_id}}/comments/{{decision_comment_id}}
parent_chain_ids={{leaf_to_root_comment_ids}}
author_type=member
author_id={{canonical_target_member_uuid}}
comment_revision={{comment_revision_or_not_provided}}
content_digest=sha256:{{decision_comment_raw_utf8_sha256}}
created_at={{created_at_rfc3339_utc}}
updated_at={{updated_at_rfc3339_utc}}
recorded_at={{recorded_at_rfc3339_utc}}
packet_ref={{packet_ref}}
packet_version={{packet_version}}
packet_digest={{packet_digest}}
packet_comment_ref=multica://issues/{{issue_id}}/comments/{{verified_packet_comment_id}}
human_actor_binding_ref={{rereadable_packet_bound_mapping_evidence_ref}}
readiness_evidence_ref={{current_readiness_sidecar_ref_or_none}}
readiness_reread_status={{verified|missing|changed}}
comment_reread_status={{verified|missing|changed}}
mapping_reread_status={{verified|missing|changed|ambiguous}}
explicit_packet_identity={{inherited|exact_current|none}}
replacement_order=({{created_at_rfc3339_utc}},{{decision_comment_id}})
```

## Consumption result

```text
effective_for_current_packet={{yes|no}}
supersedes_comment_ref={{prior_same_actor_ref_or_none}}
superseded_by_comment_ref={{later_same_actor_ref_or_none}}
waiting_human_reason={{none|mapping_conflict|evidence_invalidated|fresh_decision_required}}
closing_condition={{none|re-read exact current readiness and submit one new independent legal decision}}
```

The record is not proof by itself. Before every consumption, re-read current readiness, its target-human mapping, the packet comment/attachments, and the decision comment; any revision or raw UTF-8 content-digest drift invalidates captured evidence. The platform-read-only decision route never writes Multica. This record becomes effective only after its own `shared_workspace_sidecar_v1` write/reread under a separately explicit current-task shared-scope authorization; without it, keep the candidate as audit text and do not consume it. A valid decision for a superseded packet is retained with `decision_evidence_status=noop` and never advances the current gate. See [durable evidence records](../references/durable-evidence-records.md).
