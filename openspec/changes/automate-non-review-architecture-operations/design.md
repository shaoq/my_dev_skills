## Context

现有 adapter 使用 `multica_operational_scope_v1` 为 preparation、delivery、retry、relay、status 和 sidecar write 分别请求人工授权。该协议能冻结目标和写入顺序，但把机器审计与人的方案决定混为一谈。此次将其审计价值保留为 derived manifest，同时从用户交互中移除。

## Goals / Non-Goals

**Goals:**

- 一次明确的启动、继续或重试指令覆盖单一 Issue/stage/attempt 内的非 Review 操作。
- 只有真实方案内容决定进入 `in_review` 并 `@` 唯一 Decision Owner。
- 自动操作可重验、单次消费、失败关闭、无重复 current delivery。
- core 完全不依赖 Multica。

**Non-Goals:**

- 不自动替人接受、修改、拒绝或正式批准方案。
- 不授权实现、部署、采购、资源创建或跨 Issue/workspace 写入。
- 不修改 Multica 核心或引入私有 API。

## Decisions

### 1. Workflow mandate 是唯一自动操作边界

`architecture_workflow_mandate_v1` 绑定 workspace adapter identity（portable profile 可为 `none`）、Issue/work item、stage、attempt、Agent、触发证据、允许操作、重试上限、postconditions 与失效条件。范围变化时停止并报告需要新的任务指令，不生成 operational token。

### 2. Human Review 由内容语义派生

`requires_human_review=true` 只允许用于 `design_input|architecture_review|architecture_approval`，并要求唯一 Owner、完整可访问材料、原子决定、建议、理由、置信度、备选后果和准确回复。访问确认、路由补充和内部操作不是 Review；无法自动解决的范围/Owner 缺口以新任务指令边界报告。

### 3. Derived manifest 自动消费

Adapter 在首笔写入前生成 `architecture_operation_manifest_v1`，冻结 mandate ref、Skill revisions、输入/输出 digests、目标、ordered writes、postconditions、retained objects、attempt 与 supersession。它只要与 current mandate 和平台 readback 一致就自动单次消费；漂移则保留对象并失败关闭，不请求用户授权修复。

### 4. 状态表示真实工作

- preparation、delivery、有效回复处理：`in_progress --no-start`
- current 方案 Review 成功交付：`in_review --no-start`
- 仍有 Agent 自动恢复路径：保持 `in_progress`
- 无 Agent 或 human 可执行路径：`blocked`

### 5. Legacy authorization 只读兼容

既有 `multica_operational_scope_v1`、`AUTHORIZE OPERATION` 和相关 request 保留为历史解析与审计格式。新 mandate 不生成、不消费这些 token；激活后由新的 attempt supersede 未消费旧请求。

## Risks / Trade-offs

- mandate 过宽：强制绑定单一 stage/attempt 和允许操作类别。
- 自动 retry 重复评论：manifest 单次消费、current delivery 唯一性和 attempt 上限。
- 客户端可访问性无法证明：记录 evidence gap；不把用户变成 operational approver。
- 历史协议与新协议并存：所有 legacy 模板醒目标记 audit-only，新路径禁止渲染。

## Migration Plan

1. 更新 portable core 契约和模板。
2. 更新 adapter manifest、自动交付、状态与 decision consumption 契约。
3. 严格验证 OpenSpec、现有 Skill safety/contract tests 与 quick validation。
4. 打包激活既有 Agent 后，以新 attempt supersede UNIDRAG-12 旧式请求。

## Open Questions

无。
