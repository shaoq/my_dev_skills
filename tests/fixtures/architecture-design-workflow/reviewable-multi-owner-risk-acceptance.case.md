# Reviewable multi-owner risk acceptance

## Request

`ARCH-REVIEW v4` 对 `ARCH-DESIGN v4` 发现两个可以保留但必须分别接受的非阻断风险：`RISK-PRIVACY-1` 是 30 天 derived retention，Decision Owner 为 Privacy Owner；`RISK-SRE-2` 是试点期间单区部署，Decision Owner 为 SRE Owner。两项风险影响、条件和权限域不同，当前尚无 acceptance evidence。请发布人工请求，不得让任一 Owner 用一次“接受全部”替另一个 Owner 决定，也不得提前形成 `APPROVABLE_WITH_WARNINGS` 或 packet。

## Expected contract

```json expected
{
  "fixture_id": "reviewable-multi-owner-risk-acceptance",
  "selected": true,
  "stage": "reviewing",
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
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_version", "owner", "closure_condition", "next_action"],
  "required_markers": ["action_type=risk_acceptance", "RISK-PRIVACY-1", "Privacy Owner", "RISK-SRE-2", "SRE Owner", "Option consequences", "Exact response", "After response", "非批准"],
  "forbidden_markers": ["接受全部", "APPROVABLE_WITH_WARNINGS 已确认", "ARCH-APPROVAL-PACKET 已创建"]
}
```
