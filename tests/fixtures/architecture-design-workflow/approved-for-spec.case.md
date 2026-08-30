# Approval for target R&D Spec

## Request

ARCH-DESIGN v5 与 ARCH-REVIEW v5 已冻结为当前 ready packet `ARCH-APPROVAL-PACKET v5`（digest `sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`，recommendation `recommend_approved_for_spec`），shared workspace access 已由当前人类确认。当前 user-role 决定明确绑定该 packet ref/version/digest 并记录为 `approved_for_spec`，evidence recorded_at 为 `2026-08-30T08:05:00Z`，目标研发项目和仓库均已确认。请在当前只读测试中生成架构发布与研发交接的待发布目标；目标 R&D Team 自行决定是否创建 OpenSpec，不得声称已经持久化。

## Expected contract

```json expected
{
  "fixture_id": "approved-for-spec",
  "selected": true,
  "stage": "publishing",
  "gate": "approved_for_spec",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v5",
  "packet_digest": "sha256:2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_for_spec",
  "human_decision": "approved_for_spec",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T08:05:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "architecture-repo:ADR", "architecture-repo:detailed-design", "issue:ARCH-RD-HANDOFF"],
  "evidence_fields": ["issue", "design_version", "review_version", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "human_decision", "decision_evidence", "target_project"],
  "required_markers": ["approved_for_spec", "ARCH-RD-HANDOFF"],
  "forbidden_markers": ["OpenSpec proposal 已创建"]
}
```
