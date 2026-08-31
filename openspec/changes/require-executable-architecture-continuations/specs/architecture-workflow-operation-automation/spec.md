## ADDED Requirements

### Requirement: Portable workflow 必须表达执行连续性

portable core SHALL 用平台无关的 `execution_continuation_v1` 表达准确下一执行者引用与角色、单项任务、输入 artifact/version、关闭条件、continuation state 和 evidence ref。core MUST NOT 依赖 Multica member UUID、mention、CLI、Issue status 或 task 枚举。

#### Scenario: standalone workflow 继续 Agent 工作
- **WHEN** 当前步骤非终结、无需人工决定且 `platform_status_intent=agent_working`
- **THEN** 当前 Agent 结束前必须证明 continuation 为 `accepted|active` 且 evidence ref 可重读，否则不得报告该步骤成功完成

#### Scenario: standalone workflow 等待其他路径
- **WHEN** 下一状态是真实人工决定、无可执行路径或工作终结
- **THEN** continuation 分别记录 `waiting_human`、`blocked` 或 `terminal`，不得伪装为 active Agent work

### Requirement: Multica adapter 必须产生可执行 handoff 和 task 回读

adapter SHALL 将 current portable continuation 投影为独立的 `multica_execution_handoff_v1`，使用准确 member mention、唯一 `handoff_id` 和 attempt 触发一个 bounded task，并在完成当前 task 前回读匹配的 task ID 与 accepted/active 状态。`queued` 为 accepted，`running` 为 active；`waiting_local_directory` 仅在 runtime 在线、attribution 准确、predecessor 是当前 task 且同一 `in_place` 目录锁证据可重读时为 accepted。Agent handoff MUST 始终是非 Review 自动操作。

#### Scenario: handoff 到另一成员
- **WHEN** portable continuation 指向唯一的另一个现有 Architecture Team member
- **THEN** adapter 发布独立 handoff、精确 mention 该 member，并将匹配 task ID/status 记录为 continuation evidence

#### Scenario: Architecture Lead self-handoff
- **WHEN** portable continuation 的下一执行者仍是当前 Lead
- **THEN** adapter 使用独立 self-handoff 评论、新 handoff ID 和 single-consumption fence 入队一个任务；普通 ARCH-CONTROL 内的 Lead mention 不得作为 handoff

#### Scenario: 重复 handoff 被重放
- **WHEN** 同一 handoff ID 已有匹配 queued/running/completed task
- **THEN** adapter reconciliation 复用该证据并 no-op，不再触发第二个 task

#### Scenario: 同目录下游等待前序释放
- **WHEN** 精确下游 task 为 `waiting_local_directory`，且证据证明它只等待当前前序 task 持有的同一 `in_place` 目录锁
- **THEN** adapter 将 continuation 记为 accepted，记录 task/predecessor/lock evidence，并允许当前 task 结束以释放目录；不得要求下游先 running 形成死锁

#### Scenario: mention 没有产生可接受任务
- **WHEN** 有界 readback 未找到匹配 Issue、member 和 handoff ID 的 accepted/active task，或目录等待缺少准确前序锁证据
- **THEN** adapter 不得把连续性标为 accepted/active，也不得遗留 orphaned `in_progress + WAIT_REASON=none`；它必须继续当前恢复、进入真实 `in_review`、投影 `blocked` 或终态
