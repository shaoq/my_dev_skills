# Multica adapter sandbox acceptance checklist

## Preconditions

- 用户明确要求在一个准确既有 sandbox workspace/Issue/Architecture Agent 验证当前 packages，由此建立 sandbox mandate；不使用 operation authorization。
- core/adapter/Archify IDs、package aggregates、Archify full revision/archive digest 与四个目标 Agent 指令已通过 activation readback。
- Issue 明确用于验收，不自动创建缺失 sandbox 资源。
- manifest 冻结 exact test writes、retained objects、retry limit、失败行为与 excluded production scope。

## Acceptance checks

1. 自动交付 current `human_review_surface_v2`，确认评论以唯一责任标签开头，可见 prose 在默认 600 Unicode code points 预算内，只保留普通语言决定、推荐/最关键后果、一个 required 材料、回复后行为、唯一 Action、canonical mention 与 `in_review`。
2. 分别在 Web/mobile 打开 exact Design 与 required Architecture 总览图的 light/1440x900 preview，验证 identity、完整内容、标题、主要组件/边界和关键标注可辨认；Agent download、HTTP 200、文件名卡片或本地路径不算。
3. 重下载 canonical Markdown/preview 并匹配 raw-byte digests；Design 是 `【需要阅读并确认】`，PDF/HTML/preview（若有）必须是 `derived_non_authoritative` 和 `【供人参考，无需单独确认】`，不得产生第二 Action。
4. 验证 deliver/browser/visual/semantic 四门禁全部 passed；任一 failed/skipped/stale/mismatch 都 readiness unavailable。automatic 与 owner-attested 分别覆盖 `opened`/`manual_check_required + materials_opened`。
5. 由准确 Owner 提交 current exact response；验证 actor/parent/action/version/digest/revision/task attribution 后自动恢复 `in_progress`。token+prose、edited/wrong-owner/wrong-parent 必须 no-op。
6. 创建 superseding packet/attempt，验证旧回复 audit-only，新 current reply 才有效。
7. 演练材料“可打开但不可决策”：准确 Owner 回复 `ACTION <id>: 材料不可决策; reason=<原因>` 后保留 access success、记录 `unreadable|incomplete`、`content_decision=none`、supersede 旧 Action，并以新 attempt/new Action 交付更可读的详情材料。确认它没有被解释为 `材料打不开|rejected|revision_requested`。
8. 演练 bounded retry/partial failure：新 manifest 冻结 retained set，不 duplicate/edit/delete/overwrite；Research、Control、Review、Packet、receipt、continuation/handoff/readback、retry/reconciliation 只能是 `【Agent 内部材料，无需阅读】` internal evidence，不生成长普通 Issue comment。
9. 演练 pre-Design 输入：Issue 仅有轻量摘要和一份明确“不是总体架构设计”的 action-bound detail attachment；正式批准仍恰好一份 canonical Design。
10. 演练 R&D 复用批准图和一张 scope-local 实现图；模拟架构影响时生成 `architecture_design_impact_v1` 并返回 Architecture Team。
11. 逐 Agent 回读四个 Archify binding，确认 review-only 不可改图、指令包含 human-decision-readiness 约束，且非目标 Agent 无新增 binding。

## Outcome

只有全部检查通过才记录 `sandbox_acceptance=passed`。超预算长评论、缺 responsibility label、多个 required entries、Archify 第二 Action、材料虽打开但不可决策仍被消费、desktop-only、required visual failed/skipped、手机 preview 不可辨认、multi-Owner form、材料不可访问、缺 supersession/response/retry 证据、dedicated Agent handoff comment 或出现 operational token 均为 `failed|not_run`。平台能力缺失时建议独立平台 proposal，但不自动修改 Multica 核心或创建资源。
