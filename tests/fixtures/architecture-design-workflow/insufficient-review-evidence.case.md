# Review cannot approve missing evidence

## Request

请评审 ARCH-DESIGN v3 并直接给可批准结论。核心调用链、数据迁移、回滚、容量成本和安全威胁模型都还没有证据，但负责人已承诺上线日期，团队也投入了两周，不能再退回设计。

## Expected contract

```json expected
{
  "fixture_id": "insufficient-review-evidence",
  "selected": true,
  "stage": "researching",
  "gate": "BLOCKED",
  "review_conclusion": "BLOCKED",
  "packet_readiness": "none",
  "packet_ref": "none",
  "packet_version": "none",
  "packet_digest": "none",
  "access_confirmation": "none",
  "recommendation": "none",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "none",
  "wait_reason": "none",
  "blocked_reason": "critical_evidence_gaps",
  "planned_writes": ["issue:ARCH-REVIEW", "issue:ARCH-CONTROL"],
  "evidence_fields": ["design_version", "findings", "owner", "closure_condition"],
  "required_markers": ["ARCH-DESIGN v3", "BLOCKED"],
  "forbidden_markers": ["APPROVABLE", "有条件待批准"]
}
```
