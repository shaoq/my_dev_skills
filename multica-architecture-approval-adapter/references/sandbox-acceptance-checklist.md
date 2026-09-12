# Multica adapter sandbox acceptance checklist

## Preconditions

- 用户明确要求在一个准确既有 sandbox workspace/Issue/Architecture Agent 验证当前 packages，由此建立 sandbox mandate；不使用 operation authorization。
- core/adapter/Archify IDs、package aggregates、Archify full revision/archive digest 与四个目标 Agent 指令已通过 activation readback。
- Issue 明确用于验收，不自动创建缺失 sandbox 资源。
- manifest 冻结 exact test writes、retained objects、retry limit、失败行为与 excluded production scope。

## Acceptance checks

1. 自动交付 current brief，确认固定内容顺序、唯一 mandatory Design、Design maturity、简短 Review/风险、唯一 Action、canonical mention 与 `in_review`。
2. 分别在 Web/mobile 打开 exact Design 与 required Architecture 总览图的 light/1440x900 preview，验证 identity、完整内容、标题、主要组件/边界和关键标注可辨认；Agent download、HTTP 200、文件名卡片或本地路径不算。
3. 重下载 canonical Markdown/preview 并匹配 raw-byte digests；PDF/HTML（若有）必须是 `derived_non_authoritative`。
4. 验证 deliver/browser/visual/semantic 四门禁全部 passed；任一 failed/skipped/stale/mismatch 都 readiness unavailable。automatic 与 owner-attested 分别覆盖 `opened`/`manual_check_required + materials_opened`。
5. 由准确 Owner 提交 current exact response；验证 actor/parent/action/version/digest/revision/task attribution 后自动恢复 `in_progress`。token+prose、edited/wrong-owner/wrong-parent 必须 no-op。
6. 创建 superseding packet/attempt，验证旧回复 audit-only，新 current reply 才有效。
7. 演练 bounded retry/partial failure：新 manifest 冻结 retained set，不 duplicate/edit/delete/overwrite；Research、Control、Review、Packet、continuation/handoff/readback、retry/reconciliation 不生成普通 Issue comment。
8. 演练 R&D 复用批准图和一张 scope-local 实现图；模拟架构影响时生成 `architecture_design_impact_v1` 并返回 Architecture Team。
9. 逐 Agent 回读四个 Archify binding，确认 review-only 不可改图，且非目标 Agent 无新增 binding。

## Outcome

只有全部检查通过才记录 `sandbox_acceptance=passed`。desktop-only、required visual failed/skipped、手机 preview 不可辨认、multi-Owner form、材料不可访问、缺 supersession/response/retry 证据、dedicated Agent handoff comment 或出现 operational token 均为 `failed|not_run`。平台能力缺失时建议独立平台 proposal，但不自动修改 Multica 核心或创建资源。
