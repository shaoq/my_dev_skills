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

## Human-first presentation order

先呈现：

1. Action summary：Action ID、类型、当前状态、为什么现在需要动作、Decision Owner 与 authority scope；
2. Decision context：原子问题、候选建议或 `no_recommendation`、有限备选、事实/推断/原则依据、逐项后果与重大风险；
3. Evidence and unresolved items：可由目标人类打开的稳定材料引用，以及仍缺证据、Owner 和关闭条件；
4. Exact response：可复制的准确回复；
5. After response：每个合法选项对应的 next stage、remaining blockers、Next Owner 和 planned writes；
6. Authority boundary 与 Audit binding。

不要用“请确认”“等待审核”或只列 token 代替上述内容。完整方案不必复制进评论，但必须提供目标人类可重读的稳定引用；仅 Agent 可读的路径不算 human-accessible evidence。

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

- 每个关键材料使用稳定、目标人类可访问的 ref；记录 artifact type、version/digest（如适用）、access evidence 和 verifier。
- 审计区绑定当前 routing version、design/review/packet version 或 Risk ID；明确 `current|superseded`。
- superseded 请求与回复保留审计，但不得驱动 current action。
- 请求本身的 context ref 可以补充决策说明，但只有各自 canonical evidence 或正式批准 token 能改变对应 gate。

## Compatibility

历史有效决定继续按原规则生效。新契约只改善人类看到的决策上下文和可审计性，不追溯判无效，也不创造新的 canonical stage、Review conclusion、blocker、recommendation 或 human decision 值。
