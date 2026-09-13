# Human action material bundle

## Current profile

`multica_human_action_material_bundle_v3` renders `human_review_surface_v2` while storing `architecture_internal_evidence_v1` separately. Its ordinary Issue comment begins with exactly one of `【需要你确认】`、`【Agent 处理中，无需回复】`、`【Agent 已完成，无需确认】`; only the first may carry a current Action. Visible prose defaults to at most 600 Unicode code points, excluding stable links, attachment filenames and the sole Action code block.

Every entry binds `audience=human|agent`、`review_requirement=required|reference_only|none` and `bound_action=<action_id|none>` and renders respectively as `【需要阅读并确认】`、`【供人参考，无需单独确认】` or `【Agent 内部材料，无需阅读】`. Each Action has exactly one required entry. Formal approval uses exactly one canonical `ARCH-DESIGN-vN.md` attachment with filename, version, `design_maturity`, `text/markdown; charset=utf-8`, raw-byte SHA-256, comment ID, attachment ID, target Member and requested client scopes. Before a Design exists, one `design_input|architecture_review` Action may instead bind exactly one readable, limited-scope, non-canonical decision-detail attachment that explicitly says it is not the overall architecture Design.

New delivery requires current `architecture_workflow_mandate_v2`、a consumable `architecture_operation_manifest_v1`、one current Action and `requires_human_review=true`; `architecture_workflow_mandate_v1` is audit-only. Delivery preparation/status uses `in_progress --no-start`; verified human surface uses `in_review --no-start`.

Research、Control、完整 Review、machine-only Packet、digests、receipts、task result、continuation/handoff、reconciliation 和 retry 只进入 `agent_internal` evidence；它们不得复制到普通评论，不得成为 mandatory attachments，也不得要求 Owner 打开。

## Supporting resources

若需要改善可读性，可在同一 Design surface 提供 PDF、Archify HTML 和 receipt-bound light/1440x900 static preview，但每项必须标记：

```text
derived_non_authoritative=true
source_design_digest=sha256:<canonical-markdown-digest>
visual_manifest_ref=<architecture_visual_manifest_v1 ref|none>
resource_digest=sha256:<resource-raw-byte-digest>
```

supporting resource 使用 `human_reference` / `review_requirement=reference_only`，不计入 canonical attachment 数量，不改变 Design digest，也不创建第二个 mandatory human entry 或第二个 Action。required visual 的 preview 必须来自绑定 current HTML digest 的同一次成功 `visual-check` receipt；HTML 可选，preview 与 requested-client 可读性必须验证。完整“需要做什么”、最多三项方案权衡和 Archify 图解应位于 required material，不复制进 Issue comment。

## Atomic delivery and readback

```bash
multica issue comment add <issue> \
  --content-file <architecture-decision-brief.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  [--parent <current-trigger-comment-id>] \
  --output json
```

写后重读准确 comment、author、parent、canonical mention、current Action 和 exactly one required attachment，下载原始字节并重算 digest。校验评论责任标签、600-code-point budget、材料标签和单一 Action。`automatic` 对每个 requested scope 实际打开完整 required material 和 required preview 后记录 `material_access_state=opened`；只有内容结构、普通语言说明、方案后果和可理解架构图检查通过才记录 `decision_readiness_state=validated`。`owner_manual|owner_attested` 验证 exact identity/digest、stable same-Issue entry 与 policy/task evidence，把两个状态分别记录为 `manual_check_required`，不得声称 `opened|validated`。

材料不可用时保留对象并执行有界 `repair_or_republish_material_entry` / new attempt，不编辑旧评论。`ACTION <action_id>: 材料打不开` 只报告 access failure，`content_decision=none`。若 access 成功但材料不能支持决定，`ACTION <action_id>: 材料不可决策; reason=<原因>` 保留 access evidence、记录 `decision_readiness_state=unreadable|incomplete`、`content_decision=none`、supersede current Action 并用 new attempt/new Action 回到 `preparing`。两类回复严格区分；owner-attested 的合法决定仍必须为 `ACTION <action_id>: materials_opened; decision=<legal-token>`。

Current replies must validate as `valid_human_action_response_v1`. Access is machine-verified or Owner-attested through the current Action；不生成 `access_confirmation` Human Action。

## Legacy reader

历史 `multica_human_action_material_bundle_v1|v2`、`human_review_surface_v1` 与旧三附件 delivery 作为 frozen legacy audit 原样保留。新 writer 不追加、编辑、删除或把它们 reinterpret 为 v3；需要升级时创建 superseding attempt。legacy reply 继续按冻结 revision 读取，晚到回复不能消费 current v3 Action。
