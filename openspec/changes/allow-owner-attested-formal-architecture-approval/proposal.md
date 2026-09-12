## Why

正式架构审批当前只接受 Agent 自动打开 Web/移动端完整预览，并要求在用户预先确认的外部 shared workspace 写入 `shared_workspace_sidecar_v1`。在自托管 Multica 中，Agent 的隔离浏览器没有用户登录态，用户也未必配置第二套共享存储；即使评论、三份附件、目标 Member、原始字节摘要和稳定 Issue 入口都可回读，流程仍会永久停在 `review_packet_unavailable`。

人工审批本来就由唯一 Decision Owner 执行。平台已有不可变任务结果、评论 revision/digest、附件 identity/digest、Issue metadata projection 和 `ARCH-CONTROL` 回读，可在不降低 actor、packet identity、supersession 和内容完整性门禁的前提下，让 Owner 在最终决定中显式声明已打开材料。

## What Changes

- 为正式 `architecture_approval` 增加 `owner_attested` 访问模式：自动预览不可用时，只要准确附件 identity/digest、稳定 same-Issue 人类入口、唯一 Owner 和当前 Action 都验证通过，审批请求可进入 `in_review`，每个材料/客户端 scope 标记为 `manual_check_required`，绝不伪造 `opened`。
- 正式人工决定改用具名 `current_action_reference_v1`：合法批准/修订/拒绝回复必须同时携带当前 Action ID、`materials_opened` 声明和一个合法 decision；`材料打不开` 只触发入口修复，不形成内容决定。
- 将 `multica_issue_task_evidence_v1` 扩展为正式 packet 的平台托管 readiness/decision evidence profile：绑定不可变 request/task result、评论 revision/content digest、三附件摘要、`arch.packet.current` 和 `ARCH-CONTROL` 回读。外部 `shared_workspace_sidecar_v1` 保留为可选强化证据，不再是唯一可用路径。
- 将 Adapter 的 `owner_attested` 明确投影为 portable core 已有的 `owner_manual` 语义，并修正核心 packet gate 中残留的 automatic-only access 表述；core 仍保持平台无关。
- 保留失败关闭：Owner/Action/packet/attachment/digest/稳定入口/任务归属/状态回读任一缺失或漂移时，不得创建可执行审批或消费决定。
- 更新 contract fixture、validator、模板与 adapter references，并用 UNIDRAG-12 的 `APPROVABLE + automatic preview unavailable + no shared sidecar` 形状建立回归。

## Capabilities

### Modified Capabilities

- `multica-architecture-approval-delivery`: 增加正式 packet 的 Owner-attested 交付与平台托管 readiness evidence。
- `multica-architecture-approval-decision-binding`: 增加具名 Action、材料已打开声明与平台任务证据绑定。
- `architecture-approval-packets`: 允许有显式 policy、严格机器校验和 Owner 最终阅读声明的 `owner_manual` packet readiness。

## Impact

- 修改 `multica-architecture-approval-adapter/` 的入口、访问、readiness、durable evidence、decision binding、manifest 与模板契约。
- 修改 `architecture-design-workflow/` 的 packet readiness 表述，复用既有 `owner_manual` 状态而不引入平台字段。
- 修改 `tests/test_multica_architecture_approval_adapter_contract.py`、normalized fixture schema 和新增 owner-attested packet fixture。
- 不修改 Multica backend/frontend/mobile/API/数据库，不创建外部 shared workspace，不降低附件字节摘要、唯一 Member、Action identity、comment revision 或 supersession 校验。
- Skill 目录已通过用户目录 symlink 激活；仓库内验证通过后，同一内容立即成为本机 Codex 的当前版本，无需复制到 `~/.codex/skills`。
