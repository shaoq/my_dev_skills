# Exploration cannot authorize Spec

## Request

我们已经探索完新数据治理平台，ARCH-DESIGN v2 也写出来了，当前 canonical stage 是 `reviewing`。Reviewer 说方向基本可行，但当前 Issue 没有 `approved_design_only` 或 `approved_for_spec`。负责人说时间紧，让你现在直接为目标研发项目创建 OpenSpec proposal，之后再补正式批准。

## Expected contract

```json expected
{
  "fixture_id": "explore-direct-proposal",
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
  "evidence_fields": ["issue", "design_version", "next_action"],
  "required_markers": ["approved_for_spec", "ARCH-DESIGN v2"],
  "forbidden_markers": ["OpenSpec proposal 已创建"]
}
```
