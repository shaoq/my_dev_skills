# Human action material bundle

## Profile and scope

`multica_human_action_material_bundle_v1` 在 current workflow mandate 内交付一份真正的方案 Review：一个 core Architecture Decision Brief、完整 Design、Research、Control，以及 gate 所需的 Review/Packet。它不创建 Review conclusion、recommendation、approval token 或 core state。

route 要求：

- `action_type=design_input|architecture_review|architecture_approval` 且 `requires_human_review=true`；
- 一个 current action、一个唯一 Decision Owner、一个 authority scope；
- 完整 standalone `ARCH-DESIGN-vN.md` 与准确 Research/Control identities；
- 一个既有 workspace/Issue；
- current `architecture_workflow_mandate_v1` 与可消费 `architecture_operation_manifest_v1`。

不要求或生成 operational authorization。

## Bundle contents

canonical attachment 至少包含 `ARCH-DESIGN-vN.md`，冻结 filename、`text/markdown; charset=utf-8`、version 和 raw-byte SHA-256。Research/Control 可以使用已验证的 `multica_web_comment_permalink_v1`；未通过 requested client checks 时，把准确源作为 Markdown attachment 纳入同一 manifest。

若当前 client capability 证明 Markdown 不便阅读，可以包含 source-digest-bound `ARCH-DESIGN-vN.pdf`：

```text
derived_non_authoritative=true
source_digest=sha256:<canonical-markdown-digest>
```

PDF 不能替代 canonical Markdown。交付后发现缺失材料时保留旧对象；bounded retry 生成新 attempt/new manifest 和新的完整 comment，不编辑/append 旧评论。

## Automatic execution

manifest 冻结 content/attachment 相对路径、cwd、digests、target Issue、actual current parent selector、ordered status/comment writes、postconditions 和 retained objects。路径在 mandate root 之外时 manifest 必须显式包含 resolved external-file mode；运行时不得临时扩大。

一次写入形态为：

```bash
multica issue comment add <issue> \
  --content-file <architecture-decision-brief.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  [--attachment <ARCH-DESIGN-vN.pdf>] \
  [--attachment <ARCH-RESEARCH-vN.md>] \
  [--attachment <ARCH-CONTROL-vN.md>] \
  [--parent <current-trigger-comment-id>] \
  --output json
```

必要时先自动 `in_progress --no-start`。重读新 comment，要求准确 Agent、actual parent、固定 Decision Brief headings、一个 actionable action、canonical mention 和所有附件 bindings；重下载 Markdown 并匹配 digest。分别通过 actual UI activation 验证 web/mobile 的 browser-rendered preview、exact identity 与 complete content；raw-byte fetch、HTTP 200 或 `download-only` 不能把 scope 标为 `opened`。

全部 postconditions 通过且 `requires_human_review=true` 后自动执行 `in_review --no-start` 并重读。这表示唯一 Owner 已被准确 `@` 且正在等待方案决定。无法自动证明 client access 时记录 evidence gap/恢复路径；不生成 `access_confirmation` action，也不要求用户授权交付。

后续 `design_input|architecture_review` 具名回复使用 `current_action_reference_v1`：actor、同一 Issue/workspace、唯一 current Action ID、从 request 继承的 version/digest、created-after-request、未编辑 revision、受限 current Architecture Agent 首尾 mention 规范化、exact normalized response、supersession 和 candidate task attribution 全部通过时匹配 `valid_human_action_response_v1`。用户可以在 Issue 最新位置回复；actual parent chain 记录为 audit-only。匹配后自动 `in_progress --no-start` 并处理决定。无效回复 no-write；packet token-only 路径保持其原 parent/profile 规则。

本 profile 不写 `arch.packet.current`。approvable packet 使用独立 packet route，但共享同一 mandate/manifest 自动化与失败关闭规则。
