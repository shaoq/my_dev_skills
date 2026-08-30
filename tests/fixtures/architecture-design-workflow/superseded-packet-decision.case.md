# Superseded packet decision is a no-op

## Request

当前 ready packet 是 `ARCH-APPROVAL-PACKET v11`，digest 为 `sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`，recommendation 为 `recommend_approved_for_spec`，shared workspace access 已确认。当前人类消息中的 `approved_for_spec` 明确绑定已被取代的 v10，而不是 v11，evidence recorded_at 为 `2026-08-30T08:35:00Z`。保留该决定用于审计，但不要改变当前 gate。

## Expected contract

```json expected
{
  "fixture_id": "superseded-packet-decision",
  "selected": true,
  "stage": "waiting_human",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v11",
  "packet_digest": "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_for_spec",
  "human_decision": "approved_for_spec",
  "decision_evidence_status": "noop",
  "evidence_recorded_at": "2026-08-30T08:35:00Z",
  "wait_reason": "design_approval",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["packet_version", "packet_digest", "packet_readiness", "human_decision", "decision_evidence"],
  "required_markers": ["v10", "v11", "no-op", "waiting_human"],
  "forbidden_markers": ["进入 publishing", "ARCH-RD-HANDOFF"]
}
```
