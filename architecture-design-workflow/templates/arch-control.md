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
- 输入版本：
- 预期产物：
- Evidence：
- Next action：
- Next Owner：

## Reviewable clarification request

仅当下一动作要求可识别人类补充一个或多个设计决定时填写；没有澄清请求时写 `n/a`。每个决策项复制以下结构：

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
