## 1. 基线与失败测试

- [x] 1.1 在 `my_dev_skills` 检查 GitNexus 索引与当前 HEAD，一致后记录 `architecture-design-workflow`、测试 runner、安装器及双 Runtime 链接的影响基线；不得修改真实 HOME、Multica 或 `uni-architecture`。
- [x] 1.2 运行现有 skill quick validation、`tests/architecture-design-workflow-safety.sh` 和 `tests/test_architecture_design_workflow_runner.py`，记录变更前基线与任何既有失败。
- [x] 1.3 先扩展 fixtures、`result.schema.json` 与 runner assertions，使 raw-byte packet digest、human access confirmation、packet readiness、recommendation、decision binding、supersession、历史非自动迁移和发布失败关闭场景在旧实现上按预期失败。

## 2. Portable approval packet 契约

- [x] 2.1 新增 `references/approval-packet-and-human-gate.md`，定义 monotonic `vN`、`payload_status=delivered`、RFC 3339 UTC timestamps、immutable `ARCH-APPROVAL-PACKET` payload、raw-byte SHA-256 表示、外部 supersession projection、独立 readiness/unavailable evidence envelope 及准确 packet 人工决定绑定。
- [x] 2.2 新增 `templates/arch-approval-packet.md`，完整展示 `payload_status=delivered`、design/review refs、versions、media types、digests、access profile declarations、Reviewer conclusion、审核对象、关键决定、风险/条件、待确认项和合法决定；模板不得内嵌验证其自身 digest 的 post-finalization evidence，也不得通过改写旧 payload 表示 supersession。
- [x] 2.3 在 packet 契约和模板中加入 `ARCHITECTURE_RECOMMENDATION` 四值枚举、中文理由、适用条件和关键风险，并显著声明 recommendation 不等于人工批准且不得驱动状态迁移。
- [x] 2.4 为 `local_file` 与当前交互会话 binding profile 写明可重复验证的 raw-byte digest、shared workspace scope、目标 human actor、access confirmation 和 actor/ref/version/digest 规则；仅 Agent 进程可读必须失败关闭，同时保留 `durable_platform_ref` 等平台无关扩展点。

## 3. 控制状态与 artifact 追踪

- [x] 3.1 更新 `SKILL.md` 与 intake/control reference 的稳定 blocker 集合和 canonical transition table：`APPROVABLE*` 缺少绑定当前 packet ref/version/digest 的外部 `review_packet_ready` envelope 时保持 `reviewing` 并设置 `review_packet_unavailable`，有 readiness 时才进入 `waiting_human`。
- [x] 3.2 更新 review、solution design 与 human gate 指令，确保 Review conclusion、packet readiness、recommendation、human decision 和 `BLOCKED_REASON` 分字段记录，且 packet 失败不得改写真实 Review conclusion。
- [x] 3.3 更新 `templates/arch-control.md`、`templates/arch-design.md` 与 `templates/arch-review.md`，加入 current packet ref/version/digest、外部 readiness/unavailable evidence ref、recommendation 及准确决定证据字段。
- [x] 3.4 更新 ADR、详细设计与研发交接 references/templates，发布前从 refs 重新读取原始字节并验证当前 packet 与冻结 design/review digests，记录 packet ref/version/digest、readiness evidence ref 和 decision evidence ref；失败时保持 `publishing` 和原批准、设置 `approved_artifact_unavailable`，禁止从审核简报重建近似设计正文。
- [x] 3.5 更新 `README.md` 和 skill metadata（仅在触发/说明确有变化时），说明该 workflow 可在没有 Multica adapter 的 Claude Code/Codex 环境独立运行，以及历史 `waiting_human` 不自动迁移的边界。

## 4. Standalone 行为覆盖

- [x] 4.1 增加 approvable 但无 readiness、shared-workspace local-file raw-byte digest 匹配 ready、仅 Agent 可读、access/digest 失败四类 fixtures，断言 readiness 缺失/失败均保持 `reviewing`、设置稳定 blocker 且保留 `APPROVABLE*`。
- [x] 4.2 增加 recommendation 非批准、模糊 `OK`/紧急措辞/引用文本非批准、当前 packet 显式人工决定 fixtures，断言只有当前 user-role 的可识别人类针对准确 packet ref/version/digest 的合法决定可以通过 gate。
- [x] 4.3 增加 superseded packet 迟到决定 no-op、current-packet `revision_requested` 和 `rejected` fixtures，并更新 `approved_design_only`、`approved_for_spec` fixtures 以携带当前 ready packet digest 与 decision binding evidence；断言 supersession 不改变旧 packet bytes/digest，Reviewer `NEEDS_REVISION` 不创建 packet。
- [x] 4.4 扩展 normalized result schema 和 safety runner，分别校验 review conclusion、packet readiness、packet digest、access confirmation、recommendation、packet version、RFC 3339 timestamp、decision evidence、stage/wait/blocker，且 Claude/Codex 使用同一 fixture 语义。
- [x] 4.5 增加平台中立性静态断言：核心 required fields、templates 和行为 fixtures 不得依赖 Multica、PDF、comment/attachment ID、`parent_id` 或移动端字段。
- [x] 4.6 增加历史 `waiting_human` fixture，断言升级时无新 design/review version 的持久记录不会被自动降级或伪造 readiness，而显式 refresh/version 后执行新 packet gate。
- [x] 4.7 增加发布期 digest mismatch/恢复 fixtures 和 runner assertions，断言失败时保持 `publishing` 和原批准、设置 `approved_artifact_unavailable`，恢复准确 bytes 后清除 blocker 并继续，且不得从决策简报重建近似正文。

## 5. 双 Runtime 证据与安装边界

- [x] 5.1 为所有新增或变更 fixtures 生成 Claude Code 与 Codex 行为 evidence，验证 normalized results 在允许的 Runtime 差异之外一致，并记录 Runtime 版本与限制。
- [x] 5.2 在临时 HOME 中运行 `setup-skills-env.py` 的安装/检查测试，确认 Claude Code 与 Codex 链接仍指向仓库内同一 `architecture-design-workflow/` 源，且未写入真实 HOME 或新增 Runtime 配置。
- [x] 5.3 运行 repository 安全测试，确认本 change 未创建服务、数据库、网络依赖、平台 adapter skill，也未修改 Multica、`uni-architecture` 或真实 Agent/Team/Project/Issue。

## 6. 完整验证与交付证据

- [x] 6.1 运行 skill quick validation、architecture safety runner、runner unit tests、安装器相关测试及仓库既有相关测试，修复所有由本 change 引入的失败。
- [x] 6.2 运行 `openspec validate add-portable-architecture-approval-packets --strict`，并核对 proposal、design、spec deltas 与任务实现的一致性。
- [x] 6.3 检查最终 diff 和工作树边界，记录准确实现 commit、验证矩阵、已知限制与供后续 Multica adapter change 消费的 core contract revision；不得在本 change 内创建 adapter 或外部资源。
