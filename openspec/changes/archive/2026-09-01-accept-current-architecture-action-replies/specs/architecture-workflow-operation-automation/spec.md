## ADDED Requirements
### Requirement: 具名 current Action 回复与评论位置解耦
Skill SHALL 以准确 Owner、同一 work item、唯一 current Action ID 与合法决定值绑定 `current_action_reference_v1`，并从 current request 继承 version/digest；Multica direct parent MUST NOT 成为该 profile 的授权硬门禁。

#### Scenario: 最新位置接受 current Action
- **WHEN** 准确 Owner 在 request 后提交未编辑的唯一 current Action accept，且评论位于 Issue 最新位置并挂到线程根
- **THEN** Adapter 识别有效决定并自动恢复 `in_progress`

#### Scenario: Action identity 不可靠
- **WHEN** Action 错误、过期、重复、已 supersede、actor 错误或评论已编辑
- **THEN** Adapter 保留审计但不消费决定、不改变 Review gate

### Requirement: 只规范化准确平台 Agent mention
Adapter MAY 从具名 Action 回复首端或尾端移除至多一个准确 current Architecture Agent canonical mention；规范化后完整正文 MUST 精确匹配一个合法 response。

#### Scenario: 尾部平台 mention
- **WHEN** 合法 current Action response 只额外包含一个尾部 current Agent canonical mention
- **THEN** Adapter 规范化后接受，并记录 raw/normalized digest、mention identity 与 parent chain

#### Scenario: 额外内容产生歧义
- **WHEN** 回复含错误/多个/中间 mention、额外 prose、引用、围栏、多个 Action 或多个决定
- **THEN** Adapter 将其判为无效且不改变状态

## MODIFIED Requirements

### Requirement: 状态投影反映实际工作和 Review
系统 SHALL 在 Agent 工作时使用 `in_progress`，在 current 方案 Review 交付成功时使用 `in_review`，在有效回复开始处理时恢复 `in_progress`，并 SHALL 仅在没有 Agent 或 human 可执行路径时使用 `blocked`。

#### Scenario: Review 交付成功
- **WHEN** Decision Brief、附件、mention 和 access postconditions 均通过且 `requires_human_review=true`
- **THEN** 系统自动写入 `in_review --no-start`

#### Scenario: 有效 current Action 回复
- **WHEN** actor、同一 work item、唯一 current Action ID、继承的 version/digest、未编辑、decision grammar 与 supersession 均通过，无论 candidate 是否为 Decision Brief 的直接 child
- **THEN** 系统自动写入 `in_progress --no-start` 后处理决定
