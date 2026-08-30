## Context

`architecture-design-workflow` 已要求 `ARCH-DESIGN` 包含推荐方案，也要求正式 `ARCH-APPROVAL-PACKET` 包含非权威的 `ARCHITECTURE_RECOMMENDATION`。但当设计因 `critical_evidence_gaps` 停止时，`ARCH-CONTROL` 只有 `Next action`，没有规定向人类索取输入时必须给出什么可审核内容。`UNIDRAG-12` 因而产生了结构正确但不可有效审核的评论：五组问题完整，却没有建议默认值、理由、风险或修改入口。

该缺口发生在正式 Review/packet 之前，因此不能复用 packet recommendation 字段，也不能让候选默认值看起来像批准或测量证据。

## Goals / Non-Goals

**Goals:**

- 让每个阻塞性人类澄清请求都能在 Issue 评论本身独立审核和编辑。
- 对每个决策项固定提供候选建议或显式 `no_recommendation`、理由/证据、风险、待补证据与 Owner、回复方式。
- 保持建议、Owner 决定、测量证据和正式 packet 批准四类语义正交。
- 用真实失败场景建立回归验证。

**Non-Goals:**

- 不改变 canonical stage、blocker、Review conclusion 或 human decision token。
- 不改变 approval packet schema、adapter 合同或任何平台 API。
- 不为缺失的事实制造精确数字，也不替责任 Owner 作决定。

## Decisions

### 1. 使用正向结构契约，而不是只增加“不要只等待确认”的禁令

`ARCH-CONTROL` 增加 `Reviewable clarification request` 区块。每个需要人类输入的条目必须包含：

1. `Decision required`：人类要决定什么；
2. `Candidate recommendation`：具体候选值，或 `no_recommendation`；
3. `Basis`：事实、推断或适用原则；
4. `Material risks / consequences`：接受该候选值的主要代价；
5. `Missing evidence / Owner / closure condition`：哪些内容仍须测量或由其他 Owner 确认；
6. `Editable response`：接受、修改、拒绝的最小回复格式。

这是“遗漏必填元素”的失败，应使用模板槽位确保输出形状，而不是依赖散落的 prose reminder。

### 2. 预批准澄清建议不复用 `ARCHITECTURE_RECOMMENDATION`

正式 `ARCHITECTURE_RECOMMENDATION` 继续只属于 delivered approval packet。设计阶段使用自然语言的 `Candidate recommendation`，并明确标记为候选、非决定、非批准，避免污染既有 packet 与 decision binding 合同。

### 3. 接受候选值只关闭它有权关闭的决策缺口

可识别的人类可以接受、修改或拒绝候选建议，但一次笼统接受不得：

- 替代需要采集的流量、容量、payload、性能或恢复证据；
- 替代 Privacy、Security、Procurement、SRE 等指定 Owner 的决定；
- 构成 `approved_design_only`、`approved_for_spec` 或任何 current-packet decision evidence。

因此每项必须区分“可由当前人类决定的值”和“仍须补齐的证据/Owner”。

### 4. 无可靠候选时也必须形成可审核请求

如果证据不足以提出安全默认值，条目使用 `no_recommendation`，解释缺失证据为何会改变选择，并提供有限选项或取得证据的确定路径。不能退化为只有“请确认”或“等待输入”。

### 5. 验证覆盖静态契约与行为输出

- 静态测试验证模板和主 skill 包含上述结构与语义边界。
- 新行为场景复现 `critical_evidence_gaps`，要求评论包含候选建议、理由、风险、待补证据/Owner、编辑方式及非批准声明。
- 以修改前的 `UNIDRAG-12` 输出作为 RED 证据；修改后运行同类只读行为样例确认 GREEN。

## Risks / Trade-offs

- [评论可能变长] → 以逐项短字段和摘要优先组织，不复制完整设计正文。
- [候选数字产生虚假精确感] → 强制标记 provisional，并把测量证据与 Owner 作为独立关闭条件。
- [“接受建议”被误判为批准] → 明确限定其只回答澄清项，既有 packet ref/version/digest 人工门禁保持不变。
- [所有问题机械给默认值] → 允许 `no_recommendation`，但必须解释原因并给出有界的取证或选择路径。
