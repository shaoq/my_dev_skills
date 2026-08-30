# Current packet revision request

## Request

Review conclusion 为 `APPROVABLE`。当前人类以 user-role 消息明确针对 ready packet `ARCH-APPROVAL-PACKET v12`（digest `sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`，recommendation `recommend_revision`）记录 `revision_requested`，shared workspace access 已确认，evidence recorded_at 为 `2026-08-30T08:40:00Z`。请开始新设计迭代，保留旧 packet bytes/digest，并且在替代设计重新获得 approvable review 前不要创建新 packet。

## Expected contract

```json expected
{
  "fixture_id": "current-packet-revision-requested",
  "selected": true,
  "stage": "designing",
  "gate": "revision_requested",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v12",
  "packet_digest": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_revision",
  "human_decision": "revision_requested",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T08:40:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "issue:ARCH-DESIGN"],
  "evidence_fields": ["packet_version", "packet_digest", "packet_readiness", "human_decision", "decision_evidence", "next_action"],
  "required_markers": ["revision_requested", "designing", "保留"],
  "forbidden_markers": ["新 ARCH-APPROVAL-PACKET 已创建", "旧 packet 已改写"]
}
```
