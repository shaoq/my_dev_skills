# Clear greenfield architecture request

## Request

为公司设计一套新的内部制品签名与验证服务。Subject Project 已确认，目标、边界、预算、安全等级和决策标准都明确；`openspec-explore` 可用，不需要 brainstorming。请开始架构研究，不要进入 OpenSpec 实施。

## Expected contract

```json expected
{
  "fixture_id": "greenfield-positive",
  "selected": true,
  "stage": "researching",
  "gate": "none",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "issue:ARCH-RESEARCH"],
  "evidence_fields": ["issue", "subject_project", "design_type", "stage", "next_action"],
  "required_markers": ["greenfield", "ARCH-RESEARCH"],
  "forbidden_markers": ["OpenSpec proposal", "implementation"]
}
```
