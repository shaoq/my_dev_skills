# Portable execution continuation

## Purpose

`execution_continuation_v2` 证明非终结架构动作结束前，下一执行路径已有唯一 actor、职责、输入、完成条件和可回读接收证据。它不依赖 Team 拓扑、部署角色或具体平台；Next Owner、普通消息和 planned intent 都不能代替实际接收。

### v2 canonical fields

```text
continuation_profile=execution_continuation_v2
continuation_id=<single-consumption portable identity>
work_item_ref=<current architecture work item>
stage=<current canonical stage>
attempt=<current attempt>
next_actor_ref=<unique portable actor identity>
next_actor_authority_ref=<authority identity for this action>
next_responsibility=<coordination|research|solution_design|independent_review|dependency_input|human_decision|downstream_delivery>
action=<one bounded next task>
input_artifact_refs=<one or more stable current refs>
completion_condition=<one observable bounded condition>
state=planned|accepted|active|waiting_human|blocked|terminal
execution_evidence_mode=local_session|shared_artifact|runtime_task|human_response
evidence_refs=<rereadable execution evidence or none>
blocker_action_ref=<current blocker ref or none>
supersedes=<older continuation identity or none>
```

`planned` 只表示路径已计算。`accepted|active` 必须有准确 `evidence_refs`，分别证明执行环境已接收或正在执行。`waiting_human` 只对应真实内容决定；`blocked` 必须绑定 current actionable blocker；`terminal` 表示当前 work item 无后续动作。

## Completion gate

当 `platform_status_intent=actor_working` 且当前动作将结束时，必须同时满足：

1. `next_actor_ref`、authority 与 `next_responsibility` 唯一且匹配 current binding；
2. action、输入 artifact refs 和 `completion_condition` 单一、有界、current；
3. continuation ID 对 work item/stage/attempt 唯一且未消费；
4. execution environment 回读同一 continuation 为 `accepted|active`；
5. evidence refs 绑定准确 continuation、actor、responsibility 和 action。

当前会话可用 `local_session`，跨会话可用 `shared_artifact`，任务运行时可用 `runtime_task`，真实人工决定可用 `human_response`。除 terminal 外不得留下空 actor；跨会话 shared artifact 尚无有效 claim 时只能为 `planned`。`blocked` continuation 的 next actor 必须是 blocker 的 instruction owner，`next_responsibility=dependency_input`；若该 actor 未绑定，返回 `needs_new_mandate_v1`，而不是猜测部署角色。

## Replay, migration and self-continuation

同一 continuation ID 只消费一次。重复事件回读既有 evidence 并 reconciliation no-op。下一 actor 与当前 actor 相同也必须建立新 continuation/attempt、单一 action 和独立 evidence。

reader 执行 v1 dual-read；continuation writer 执行 v2-only write。历史 `execution_continuation_v1` 中 `next_executor_ref` 可映射为 actor，legacy role 只能经显式 profile 映射为 responsibility；未知或冲突时 fail closed，并创建 v3 blocker/v2 continuation，不猜测。

execution continuation 始终 `requires_human_review=false`。它不批准方案、不改变 Review conclusion，也不授权新资源、业务实现、部署、采购或跨 work item 写入。
