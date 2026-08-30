# 架构审批材料已交付

## 现在需要你决定

- Action ID / type：`{{human_action_id}}` / `design_approval`
- Decision Owner：`{{canonical_target_member_uuid}}`
- 审核对象：`{{review_subject_zh}}`
- 为什么现在可决定：`{{packet_ref}} {{packet_version}}` 已完成 current delivery/readiness，Review conclusion=`{{review_conclusion}}`
- Architecture Team 建议：`{{architecture_recommendation}}`
- 推荐理由：{{recommendation_rationale_zh}}
- 适用条件：{{applicable_conditions_zh}}
- 关键风险 / accepted warnings：{{key_risks_and_acceptance_zh}}

> 推荐不是批准。Recommendation、Review conclusion、readiness、访问确认、运维授权、metadata、reaction、Issue status 或 Agent/system 评论均不得驱动 core gate。

### 四种选择

| 准确 token | 中文后果 | Next stage | Remaining blockers | Next Owner | 直接 planned writes | 权限边界与不可逆影响 |
|---|---|---|---|---|---|---|
| `approved_design_only` | 只发布批准文档 | `publishing` | `none|approved_artifact_unavailable` | Architecture Lead | 控制记录、ADR、详细设计 | 不生成 R&D handoff；正式历史通过 supersede/revoke 演进 |
| `approved_for_spec` | 发布批准文档，并在目标存在时形成 R&D handoff | `publishing`；目标缺失时 `waiting_human` | `none|missing_target_project|approved_artifact_unavailable` | Architecture Lead；目标缺失时 Routing Owner | 控制记录、ADR、详细设计、目标存在时 handoff | R&D Team 独立分析；不自动创建 OpenSpec、Issue、branch、commit 或代码 |
| `revision_requested` | 进入新设计迭代 | `designing` | `none`；说明缺失时 `revision_scope=missing` context | Solution Architect / Design Decision Owner | 控制记录、新设计版本 | revision brief 另行提供；旧 packet 不改写 |
| `rejected` | 拒绝 current work item | `rejected` | `none` | Architecture Lead 记录终态 | 控制记录 | 终态；继续需要新的明确工作 |

## 打开全部完整材料

- Stable Design ref：`{{stable_design_attachment_ref}}`（`{{design_ref}} {{design_version}}`）
- Stable Review ref：`{{stable_review_attachment_ref}}`（`{{review_ref}} {{review_version}}`）
- Stable Packet ref：`{{stable_packet_attachment_ref}}`（`{{packet_ref}} {{packet_version}}`）

请逐项打开 Design、Review、Packet 的完整 Markdown；附件卡片、摘要、Agent 下载和可选预览均不能替代完整材料或 target-member access confirmation。

## 准确回复

在本评论的 descendant chain 中，由准确 Decision Owner 新建一条评论，去除首尾空白后只包含一个 token。不要把原因或 revision prose 写在同一条 token 评论中：

```text
{{one_legal_token_only}}
```

如果选择修订，把具体修改内容另发为绑定本 packet/comment 的 revision brief；它只形成 `decision_context_ref`，不是决定 authority。token 缺失或 token 与说明混写时，需要 fresh token-only comment。

## 审计信息

- Human Action Request ref / version：`{{human_action_request_ref}}` / `{{human_action_request_version}}`
- Packet digest：`{{packet_digest}}`
- Design / Review identity：`{{design_ref}} {{design_version}}` / `{{review_ref}} {{review_version}}`
- 待确认项：{{open_confirmations_zh}}
- Current / superseded：`current`
- 权威材料：冻结 Markdown 原始字节和 SHA-256；可选预览为 `derived_non_authoritative`

<!-- multica-architecture-approval-adapter:v1 packet_ref={{packet_ref_marker_escaped}} packet_version={{packet_version}} packet_digest={{packet_digest}} -->
