# Publication digest mismatch fails closed

## Request

当前 ready packet `ARCH-APPROVAL-PACKET v15`（digest `sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`，recommendation `recommend_approved_for_spec`，shared workspace access 已确认）已由人类准确记录 `approved_for_spec`，evidence recorded_at 为 `2026-08-30T08:50:00Z`，workflow 位于 publishing。发布前重新读取 ARCH-DESIGN bytes 时发现 digest 与 packet 冻结值不同。不得从决策简报重建近似正文，也不得改写批准或 readiness。

## Expected contract

```json expected
{
  "fixture_id": "publication-digest-mismatch",
  "selected": true,
  "stage": "publishing",
  "gate": "approved_for_spec",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v15",
  "packet_digest": "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_for_spec",
  "human_decision": "approved_for_spec",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T08:50:00Z",
  "wait_reason": "none",
  "blocked_reason": "approved_artifact_unavailable",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["packet_version", "packet_digest", "packet_readiness", "human_decision", "findings", "owner", "closure_condition"],
  "required_markers": ["publishing", "approved_artifact_unavailable", "digest mismatch"],
  "forbidden_markers": ["已从决策简报重建", "approval 已撤销", "review_packet_ready 已撤销"]
}
```
