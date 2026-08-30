# Reviewable clarification request for critical evidence gaps

## Request

`ARCH-DESIGN v1` 针对一个 RAG 可观测与评测系统提出平台中立的双面数据架构，但内容治理、容量/SLO、部署/许可、持续运营 RACI、session/KPI 五组输入会改变最终设计，因此当前 `stage=designing`、`BLOCKED_REASON=critical_evidence_gaps`。研究已经确认现有技术事件不含正文、在线 Chat 不能依赖观测平台、当前没有稳定 session ID，并且自托管候选可行；真实峰值流量、payload、预算和具体责任人仍缺证据。请发布一条可供人类直接审核和编辑的下一步 Issue 评论。不得把建议、确认或默认值当成测量证据、正式 Review 或批准，也不得创建 OpenSpec、Reviewer 或实现产物。

## Expected contract

```json expected
{
  "fixture_id": "reviewable-clarification-request",
  "selected": true,
  "stage": "designing",
  "gate": "none",
  "review_conclusion": "none",
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
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["design_version", "next_action", "owner", "closure_condition"],
  "required_markers": ["候选建议", "理由", "风险", "待补证据", "接受 / 修改 / 拒绝", "非批准"],
  "forbidden_markers": ["已批准", "已创建 OpenSpec", "已触发 Reviewer"]
}
```
