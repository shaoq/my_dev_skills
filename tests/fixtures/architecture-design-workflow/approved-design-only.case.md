# Design-only approval

## Request

ARCH-DESIGN v4 已由 ARCH-REVIEW v4 给出 APPROVABLE，当前 Issue 中的人类决定针对这两个准确版本明确记录为 `approved_design_only`。请在当前只读测试中生成待发布目标；不得创建研发交接或 OpenSpec，也不得声称已经持久化。

## Expected contract

```json expected
{
  "fixture_id": "approved-design-only",
  "selected": true,
  "stage": "publishing",
  "gate": "approved_design_only",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "architecture-repo:ADR", "architecture-repo:detailed-design"],
  "evidence_fields": ["issue", "design_version", "review_version", "approval_evidence"],
  "required_markers": ["approved_design_only", "publishing"],
  "forbidden_markers": ["已生成 ARCH-RD-HANDOFF", "OpenSpec proposal 已创建"]
}
```
