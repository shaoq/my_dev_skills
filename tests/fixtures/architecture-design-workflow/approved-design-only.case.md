# Design-only approval

## Request

ARCH-DESIGN v4 与 ARCH-REVIEW v4 已冻结为当前 ready packet `ARCH-APPROVAL-PACKET v4`（digest `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，recommendation `recommend_approved_design_only`），shared workspace access 已由当前人类确认。当前 user-role 决定明确绑定该 packet ref/version/digest 并记录为 `approved_design_only`，evidence recorded_at 为 `2026-08-30T08:00:00Z`。请在当前只读测试中生成待发布目标；不得创建研发交接或 OpenSpec，也不得声称已经持久化。

## Expected contract

```json expected
{
  "fixture_id": "approved-design-only",
  "selected": true,
  "stage": "publishing",
  "gate": "approved_design_only",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v4",
  "packet_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_design_only",
  "human_decision": "approved_design_only",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T08:00:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "architecture-repo:ADR", "architecture-repo:detailed-design"],
  "evidence_fields": ["issue", "design_version", "review_version", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "human_decision", "decision_evidence"],
  "required_markers": ["approved_design_only", "publishing"],
  "forbidden_markers": ["已生成 ARCH-RD-HANDOFF", "OpenSpec proposal 已创建"]
}
```
