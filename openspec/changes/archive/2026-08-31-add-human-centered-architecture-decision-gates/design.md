## Context

Core 当前存在两套人机界面：`critical_evidence_gaps` 使用新增加的 reviewable clarification 结构，而路由、风险接受、正式 packet 决定、发布和 handoff 仍分别依赖 `Next action`、模板字段或合法 token。安全和审计语义完整，但缺少一个平台无关的正向输出契约，导致 Agent 容易把控制面数据直接当作人的决策界面。

本变更只修改 `architecture-design-workflow`。Multica、Issue comment、附件 ID 和移动端属于 sibling adapter 的后续投影；core 只要求稳定的人类可访问 ref 和明确的 access status。

## Goals / Non-Goals

**Goals:**

- 让每个需要人类推进的 core 环节都先给出一屏可扫描摘要，再提供足够细节和完整材料引用。
- 让一次回复只影响一个明确 action type、一个权限域和一个版本绑定，避免笼统接受关闭其他 Owner 或证据缺口。
- 让人类在回复前知道每个选项的依据、代价、下一状态、计划写入和非授权边界。
- 保持 `architecture-design-workflow` 可独立安装和使用，不要求 Multica 或其他平台。
- 用行为测试覆盖当前容易失败的路由、风险接受、正式批准和修订场景。

**Non-Goals:**

- 不改变 canonical stage、`WAIT_REASON`、`BLOCKED_REASON`、Review conclusion 或四种正式 human decision token。
- 不把 pre-approval clarification、risk acceptance、access confirmation 或 routing confirmation 提升为 packet approval。
- 不改变 packet digest、不可变 payload 或平台 adapter 的专有 binding profile。
- 不修改 Multica、业务项目、Runtime 配置或安装状态。

## Decisions

### 1. 新增一个正向 `Human Action Request` 呈现契约

所有 core 人工推进点复用一个模板，而不是在每个 reference 中重新描述字段。模板按阅读顺序固定为：`Action summary`、`Decision context`、`Options and recommendation`、`Evidence and unresolved items`、`Exact response`、`After response`、`Authority boundary`、`Audit binding`。

选择正向结构是因为现有失败属于“输出形状错误或遗漏”，继续增加禁止性 prose 不能稳定得到可读结果。

### 2. 统一呈现，不统一决定语义

Core action type 至少包括：

- `design_input`：接受、修改或拒绝一个设计输入；
- `risk_acceptance`：由准确风险 Owner 接受、修改条件或拒绝一个非阻断风险；
- `design_approval`：只允许四种 current-packet legal decision；
- `routing`：选择 Subject Project、Target Project、repository、branch 或发布目标；
- `access_confirmation`：确认完整材料可由目标人类通过稳定 ref 打开。

Action type 决定合法回复和状态后果。不同类型不得共享“接受”语义，也不得因为显示结构相同而互相授权。

### 3. 一个 action item 只绑定一个权限域

每个 item 必须声明 `Decision Owner`、`Authority scope` 和准确版本。跨 Owner、可独立选择或产生不同后果的字段拆成独立 item；摘要可以聚合展示，但不能提供跨权限域的“全部接受”。

### 4. 首屏摘要与完整材料分层

人类可见输出先展示不超过当前 action 必要内容的摘要：现在为什么需要决定、推荐选择、主要代价、谁决定、如何回复、回复后发生什么。完整 Design、Review、Packet、证据和详细比较通过稳定 ref 提供。仅 Agent 可读的本机绝对路径不满足 evidence link。

审计字段仍保留在 artifact 或尾部 `Audit binding`，但不得把 digest、sidecar 和状态投影放在决策摘要之前。

### 5. 正式批准保持 token 权威，中文解释真实后果

`approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected` 不变。Human review brief 必须逐项说明发布、handoff、OpenSpec 边界、终态和可替代关系；推荐值不预选人类决定。

`revision_requested` 的权威决定仍是 token。可执行的修改意见作为独立 `Revision brief ref` 与决定证据关联，不进入 token 文本、不修改 frozen packet；缺少说明时工作流可以进入新的 `designing`，但必须立即生成一个 `design_input` 请求补齐具体修订范围，不能声称修订要求已经明确。

### 6. 非阻断风险接受成为独立人工动作

`APPROVABLE_WITH_WARNINGS` 的每个 accepted risk 必须具有准确 risk ID、Owner、适用期限/条件、影响和 acceptance evidence。不同 Owner 的风险不能由一个笼统回复关闭。Reviewer 只读取证据，不代替 Owner 接受风险。

### 7. 保持历史兼容

现有 packet、decision evidence 和历史 `waiting_human` 不重写。新 design/review version 或显式 refresh 才要求新 Human Action Request；旧决定继续按既有 current/superseded 规则处理。

## Risks / Trade-offs

- [模板字段增加导致评论变长] → 首屏只展示摘要，完整材料通过稳定 ref，审计字段后置。
- [统一模板使不同决定看起来等价] → 强制 action type、Owner、authority scope 和合法回复集合，明确每类状态后果。
- [revision brief 与 token 分离后出现缺失或漂移] → brief 只作为指导性 context ref，token 仍是 gate authority；缺失时生成新的澄清 action。
- [Agent 机械拆出过多 action] → 只拆分权限域、独立选择或不同后果；同一 Owner 的同一原子决定可保留一项。
- [历史 Work Item 不满足新呈现结构] → 无 refresh/no new version 时保持历史投影，不伪造新决定卡片。

## Migration Plan

1. 先增加 fixtures/runner 对路由、风险接受、批准和修订可读性的失败断言。
2. 新增 Human Action Request reference/template 并在 core SKILL 中路由。
3. 更新直接 references 和现有模板，保持 canonical enums 不变。
4. 同步主规格并运行现有与新增 behavior matrix。
5. 不执行安装、Skill import 或平台 activation；部署由后续单独授权处理。

## Open Questions

无阻塞问题。平台如何渲染 stable refs、token 和 revision brief 由依赖的 Multica adapter 变更处理，不进入 core contract。
