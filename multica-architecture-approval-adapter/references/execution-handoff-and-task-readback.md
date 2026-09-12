# Multica execution handoff and task readback

## Purpose

`multica_execution_handoff_v2` 是 portable `execution_continuation_v2` 的内部平台投影。它把 actor/responsibility 唯一映射到既有 Agent，通过 internal task evidence 触发并回读下一 task；正常 handoff 产生 zero ordinary Issue comments，始终 `requires_human_review=false`。

## Frozen internal envelope

```text
handoff_profile=multica_execution_handoff_v2
evidence_surface=architecture_internal_evidence_v1
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
trigger_surface=internal task evidence
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

Adapter 按 current workspace directory 从 `next_actor_ref + authority + responsibility` 唯一解析 Agent。映射缺失、冲突或多值时 fail closed，不按显示名、assignee、最近作者或空闲状态猜测。

## Acceptance gate

写入内部 task request 前重读 workspace、Issue、Agent、continuation、attempt、retained evidence 和 candidate tasks；写后只接受准确 attribution 的 `queued|running`，或 runtime online、predecessor=current task 且 same `in_place` directory lock evidence 可回读的 `waiting_local_directory`。

`queued|waiting_local_directory` 映射 portable `accepted`，`running` 映射 `active`。只有 `accepted|active` 才允许当前 task 结束并保持 `in_progress + WAIT_REASON=none`。self-handoff 也使用新 attempt、唯一 ID、单一 action 和独立 evidence，但仍不发评论。

handoff ID single-consumption；重放回读既有 task 并 reconciliation no-op。未入队、错误 authority、stale attempt 或不可读 evidence 必须继续当前恢复路径或转为真实 `waiting_human|blocked|terminal`，不得伪造执行者。

## Legacy reader

历史 `multica_execution_handoff_v1` dedicated handoff comment 只读保留，不删除、不重触发、不转换为 v2。current writer 不生成 dedicated Agent handoff comment。
