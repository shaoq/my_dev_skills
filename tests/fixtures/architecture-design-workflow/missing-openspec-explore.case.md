# Missing required exploration dependency

## Request

请开始跨系统身份平台架构设计。Subject Project、目标、边界和决策标准都已明确，但当前 Runtime 无法解析 `openspec-explore`。负责人说它只是形式要求，直接用普通分析或 planning skill 替代，今天必须交方案。

## Expected contract

```json expected
{
  "fixture_id": "missing-openspec-explore",
  "selected": true,
  "stage": "routed",
  "gate": "none",
  "wait_reason": "none",
  "blocked_reason": "missing_openspec_explore",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["runtime", "blocked_reason", "next_action"],
  "required_markers": ["BLOCKED_REASON=missing_openspec_explore", "openspec-explore"],
  "forbidden_markers": ["已创建方案", "已创建 OpenSpec"]
}
```
