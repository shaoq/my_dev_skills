## Why

当前架构 Skill 把材料准备、交付、状态投影、重试和 evidence sidecar 等内部操作也建模为逐步人工授权，导致真正的方案决定被 `AUTHORIZE OPERATION` 淹没。用户明确启动、继续或重试一个既有架构阶段后，非 Review 操作应在有界范围内自动完成并留下机器审计证据。

## What Changes

- 在 portable `architecture-design-workflow` 中定义 `architecture_workflow_mandate_v1` 与 `requires_human_review` 派生规则。
- 只有 `design_input`、`architecture_review`、`architecture_approval` 可以成为方案人工 Review；访问验证、准备、交付、状态、relay、retry 和 verification 均不是人工授权点。
- 在 `multica-architecture-approval-adapter` 中用 immutable `architecture_operation_manifest_v1` 取代二次 operational authorization，并自动完成当前 mandate 内的最小写入及 readback。
- 成功交付真正的方案决定后自动进入 `in_review`；收到有效 current 回复后自动恢复 `in_progress`。
- 旧式 delivery/retry/relay/status authorization request 只保留 audit，并由新 attempt supersede。
- 人类可访问性只由真实客户端内联渲染证明；download-only、raw-byte fetch、HTTP 200 或 digest 一致不再满足 Review readiness。
- 不新增 Multica 服务端接口；在 Multica 共享 `packages/views` 复用既有 Markdown preview 修正附件普通链接的主点击行为。不创建缺失资源，不扩大到业务实现或部署。

## Capabilities

### New Capabilities

- `architecture-workflow-operation-automation`: 有界 workflow mandate、方案 Review 分类、derived manifest、自动状态投影、失败关闭和旧请求迁移。

### Modified Capabilities

- `architecture-design-governance`: 人工门禁只表达方案内容决定，不再表达内部操作授权。
- `multica-architecture-approval-delivery`: 当前 mandate 内自动交付并以 derived manifest 审计。
- `multica-architecture-human-action-rendering`: 只向人展示真实方案决定与完整材料入口。

## Impact

- 修改 `architecture-design-workflow/`、`multica-architecture-approval-adapter/` 及其 references/templates。
- 保持 portable core 可独立安装和运行；Multica 字段只存在于 sibling adapter。
- 不修改 Multica 服务端、CLI 或业务项目；Multica 共享只读内容渲染层的有界修正保存在 Multica 仓库，不放入本 Skill 仓库。
- 用户明确豁免本 change 新增测试；实施只运行并维护现有验证矩阵。
