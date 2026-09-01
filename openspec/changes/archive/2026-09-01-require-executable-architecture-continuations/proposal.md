## Why

当前 architecture workflow 可以把有效人工回复自动恢复为 `in_progress`，但并未强制证明下一名 Agent 的 task 已被平台接受。UNIDRAG-12 因而出现 Issue 显示进行中、所有 Agent 空闲、没有明确执行任务的 orphaned execution 状态。

## What Changes

- 在 portable `architecture-design-workflow` 中增加平台无关的 execution continuation contract，区分下一执行者、任务、输入、关闭条件、连续性状态和证据引用。
- 规定非终结工作处于 `agent_working` 意图时，当前步骤只有在下一工作已有 accepted/active evidence 后才能完成；否则必须继续执行、等待人工、显式 blocked 或进入终态。
- 在可选 `multica-architecture-approval-adapter` 中把 portable continuation 投影为独立的精确 member handoff、唯一 `handoff_id`、task 接受和 ID/status/readback；同目录串行等待必须绑定当前前序 task 与目录锁证据。
- 对 self-handoff 使用独立且有界的单次触发，不允许从普通 `ARCH-CONTROL` 中的自 mention 推断已接单。
- 增加 orphaned `in_progress`、无效自触发、跨成员 handoff、有效 self-handoff 和 fail-closed 状态的契约回归测试。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `architecture-workflow-operation-automation`: 增加 portable execution continuation、Multica 精确 handoff、task readback 和无人接单失败关闭要求。

## Impact

- `architecture-design-workflow/SKILL.md` 及其 workflow mandate、control template/reference。
- `multica-architecture-approval-adapter/SKILL.md` 及 operation manifest/handoff reference。
- `tests/test_multica_architecture_approval_adapter_contract.py`、core safety checks 和相应 fixtures。
- 不修改 Multica 核心代码；adapter 仍为 optional sibling，portable core 不依赖 Multica 名词、ID、CLI 或状态枚举。
