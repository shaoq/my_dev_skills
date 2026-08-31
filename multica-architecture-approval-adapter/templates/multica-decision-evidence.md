# Multica human decision evidence

## Record

```text
evidence_type=human_decision_evidence
evidence_profile=shared_workspace_sidecar_v1|multica_issue_task_evidence_v1
evidence_ref={{shared_workspace_sidecar_or_task_control_ref}}
workflow_mandate_ref={{current_workflow_mandate_ref_or_none}}
operation_manifest_ref={{current_operation_manifest_ref_or_none}}
decision_evidence_status=valid|invalid|noop|superseded
binding_profile=current_action_reference_v1|multica_packet_comment_reply_v1|multica_explicit_packet_reference_v1
decision={{approved_design_only|approved_for_spec|revision_requested|rejected|type_specific_current_action_decision}}
issue_ref=multica://issues/{{issue_id}}
decision_comment_id={{decision_comment_id}}
decision_comment_ref=multica://issues/{{issue_id}}/comments/{{decision_comment_id}}
parent_chain_ids={{leaf_to_root_comment_ids}}
parent_chain_authority={{audit_only|packet_binding|explicit_identity}}
author_type=member
author_id={{canonical_target_member_uuid}}
comment_revision={{comment_revision_or_not_provided}}
content_digest=sha256:{{decision_comment_raw_utf8_sha256}}
normalized_content_digest={{sha256_or_not_applicable}}
normalized_platform_mention={{current_architecture_agent_canonical_mention_or_none}}
created_at={{created_at_rfc3339_utc}}
updated_at={{updated_at_rfc3339_utc}}
recorded_at={{recorded_at_rfc3339_utc}}
packet_ref={{packet_ref}}
packet_version={{packet_version}}
packet_digest={{packet_digest}}
packet_comment_ref=multica://issues/{{issue_id}}/comments/{{verified_packet_comment_id}}
action_id={{current_action_id_or_none}}
action_version={{current_action_version_or_none}}
action_digest={{current_action_digest_or_none}}
action_request_comment_ref={{current_action_request_comment_ref_or_none}}
action_identity_status={{current_unique|missing|ambiguous|superseded|not_applicable}}
human_actor_binding_ref={{rereadable_packet_bound_mapping_evidence_ref}}
readiness_evidence_ref={{current_readiness_sidecar_ref_or_none}}
readiness_reread_status={{verified|missing|changed}}
comment_reread_status={{verified|missing|changed}}
mapping_reread_status={{verified|missing|changed|ambiguous}}
explicit_packet_identity={{inherited|exact_current|none}}
replacement_order=({{created_at_rfc3339_utc}},{{decision_comment_id}})
human_action_request_ref={{current_human_action_request_ref}}
human_action_request_version={{current_human_action_request_version}}
human_action_rendering_status={{current|superseded|missing}}
decision_context_ref={{separate_packet_bound_revision_brief_ref_or_none}}
decision_context_digest={{sha256_or_none}}
decision_context_profile={{multica_revision_context_v1|none}}
revision_brief_ref={{stable_revision_brief_ref_or_none}}
revision_brief_digest={{sha256_or_none}}
decision_context_reread_status={{verified|missing|changed|not_applicable}}
decision_context_author_id={{canonical_target_member_uuid_or_none}}
revision_scope={{provided|missing|changed|not_applicable}}
context_authority=non_authoritative_context
fresh_token_required={{yes|no}}
```

## Consumption result

```text
effective_for_current_action_or_packet={{yes|no}}
supersedes_comment_ref={{prior_same_actor_ref_or_none}}
superseded_by_comment_ref={{later_same_actor_ref_or_none}}
waiting_human_reason={{none|mapping_conflict|evidence_invalidated|fresh_decision_required}}
closing_condition={{none|re-read exact current readiness and submit one new independent legal decision}}
```

`decision_context_ref` 永远与 token authority 分离。只有 exact token-only candidate 能进入 binding parser；token 与 prose 混写时记录 `decision_evidence_status=invalid`、`context_authority=non_authoritative_context`、`fresh_token_required=yes`，保留原评论供审计并要求新的独立 token-only 评论。有效 `revision_requested` 没有可重读 context 时保持决定有效并记录 `revision_scope=missing`；context changed 只触发 core follow-up，不改写或撤销已验证 token evidence。

The record is not proof by itself. Before every consumption, re-read the selected current request/readiness、target-human binding and decision comment; revision or raw/normalized digest drift invalidates captured evidence. Formal packet decisions become effective only after `shared_workspace_sidecar_v1` no-clobber write/reread; `design_input|architecture_review` current Action decisions use manifest-bound `multica_issue_task_evidence_v1` candidate/status/task/ARCH-CONTROL rereads. Neither path requests an operational token. A valid decision for a superseded Action/packet is retained with `decision_evidence_status=noop` and never advances the current gate. See [durable evidence records](../references/durable-evidence-records.md).
