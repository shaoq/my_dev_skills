# Multica adapter sandbox acceptance checklist

## Preconditions

- 用户明确要求在一个准确既有 sandbox workspace/Issue/Architecture Agent 验证当前 packages，由此建立 sandbox mandate；不使用 operation authorization。
- core/adapter IDs 与 package aggregates 已通过 activation readback。
- Issue 明确用于验收，不自动创建缺失 sandbox 资源。
- manifest 冻结 exact test writes、retained objects、retry limit、失败行为与 excluded production scope。

## Acceptance checks

1. 自动交付一个 current `requires_human_review=true` design-input brief，确认固定内容顺序、完整 Design/Research/Control、唯一 actionable Owner、canonical mention 与 `in_review` 状态。
2. 分别在 Web/mobile 打开 exact materials，验证 identity/complete content；Agent download、文件名卡片、本地路径或 unsupported URI 不算。
3. 重下载 canonical Markdown 并匹配 raw-byte digest；PDF（若有）必须是 source-bound non-authoritative copy。
4. 自动交付一个 current packet brief，验证 Design/Review/Packet、四个中文 option consequences 和 `in_review`。
5. 由准确 Owner 提交 current exact response；验证 actor/parent/action/version/digest/revision/task attribution 后自动恢复 `in_progress`。token+prose、edited/wrong-owner/wrong-parent 必须 no-op。
6. 创建 superseding packet/attempt，验证旧回复 audit-only，新 current reply 才有效。
7. 演练 bounded retry/partial failure：新 manifest 冻结 retained set，不 duplicate/edit/delete/overwrite；全过程不产生 `AUTHORIZE OPERATION`、relay、access-confirmation 或逐状态授权请求。

## Outcome

只有全部检查通过才记录 `sandbox_acceptance=passed`。desktop-only、multi-Owner form、材料不可访问、缺 supersession/response/retry 证据或出现 operational token 均为 `failed|not_run`。平台能力缺失时建议独立平台 proposal，但不自动修改 Multica 核心或创建资源。
