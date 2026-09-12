## Context

UNIDRAG-12 已产生准确 `ARCH-DESIGN v7`、`ARCH-REVIEW v3` 和 `APPROVABLE` 结论，三份附件也完成 raw-byte SHA-256 回读。审批 preflight 仍失败在两个与设计内容无关的环境前提：隔离 Agent 浏览器无法继承唯一 Owner 的登录态，以及不存在本次任务已确认的外部 `shared_workspace_sidecar_v1` scope。

现有 adapter 已允许 `design_input|architecture_review` 使用 `owner_manual + multica_issue_task_evidence_v1`，但人为禁止正式 `architecture_approval` 复用同一安全模式。这造成同一平台、同一 Owner、同一附件证据在较早阶段可评审、到最终阶段反而不可评审。

## Goals / Non-Goals

**Goals:**

- 在没有 Agent 用户登录态或外部 shared scope 的自托管环境中，仍能向唯一 Owner 交付可审阅的正式 packet。
- 将“机器验证身份与字节”和“人类确认实际阅读”分离：机器不得声称 `opened`，Owner 的 exact response 必须显式声明 `materials_opened`。
- 复用平台已有不可变 task result、评论/附件 identity、revision/digest、metadata projection 与 Control readback，避免新增 Multica runtime 或数据库能力。
- 保留 automatic + shared sidecar 作为更强模式，并保持所有失败关闭与 supersession 规则。

**Non-Goals:**

- 不把普通 `OK`、Issue 状态、Reaction、Agent recommendation 或 Reviewer conclusion 当作批准。
- 不允许 download-only、HTTP 200 或 Agent raw-byte fetch 伪装成人类预览已打开。
- 不创建共享存储、公开附件、绕过认证或修改 Multica 应用代码。
- 不让 `materials_opened` 声明替代准确 packet/Action/Owner/digest/readback 校验。

## Decisions

### 1. 正式审批支持两种证据模式

`automatic` 保持现有严格路径：每份材料在请求的客户端 scope 实际 UI 打开，并可选持久化 `shared_workspace_sidecar_v1`。

`owner_attested` 是自动路径不可用时的正式降级：Adapter 验证唯一 Owner、current Action、单评论三附件、raw-byte digests、稳定 same-Issue 可点击入口、`arch.packet.current` 和 task/control evidence；每个 scope 记录 `manual_check_required`。Issue 可进入 `in_review`，但 readiness 明确是“可供 Owner 核验”，不是“Agent 已打开”。

### 2. Owner 的决定同时承载阅读声明

`owner_attested` 只接受具名 Action 语法：

```text
ACTION <action-id>: materials_opened; decision=<approved_design_only|approved_for_spec|revision_requested|rejected>
```

该回复必须由唯一 canonical Member 创建、位于同一 Issue、晚于 request、revision 未变、只包含一个 current Action 和一个 legal decision。`ACTION <action-id>: 材料打不开` 仍只触发 `repair_or_republish_material_entry`，`content_decision=none`。

### 3. 平台托管 task evidence 成为正式 evidence profile

`multica_issue_task_evidence_v1` 对正式 packet 必须绑定：request/action identity、packet ref/version/digest、三附件 identity/size/digest、稳定入口、Owner UUID、candidate comment revision/content digest、task ID/result、`arch.packet.current` 精确值、`ARCH-CONTROL` ref/digest、status timeline 和 supersession scan。每次消费前全部回读；任何漂移使 evidence `invalid|noop`。

该 profile 不依赖可变 metadata 单独证明批准。metadata 只做 current projection，权威证据仍由不可变评论、附件、任务结果与 Control 的交叉回读组成。

### 4. 外部 sidecar 保留但不再强制

已有 `shared_workspace_sidecar_v1` 继续可用于 automatic 或明确配置的强化审计。Adapter 不创建 scope，也不把本地路径冒充 shared ref。缺少 sidecar 本身不再阻塞 `owner_attested`；缺少平台 task/control evidence 仍阻塞。

### 5. UNIDRAG-12 回归形状

新 fixture 固定：Review=`APPROVABLE`、三附件摘要匹配、唯一 Owner、稳定 Issue 入口存在、automatic client rendering unavailable、external sidecar absent。预期为 `review_packet_ready`、`in_review`、`manual_check_required` 和一个具名 `architecture_approval` Action；若去掉 `materials_opened`、Action ID、task/control readback 或任一 digest，决定不得生效。

## Risks / Trade-offs

- **Owner 可能未实际阅读却声明已阅读**：这是显式人类声明风险，不是 Agent 推断；通过具名 Action、唯一 Member、精确 packet 和不可变审计记录追责。
- **平台证据由多个对象组成**：manifest 固定全部 refs/digests 并在消费前整体回读，任一漂移失败关闭。
- **旧 token-only packet 回复不兼容 owner-attested**：automatic/sidecar 路径继续兼容；owner-attested 新请求只展示具名语法，避免混淆。
- **现有 fixtures 假设 workspace ref**：schema 改为显式 evidence profile + profile-specific ref 校验，防止任意字符串通过。

## Migration Plan

1. 新增 RED fixture/test，证明当前 validator 和 Skill 表面拒绝 owner-attested formal packet。
2. 更新 normalized schema/validator 支持 `shared_workspace_sidecar_v1|multica_issue_task_evidence_v1`，并保持 profile-specific strict checks。
3. 更新 adapter references、templates 和入口路由。
4. 运行 adapter contract、全仓 Skill safety/quick validation 和 OpenSpec strict validation。
5. 对 UNIDRAG-12 建立新 attempt，重验当前 Design/Review/subject HEAD；若 exact evidence 通过，交付新的 current Action 并进入 `in_review`。

回滚恢复旧 Skill/contracts；不删除历史 v46、附件、metadata 或 blocked evidence。旧失败记录保留审计。

## Open Questions

无。用户已明确要求依据本次分析进入实施优化。
