# Architecture internal evidence

```text
evidence_contract=architecture_internal_evidence_v1
work_item_ref=<current work item>
attempt_id=<current attempt>
core_contract_revision=<aggregate identity>
human_surface_contract=human_review_surface_v1
research_refs=<refs/digests>
control_ref=<ref/digest>
review_ref=<version-bound ref/digest/conclusion>
machine_only_packet_ref=<ref/version/digest>
visual_manifest_refs=<refs/digests/receipts/statuses>
impact_record_ref=<architecture_design_impact_v1 ref|none>
continuation_ref=<execution_continuation_v2 ref|none>
handoff_readback_ref=<runtime task evidence|none>
readiness_ref=<ref|none>
reconciliation_retry_refs=<refs|none>
supersedes=<older attempt/action/manifest refs|none>
```

该 evidence 保存完整机器审计和恢复信息，默认不进入人类时间线。只有真实 dependency input、内容决定、新 Design 通知、终态交付或真实 blocked/rejected/terminal 摘要可以产生普通人类消息。
