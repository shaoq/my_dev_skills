# Multica execution handoff and task readback

## Purpose

`multica_execution_handoff_v1` 是 portable `execution_continuation_v1` 在一个准确既有 Multica Issue 上的自动投影。它证明下一名 Architecture Agent 的实际 task 已被平台接收，而不是只在 `ARCH-CONTROL` 中写了 Next Owner、改变 Issue status 或发布普通 mention。

handoff 始终 `requires_human_review=false`，属于 current workflow mandate 内的非 Review 自动操作，不请求 `AUTHORIZE OPERATION`。

## Frozen handoff envelope

```text
handoff_profile=multica_execution_handoff_v1
handoff_id=<issue-id>:<stage>:<input-artifact-version>:<attempt>
continuation_id=<portable-continuation-id>
workspace_id=<existing-workspace-id>
issue_id=<existing-issue-id>
next_executor_id=<exact existing Agent id>
next_executor_role=<Architecture role>
action=<one bounded task>
input_artifact_ref=<current stable ref>
input_artifact_version=<current version>
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

评论正文必须精确 mention `next_executor_id` 对应的一个 Agent，并完整呈现 handoff_id、角色、action、输入 artifact/version 和 completion condition。不得包含第二个 Agent mention，也不得把 Decision Owner mention 当作执行交接。

## Dedicated comment and self-handoff

handoff 必须使用 dedicated handoff comment，与 `ARCH-CONTROL`、artifact、Decision Brief、Review 回复和 task-result 评论分离。普通 `ARCH-CONTROL` 内的任何 Architecture Lead 自 mention 或下一成员 mention都不是有效触发表面，必须 `no_trigger`。

当下一执行者就是当前 Architecture Lead 时，仍使用独立 self-handoff、新 attempt/唯一 handoff ID、单一 action 和 completion condition。self-handoff 与跨成员 handoff 使用相同的 single-consumption fence；不得通过复用旧 handoff、在普通控制评论中提到自己或递归发布多个评论维持运行。

## Trigger and readback postcondition

写入前重读 exact workspace、Issue、current Agent directory、portable continuation、attempt、retained comments 和 candidate tasks。写入后执行有界 readback，只接受同时匹配以下字段的 task：

- 同一 Issue/workspace；
- assignee/runner 为 `next_executor_id`；
- task attribution 包含准确 handoff_id、continuation_id 和 attempt；
- task 在 handoff comment 之后创建；
- task 状态为 `queued|running`；或为 `waiting_local_directory` 且 runtime 在线、task attribution 准确、`predecessor_task_id` 是当前 task，并有 `same in_place directory lock` 的可重读 evidence。其他目录等待不能推断为已接收。

`accepted_task_status=queued|waiting_local_directory`：匹配 `queued` 时直接 accepted；匹配 `waiting_local_directory` 时，只有上述前序目录锁关系全部成立才 accepted，因为当前 task 释放目录正是其可观察启动条件。`active_task_status=running` 时 portable state 为 active。`queued_task_id`、实际状态、predecessor、目录锁证据和 readback evidence ref 必须写入 task evidence。只有完成该回读，当前 task 才能结束并保持 `in_progress + WAIT_REASON=none`。

## Replay and failure closure

handoff ID 是 single-consumption。若已有匹配 task，则复用其 evidence 并 reconciliation no-op，不再发布第二个 handoff。若已有 task 已完成，必须从其 current result 派生新的 continuation；completed 历史本身不能证明后续仍在执行。

有界 readback 找不到匹配 task、目标不唯一、mention 未触发、attempt/version 漂移、task attribution 不完整，或 `waiting_local_directory` 无法证明只等待当前前序 task 的同一目录锁时，continuation 不得成为 accepted/active。当前 Agent 仍可恢复时继续当前 task；真实等待方案决定时进入 `in_review`；不存在 Agent/human 路径时进入 `blocked` 并记录 Owner/closing condition；已完成则进入终态。任何失败路径都不得遗留 orphaned `in_progress + WAIT_REASON=none`。
