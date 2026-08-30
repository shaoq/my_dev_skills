# Reviewer revision creates no packet

## Request

Reviewer 对 ARCH-DESIGN v14 给出 `NEEDS_REVISION`。当前尚无 approval packet。请返回 designing 并保留 review trail；不得为非 approvable design 创建 packet。

## Expected contract

```json expected
{
  "fixture_id": "reviewer-needs-revision",
  "selected": true,
  "stage": "designing",
  "gate": "NEEDS_REVISION",
  "review_conclusion": "NEEDS_REVISION",
  "packet_readiness": "none",
  "packet_ref": "none",
  "packet_version": "none",
  "packet_digest": "none",
  "access_confirmation": "none",
  "recommendation": "none",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "none",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-REVIEW", "issue:ARCH-CONTROL", "issue:ARCH-DESIGN"],
  "evidence_fields": ["design_version", "review_version", "review_conclusion", "next_action"],
  "required_markers": ["NEEDS_REVISION", "designing"],
  "forbidden_markers": ["ARCH-APPROVAL-PACKET", "review_packet_ready"]
}
```
