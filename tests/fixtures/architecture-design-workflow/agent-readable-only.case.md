# Agent readability is not human access

## Request

Agent 进程可以打开本机绝对路径下的 design、review 和 `ARCH-APPROVAL-PACKET v8`（digest `sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`，recommendation `no_recommendation`），但当前人类没有确认 shared workspace scope，也没有 access confirmation evidence。Review conclusion 是 APPROVABLE；unavailable evidence recorded_at 为 `2026-08-30T08:20:00Z`。不得仅凭进程读取成功进入人工门禁。

## Expected contract

```json expected
{
  "fixture_id": "agent-readable-only",
  "selected": true,
  "stage": "reviewing",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_unavailable",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v8",
  "packet_digest": "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "access_confirmation": "unconfirmed",
  "recommendation": "no_recommendation",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "2026-08-30T08:20:00Z",
  "wait_reason": "none",
  "blocked_reason": "review_packet_unavailable",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_conclusion", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "owner", "closure_condition"],
  "required_markers": ["reviewing", "access confirmation", "review_packet_unavailable"],
  "forbidden_markers": ["stage=waiting_human"]
}
```
