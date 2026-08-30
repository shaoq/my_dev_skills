# Reviewable Subject Project routing

## Request

一个 hybrid 事件平台横跨支付、会员和通知。现有证据显示支付拥有事件生产合同，会员和通知是消费者；`shared-platform` 已存在并由 Platform Owner 管理共同协议。当前没有唯一 Subject Project，因此 `stage=waiting_human`、`WAIT_REASON=target_project`、`BLOCKED_REASON=missing_subject_project`。请让 Architecture Sponsor 选择架构决定的长期归属，不能创建新 Project，也不能用“选一个项目”代替建议、备选后果和准确回复。

## Expected contract

```json expected
{
  "fixture_id": "reviewable-subject-project-routing",
  "selected": true,
  "stage": "waiting_human",
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
  "wait_reason": "target_project",
  "blocked_reason": "missing_subject_project",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["subject_project", "next_action", "owner", "closure_condition"],
  "required_markers": ["action_type=routing", "Decision Owner", "Authority scope", "Candidate recommendation", "Bounded alternatives", "Stable human-accessible evidence refs", "Exact response", "After response", "Does not authorize"],
  "forbidden_markers": ["已创建 Project", "接受全部"]
}
```
