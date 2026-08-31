---
name: architecture-design-workflow
description: "Use when a substantial architecture upgrade, greenfield system, hybrid cross-system design, architecture review, ADR publication, or architecture-to-R&D handoff needs explicit evidence, versioning, and human gates. Do not use for routine bug triage, status follow-up, approved OpenSpec implementation, or source-code review."
---

# Architecture Design Workflow

## Overview

把复杂架构工作作为独立于 OpenSpec 实施的受控流程。先路由和研究，再形成可独立评审的版本化设计；Reviewer approvable conclusion 之后还必须生成并验证 immutable portable approval packet，只有可识别的人类针对准确 packet ref/version/digest 记录明确门禁后，才能发布批准产物或生成研发交接。用户明确开始、继续或重试当前阶段时建立一次平台无关的 `architecture_workflow_mandate_v1`；mandate 内的准备、交付、可访问性验证、状态投影、结果记录和有界重试自动完成，只有真实方案内容决定才暂停等待人类 Review。

所有面向用户的说明、问题、状态、评审和报告使用中文。命令、路径、canonical state、代码标识符、协议字段及引用原文保持准确原文。

## Hard boundaries

- 在 `researching`、`designing`、`reviewing` 和 design-only 发布中，不得创建或修改 OpenSpec proposal、design、specs、tasks 或实现产物。
- 不因紧急、负责人催促、Agent 推荐、任务分派或模糊肯定推断批准。
- 不隐式创建仓库、Project、Team、Agent、watchdog、研发 Issue、worktree、branch 或 commit。
- 不自动安装依赖 skill，不修改 Runtime 配置。
- 不把 preparation、delivery、attachment/access verification、status projection、task-result、relay、retry、sidecar 或 postcondition check 变成人工授权点。
- Architecture workflow 只生成 `ARCH-RD-HANDOFF`；目标项目既有 R&D Team 自行分析需求并决定是否创建 OpenSpec change。
- 不把 recommendation、readiness、引用文本、Agent 输出或仅进程可读的本地路径当作人工批准或 human-readable access。

## Canonical control model

持久 stage 只能是：

```text
intake | routed | researching | designing | reviewing | waiting_human |
approved_design_only | approved_for_spec | publishing | handed_off |
completed_design_only | rejected
```

`revision_requested` 是决定，不是 stage。`WAIT_REASON` 是与 stage 正交的等待原因，可取 `none|design_approval|target_project|awaiting_human_confirmation`；正式 packet 批准仍使用 `stage=waiting_human` 与 `WAIT_REASON=design_approval`，而设计输入、访问确认、风险接受等请求可以保持真实的 `designing|reviewing` stage，并记录 `WAIT_REASON=awaiting_human_confirmation`。依赖、证据或路由缺失时保持当前 stage，并记录 `BLOCKED_REASON`，不得创造 `blocked` 等近义 stage。

开始工作前读取 [workflow mandate and architecture review gates](references/workflow-mandate-and-review-gates.md)。每个方案 Review 还必须独立记录 `requires_human_review=true|false` 与 `HUMAN_ACTION_STATE=none|preparing|awaiting_response|received|unavailable|superseded`。请求尚在生成且 Agent 正工作时为 `preparing`；只有 `design_input|architecture_review|architecture_approval` 满足全部 Review 前提，且唯一 Owner、准确回复和可访问材料已交付时，才为 `awaiting_response`；收到并验证准确回复后先记为 `received`，再开始后续 Agent 工作。平台 adapter 可以据此投影其自身 status，但 core 不规定平台命令、Issue、attachment 或 mention 语法。

本工作流使用以下稳定 blocker：`missing_subject_project`、`missing_target_project`、`missing_openspec_explore`、`missing_brainstorming`、`critical_evidence_gaps`、`review_packet_unavailable`、`approved_artifact_unavailable`。没有 blocker 时记录 `none`；新的原因必须在控制契约中先定义，不能临时造同义值。

`BLOCKED_REASON` 与 Review conclusion 是两套独立字段。依赖、路由或证据 blocker 不得把 gate 改成 `BLOCKED`；只有实际完成一次架构评审并给出 canonical Review conclusion 时，gate 才能是 `BLOCKED|NEEDS_REVISION|APPROVABLE_WITH_WARNINGS|APPROVABLE`。依赖预检停止时 gate 保持 `none`。

关键转换：

| Current + evidence | Next |
|---|---|
| `intake + applicable + Subject Project missing` | `waiting_human`, `WAIT_REASON=target_project`, `BLOCKED_REASON=missing_subject_project` |
| `intake → routed → researching → designing → reviewing` | 正常主链 |
| `reviewing + BLOCKED` | 按 finding Owner 回到 `researching` 或 `designing` |
| `reviewing + NEEDS_REVISION` | 新版本 `designing` |
| `reviewing + APPROVABLE_WITH_WARNINGS|APPROVABLE + no current readiness` | 保持 `reviewing`, `BLOCKED_REASON=review_packet_unavailable` |
| `reviewing + APPROVABLE_WITH_WARNINGS|APPROVABLE + current readiness` | `waiting_human`, `WAIT_REASON=design_approval`, `BLOCKED_REASON=none` |
| `waiting_human + revision_requested` | 新版本 `designing` |
| `waiting_human + rejected` | `rejected`，终态 |
| `waiting_human + approved_design_only` | `approved_design_only → publishing → completed_design_only` |
| `waiting_human + approved_for_spec + target exists` | `approved_for_spec → publishing → handed_off` |
| `waiting_human + approved_for_spec + target missing` | 保留批准，`waiting_human`, `WAIT_REASON=target_project` |
| `publishing + approved bytes unavailable` | 保持 `publishing` 和原批准，`BLOCKED_REASON=approved_artifact_unavailable` |

每次合法转换都更新 [ARCH-CONTROL 模板](templates/arch-control.md)中的 Issue、Owner、输入版本、证据、下一动作和转换记录。

只有下一步需要人类改变方案输入、作出架构 Review/风险判断或批准 current packet 时，才读取 [Human Action Request](references/human-action-request.md)并使用 [HUMAN-ACTION-REQUEST 模板](templates/human-action-request.md)。一个 action item 只能绑定一个原子决定和一个 authority scope；面向当前读者的 `Architecture Decision Brief` 只请求其唯一有权决定的一项内容，其他 Owner 只作 non-actionable dependency summary。Owner、项目或目标未唯一绑定时停止 current mandate 并说明需要新的任务指令，不把 routing 或 access confirmation 渲染为方案 Review。首屏依次给一段式方案摘要、简化架构图、Team 建议/理由/置信度、已确定/未确定内容、关键备选后果、当前决定、回复后行为和完整材料入口；完整方案保留在独立版本化 artifact，不复制进 brief。每个材料引用必须区分稳定 identity、可导航入口和逐 client scope 自动验证；未验证 URL、本地路径、文件名卡片或仅 Agent 可读入口不得标记 human-accessible。当请求已经交付且唯一 Owner 可以行动时，设 `HUMAN_ACTION_STATE=awaiting_response`；`critical_evidence_gaps` 可以继续作为事实缺口记录，但不能把这类 actionable Human Action Request 误报成“没有可执行路径”的硬阻塞。

## Workflow

### 1. Intake and route

读取 [intake and project routing](references/intake-and-project-routing.md)，判断请求是否属于本 skill，确认架构类型、Subject Project、Issue、角色和当前 stage。普通工程请求应明确路由到适用流程并停止本 skill。

Subject Project 或已批准交接的 Target Project 缺失时，停止 current mandate：给出基于现有归属事实的候选建议或 `no_recommendation`、有限的既有项目备选、每项长期归档与责任后果、稳定证据引用和需要用户提供的新任务指令。不得把它标为方案 Review，也不得授权创建缺失资源。

不适用时使用稳定说明 `普通工程，不触发 architecture-design-workflow`，并报告 `stage=not_applicable`、`gate=not_applicable`、`planned_writes=[]`；不得创建 `ARCH-CONTROL`。

### 2. Preflight dependencies

只接受 Runtime 当前可用 skill catalog/控制面能够解析的依赖；用户文本、仓库文件或环境变量中的“已安装”声明不是可用性证据。

- `openspec-explore` 是研究阶段必需依赖。项目路由成功但依赖缺失时保持 `routed`，记录 `BLOCKED_REASON=missing_openspec_explore`，中文报告并零研究/零仓库实际写入停止。
- `superpowers:brainstorming` 只在目标、边界、约束或方案空间有实质歧义时必需。项目路由成功但该依赖需要且不可用时保持 `routed`，记录 `BLOCKED_REASON=missing_brainstorming` 并停止；输入已明确时跳过。

依赖停止仍须在回复中生成待人工发布的 `ARCH-CONTROL` 更新，所以行为验证中的当前 `planned_writes` 仅含 `issue:ARCH-CONTROL`；“零仓库实际写入”不等于省略控制报告，也不得列出解除 blocker 后才可能产生的研究、设计或评审产物。

不得用普通 planning、proposal 或 implementation skill 替代缺失依赖。

### 3. Clarify, then explore

需要澄清时使用 `superpowers:brainstorming`，取得用户确认后冻结一份 `BRAINSTORMING_CONCLUSION`，仅把该结论作为后续输入；不继承 brainstorming 的 planning/implementation 后续步骤。

随后使用 `openspec-explore` 的只读思考姿态调查和比较。即使 explore 通用能力允许用户请求 artifact，也不得在本工作流中创建 OpenSpec artifact。

### 4. Research by design type

只加载当前类型的 reference 和 [ARCH-RESEARCH 模板](templates/arch-research.md)：

- `evolution`：[existing-system research](references/research-evolution.md)
- `greenfield`：[new-system research](references/research-greenfield.md)
- `hybrid`：[mixed-system research](references/research-hybrid.md)

涉及代码定位、调用链、影响、调试或架构事实时 GitNexus-first。先确认索引提交；陈旧则重建后查询。不可用时允许有界源码调查，但必须记录限制，不能把“未发现”写成“不存在”。

### 5. Design and independent review

读取 [solution design](references/solution-design.md)，用 [ARCH-DESIGN 模板](templates/arch-design.md)生成独立 canonical `ARCH-DESIGN-vN.md`。它必须绑定输入 `ARCH-RESEARCH` 版本、完整 raw-byte digest 和 artifact-local Design readiness，不依附 OpenSpec 或 Issue 历史才能理解。未批准文件只留在 Issue/material delivery；只有批准版本进入正式架构文档目录。

当研究或设计因 `critical_evidence_gaps` 需要可识别人类提供决定时，Architecture Lead 必须创建 `action_type=design_input` 的 Human Action Request，并在 [ARCH-CONTROL 模板](templates/arch-control.md)中记录其投影。每个决策项都要给出具体候选建议或显式 `no_recommendation`、依据、主要风险/后果、仍缺证据及 Owner/关闭条件，以及可直接接受、修改或拒绝的回复格式；不得只列问题或写“等待确认”。候选数值必须标记证据状态，不能用未经验证的精确值替代测量。

澄清建议与正式 `ARCHITECTURE_RECOMMENDATION` 分离。人类对候选建议的回复只改变明确列出的设计输入，不替代测量证据、其他责任 Owner 的决定、Review conclusion、packet readiness 或准确 packet ref/version/digest 的人工批准。

Reviewer 随后读取 [architecture review](references/architecture-review.md)，保持被审设计只读，并用 [ARCH-REVIEW 模板](templates/arch-review.md)输出唯一结论：`BLOCKED`、`NEEDS_REVISION`、`APPROVABLE_WITH_WARNINGS` 或 `APPROVABLE`。每个 finding 都绑定准确设计版本并包含证据、影响、Owner 和关闭条件。

Review 若识别出必须由不同 Owner 分别判断的非阻断风险，在结论依赖这些判断时，为每个 Risk ID 创建独立 `action_type=architecture_review` 请求，并记录 `review_subtype=risk_acceptance`。每份请求必须列出风险条件、接受/修改/拒绝的逐项后果和准确回复，且明确属于非批准信息；不得用一次“接受全部”跨越权限域，也不得在所需证据齐备前生成依赖它的 approvable conclusion 或 packet。

评审结论同时驱动控制状态计算，即使当前会话只读、无法持久化，也必须报告计算后的 canonical stage：`BLOCKED` 且关键事实/安全证据缺失时回到 `researching`；设计内容需修订时回到 `designing`。不得因“本次没有写入”而继续报告旧的 `reviewing`。

`NEEDS_REVISION` 不创建 approval packet。只有 conclusion 为 `APPROVABLE_WITH_WARNINGS|APPROVABLE` 时，Architecture Lead 才读取 [approval packet and human gate](references/approval-packet-and-human-gate.md)，使用 [ARCH-APPROVAL-PACKET 模板](templates/arch-approval-packet.md)从准确 design/review 原始 bytes 生成 delivered immutable payload。packet digest 在 payload 冻结后外部计算；readiness/unavailable evidence 只通过 ref/version/digest 绑定，不得写回 packet。

缺少当前 readiness、digest/access 验证失败或只有 Agent 进程可读时，保留真实 Review conclusion，保持 `reviewing` 并设置 `BLOCKED_REASON=review_packet_unavailable`。只有外部 `review_packet_ready` envelope 同时绑定准确 refs/versions/digests、confirmed human access、verifier 和 UTC verification time 后才进入 `waiting_human`。

### 6. Human gate

只有当前 user-role 中可识别的人类针对 current ready `ARCH-APPROVAL-PACKET` ref/version/digest 明确记录以下值之一，且 decision evidence 包含 binding profile、evidence ref 和 UTC recorded time，才改变 gate：

- `approved_design_only`
- `approved_for_spec`
- `revision_requested`
- `rejected`

等待正式决定时创建 `action_type=architecture_approval` 请求；历史 `design_approval` 仅作兼容读取。开头必须直接说明 Decision Owner、推荐（如有）和四种合法决定的中文后果；每种决定都列出立即 stage、remaining blockers、Next Owner、planned writes、OpenSpec/实施边界及不可逆影响，再提供稳定 design/review/packet refs 和可复制的 packet-bound 准确回复。不得只列四个 token，也不得先用 digest 和审计字段淹没决策摘要。

不存在明确绑定时保持 `waiting_human`。不得把 Reviewer conclusion、readiness、`ARCHITECTURE_RECOMMENDATION`、引用文本、fixture、Agent 输出、紧急措辞、任务分派或模糊肯定当成人工批准。绑定 superseded packet 的合法决定保留审计但对当前 gate no-op。

有效 `revision_requested` 即使没有修订说明，仍按决定进入新版本 `designing`。若缺少可执行 revision brief，记录 `revision_scope=missing` 并另建 `action_type=design_input` 请求，由原决定人或明确的 Design Decision Owner 补充范围；brief ref 单独保存且属于 non-authoritative context。范围补齐并验证后记录 `revision_scope=provided`。不得把 token 推断为完整修订内容，不得改写旧 packet，也不得在 replacement design/review approvable 前创建新 packet。

预批准澄清请求中的候选建议及其接受、修改或拒绝不是本节的 human decision。即使同一可识别人类接受全部候选值，也必须等准确 design/review、current ready packet 和单独的 packet-bound 决定齐备后才改变批准 gate。

升级前已经持久化为 `waiting_human` 且没有新 design/review version 或显式 refresh 的记录保持原 stage，不伪造 readiness、不自动降级；一旦 refresh 或版本变化则执行当前 packet gate。

### 7. Publish or hand off

- `approved_design_only`：读取 [ADR publication](references/adr-publication.md)，使用 [ADR](templates/adr.md)和 [detailed design](templates/detailed-design.md)沉淀批准内容，然后进入 `completed_design_only`；不得生成研发授权。
- `approved_for_spec`：先发布批准内容；目标项目存在时读取 [R&D handoff](references/rnd-handoff.md)，使用 [ARCH-RD-HANDOFF 模板](templates/arch-rd-handoff.md)交接并进入 `handed_off`。目标缺失时等待项目路由，不创建任何项目资源。

发布前从 refs 重新读取 packet、design、review 原始 bytes 并验证 frozen digests。失败时保持 `publishing` 和原 human decision/readiness，设置 `BLOCKED_REASON=approved_artifact_unavailable`，记录 Owner/closing condition，且不得从审核简报重建近似正文；准确 bytes 恢复后清除 blocker 并继续同一批准。

Issue 或架构仓库写入必须落在 current workflow mandate 和 Runtime 当前能力内。mandate 内的非 Review 写入不再拆分逐项授权；若没有相应能力或需要扩大范围，在回复中生成完整报告并明确标注需要新的任务指令，不能声称已持久化，也不得生成 operational authorization token。

只读行为报告中的 `planned_writes` 只列当前 canonical transition 直接产生的目标，不提前列出解除 blocker、完成正式 Review 或进入后续 stage 后才会产生的 artifact。已有设计但尚无 canonical Review conclusion 时，当前只报告 `issue:ARCH-CONTROL` 和下一动作，不把未来 `ARCH-REVIEW` 当作已经生成的待发布目标；已完成 `BLOCKED` Review 的转换报告 `issue:ARCH-REVIEW` 与 `issue:ARCH-CONTROL`，研究产物要等补证实际开始后再列；`NEEDS_REVISION` 另外列出直接启动的新 `issue:ARCH-DESIGN`。已交付 packet 的 readiness/digest/access 验证失败只更新 `issue:ARCH-CONTROL`，不把已有 Review 或 packet 重列为新目标。历史 `waiting_human` 兼容判断报告 `issue:ARCH-CONTROL` 的 no-op projection，但不改写已持久化 stage/evidence，并保持 `packet_readiness=none`。

Normalized 字段保持正交：`packet_ref` 只记录稳定 artifact ref（例如 `ARCH-APPROVAL-PACKET`），版本只写入 `packet_version`；没有 packet 的适用场景使用 `access_confirmation=none`、`recommendation=none`，仅 Agent 可读、或 packet 已存在但人类访问尚未确认时使用 `unconfirmed`，只有本工作流不适用时使用 `access_confirmation=not_applicable`。`no_recommendation` 只用于已存在 packet 的显式 recommendation 值，不能代替“没有 packet”。`decision_evidence_status` 只描述 human decision evidence：没有任何 human decision evidence 时必须是 `none`；readiness/digest 验证失败不等于 invalid decision，历史 no-op control projection 也不等于 noop decision。

`completed_design_only` 与 `handed_off` 只能在对应 ADR、详细设计以及（如适用）`ARCH-RD-HANDOFF` 已实际持久化并验证后报告。只读、plan 或行为测试会话即使能生成完整待发布内容，canonical stage 也停在 `publishing`；`planned_writes` 列出当前待发布目标，不得把“逻辑上可完成”写成终态。

## Role boundaries

| Role | Owns | Must not do |
|---|---|---|
| Architecture Lead | intake、路由、`ARCH-CONTROL`、approval packet、readiness 与人工决定记录 | 代替用户批准或改写 delivered packet |
| Architecture Analyst | `ARCH-RESEARCH` 与证据限制 | 把建议伪装成事实 |
| Solution Architect | `ARCH-DESIGN vN` | 创建 OpenSpec 或实施 |
| Architecture Reviewer | 只读 `ARCH-REVIEW` | 修改被审版本或批准自身方案 |
| Target R&D Team | 接收 handoff 后独立进入自身流程 | 把 handoff 当作已创建 OpenSpec |

## Progressive disclosure

始终先读取 workflow mandate reference，再只读取当前阶段需要的一个 reference 和对应模板。例外：需要方案人工 Review 时同时读取 Human Action Request reference/template；`ARCH-CONTROL` 在每次转换时加载；approvable review 后同时读取 approval packet reference/template；进入发布/交接时可同时读取 approval packet、ADR publication、R&D handoff 及其模板。运行时与安装验证才读取 [runtime and validation](references/runtime-and-validation.md)。

## Common mistakes

- 使用 `blocked`、`waiting_human_design` 或 `NO-GO` 等非 canonical 状态/结论。
- 把 `APPROVABLE` 当作 `approved_for_spec`。
- 把 readiness 或 `ARCHITECTURE_RECOMMENDATION` 当作批准。
- 把验证 packet digest 的 evidence 写回 packet，或通过修改旧 packet 表示 supersession。
- 仅因 Agent 能读取本地路径就声称目标人类可访问。
- 批准后由 Architecture workflow 自己创建 OpenSpec，而不是交给目标 R&D Team。
- 在缺失 `openspec-explore` 时自行分析并补写“等价结论”。
- 一次性加载所有 references/templates，掩盖当前阶段的判断。
- 没有 Issue/仓库写入能力却声称报告已经发布。
- 只写“等待确认”、只列批准 token，或让不同权限 Owner 用一次“接受全部”作决定。
- 为材料交付、访问检查、状态、retry、relay 或 verification 请求 `AUTHORIZE OPERATION`。
- 把任何平台的 workspace、work item、actor、message、material delivery 或 command 字段加入 portable required fields。
