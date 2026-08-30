# Historical waiting-human explicit refresh

## Request

这是升级前持久化为 `waiting_human` 的记录，现在已显式 refresh，并产生新的 ARCH-DESIGN v16、APPROVABLE ARCH-REVIEW v16 与 delivered `ARCH-APPROVAL-PACKET v16`（digest `sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`，recommendation `no_recommendation`），但 access confirmation 为 unconfirmed，尚无绑定 current packet digest 的 readiness envelope；unavailable evidence recorded_at 为 `2026-08-30T09:00:00Z`。显式 refresh 后必须执行当前 packet gate，不能继续沿用历史豁免。

## Expected contract

```json expected
{
  "fixture_id": "historical-waiting-human-refreshed",
  "selected": true,
  "stage": "reviewing",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_unavailable",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v16",
  "packet_digest": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "access_confirmation": "unconfirmed",
  "recommendation": "no_recommendation",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "2026-08-30T09:00:00Z",
  "wait_reason": "none",
  "blocked_reason": "review_packet_unavailable",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_conclusion", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "owner", "closure_condition"],
  "required_markers": ["显式 refresh", "reviewing", "review_packet_unavailable"],
  "forbidden_markers": ["stage=waiting_human"]
}
```
