# Architecture design impact

## Purpose

`architecture_design_impact_v1` 决定一项新输入是否需要产生新的、人类可见的 Design 版本。减少评论或附件数量不能作为复用旧批准的理由；无法证明无影响的 `unknown` 必须保守归类为 `architecture_impact`。

## Canonical record

```text
impact_profile=architecture_design_impact_v1
work_item_ref=<current work item>
attempt_id=<current attempt>
changed_input_refs=<stable refs and digests>
classification=no_architecture_impact|architecture_impact
reason=<evidence-backed rationale>
affected_design_sections=<section IDs or none>
verifier=<independent actor or deterministic check>
verified_at=<RFC3339 UTC>
design_action=retain|create_new_version
review_action=retain|create_new_version
current_action_effect=retain|supersede
manifest_effect=retain|supersede
evidence_ref=<architecture_internal_evidence_v1 durable ref>
```

## Decision table

| Change | Classification | Required action |
|---|---|---|
| Raw evidence、日志、状态、措辞或不改变结论的实现细节 | `no_architecture_impact` | 仅追加内部 evidence；不创建 Design/Review/审批评论 |
| Recommendation、系统/责任/信任边界、外部接口、一致性、NFR、安全/隐私/可靠性、容量/成本、迁移/回滚、accepted risk、未决人类决定、validation criteria 或 maturity 改变 | `architecture_impact` | 新建 Design 和独立 Review；supersede current Action/manifest |
| 影响为 unknown、证据不足或 verifier 无法确认 | `architecture_impact` | fail closed；按有影响处理并 supersede |

纯渲染变化只有在不改变图的语义、Design 正文引用、preview identity 或可读性结论时才可归为无影响；任何拓扑、边、消息、状态、边界或 evidence mapping 变化均为架构影响。
