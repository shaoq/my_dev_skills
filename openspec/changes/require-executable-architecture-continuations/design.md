## Context

portable workflow 已能描述 stage、human gate 和 status intent，Multica adapter 已能自动交付、投影状态和消费有效回复，但二者都缺少“当前 Agent 结束后谁真正继续”的强制 postcondition。UNIDRAG-12 证明 `Next Owner=Architecture Lead` 和 Issue `in_progress` 不能替代实际 task；普通 ARCH-CONTROL 自 mention 还触发了一次无实际工作的 no-op run。

## Goals / Non-Goals

**Goals:**

- 提供完全平台无关的 continuation envelope，使 standalone core 能表达下一执行责任和证据。
- 由 Multica adapter 将 envelope 映射为独立 member handoff、task accepted/active 与 readback。
- 通过契约测试阻止 orphaned in_progress、嵌入式自触发和重复 handoff。

**Non-Goals:**

- 不让 portable core 依赖 Multica status、UUID、mention URL、CLI 或 task schema。
- 不修改 Multica core，不实现 watchdog，不新增平台资源。
- 不把 Agent handoff 误分类为 `requires_human_review=true`。

## Decisions

### 1. 新增 portable `execution_continuation_v1`

envelope 使用平台中立字段：`continuation_id`、`next_executor_ref`、`next_executor_role`、`action`、`input_artifact_ref`、`input_artifact_version`、`completion_condition`、`state`、`evidence_ref`。`state` 仅为 `planned|accepted|active|waiting_human|blocked|terminal`，避免泄漏 Multica `queued|running` 枚举。

当 `platform_status_intent=agent_working` 且 current task 将结束时，continuation 必须为 `accepted|active` 并有可重读 evidence；否则不得报告完成。

### 2. Adapter 使用 `multica_execution_handoff_v1` 投影

adapter 从 portable envelope 与只读 member/task 事实派生 handoff，冻结 exact member ID、comment body/digest、`handoff_id`、attempt、task selector 和 postcondition。handoff comment 必须独立于 ARCH-CONTROL；写入后按准确 Issue、Agent、handoff ID 回读 task ID/status。`queued` 为 accepted、`running` 为 active；`waiting_local_directory` 只有在 runtime 在线、attribution 准确、predecessor 是当前 task 且同一 `in_place` 目录锁证据可重读时为 accepted，允许前序释放目录。

### 3. self-handoff 也是有界的跨 task 交接

self-handoff 不通过 ARCH-CONTROL 自 mention隐式完成。它必须使用独立评论、新 continuation/handoff ID、准确 Lead mention、单一闭包条件和 single-consumption fence。这样既能唤醒 Lead，又不会把普通状态记录变成无限递归触发器。

### 4. 失败状态映射

adapter 仅在 task readback 具有 accepted/active 证据时把 portable `accepted|active` 投影为 `in_progress`。无法取得该证据但仍有当前 Agent 恢复路径时由当前 task继续处理；等待真实人类决定时为 `in_review`；无 Agent/human 路径时为 `blocked`；完成时为终态。

## Risks / Trade-offs

- [平台事件可能延迟] → 使用有界 readback/reconciliation；上限内未出现 task 就不宣称交接完成。
- [同一 comment 重放] → handoff/continuation ID single-consumption，并将 existing task 视为成功回读而非再次创建。
- [portable state 与平台状态混淆] → core 只使用 `planned|accepted|active|waiting_human|blocked|terminal`，映射细节限定在 adapter。
- [契约只由文档驱动] → 添加结构化 fixtures 和静态契约测试，并在实际 UNIDRAG-12 上做一次 live readback。

## Migration Plan

1. 先添加 RED fixtures/contract assertions。
2. 更新 portable core reference/template，再更新 adapter manifest/handoff reference。
3. 运行 targeted/full/safety/quick validation。
4. 将两个既有 Skill overwrite 同步到 Multica 并回读 digest/binding。
5. 用新 handoff attempt 继续 UNIDRAG-12；失败则保留历史，不删除/编辑旧评论。

## Open Questions

无。Multica 的具体下一成员由 Architecture Lead 根据 current evidence gap 选择，adapter 只负责验证其唯一性与 accepted/active 事实。
