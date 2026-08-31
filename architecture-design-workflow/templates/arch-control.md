# ARCH-CONTROL

## Identity

- Issue：
- 版本：
- Owner：
- Subject Project：
- 设计类型：`evolution|greenfield|hybrid`
- 当前 stage：
- Status：

## Control fields

- `WAIT_REASON`：`none|design_approval|target_project`
- Workflow mandate ref / profile：`<ref>|none` / `architecture_workflow_mandate_v1|none`
- Workflow attempt / allowed operations / invalidation：
- `BLOCKED_REASON`：`none|missing_subject_project|missing_target_project|missing_openspec_explore|missing_brainstorming|critical_evidence_gaps|review_packet_unavailable|approved_artifact_unavailable`
- Review conclusion：`none|BLOCKED|NEEDS_REVISION|APPROVABLE_WITH_WARNINGS|APPROVABLE`
- Current packet ref / version / digest：
- Current packet external status：`none|delivered|superseded`
- Packet readiness：`none|review_packet_ready|review_packet_unavailable`
- Readiness / unavailable evidence ref：
- Target human / access confirmation ref：
- `ARCHITECTURE_RECOMMENDATION`：`none|recommend_approved_for_spec|recommend_approved_design_only|recommend_revision|no_recommendation`
- Human gate：`none|approved_design_only|approved_for_spec|revision_requested|rejected`
- Human decision evidence：actor、packet ref/version/digest、binding profile、evidence ref、recorded_at
- Revision scope：`n/a|missing|provided`
- Revision brief ref / access evidence：
- 输入版本：
- 预期产物：
- Evidence：
- Next action：
- Next Owner：

## Execution continuation

终结状态或当前正在等待真实人工决定时填写相应 `terminal|waiting_human`；其他非终结工作不得只写 Next Owner：

- Continuation profile / ID：`execution_continuation_v1` / `<id>`
- Next executor ref / role：
- Action：
- Input artifact ref / version：
- Completion condition：
- Continuation state：`planned|accepted|active|waiting_human|blocked|terminal`
- Continuation evidence：`<rereadable-ref>|none`
- Supersedes：`<continuation-id>|none`

当 `platform_status_intent=agent_working` 且当前 task 将结束时，Continuation state 必须为 `accepted|active` 且 Continuation evidence 可重读。Next Owner、普通控制文本或 planned 状态均不能代替已接收的下一执行任务。

## Current human actions

没有人工动作时写 `n/a`。每个原子动作重复一份条目；不得合并不同 Decision Owner：

- Human Action Request ref / action ID：
- Action type：`design_input|architecture_review|architecture_approval`
- Requires human review：`true`
- Decision Owner / authority scope：
- Why now：
- Atomic decision：
- Candidate recommendation：
- Stable human-accessible evidence refs：
- Exact response ref：
- After-response projection：next stage / remaining blockers / Next Owner / planned writes
- Current / superseded：`current|superseded`

Human Action Request 不新增 canonical artifact type 或 `planned_writes` 目标；随控制评论呈现时 normalized write 仍为 `issue:ARCH-CONTROL`。

## Reviewable clarification request

仅作为历史兼容投影；新的人工动作以独立 Human Action Request 为准。下一动作要求可识别人类补充一个或多个设计决定时填写；没有澄清请求时写 `n/a`。每个决策项复制以下结构：

- Decision required：
- Candidate recommendation：具体候选值；或 `no_recommendation` 及原因
- Basis：事实、推断或适用原则
- Material risks / consequences：
- Missing evidence / Owner / closure condition：
- Editable response：`接受：<item>` / `修改：<item>=<value>` / `拒绝：<item>，原因=<reason>`

评论中同时声明：候选建议及 `接受 / 修改 / 拒绝` 回复只处理这里列出的设计输入，属于非批准信息；不得替代测量证据、其他责任 Owner 的决定、Review conclusion、packet readiness、`ARCHITECTURE_RECOMMENDATION` 或准确 packet ref/version/digest 的 human decision。

## Role assignment

| Role | Owner | Handoff evidence |
|---|---|---|
| Architecture Lead |  |  |
| Architecture Analyst |  |  |
| Solution Architect |  |  |
| Architecture Reviewer |  |  |

## Transition log

| From | Decision/evidence | To | Owner | Time/message |
|---|---|---|---|---|

Delivered packet payload 不随 external status、readiness 或 human decision 更新；这里只保存 projection 和 evidence refs。

## Evidence limitations

- 无；或列出不能验证的来源及其影响。
