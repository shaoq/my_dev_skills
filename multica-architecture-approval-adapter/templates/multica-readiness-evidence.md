# Multica review packet readiness evidence

## Envelope identity

```text
evidence_type=review_packet_ready|review_packet_unavailable
platform_profile=multica_attachment_v1
evidence_profile=shared_workspace_sidecar_v1
evidence_ref={{shared_workspace_sidecar_ref_or_none}}
capability_profile={{capability_profile}}
adapter_marker_profile=multica-architecture-approval-adapter:v1
reconciliation_outcome={{reconciliation_outcome}}
delivery_state=absent|delivering|delivered_unverified|ready|unavailable
delivery_attempt_id={{delivery_attempt_id}}
delivery_evidence_ref={{deterministic_comment_fragment_or_none}}
fence_outcome=current|stale|identity_conflict|marker_author_conflict
verifier={{verifier}}
verified_at={{verified_at_rfc3339_utc}}
```

`review_packet_unavailable` 必须保留真实 `review_conclusion`、已存在的评论/附件 refs、失败检查、Owner 与可观察 closing condition；不得改写 frozen packet 或删除平台对象。

## Portable current-packet binding

```text
core_revision={{pinned_core_revision}}
packet_ref={{packet_ref}}
packet_version={{packet_version}}
packet_digest={{packet_digest}}
design_ref={{design_ref}}
design_version={{design_version}}
design_digest={{design_digest}}
review_ref={{review_ref}}
review_version={{review_version}}
review_digest={{review_digest}}
review_conclusion={{real_review_conclusion}}
architecture_recommendation={{architecture_recommendation}}
```

## Target human and availability

```text
human_actor={{canonical_multica_member_uuid}}
human_actor_binding_ref={{packet_bound_mapping_evidence_ref}}
workspace_scope=multica_workspace:{{workspace_id}}
issue_ref=multica://issues/{{issue_id}}
target_member_issue_scope={{confirmed|unconfirmed}}
target_member_durable_access={{confirmed|unconfirmed}}
```

## Exact packet-comment delivery

```text
packet_comment_id={{actual_packet_comment_id_or_none}}
packet_comment_ref={{actual_packet_comment_ref_or_none}}
packet_comment_parent_id={{actual_trigger_comment_id_or_none}}
packet_comment_author_type={{adapter_author_type}}
packet_comment_author_id={{adapter_author_id}}
packet_marker_ref={{packet_ref}}
packet_marker_version={{packet_version}}
packet_marker_digest={{packet_digest}}
delivery_evidence_ref={{deterministic_comment_fragment_or_none}}
comment_reread_status={{verified|missing|identity_conflict}}
brief_reread_status={{verified|missing|identity_conflict}}
human_action_request_ref={{current_human_action_request_ref_or_none}}
human_action_request_version={{current_human_action_request_version_or_none}}
brief_rendering_status={{verified|missing|superseded|incomplete}}
```

## Required durable artifacts

Repeat this block once each for `design`, `review`, and `packet`; a ready envelope contains exactly three blocks.

```text
artifact_kind={{design|review|packet}}
artifact_ref=multica://issues/{{issue_id}}/comments/{{packet_comment_id}}/attachments/{{attachment_id}}
attachment_id={{attachment_id}}
media_type={{media_type}}
expected_digest={{frozen_sha256}}
verified_digest={{redownloaded_raw_byte_sha256}}
stable_access_ref={{browser_rendered_preview_entry}}
availability_scope=multica_workspace:{{workspace_id}}/issue:{{issue_id}}
attachment_bound_to_comment={{verified|missing|identity_conflict}}
raw_byte_reread_status={{verified|missing|digest_mismatch}}
design_access_confirmation={{desktop:opened|unavailable|unconfirmed;mobile:opened|unavailable|unconfirmed}}
review_access_confirmation={{desktop:opened|unavailable|unconfirmed;mobile:opened|unavailable|unconfirmed}}
packet_access_confirmation={{desktop:opened|unavailable|unconfirmed;mobile:opened|unavailable|unconfirmed}}
```

三个 access confirmation 字段按相应 `artifact_kind` 使用：每个 artifact、每个请求的 client scope 单独记录 canonical target member 的 `opened|unavailable|unconfirmed`。通用“可以访问”、附件卡片存在、Agent 下载或只完成 desktop 都不能把 mobile 或其他 artifact 记为 confirmed。

Never persist a signed or expiring `download_url`. `stable_access_ref` identifies the platform-rendered preview action backed by the stable attachment identity; a `markdown_url` or stable endpoint is only its identity input, not human-access evidence by itself. Each `opened` value requires actual UI activation and complete rendered content. Raw-byte re-download may obtain a fresh transient URL at read time but never upgrades `download-only` to `opened`.

## Projection and closing record

```text
metadata_key=arch.packet.current
metadata_projection={{exact_read_back_value_or_none}}
metadata_readback={{verified|failed|identity_conflict}}
projection_evidence_ref={{deterministic_comment_fragment_or_none}}
final_marker_scan={{current|stale|identity_conflict|marker_author_conflict|canonical_changed}}
failed_checks={{ordered_names_or_none}}
owner={{owner_or_none}}
closing_condition={{observable_condition_or_none}}
```

`evidence_ref` is the sidecar's own rereadable `workspace://...` ref. It is non-`none` only after an explicitly authorized shared-workspace sidecar write and reread, and a ready envelope requires it. If no such durable scope exists, emit unavailable with `evidence_ref=none`; a delivery-comment fragment never substitutes. `packet_comment_id` and `packet_comment_ref` are actual values only when an actual packet comment exists; for core absence, preflight failure, or no packet comment, both are literal `none`. Never construct a `comments/none` URL. Only after the packet comment has been successfully re-read and its marker, adapter author, and required attachment bindings verify may `delivery_evidence_ref` contain `multica://issues/<issue-id>/comments/<packet-comment-id>#adapter-delivery-evidence-v1`; for core absence, preflight failure, no packet comment, or any such reread failure it is the literal `none`. `projection_evidence_ref` is that same value only when the projection was actually written and read back; otherwise it is the literal `none`. These refs identify only pre-existing comment evidence, not readiness itself. See [durable evidence records](../references/durable-evidence-records.md). This envelope is external evidence bound by packet ref/version/digest. It must never be inserted into, or used to rewrite, the frozen `ARCH-APPROVAL-PACKET`.
