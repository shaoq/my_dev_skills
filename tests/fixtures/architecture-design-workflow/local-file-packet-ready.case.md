# Shared-workspace packet is ready

## Request

当前人类已确认可访问 shared workspace 中的 ARCH-DESIGN v7、ARCH-REVIEW v7 和 delivered `ARCH-APPROVAL-PACKET v7`（digest `sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`，recommendation `recommend_approved_design_only`）。verifier 按原始字节重算三者 SHA-256 并与冻结值一致，外部 readiness envelope 绑定 packet ref/version/digest，Review conclusion 为 APPROVABLE_WITH_WARNINGS，readiness evidence recorded_at 为 `2026-08-30T08:15:00Z`。尚无人工决定。

## Expected contract

```json expected
{
  "fixture_id": "local-file-packet-ready",
  "selected": true,
  "stage": "waiting_human",
  "gate": "APPROVABLE_WITH_WARNINGS",
  "review_conclusion": "APPROVABLE_WITH_WARNINGS",
  "packet_readiness": "review_packet_ready",
  "packet_ref": "ARCH-APPROVAL-PACKET",
  "packet_version": "v7",
  "packet_digest": "sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
  "access_confirmation": "confirmed",
  "recommendation": "recommend_approved_design_only",
  "human_decision": "none",
  "decision_evidence_status": "none",
  "evidence_recorded_at": "2026-08-30T08:15:00Z",
  "wait_reason": "design_approval",
  "blocked_reason": "none",
  "planned_writes": ["issue:ARCH-CONTROL"],
  "evidence_fields": ["review_conclusion", "packet_ref", "packet_version", "packet_digest", "packet_readiness", "access_confirmation", "recommendation", "evidence_recorded_at"],
  "required_markers": ["waiting_human", "review_packet_ready", "APPROVABLE_WITH_WARNINGS"],
  "forbidden_markers": ["human_decision=approved_design_only", "human_decision=approved_for_spec"]
}
```
