# 架构审批材料已交付（请打开全部附件）

- Packet：`{{packet_ref}} {{packet_version}}`（摘要展示：`{{packet_digest_short}}`）
- Design：`{{design_ref}} {{design_version}}`
- Review：`{{review_ref}} {{review_version}}`
- Review conclusion：`{{review_conclusion}}`

## Architecture Team 建议（不构成人工批准）

- `ARCHITECTURE_RECOMMENDATION`：`{{architecture_recommendation}}`
- 中文理由：{{recommendation_rationale_zh}}
- 适用条件：{{applicable_conditions_zh}}
- 关键风险：{{key_risks_zh}}

## 人工审核

- 审核对象：{{review_subject_zh}}
- 待确认项：{{open_confirmations_zh}}
- 合法决定（去除首尾空白后仅可为其中一个）：`approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected`

> Architecture Team 的建议、Review conclusion、metadata、reaction、Issue status 或任何 Agent/system 评论均不构成人工批准，也不得驱动 core gate。

请在本评论下方打开并核对全部附件：完整 `ARCH-DESIGN`、完整 `ARCH-REVIEW` 与完整 `ARCH-APPROVAL-PACKET`。附件中的冻结 Markdown 原始字节和 SHA-256 才是权威材料；可选 PDF 仅为 `derived_non_authoritative` 预览件。

<!-- multica-architecture-approval-adapter:v1 packet_ref={{packet_ref_marker_escaped}} packet_version={{packet_version}} packet_digest={{packet_digest}} -->
