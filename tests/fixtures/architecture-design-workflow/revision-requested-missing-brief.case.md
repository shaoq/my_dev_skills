# Revision requested without actionable brief

## Request

当前目标人类已针对 ready `ARCH-APPROVAL-PACKET v20`（digest `sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad`）记录有效 `revision_requested`，Review conclusion=`APPROVABLE`，recommendation=`recommend_revision`，evidence recorded_at=`2026-08-30T15:30:00Z`。决定评论没有任何具体修改内容，也没有可重读 revision brief。请计算状态并让人补齐可执行修订范围；不得把 token 当作完整修订说明，也不得修改旧 packet。

## Expected contract

```json expected
{
  "fixture_id": "revision-requested-missing-brief",
  "selected": true,
  "stage": "designing",
  "gate": "revision_requested",
  "review_conclusion": "APPROVABLE",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v20",
  "packet_digest": "sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_revision",
  "human_decision": "revision_requested",
  "decision_evidence_status": "valid",
  "evidence_recorded_at": "2026-08-30T15:30:00Z",
  "wait_reason": "none",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL", "issue:ARCH-DESIGN"],
  "evidence_fields": ["packet_version", "packet_digest", "human_decision", "decision_evidence", "next_action", "owner", "closure_condition"],
  "required_markers": ["revision_scope=missing", "action_type=design_input", "Decision Owner", "Candidate recommendation", "Exact response", "After response", "旧 packet 保持不变"],
  "forbidden_markers": ["修订要求已完整", "旧 packet 已改写", "新 packet 已创建"]
}
```
