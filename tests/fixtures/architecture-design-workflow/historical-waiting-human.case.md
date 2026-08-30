# Historical waiting-human compatibility

## Request

这是升级前已持久化的 `waiting_human` 记录，Review conclusion 为 APPROVABLE，但没有 packet 或 readiness evidence；本次没有产生新的 design/review version，也没有显式 refresh。请保留历史 stage，不能伪造 readiness 或自动降级。

## Expected contract

```json expected
{
  "fixture_id": "historical-waiting-human",
  "selected": true,
  "stage": "waiting_human",
  "gate": "APPROVABLE",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "none",
  "packet_ref": "none",
  "packet_version": "none",
  "packet_digest": "none",
  "access_confirmation": "none",
  "recommendation": "none",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "none",
  "wait_reason": "design_approval",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["stage", "review_conclusion", "next_action"],
  "required_markers": ["历史", "waiting_human", "不自动迁移"],
  "forbidden_markers": ["review_packet_ready 已生成", "降级到 reviewing"]
}
```
