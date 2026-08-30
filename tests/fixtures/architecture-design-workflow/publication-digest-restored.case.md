# Publication resumes after exact bytes are restored

## Request

publishing 阶段此前因 approved_artifact_unavailable 停止。现在 packet、design、review refs 再次返回与冻结 digest 完全匹配的原始 bytes；原 ready `ARCH-APPROVAL-PACKET v15`（digest `sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`，recommendation `recommend_approved_for_spec`，shared workspace access 已确认）和 approved_for_spec 决定保持有效，evidence recorded_at 为 `2026-08-30T08:55:00Z`。请清除 blocker 并恢复待发布目标。

## Expected contract

```json expected
{
  "fixture_id": "publication-digest-restored",
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
  "evidence_recorded_at": "2026-08-30T08:55:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "architecture-repo:ADR", "architecture-repo:detailed-design", "issue:ARCH-RD-HANDOFF"],
  "evidence_fields": ["packet_version", "packet_digest", "packet_readiness", "human_decision", "decision_evidence", "next_action"],
  "required_markers": ["publishing", "approved_artifact_unavailable 已清除", "approved_for_spec"],
  "forbidden_markers": ["新 packet", "新批准"]
}
```
