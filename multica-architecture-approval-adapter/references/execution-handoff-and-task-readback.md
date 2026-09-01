# Multica execution handoff and task readback

## Purpose

`multica_execution_handoff_v1` 是 portable `execution_continuation_v2` 在一个准确既有 Multica Issue 上的自动投影。它把 generic actor/responsibility 映射到既有 Agent，证明下一 task 已被平台接收；普通 mention、Next Owner 或状态更新不能代替 task readback。handoff 始终 `requires_human_review=false`。

## Frozen handoff envelope

```text
handoff_profile=multica_execution_handoff_v1
handoff_id=<issue-id>:<stage>:<attempt>:<continuation-id>
continuation_id=<portable-continuation-id>
workspace_id=<existing-workspace-id>
issue_id=<existing-issue-id>
next_actor_ref=<portable actor ref>
next_actor_authority_ref=<portable authority ref>
next_responsibility=<portable responsibility>
next_agent_id=<exact existing Agent id>
action=<one bounded task>
input_artifact_refs=<stable current refs>
completion_condition=<observable closing condition>
trigger_surface=dedicated handoff comment
requires_human_review=false
queued_task_id=<platform task id or none>
queued_task_status=<queued|waiting_local_directory|running|none>
accepted_task_status=queued|waiting_local_directory
active_task_status=running
predecessor_task_id=<current task id or none>
directory_lock_evidence_ref=<same in_place directory lock evidence or none>
readback_evidence_ref=<exact task readback ref>
supersedes=<older handoff id or none>
```

Adapter 先按 current workspace Team directory 将 `next_actor_ref + next_actor_authority_ref + next_responsibility` 唯一映射到一个既有 Agent。映射缺失、冲突或多值时不得按显示名、assignee、最近作者或空闲状态猜测；应发布/保持 actionable blocker。

## Dedicated comment and self-handoff

dedicated handoff comment 必须准确 mention `next_agent_id` 对应的唯一 Agent，并完整呈现 handoff ID、responsibility、action、input artifact refs 与 completion condition。它与 `ARCH-CONTROL`、Decision Brief、Review 回复和 task-result 分离。普通控制评论内的自 mention/成员 mention 必须 `no_trigger`。

当下一 actor 就是当前 actor 时仍使用独立 self-handoff、新 attempt、唯一 handoff ID、单一 action 和 completion condition。self-handoff 与跨成员 handoff 使用相同 single-consumption fence。

## Trigger and readback postcondition

写入前重读 workspace、Issue、Agent directory、continuation、attempt、retained comments 和 candidate tasks。写入后执行有界 readback，只接受同时满足：

- 同一 workspace/Issue；
- assignee/runner 为 `next_agent_id`；
- attribution 含准确 handoff ID、continuation ID、actor、responsibility 和 attempt；
- task 在 handoff comment 后创建；
- task 为 `queued|running`；或为 `waiting_local_directory` 且 runtime 在线、`predecessor_task_id` 是当前 task，并有 `same in_place directory lock` evidence。

`accepted_task_status=queued|waiting_local_directory` 映射 portable `accepted`；`active_task_status=running` 映射 portable `active`。只有 `accepted|active` 才允许当前 task 结束并保持 `in_progress + WAIT_REASON=none`。`queued_task_id`、实际状态、predecessor、锁证据和 readback evidence 必须记录。

## Replay and failure closure

handoff ID 是 single-consumption。已有匹配 task 时复用 evidence 并 reconciliation no-op；completed 历史不能证明后续仍执行。

若映射失败、mention 未触发、task 未入队、attribution 不完整、attempt 漂移或目录锁不可证明，continuation 不得成为 accepted/active。当前 actor 可恢复时继续当前 task；需要依赖输入时投影 actionable blocker；真实方案决定时进入 `in_review`；终结时进入 terminal。任何失败路径都不得遗留 orphaned `in_progress + WAIT_REASON=none`。
