# architecture-workflow-operation-automation Specification

## Purpose
TBD - created by archiving change automate-non-review-architecture-operations. Update Purpose after archive.
## Requirements
### Requirement: 当前 workflow mandate 自动完成非 Review 操作
系统 SHALL 在用户明确启动、继续或重试既有架构阶段时建立 `architecture_workflow_mandate_v1`，并在其绑定的单一 work item、stage、attempt、Agent 与允许操作内自动完成准备、交付、状态投影、relay、verification 和有界 retry，不得逐步请求 operational authorization。

#### Scenario: 当前阶段可唯一解析
- **WHEN** work item、stage、attempt、Agent、输入和目标均可唯一解析
- **THEN** 系统自动执行 manifest 中的有序操作并逐步重读 postcondition

#### Scenario: 后续操作超出范围
- **WHEN** 操作要求创建资源、跨 work item 写入或进入实现、部署、采购范围
- **THEN** 系统停止并说明需要新的任务指令，不生成 `AUTHORIZE OPERATION` token

### Requirement: 只有方案内容决定进入人工 Review
系统 MUST 仅对 `design_input`、`architecture_review` 或 `architecture_approval` 派生 `requires_human_review=true`，并 MUST 要求唯一 Decision Owner、完整可访问材料、原子决定、Team 建议和备选后果齐备。

#### Scenario: 完整方案需要人的决定
- **WHEN** current action 满足全部 Review 前提
- **THEN** 系统发布 Decision Brief、首行准确 mention 唯一 Owner 并进入 `in_review`

#### Scenario: 内部操作或访问验证
- **WHEN** 当前步骤是 preparation、delivery、attachment/access verification、status、relay、retry 或 postcondition check
- **THEN** 系统自动处理且不得请求用户授权

### Requirement: Human access 必须由完整客户端渲染证明
系统 SHALL 仅在具名 verifier 对目标人类入口执行 actual UI activation，并看到准确完整的 human-readable rendering 后，把对应 scope 记录为 `opened`。download-only、raw-byte fetch、HTTP 200、digest 一致或本地文件存在 MUST NOT 单独满足该条件。

#### Scenario: Markdown attachment preview 成功
- **WHEN** verifier 点击能解析为当前 Multica attachment 的 Design/Research/Control 链接，browser-rendered preview 呈现准确完整正文
- **THEN** 系统可以把该 material/scope 记录为 `opened`，并单独保留 raw-byte digest 证据

#### Scenario: 点击只触发下载
- **WHEN** 入口只下载文件或 verifier 只 fetch 原始字节，没有检查目标客户端渲染
- **THEN** 系统记录 `unavailable|not_run` 和关闭条件，且不得因此投影 `in_review`

### Requirement: Adapter 使用 immutable derived manifest
Adapter SHALL 在首笔平台写入前生成并重验 `architecture_operation_manifest_v1`，冻结 mandate、输入/输出 digest、目标、ordered writes、postconditions、retained objects、attempt 与 supersession，并 SHALL 在匹配时自动单次消费。

#### Scenario: Manifest current 且匹配
- **WHEN** identity、digest、target、parent selector、status 和 Skill revision 均与 current runtime 一致
- **THEN** Adapter 自动执行并把完整证据写入 task evidence

#### Scenario: Manifest 漂移
- **WHEN** 任一冻结值与重读事实不一致
- **THEN** Adapter 保留既有对象、停止后续写入并报告恢复路径，不请求授权修复

### Requirement: 状态投影反映实际工作和 Review
系统 SHALL 在 Agent 工作时使用 `in_progress`，在 current 方案 Review 交付成功时使用 `in_review`，在有效回复开始处理时恢复 `in_progress`，并 SHALL 仅在没有 Agent 或 human 可执行路径时使用 `blocked`。

#### Scenario: Review 交付成功
- **WHEN** Decision Brief、附件、mention 和 access postconditions 均通过且 `requires_human_review=true`
- **THEN** 系统自动写入 `in_review --no-start`

#### Scenario: 有效 current 回复
- **WHEN** actor、parent、action、version、digest、revision 和 task attribution 均通过
- **THEN** 系统自动写入 `in_progress --no-start` 后处理决定

### Requirement: Legacy operational request 只作审计
新契约 MUST NOT 生成或消费 delivery、retry、relay、status 的旧式 operational token；激活时 SHALL 保留历史对象并通过新 attempt supersede 未消费请求。

#### Scenario: 存在未消费旧请求
- **WHEN** 新 Skill 契约激活且旧 request 仍为 current-looking
- **THEN** 系统将其标记为 superseded/audit-only，并从新 manifest 开始自动流程

### Requirement: Portable core 不依赖 Multica
`architecture-design-workflow` MUST NOT 要求 Multica URL、workspace、Issue、member、comment、attachment、status 或 CLI 字段；平台状态和交付只由 optional sibling adapter 投影。

#### Scenario: 只安装 portable core
- **WHEN** Runtime 只提供 `architecture-design-workflow`
- **THEN** 工作流仍可用 local/shared artifact refs 和当前会话人类身份完成研究、设计、Review、批准与发布门禁
