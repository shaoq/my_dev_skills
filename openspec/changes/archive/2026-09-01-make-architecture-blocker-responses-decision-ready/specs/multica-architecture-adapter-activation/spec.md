## ADDED Requirements

### Requirement: Adapter 必须友好纠正单一明确但格式无效的 Blocker 回复

当准确 instruction owner 在同一 Issue、current request 之后提交未编辑且只对应一个 current blocker 的回复，文本能唯一映射到一个允许业务意图但缺少 Action ID、使用非 canonical 措辞或包含额外正文时，adapter SHALL 标记 `reply_correction_candidate_v1`，MUST NOT 消费该回复，并 MAY 为同一 `action_id + request_revision` 自动发布至多一次 `reply_correction_v1`。

纠错 SHALL 说明原回复尚未生效、一个普通语言失败原因、唯一完整 canonical Action 和再次回复后的行为。纠错 MUST 绑定 invalid comment ref、revision、raw digest 与 current Action，MUST 保持 `BLOCKER_ACTION_STATE=awaiting_input` 和 Issue `blocked`，不得 mention Architecture Agent、创建 task、恢复 Issue 或改变任何架构 gate。重复事件 MUST reconciliation no-op；wrong actor、多意图、占位值、旧/superseded Action 或意图不明 MUST 静默 fail closed。

#### Scenario: 明确自荐但缺少 Action ID
- **WHEN** 准确 instruction owner 在 current request 后回复“我负责提供”，且回复未编辑、只表达 `provide_self` 并唯一绑定 current blocker
- **THEN** adapter 不消费回复，最多发布一次说明“缺少当前处理编号”的纠错，并给出完整 `ACTION <current-id>: 由我负责`

#### Scenario: 重复事件不重复纠错
- **WHEN** 同一 invalid comment ref/revision/raw digest 与 `action_id + request_revision` 再次被观察
- **THEN** adapter reconciliation no-op，不重复评论、不创建 task、不改变状态

#### Scenario: 纠错证据无法安全写入
- **WHEN** mandatory correction identity 无法通过容量门禁或写后回读
- **THEN** adapter 保持 blocked 并报告恢复条件，不重试同一纠错、不消费原回复

#### Scenario: 错误 actor 或多个意图
- **WHEN** 回复来自非 instruction owner、对应多个 current action、含占位值或表达多个互斥意图
- **THEN** adapter 不发布纠错、不消费回复、不改变状态或 gate

## MODIFIED Requirements

### Requirement: Adapter 必须把 Actionable Blocker 投影给唯一 Member

adapter SHALL 从 current `architecture_blocker_action_v3` 与外部 deployment profile 唯一映射既有 Member/Agent，并在发布人类 blocker 前执行 `automatic_before_human` discovery。comment MUST 按 Member mention、为什么暂停、一个普通业务问题、标为推荐的完整 current Action、普通语言理由/置信度/适用边界、有序备选及适用条件、回复后行为、可选依据入口的顺序呈现；machine binding schema 和企业治理记录类型不得成为默认人类表单。推荐 Action MUST 位于 mention 后前 800 个 Unicode code points 内，并早于 evidence link、digest、control 或 machine field。reader 保留 blocker v1/v2 audit-only；新写只使用 v3。

#### Scenario: 唯一 instruction owner 可映射
- **WHEN** action、work item、attempt、owner authority、Member 和 Issue 均 current 且唯一
- **THEN** adapter 先运行 discovery；唯一 verified binding 自动恢复，多个候选按 core recommendation 发布简单选择，零候选才发布一次含单一推荐的 comment 并记录 `BLOCKER_ACTION_STATE=awaiting_input`

#### Scenario: 手机端首屏可复制推荐
- **WHEN** adapter 为 current blocker 生成 Multica comment
- **THEN** 推荐完整 Action、理由和置信度出现在 mention 后 800 个 Unicode code points 内，且所有审计字段后置

#### Scenario: Owner 不能唯一映射
- **WHEN** owner 缺失、冲突或只能从 creator/assignee/recent commenter 猜测
- **THEN** adapter 在首笔写入前返回 `needs_new_mandate_v1` 或 mapping failure，不写 status/comment/task

### Requirement: Adapter 必须消费 Current Blocker 回复并恢复真实任务

adapter SHALL 仅消费准确 instruction owner 在 current request 后提交的 current canonical Action reply，并 SHALL 验证 work item、Action ID、created-after、未编辑 revision、`provide_input|request_discovery` response mode、single action、supersession 和 task attribution；`provide_input` 还验证 required fields。格式无效但意图唯一的回复只能进入 `reply_correction_candidate_v1`，不得被消费。有效 provide-input 记录 received 并映射 resume actor；有效 request-discovery 记录 discovery_needed 并映射既有 coordination/research actor。两者都创建 single-consumption handoff、回读 task accepted/active 后才写 `in_progress --no-start`。

#### Scenario: 最新位置的有效回复
- **WHEN** 唯一 instruction owner 在同一 Issue 最新位置提交 current Action ID 的有效 provide-input 或本地化 request-discovery
- **THEN** adapter 不依赖 direct parent，回读 resume/discovery task accepted/active 后自动投影 in_progress

#### Scenario: 中文 request-discovery
- **WHEN** 用户提交 current Action 定义的准确本地化 request-discovery，且仅存在一个可规范化的边缘 Agent mention、Markdown mention 转义或无语义空白
- **THEN** adapter 规范化并消费 request-discovery；其他附加自然语言不得通过宽松匹配消费

#### Scenario: 无效但意图唯一的回复
- **WHEN** 准确 Owner 的回复唯一表达一个允许意图，但缺少 current Action ID 或不符合 canonical grammar
- **THEN** adapter 不消费回复、不创建 handoff，最多进入一次友好纠错，Issue 继续 blocked

#### Scenario: 无效或过期回复
- **WHEN** actor、Action、时间、revision、字段、single action 或 supersession 任一无法唯一通过
- **THEN** adapter audit-only/no-op；除满足严格 correction candidate 的当前 Owner 单意图回复外，不发布纠错，不创建 task、不改变 Review gate

#### Scenario: Resume task 未入队
- **WHEN** canonical reply 内容有效但 mapped handoff 没有 accepted/active task evidence
- **THEN** adapter 不遗留 orphaned in_progress，保留 response evidence并保持/恢复 blocked
