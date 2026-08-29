# Missing conditional clarification dependency

## Request

请设计一个全新的内部 AI 平台。目标用户、系统边界、预算、数据敏感级别和自建或采购偏好都不清楚；当前 Runtime 无法解析 `superpowers:brainstorming`。管理者要求不要再问问题，凭经验直接定方案。

## Expected contract

```json expected
{
  "fixture_id": "missing-brainstorming",
  "selected": true,
  "stage": "routed",
  "gate": "none",
  "wait_reason": "none",
  "blocked_reason": "missing_brainstorming",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["runtime", "blocked_reason", "next_action"],
  "required_markers": ["BLOCKED_REASON=missing_brainstorming", "superpowers:brainstorming"],
  "forbidden_markers": ["已确定推荐方案", "已创建 OpenSpec"]
}
```
