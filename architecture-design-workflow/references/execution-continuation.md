# Portable execution continuation

## Purpose

`execution_continuation_v1` 证明一个非终结架构步骤在当前执行者结束后仍有准确、已接收的下一执行路径。它与 stage、Human Action 和 Review gate 正交；Next Owner 文本、角色分配、建议、普通消息或“稍后继续”不能代替该证据。

本契约只使用 portable identity、artifact ref 与 execution evidence。具体平台如何通知执行者、生成任务或显示状态，由 optional adapter/runtime 负责；standalone Runtime 可以用当前会话、共享队列或其他可重读执行记录满足相同语义。

## Canonical envelope

```text
continuation_profile=execution_continuation_v1
continuation_id=<single-consumption portable identity>
work_item_ref=<current architecture work item>
stage=<current canonical stage>
attempt=<current attempt>
next_executor_ref=<unique portable actor or role identity>
next_executor_role=<Architecture Lead|Architecture Analyst|Solution Architect|Architecture Reviewer>
action=<one bounded next task>
input_artifact_ref=<stable current input ref>
input_artifact_version=<current input version>
completion_condition=<observable bounded condition>
state=planned|accepted|active|waiting_human|blocked|terminal
evidence_ref=<rereadable execution evidence or none>
supersedes=<older continuation identity or none>
```

`planned` 只表示下一任务已确定，不能证明有人接单。`accepted|active` 分别表示执行环境已经接收或正在执行，并且必须有准确 `evidence_ref`。`waiting_human|blocked|terminal` 表示下一推进路径不是 active Agent work。

## Completion gate

当 `platform_status_intent=agent_working` 且当前执行任务将结束时，必须同时满足：

1. `next_executor_ref` 唯一并与角色责任匹配；
2. action、输入 artifact/version 和 completion condition 均为单项、current 且可验证；
3. continuation ID 对本 work item/stage/attempt 唯一且未消费；
4. 执行环境回读同一 continuation，state 为 `accepted|active`；
5. evidence ref 可重读并绑定准确 continuation、执行者与任务。

任何一项不满足，当前执行者不得报告工作成功完成。仍有本执行者可用的确定性恢复路径时继续处理；确实等待方案决定时用 `waiting_human`；没有 Agent 或 human 可执行路径时用 `blocked`；已完成时用 `terminal`。

## Replay and self-continuation

同一 continuation ID 只能消费一次。重复事件必须回读既有 evidence 并 reconciliation no-op，不得创建第二个执行任务。下一执行者与当前执行者相同也不降低要求：必须形成新的 continuation/attempt、一个有界 action 和独立可回读 evidence；普通控制记录中的角色名或自引用不构成 self-continuation。

execution continuation 是自动工作编排证据，始终 `requires_human_review=false`。它不批准方案、不改变 Review conclusion，也不授权资源创建、业务实现、部署、采购或跨 work item 写入。
