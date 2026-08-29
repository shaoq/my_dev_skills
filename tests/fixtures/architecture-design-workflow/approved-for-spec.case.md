# Approval for target R&D Spec

## Request

ARCH-DESIGN v5 已由 ARCH-REVIEW v5 给出 APPROVABLE，当前 Issue 中的人类决定针对这两个准确版本明确记录为 `approved_for_spec`，目标研发项目和仓库均已确认。请在当前只读测试中生成架构发布与研发交接的待发布目标；目标 R&D Team 自行决定是否创建 OpenSpec，不得声称已经持久化。

## Expected contract

```json expected
{
  "fixture_id": "approved-for-spec",
  "selected": true,
  "stage": "publishing",
  "gate": "approved_for_spec",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "architecture-repo:ADR", "architecture-repo:detailed-design", "issue:ARCH-RD-HANDOFF"],
  "evidence_fields": ["issue", "design_version", "review_version", "approval_evidence", "target_project"],
  "required_markers": ["approved_for_spec", "ARCH-RD-HANDOFF"],
  "forbidden_markers": ["OpenSpec proposal 已创建"]
}
```
