## ADDED Requirements

### Requirement: Multica blocker 必须投影为普通用户可直接回答的业务问题

adapter SHALL 将 portable blocker 的唯一 requested input 渲染为一个简体中文业务问题，并提供至多三个完整、可复制且包含 current Action ID 的回复：当前用户负责、指定其他负责人、不确定并请团队建议。默认评论 MUST NOT 要求用户提供 `RACI`、组织目录、服务目录、策略批准记录或 machine binding 字段。

#### Scenario: 自然语言负责人声明
- **WHEN** current instruction owner 回复 `ACTION <current-id>: 由我负责` 或 `ACTION <current-id>: 负责人是 <可识别的人或团队>`
- **THEN** adapter 从 comment author、current Action scope、comment ref/revision/time 和 readback 派生 evidence，创建验证 handoff；不得把声明直接解释为领域接受、方案批准或实现授权

#### Scenario: 不确定并请求建议
- **WHEN** current instruction owner 回复 `ACTION <current-id>: 我不确定，请团队给出建议`
- **THEN** adapter 规范化为 `request_discovery` 并创建既有 discovery actor task，回读 accepted/active 后才投影 `in_progress`

#### Scenario: 条件性来源追问
- **WHEN** 用户未声称存在正式记录且 deployment policy 未要求外部 authority record
- **THEN** adapter 不显示来源链接必填项；只有上述条件成立时才追加一个普通语言的来源问题

### Requirement: Adapter 必须兼容 portable 历史版本并只投影 current 新操作

adapter SHALL 读取 mandate/continuation v1 与 v2，以及 blocker v1/v2/v3，用于审计和 reconciliation。任何新 mandate/continuation/handoff 或状态副作用 MUST 绑定 v2，任何新 blocker/retry MUST 绑定 v3。v1 actor/role 只有在 identity 与 deployment mapping 唯一时才可确定性迁移；历史 blocker v1/v2 只读，歧义时 fail closed。

#### Scenario: v1 live attempt 需要新写入
- **WHEN** current portable evidence 为 v1，且请求需要 comment、status 或 task 副作用
- **THEN** adapter 保留 v1 audit-only，创建并验证 superseding v2 mandate/continuation；需要 blocker 时生成 superseding v3 action 后才执行

#### Scenario: v1 role mapping 冲突
- **WHEN** legacy role 对应多个 Member/Agent 或 authority identity 不一致
- **THEN** adapter 不选择最近 actor、assignee 或显示名，并返回准确 compatibility failure

### Requirement: Adapter 必须把 Actionable Blocker 投影给唯一 Member

adapter SHALL 从 current `architecture_blocker_action_v3` 与外部 deployment profile 唯一映射既有 Member/Agent，并在发布人类 blocker 前执行 `automatic_before_human` discovery。comment MUST 按 Member mention、为什么暂停、团队建议/理由/置信度、一个普通业务问题、最多三个自然语言回复、回复后行为、可选依据入口的顺序呈现；machine binding schema 和企业治理记录类型不得成为默认人类表单。reader 保留 blocker v1/v2 audit-only；新写只使用 v3。

#### Scenario: 唯一 instruction owner 可映射
- **WHEN** action、work item、attempt、owner authority、Member 和 Issue 均 current 且唯一
- **THEN** adapter 先运行 discovery；唯一 verified binding 自动恢复，多个候选发布简单选择，零候选才发布一次 comment 并记录 `BLOCKER_ACTION_STATE=awaiting_input`

#### Scenario: Owner 不能唯一映射
- **WHEN** owner 缺失、冲突或只能从 creator/assignee/recent commenter 猜测
- **THEN** adapter 在首笔写入前返回 `needs_new_mandate_v1` 或 mapping failure，不写 status/comment/task

### Requirement: Adapter 必须消费 Current Blocker 回复并恢复真实任务

adapter SHALL 验证 reply actor、work item、current Action ID、created-after、未编辑 revision、`provide_input|request_discovery` response mode、single action、supersession 和 task attribution；`provide_input` 还验证 required fields。有效 provide-input 记录 received 并映射 resume actor；有效 request-discovery 记录 discovery_needed 并映射既有 coordination/research actor。两者都创建 single-consumption handoff、回读 task accepted/active 后才写 `in_progress --no-start`。

#### Scenario: 最新位置的有效回复
- **WHEN** 唯一 instruction owner 在同一 Issue 最新位置提交 current Action ID 的有效 provide-input 或本地化 request-discovery
- **THEN** adapter 不依赖 direct parent，回读 resume/discovery task accepted/active 后自动投影 in_progress

#### Scenario: 中文 request-discovery
- **WHEN** 用户提交 `ACTION <current-id>: 我不知道，请团队调查并给出建议`，且仅存在一个可规范化的边缘 Agent mention/Markdown 转义/无语义空白
- **THEN** adapter 规范化为 request-discovery；其他附加自然语言不得通过宽松匹配消费

#### Scenario: 无效或过期回复
- **WHEN** actor、Action ID、时间、revision、字段、single action 或 supersession 任一失败
- **THEN** adapter audit-only/no-op，Issue 继续 blocked，不创建 task、不改变 Review gate、不请求 operational authorization

#### Scenario: Resume task 未入队
- **WHEN** reply 内容有效但 mapped handoff 没有 accepted/active task evidence
- **THEN** adapter 不遗留 orphaned in_progress，保留 response evidence 并保持/恢复 blocked

### Requirement: Blocker 回复不得扩大架构或实施权限

adapter MUST 把 blocker reply 仅作为 dependency input；它 MUST NOT 将 instruction owner 视为 domain Owner，也 MUST NOT 据此接受设计、风险、Review、approval、PoC、实现、部署、采购或资源创建。

#### Scenario: 回复包含额外批准措辞
- **WHEN** current blocker 回复除 required fields 外包含设计接受或实施授权文字
- **THEN** adapter 只消费合法 dependency-input fields，额外文字仅作审计且不得改变 gate 或 planned writes

### Requirement: Adapter 必须支持显式 Owner 手动材料检查

adapter SHALL 在 `design_input|architecture_review` 的唯一 Decision Owner 已明确选择自行检查时，把准确 attachment identity/digest、stable same-Issue entry 和 policy evidence 投影为 `access_verification_mode=owner_manual`、`material_access_state=manual_check_required`。这些 postcondition 通过后 SHALL 自动写入 `in_review --no-start`；未经认证的 Agent 浏览器失败不得单独产生 hard blocker。

#### Scenario: Owner-manual Decision Brief 交付
- **WHEN** comment、mention、attachment、digest、稳定入口和 policy evidence 全部回读成功
- **THEN** adapter 发布可执行决策卡和 `ACTION <action-id>: 材料打不开`，并将 Issue 投影为 in_review

#### Scenario: 材料打不开回复
- **WHEN** 准确 Owner 对 current Action 提交“材料打不开”
- **THEN** adapter 不记录候选选择，自动触发 coordination repair task 并在 task accepted/active 后投影 in_progress
