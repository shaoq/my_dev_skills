## ADDED Requirements

### Requirement: Portable v2 contract 必须与 Team topology 解耦

core SHALL 使用 `architecture_workflow_mandate_v2` 与 `execution_continuation_v2`，以通用 actor、authority identity、responsibility 和 portable evidence 表达架构工作。responsibility MUST 只允许 `coordination|research|solution_design|independent_review|dependency_input|human_decision|downstream_delivery`；portable required fields MUST NOT 要求固定角色名、Team、Member、Agent、Issue、comment 或 task。

#### Scenario: 单 Actor standalone
- **WHEN** 没有 Team、Issue 平台或多 Agent Runtime
- **THEN** core 使用 local/shared work item、current session actor 和 portable evidence 完成流程，不构造平台字段

#### Scenario: 独立评审
- **WHEN** current design 进入 review
- **THEN** core 以 authority identity 验证 reviewer 与 design author 不同，无法证明时 fail closed

### Requirement: Portable continuation 必须保持真实执行连续性

`execution_continuation_v2` SHALL 绑定唯一 work item/stage/attempt、非终态 next actor/authority/responsibility、单项 action、input refs、closing condition、state、evidence mode、evidence refs 和 supersession。除 terminal 外 MUST NOT 使用空 next actor；accepted/active 必须有 `local_session|shared_artifact|runtime_task|human_response` 对应的可回读 evidence。

#### Scenario: 同会话继续
- **WHEN** current standalone invocation 继续下一 action
- **THEN** local_session evidence 包含 actor、attempt、input digest、output revision 和观察时间后才可为 active

#### Scenario: 跨会话尚未触发
- **WHEN** 只有 Next Owner 或计划文字，没有新的 invocation/claim
- **THEN** continuation 保持 planned，不能声称仍在执行

#### Scenario: Blocked continuation
- **WHEN** next path 是 dependency input
- **THEN** state=blocked、next responsibility=dependency_input、next actor 等于 current blocker instruction owner，并绑定 current blocker ID

### Requirement: 非终态 Blocker 必须具名且可行动

core SHALL 生成 `architecture_blocker_action_v3`，绑定唯一 action/work item/stage/attempt、instruction owner/authority、一个 requested input object、`discovery_policy=automatic_before_human`、有界只读 discovery scope、discovery actor/authority/responsibility/completion、`provide_input|request_discovery`、一个普通业务问题、人类声明 profile、reply-context evidence derivation、conditional formal-source policy、context、recommendation、closing condition、resume actor/authority/responsibility、`requires_human_review=false`、state、evidence 和 supersession。v1/v2 仅双读/audit-only；新 blocker/retry/superseding attempt 只写 v3。

#### Scenario: 生成 dependency-input action
- **WHEN** current stage 缺少 routing、Owner、scope 或 evidence reference，且 instruction owner 可唯一识别
- **THEN** core 先查询授权范围内的 current artifacts、evidence、ownership/config、directory 与 Issue history；只有 discovery 不能自动解除阻塞时才生成人类 blocker

#### Scenario: Instruction owner 不等于 domain Owner
- **WHEN** instruction owner 提供缺失 domain binding
- **THEN** core 只记录待验证 dependency input，不把该 actor 或回复视为 domain acceptance 或方案决定

#### Scenario: Discovery 得到唯一 verified binding
- **WHEN** authority 与 current evidence 同时可回读且只存在一个 binding
- **THEN** core 不要求用户填写字段，生成可恢复的 continuation 并自动继续

#### Scenario: Discovery 得到多个候选
- **WHEN** 存在多个可信候选且 evidence 无法唯一选择
- **THEN** blocker 只展示候选、Architecture recommendation、理由、置信度和后果，让用户作一项简单选择

### Requirement: 用户不知道正式值时必须能请求调查

core MUST 支持 `request_discovery` portable intent；具体 adapter MAY 提供本地化表达。该回复只是 dependency input，不是 Review、approval、实现授权或 domain Owner acceptance。

#### Scenario: Request discovery
- **WHEN** current instruction owner 回复 `ACTION <current-id>: request discovery and recommendation`
- **THEN** blocker 记录 `discovery_needed`，创建由既有 `coordination|research` actor 承担的有界只读发现 continuation

#### Scenario: 内部字段不得成为默认表单
- **WHEN** instruction owner 未被证据证明掌握 Owner、authority 与 evidence 正式值
- **THEN** 用户界面不得要求其填写 machine binding schema，必须提供 request-discovery 或基于 verified candidates 的简单选择

### Requirement: Blocker 首屏必须让普通用户只回答一个业务问题

core SHALL 将 current dependency input 冻结为一个不依赖组织治理术语的业务问题。adapter 的默认首屏 MUST 依次说明为什么暂停、团队建议与理由/置信度、唯一业务问题、最多三个可直接复制的自然语言回复、回复后行为和可选审计入口；MUST NOT 默认要求用户理解或提供 `RACI`、组织目录、服务目录、策略批准记录或 machine binding 字段。

#### Scenario: 用户声明自己负责
- **WHEN** instruction owner 对 current Action 回复“由我负责”
- **THEN** adapter 将其记录为待验证的 `provide_input` 人类声明，从评论作者、Action 中冻结的业务范围、comment ref/revision/time 与 readback 派生 machine evidence，并交给 resume actor 验证；该声明不自动成为领域接受或架构批准

#### Scenario: 用户指定其他负责人
- **WHEN** instruction owner 对 current Action 回复“负责人是 <可识别的人或团队>”
- **THEN** adapter 只把该对象作为待验证候选并恢复验证任务，不要求用户同时填写 authority scope、evidence ref/version/date

#### Scenario: 用户不确定
- **WHEN** instruction owner 对 current Action 回复“我不确定，请团队给出建议”
- **THEN** adapter 将其规范化为 `request_discovery`，使用既有 discovery actor 继续有界调查

#### Scenario: 正式来源仅按条件追问
- **WHEN** 用户没有表示存在正式记录，且部署 policy 没有规定必须提供外部权威记录
- **THEN** blocker 不得把来源链接作为解除阻塞的默认必填项；只有用户明确表示已有正式记录或 policy 明确要求时才追加来源问题

### Requirement: 无 Instruction Owner 时必须返回非成功结果

core MUST 在任何外部写入前唯一解析 instruction owner；无法解析时 SHALL 返回 `needs_new_mandate_v1`，包含 `success=false`、missing binding、required instruction、Issue state unchanged、current task completed-with-non-success、no downstream task、resume condition 和 evidence。

#### Scenario: Identity 缺失或冲突
- **WHEN** mandate、trigger evidence 与既有 binding 都不能唯一解析 instruction owner
- **THEN** core 不生成 blocker/continuation，并要求一个具名 trigger actor/authority/work item/task 的新 v2 mandate

## MODIFIED Requirements

### Requirement: 当前 workflow mandate 自动完成非 Review 操作

系统 SHALL 在用户明确启动、继续或重试既有架构阶段时建立 `architecture_workflow_mandate_v2`，并在其绑定的 work item、stage、attempt、workflow actor/responsibility 与允许操作内自动完成准备、交付、状态投影、relay、verification 和有界 retry，不得逐步请求 operational authorization。reader SHALL 双读 v1/v2；writer MUST 只写 v2，需要新副作用的 v1 attempt 必须迁移为 superseding v2 attempt。

#### Scenario: 当前阶段可唯一解析
- **WHEN** work item、stage、attempt、trigger actor、workflow actor、responsibility、输入和目标均可唯一解析
- **THEN** 系统以 v2 mandate 自动执行有序操作并逐步重读 postcondition

#### Scenario: v1 live attempt 继续
- **WHEN** current evidence 使用 v1 且下一动作需要新副作用
- **THEN** 系统只读保留 v1，确定性映射 identity/responsibility 后创建 v2 superseding attempt；歧义时 fail closed

#### Scenario: 后续操作超出范围
- **WHEN** 操作要求创建资源、跨 work item 写入或进入实现、部署、采购范围
- **THEN** 系统停止并说明需要新的任务指令，不生成 `AUTHORIZE OPERATION` token

### Requirement: 只有方案内容决定进入人工 Review

系统 MUST 仅对 `design_input`、`architecture_review` 或 `architecture_approval` 派生 `requires_human_review=true`，并 MUST 要求唯一 Decision Owner、完整可访问材料、原子决定、Architecture recommendation 和备选后果齐备。routing、Owner binding、scope 或 evidence reference MUST 使用 `dependency_input` blocker，固定 `requires_human_review=false`。

#### Scenario: 完整方案需要人的决定
- **WHEN** current action 满足全部 Review 前提
- **THEN** 系统发布 Decision Brief、首行准确 mention 唯一 Owner 并进入 `in_review`

#### Scenario: Dependency input
- **WHEN** current action 只要求补充 routing、Owner、scope 或 evidence reference
- **THEN** 系统先自动 discovery；只有真实依赖输入仍需人类时才生成 actionable blocker，保持 blocked，不创建 Decision Brief 或进入 in_review

#### Scenario: 内部操作或访问验证
- **WHEN** 当前步骤是 preparation、delivery、attachment/access verification、status、relay、retry 或 postcondition check
- **THEN** 系统自动处理且不得请求用户授权

### Requirement: 状态投影反映实际工作和 Review

系统 SHALL 仅在 workflow actor 有 active evidence 时使用 `in_progress`，在 current 方案 Review 交付成功时使用 `in_review`，并在有效 Review/blocker 回复产生 accepted/active resume/discovery task 后恢复 `in_progress`。系统 SHALL 仅在 discovery-first 已完成且 current actionable blocker 已绑定唯一 instruction owner、双 response mode、closing condition 和 resume/discovery actor 时使用 `blocked`。

#### Scenario: Review 交付成功
- **WHEN** Decision Brief、附件、mention 和 access postconditions 均通过且 `requires_human_review=true`
- **THEN** 系统自动写入 `in_review --no-start`

#### Scenario: 有效 current Review 回复
- **WHEN** actor、action、version、digest、revision 和 task attribution 均通过，且处理 task accepted/active
- **THEN** 系统自动写入 `in_progress --no-start` 后处理决定

#### Scenario: 有效 blocker 回复
- **WHEN** blocker reply 通过并且 resume task 回读 accepted/active
- **THEN** 系统才投影 `in_progress`；task 未入队时保持/恢复 blocked

### Requirement: Portable core 不依赖 Multica

`architecture-design-workflow` MUST NOT 要求 Multica URL、workspace、Issue、member、comment、attachment、status、CLI 或平台 task 字段；平台状态、Member mention、delivery 和 task readback 只由 optional sibling adapter 投影。

#### Scenario: 只安装 portable core
- **WHEN** Runtime 只提供 `architecture-design-workflow`
- **THEN** 工作流使用 local/shared artifact refs、当前会话 actor/authority 和 portable evidence 完成研究、设计、Review、批准与发布门禁

### Requirement: 显式 Owner 手动检查不得被匿名浏览器能力阻塞

系统 SHALL 默认使用 `access_verification_mode=automatic`。对于 `design_input|architecture_review`，当唯一 Decision Owner 已明确选择自行在其客户端检查材料时，系统 MAY 使用 `owner_manual`；它 MUST 自动验证准确 artifact identity/digest、完整 bytes、Decision Brief 与稳定 work-item 入口，逐 scope 记录 `manual_check_required` 而不是 `opened`。正式 `architecture_approval` MUST 继续使用 automatic packet readiness。

#### Scenario: Owner 明确自行检查且机器证据完整
- **WHEN** Owner policy、唯一 binding、附件 identity/digest、完整内容回读和稳定入口均通过，但 Agent 没有已认证客户端
- **THEN** 系统发布唯一方案决定，设置 `HUMAN_ACTION_STATE=awaiting_response` 并投影 `in_review`；不得因匿名浏览器只能看到登录页而投影 blocked

#### Scenario: Owner 报告材料打不开
- **WHEN** current Owner 回复 `ACTION <action-id>: 材料打不开`
- **THEN** 系统记录 `content_decision=none`，恢复 coordination actor 自动执行 `repair_or_republish_material_entry`，不得把该回复解释为拒绝、修订、风险接受或批准

#### Scenario: 机器证据失败
- **WHEN** attachment identity/digest、稳定入口、唯一 Owner 或 owner-manual policy 任一失败
- **THEN** content-decision activation gate 保持 not-ready，并给出准确修复路径
