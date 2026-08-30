# Approvable review without readiness

## Request

ARCH-REVIEW v6 对 ARCH-DESIGN v6 给出 `APPROVABLE`，并已形成 delivered `ARCH-APPROVAL-PACKET v6`（digest `sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`，recommendation `no_recommendation`），但当前没有绑定 packet digest 的 readiness envelope，access confirmation 为 unconfirmed；unavailable evidence recorded_at 为 `2026-08-30T08:10:00Z`。请计算 canonical stage；不得把 Review conclusion 改写成 BLOCKED。

## Expected contract

```json expected
{
  "fixture_id": "approvable-no-readiness",
  "selected": true,
  "stage": "reviewing",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_unavailable",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v6",
  "packet_digest": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "access_confirmation": "unconfirmed",
  "recommendation": "no_recommendation",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "2026-08-30T08:10:00Z",
  "wait_reason": "none",
  "blocked_reason": "review_packet_unavailable",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_conclusion", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "owner", "closure_condition"],
  "required_markers": ["reviewing", "review_packet_unavailable", "APPROVABLE"],
  "forbidden_markers": ["进入 waiting_human", "Review conclusion=BLOCKED"]
}
```
