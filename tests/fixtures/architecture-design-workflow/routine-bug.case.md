# Routine engineering task does not trigger

## Request

订单服务昨天开始偶发 502。请定位错误调用链，找出最近提交中的回归并修复；已有明确复现步骤和批准的 OpenSpec change。

## Expected contract

```json expected
{
  "fixture_id": "routine-bug",
  "selected": false,
  "stage": "not_applicable",
  "gate": "not_applicable",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": [],
  "evidence_fields": ["routing_reason", "next_action"],
  "required_markers": ["普通工程", "不触发"],
  "forbidden_markers": ["已创建 ARCH-CONTROL", "approved_for_spec"]
}
```
