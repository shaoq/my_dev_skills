## MODIFIED Requirements

### Requirement: Human access 必须由完整客户端渲染证明
系统 SHALL 仅在具名 verifier 对 canonical Design 的目标人类入口执行 actual UI activation，并看到准确完整的 human-readable rendering 后，把对应 scope 记录为 `opened`。`owner_manual` 可以在准确 Design identity/digest、稳定入口和唯一 Owner policy 通过后记录 `manual_check_required`，但不得声称 `opened`。Research、Control、Review、Packet、continuation 与 handoff 只需 machine readback，不得作为内容决定的额外 human-rendering 前提。download-only、raw-byte fetch、HTTP 200、digest 一致或本地文件存在 MUST NOT 单独证明 Design 已被人类打开。

#### Scenario: Design Markdown attachment preview 成功
- **WHEN** verifier 激活当前 Design attachment 并确认完整正文与准确 identity
- **THEN** 系统可将该 Design/client scope 记录为 `opened`，并单独保留 raw-byte digest 证据

#### Scenario: 点击只触发下载
- **WHEN**入口只下载 Design 或 verifier 只 fetch 原始字节
- **THEN** 系统记录 `unavailable|manual_check_required|not_run` 中符合当前 profile 的状态，且不得伪造 `opened`

#### Scenario: Internal evidence is not rendered
- **WHEN** Review、Control 或 Packet 完成 machine identity/digest/readback 但未在客户端打开
- **THEN** 其状态不阻止已经满足 Design access 的人类内容决定

### Requirement: Portable continuation 必须保持真实执行连续性
`execution_continuation_v2` SHALL 绑定唯一 work item/stage/attempt、非终态 next actor/authority/responsibility、单项 action、input refs、closing condition、state、evidence mode、evidence refs 和 supersession。除 terminal 外 MUST NOT 使用空 next actor；`accepted|active` 必须有 `local_session|shared_artifact|runtime_task|human_response` 的可回读 evidence。continuation、Agent handoff 和 readback MUST default to `architecture_internal_evidence_v1` and MUST NOT require a dedicated human timeline comment.

#### Scenario: 同会话继续
- **WHEN** current standalone invocation 继续下一 action
- **THEN** local-session evidence 完整后 continuation 可为 active，且不发布进度评论

#### Scenario: 跨会话尚未触发
- **WHEN** 只有 Next Owner 或计划文字而没有 invocation/claim
- **THEN** continuation 保持 planned，不能声称仍在执行，也不能用人类评论冒充 task acceptance

#### Scenario: Blocked continuation
- **WHEN** next path 是 dependency input
- **THEN** state=blocked、next responsibility=dependency_input、next actor 等于 current instruction owner，并仅在自动 discovery 无法关闭时发布人类 action

## ADDED Requirements

### Requirement: Human timeline only carries decision-relevant milestones
The workflow SHALL keep Research progress, Control transitions, packet/readiness, digest verification, continuation, Agent handoff/readback, reconciliation, retry and status-projection readback in `architecture_internal_evidence_v1`. It MAY write an ordinary human timeline entry only for unresolved dependency input, a human architecture-content decision, a new canonical Design delivery/supersession, a final approved handoff summary, or a true blocked/rejected/terminal summary. Each logical milestone MUST produce at most one current human entry unless a new Action or Design version supersedes it.

#### Scenario: Agent hands work to another Agent
- **WHEN** the next runtime task is accepted or active and no human decision is required
- **THEN** the workflow records payload/result/readback internally and writes no dedicated handoff comment

#### Scenario: Internal retry succeeds
- **WHEN** delivery reconciliation or status readback is repaired without changing Design or human action
- **THEN** the workflow updates internal evidence and does not post a progress comment

#### Scenario: Human decision is genuinely required
- **WHEN** automatic work cannot resolve one dependency input or architecture-content choice
- **THEN** the workflow publishes one current actionable human entry and suppresses machine-only fields from its primary content
