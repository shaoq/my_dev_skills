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
