# Human action material bundle

## Current profile

`multica_human_action_material_bundle_v2` renders `human_review_surface_v1` while storing `architecture_internal_evidence_v1` separately. A current delivery has exactly one canonical attachment: `ARCH-DESIGN-vN.md`. It binds filename, version, `design_maturity`, `text/markdown; charset=utf-8`, raw-byte SHA-256, comment ID, attachment ID, target Member and requested client scopes.

New delivery requires current `architecture_workflow_mandate_v2`、a consumable `architecture_operation_manifest_v1`、one current Action and `requires_human_review=true`; `architecture_workflow_mandate_v1` is audit-only. Delivery preparation/status uses `in_progress --no-start`; verified human surface uses `in_review --no-start`.

Research、Control、完整 Review、machine-only Packet、digests、task result、continuation/handoff、reconciliation 和 retry 只进入 internal evidence；它们不得成为 mandatory attachments 或要求 Owner 打开的材料。

## Supporting resources

若需要改善可读性，可在同一 Design surface 提供 PDF、Archify HTML 和 receipt-bound light/1440x900 static preview，但每项必须标记：

```text
derived_non_authoritative=true
source_design_digest=sha256:<canonical-markdown-digest>
visual_manifest_ref=<architecture_visual_manifest_v1 ref|none>
resource_digest=sha256:<resource-raw-byte-digest>
```

supporting resource 不计入 canonical attachment 数量，不改变 Design digest，也不创建第二个 mandatory human entry。required visual 的 preview 必须来自绑定 current HTML digest 的同一次成功 `visual-check` receipt；HTML 可选，preview 与 requested-client 可读性必须验证。

## Atomic delivery and readback

```bash
multica issue comment add <issue> \
  --content-file <architecture-decision-brief.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  [--parent <current-trigger-comment-id>] \
  --output json
```

写后重读准确 comment、author、parent、canonical mention、current Action 和 exactly one Design attachment，下载原始字节并重算 digest。`automatic` 对每个 requested scope 实际打开完整 Design 和 required preview 后记录 `opened`；`owner_manual|owner_attested` 验证 exact identity/digest、stable same-Issue entry 与 policy/task evidence，记录 `manual_check_required`，不得声称 `opened`。

材料不可用时保留对象并执行有界 `repair_or_republish_material_entry` / new attempt，不编辑旧评论。决策卡始终提供 `ACTION <action_id>: 材料打不开`；该回复 `content_decision=none`。owner-attested 的合法决定必须为 `ACTION <action_id>: materials_opened; decision=<legal-token>`。

Current replies must validate as `valid_human_action_response_v1`. Access is machine-verified or Owner-attested through the current Action；不生成 `access_confirmation` Human Action。

## Legacy reader

历史 `multica_human_action_material_bundle_v1` 与旧三附件 delivery 作为 frozen legacy audit 原样保留。新 writer 不追加、编辑、删除或把它们 reinterpret 为 v2；需要升级时创建 superseding attempt。legacy reply 继续按冻结 revision 读取，晚到回复不能消费 current v2 Action。
