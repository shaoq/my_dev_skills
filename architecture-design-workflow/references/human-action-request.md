# Human Action Request

## Purpose

任何需要人类才能继续的下一动作，都用同一份平台无关请求表达。请求必须让 Decision Owner 在不先阅读完整审计记录的情况下，快速理解“为什么现在需要我、我能决定什么、有哪些真实选项、每个选项会发生什么、如何准确回复”。详细证据仍保留并通过稳定引用打开。

该请求是决策界面，不是新的 stage、Review conclusion 或批准协议。它不得把 recommendation、风险接受、路由确认、访问确认或修订说明提升为正式架构批准。

## Action types

`action_type` 只能是：

- `design_input`：确认或修改会影响方案的设计输入，也用于补齐缺失的 revision brief；
- `risk_acceptance`：由准确 Risk Owner 接受、修改条件或拒绝一项非阻断风险；
- `design_approval`：针对 current ready packet 作正式决定；
- `routing`：确认 Subject Project、Target Project 或长期文档归属；
- `access_confirmation`：由目标人类确认其可通过稳定引用读取指定材料。

## Atomicity and authority

- 每个 action item 只绑定一个原子决定和一个 authority scope。
- 两个 Owner、两个权限域或可以独立选择的两项风险，必须拆成两个 action item；不得提供“接受全部”来跨 Owner 决策。
- 同一时刻可以存在多个 current action items；`ARCH-CONTROL` 以可重复条目列出每个 action ref、Owner 和状态，不用单数摘要覆盖其他动作。
- `Decision Owner` 必须是可识别的人类或明确角色；未知时写明 Owner 缺口和关闭条件，不得让任意回复者代替。
- 请求必须写明该 Owner 有权决定什么，以及明确无权授权什么。

## Architecture Decision Brief

面向一个当前读者的请求按以下固定顺序呈现：

1. 当前方案的一段式摘要；
2. 简化架构图；
3. Architecture Team 总体建议、理由和置信度；
4. 已确定与尚未确定的内容；
5. 最重要的备选及后果；
6. 当前读者真正有权决定的一项内容；
7. 回复后会发生什么；
8. 可点击的完整 Design、Research、Control（以及当前 gate 必需的 Review/Packet）入口；
9. Exact response、authority boundary 与最小 current/superseded audit binding。

不要用“请确认”“等待审核”、只列 token、多 Owner 问卷或完整设计正文代替上述 brief。完整方案必须是独立版本化 artifact，通过目标人类可重读的稳定入口打开；仅 Agent 可读的路径不算 human-accessible evidence。

## Current reader and authority

- 一个 brief 只绑定一个 current action、一个 Decision Owner 和一个 authority scope。
- renderer 必须记录 Current reader / authority binding 和 `Content-decision activation gate`；只有唯一匹配且当前请求所需材料在全部 requested client scopes 已验证时，才展示内容 action 的 Exact response。
- 其他 Owner 的未决 action 只能列在 `Other-owner dependencies (non-actionable)`，包含 action ID、Owner、依赖影响和关闭条件，不得显示可执行回复表单。
- Decision Owner 为未知角色、零匹配或多匹配时，当前 action 只能是 routing/owner-binding；不能要求当前读者代替该角色决定内容。

## Human-accessible evidence contract

每个完整材料入口分别记录 exact artifact identity/type/version/digest、可导航 ref、Requested client scopes、Access status by scope（`opened|unavailable|not_run`）、Verifier / verification time，以及失败时的 Owner/closure condition。

某个 scope 只有在具名 verifier 实际打开入口、解析到准确完整材料并核对 identity 后才能记录 `opened`。一个 scope 的成功不能推出另一个 scope；Agent 进程、CLI 或 raw-byte download 不能替代人的客户端证据。目标人类尚未打开时保持 target access `unconfirmed`，即使 renderer verification 已通过。若新发布入口必须在发布后才能验证，首次 current action 只能是 `access_confirmation`；验证完成后才可生成新的 current Human Action Request 版本请求内容决定，不得编辑旧请求或把访问确认当成内容批准。

core 不规定平台 URL、附件或预览语法。没有经验证入口时，brief 保留建议和 unavailable 报告，但不得请求正式内容决定；需要正式批准且 packet 不可访问时继续适用既有 `review_packet_unavailable`。

## Recommendation and alternatives

- 有足够依据时给出一个具体 `Candidate recommendation`，并明确它是建议而非决定。
- 没有可靠建议时写 `no_recommendation`，仍需提供有限备选或确定的补证路径。
- 每个备选分别写明即时状态变化、后续写入、主要收益、代价、风险和不可逆影响；没有不可逆影响也明确写 `none known`。
- Basis 必须分为 facts、inferences、principles；不得把推断写成事实。

## Exact responses by type

### Design input

提供可复制格式：

```text
ACTION <action_id>: accept <candidate_id>
ACTION <action_id>: modify <field>=<value>; reason=<reason>
ACTION <action_id>: reject; reason=<reason>
```

有效 `revision_requested` 即使缺少 revision brief，仍按其 packet-bound 决定进入新版本 `designing`。同时生成新的 `design_input` 请求，标记 `revision_scope=missing`，要求人类补充可执行范围；revision brief ref 独立记录且属于非授权上下文。旧 packet 保持不变。

### Risk acceptance

每个 Risk ID 单独提供：

```text
ACTION <action_id>: accept risk=<risk_id>; conditions=<conditions>
ACTION <action_id>: modify risk=<risk_id>; conditions=<conditions>
ACTION <action_id>: reject risk=<risk_id>; reason=<reason>
```

接受只绑定该 Risk ID、Owner、条件和 evidence ref。所有要求的风险接受齐备前，不得形成依赖这些接受的 approvable conclusion 或创建 packet。

### Design approval

决定值保持为：`approved_design_only|approved_for_spec|revision_requested|rejected`。准确回复必须同时绑定 current packet ref/version/digest；不得修改 token 语法，也不得让解释文字替代 token。

对四种选项分别说明：

- `approved_design_only`：只发布批准的 ADR/详细设计，完成 design-only 流程，不产生研发授权；
- `approved_for_spec`：发布批准文档，并在目标项目存在时形成 R&D handoff；目标 Team 之后独立分析，不自动创建 OpenSpec 或实现；
- `revision_requested`：进入新设计迭代；附带的 revision brief 是非授权上下文，缺失时另行请求；
- `rejected`：current work item 进入 `rejected` 终态，后续如需继续必须由明确的新工作重新进入流程。

### Routing

回复必须指定现有目标，例如：

```text
ACTION <action_id>: select subject_project=<existing_project>; reason=<reason>
```

它只确认归属，不授权创建缺失 Project、仓库、Issue、Team 或 Agent。

### Access confirmation

回复必须绑定 artifact ref/version、human actor 和共享 scope；确认后仍须由 verifier 从同一稳定引用读取并匹配 digest。访问确认不等于内容批准。

## After-response projection

每个选项必须在回复前就说明：

- Next stage；
- remaining blockers；
- Next Owner；
- 当前动作直接产生的 planned writes；
- 是否会生成新 artifact/version；
- 不会被该回复授权的动作。

只投影当前合法转换的直接结果，不提前声称未来 Review、packet、发布、OpenSpec 或实现已经发生。

Human Action Request 是现有控制或 artifact 的人类决策入口，不新增 canonical artifact type。core normalized `planned_writes` 只使用既有目标；请求随 `ARCH-CONTROL` 评论呈现时写 `issue:ARCH-CONTROL`，不得临时创造 `issue:HUMAN-ACTION-REQUEST/...` 等目标。平台 renderer 可以记录自己的 delivery evidence，但不能改写 core normalized 字段。

## Stable evidence and audit binding

- 每个关键材料使用稳定、经对应 client scope 验证的可导航 ref；记录 artifact type、version/digest、requested scopes、逐 scope status、access evidence、verifier 和 verification time。
- 内部对象 identity、可导航入口和 target-human access confirmation 分开记录；任一项不能替代另一项。
- 审计区绑定当前 routing version、design/review/packet version 或 Risk ID；明确 `current|superseded`。
- superseded 请求与回复保留审计，但不得驱动 current action。
- 请求本身的 context ref 可以补充决策说明，但只有各自 canonical evidence 或正式批准 token 能改变对应 gate。

## Compatibility

历史有效决定继续按原规则生效。新契约只改善人类看到的决策上下文和可审计性，不追溯判无效，也不创造新的 canonical stage、Review conclusion、blocker、recommendation 或 human decision 值。
