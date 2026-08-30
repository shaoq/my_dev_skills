# Packet digest mismatch fails closed

## Request

ARCH-REVIEW v9 的结论为 APPROVABLE，目标人类已确认访问 `ARCH-APPROVAL-PACKET v9`；readiness envelope 冻结 digest 为 `sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`，recommendation 为 `recommend_revision`，但 verifier 重算 delivered packet 原始字节所得 digest 不同。unavailable evidence recorded_at 为 `2026-08-30T08:25:00Z`。请保留真实 Review conclusion 并报告关闭条件。

## Expected contract

```json expected
{
  "fixture_id": "packet-digest-mismatch",
  "selected": true,
  "stage": "reviewing",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_unavailable",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v9",
  "packet_digest": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_revision",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "2026-08-30T08:25:00Z",
  "wait_reason": "none",
  "blocked_reason": "review_packet_unavailable",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_conclusion", "packet_version", "packet_digest", "packet_readiness", "findings", "owner", "closure_condition"],
  "required_markers": ["digest mismatch", "review_packet_unavailable", "APPROVABLE"],
  "forbidden_markers": ["Review conclusion=BLOCKED", "stage=waiting_human"]
}
```
