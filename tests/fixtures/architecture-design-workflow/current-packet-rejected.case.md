# Current packet rejection

## Request

Review conclusion 为 `APPROVABLE`。当前人类以 user-role 消息明确针对 ready packet `ARCH-APPROVAL-PACKET v13`（digest `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，recommendation `no_recommendation`）记录 `rejected`，shared workspace access 已确认，evidence recorded_at 为 `2026-08-30T08:45:00Z`。不得发布 ADR、详细设计或研发交接。

## Expected contract

```json expected
{
  "fixture_id": "current-packet-rejected",
  "selected": true,
  "stage": "rejected",
  "gate": "rejected",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v13",
  "packet_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "access_confirmation": "confirmed",
  "recommendation": "no_recommendation",
  "human_decision": "rejected",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T08:45:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["packet_version", "packet_digest", "packet_readiness", "human_decision", "decision_evidence"],
  "required_markers": ["rejected", "ARCH-APPROVAL-PACKET v13"],
  "forbidden_markers": ["architecture-repo:ADR", "ARCH-RD-HANDOFF", "publishing"]
}
```
