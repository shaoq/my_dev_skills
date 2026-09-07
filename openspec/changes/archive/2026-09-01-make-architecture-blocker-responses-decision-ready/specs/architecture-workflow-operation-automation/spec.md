## ADDED Requirements

### Requirement: Actionable Blocker 推荐必须基于证据且可决策

core SHALL 为每个仍需 instruction owner 输入的 current actionable blocker 派生一个平台无关的推荐投影，包含 `recommendation_intent=provide_self|provide_candidate|request_discovery`、普通语言理由、`high|medium|low|unknown` 置信度、适用边界和有序备选及其主要后果。多个回复语法 MUST NOT 作为无差别的平级列表交给用户自行判断。

推荐 MUST 基于 current discovery evidence，不得从 Issue creator、assignee、最近评论者、显示名或 instruction-owner 身份推断领域责任。唯一 verified binding MUST 自动继续而不发布 blocker；多个候选无法由证据排序、`unavailable_with_evidence`、low 或 unknown confidence 时 MUST 推荐 `request_discovery`。推荐本身 MUST NOT 构成 domain acceptance、Architecture Review、风险接受、批准或实施授权。

#### Scenario: 证据不足时推荐继续调查
- **WHEN** discovery 为 `unavailable_with_evidence`，或候选责任人的置信度为 low/unknown
- **THEN** core 推荐 `request_discovery`，说明只会创建有界只读调查 continuation，并列出其他意图只在何种证据成立时适用

#### Scenario: 候选可由证据排序
- **WHEN** current evidence 支持多个 verified candidates 且其中一个具有可回读的较强责任证据
- **THEN** core 可以推荐 `provide_candidate`，同时说明证据、置信度、边界和其余候选后果

#### Scenario: 唯一 binding 自动继续
- **WHEN** discovery 得到唯一 verified binding
- **THEN** core 不发布人工 blocker，直接生成并回读 continuation

#### Scenario: 平台角色不能作为领域责任证据
- **WHEN** 唯一可见事实只是用户为 Issue creator、assignee、最近评论者或 instruction owner
- **THEN** core 不推荐其承担领域责任，并按证据不足处理

## MODIFIED Requirements

### Requirement: Blocker 首屏必须让普通用户只回答一个业务问题

core SHALL 将 current dependency input 冻结为一个不依赖组织治理术语的业务问题，并 SHALL 提供一个明确推荐意图、普通语言理由、置信度、适用边界及有序备选。adapter 的默认首屏 MUST 依次说明为什么暂停、唯一业务问题、一个可直接复制的推荐回复及理由/置信度/边界、其余回复仅在何种条件下适用、回复后行为和可选审计入口；MUST NOT 默认要求用户理解或提供 `RACI`、组织目录、服务目录、策略批准记录或 machine binding 字段。

#### Scenario: 用户声明自己负责
- **WHEN** evidence 足以支持 instruction owner 对 current Action 声明“由我负责”作为推荐，且其提交准确 canonical reply
- **THEN** adapter 将其记录为待验证的 `provide_input` 人类声明，从评论作者、Action 中冻结的业务范围、comment ref/revision/time 与 readback 派生 machine evidence，并交给 resume actor 验证；该声明不自动成为领域接受或架构批准

#### Scenario: 用户指定其他负责人
- **WHEN** evidence 足以支持一个可识别候选，且 instruction owner 对 current Action 提交准确 canonical reply
- **THEN** adapter 只把该对象作为待验证候选并恢复验证任务，不要求用户同时填写 authority scope、evidence ref/version/date

#### Scenario: 用户不确定
- **WHEN** evidence 不足且 instruction owner 对 current Action 回复推荐的“我不确定，请团队给出建议”canonical Action
- **THEN** adapter 将其规范化为 `request_discovery`，使用既有 discovery actor 继续有界调查

#### Scenario: 正式来源仅按条件追问
- **WHEN** 用户没有表示存在正式记录，且部署 policy 没有规定必须提供外部权威记录
- **THEN** blocker 不得把来源链接作为解除阻塞的默认必填项；只有用户明确表示已有正式记录或 policy 明确要求时才追加来源问题

#### Scenario: 推荐不构成批准
- **WHEN** core 或 adapter 展示 blocker recommendation
- **THEN** recommendation boundary 明确它只用于补齐 dependency input，不改变 Review、approval、risk acceptance 或 implementation gate
