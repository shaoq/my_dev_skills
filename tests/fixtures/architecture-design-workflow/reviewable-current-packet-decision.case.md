# Reviewable current packet decision

## Request

当前 ready `ARCH-APPROVAL-PACKET v19` 绑定 `ARCH-DESIGN v19` 与 `ARCH-REVIEW v19`，packet digest 为 `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，Review conclusion=`APPROVABLE_WITH_WARNINGS`，recommendation=`recommend_approved_for_spec`，完整三份材料已有目标人类可访问的稳定 refs，两个 accepted risks 也有具名 Owner 和证据。尚无 human decision。请让目标人类快速比较四种合法决定的中文后果、OpenSpec 边界、立即写入及不可逆影响，不能只列 token 或先展示审计 digest。

## Expected contract

```json expected
{
  "fixture_id": "reviewable-current-packet-decision",
  "selected": true,
  "stage": "waiting_human",
  "gate": "APPROVABLE_WITH_WARNINGS",
  "review_conclusion": "APPROVABLE_WITH_WARNINGS",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v19",
  "packet_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_for_spec",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "none",
  "wait_reason": "design_approval",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "recommendation", "next_action"],
  "required_markers": ["action_type=design_approval", "approved_design_only", "只发布", "approved_for_spec", "R&D", "不自动创建 OpenSpec", "revision_requested", "新设计迭代", "rejected", "终态", "Stable human-accessible evidence refs", "Exact response", "After response"],
  "forbidden_markers": ["已批准", "推荐即批准"]
}
```
