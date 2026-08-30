# ADR publication

## Entry gate

仅当 current `ARCH-APPROVAL-PACKET` 已有绑定准确 packet/design/review refs、versions、digests 与 confirmed human access 的 readiness envelope，且当前 user-role 中可识别的人类针对该 packet ref/version/digest 明确记录 `approved_design_only` 或 `approved_for_spec` 时进入。

## Publication

1. 冻结 packet ref/version/digest、readiness ref、decision evidence、design/review refs/versions/digests。
2. 从 refs 重新读取 packet、design、review 原始 bytes 并核对 frozen digests；不得从审核简报重建技术正文。
3. 无法恢复准确 bytes 时保持 `publishing` 和原批准/readiness，记录 `BLOCKED_REASON=approved_artifact_unavailable`、失败 artifact、Owner 和 closing condition；恢复并重新验证后清除 blocker。
4. 确认目标架构仓库、ADR/详细设计目录与写入权限；目标不明确则等待人工路由。
5. 用模板生成 ADR 和 detailed design，保留批准技术内容，不在发布时重新设计。
6. 写入后记录路径、版本、取代关系和提交/发布证据；无写入能力时输出完整待发布内容，不声称已落库。

若发布前需要人类选择目标架构仓库、处理未决发布风险或确认材料访问，分别使用 `routing`、`risk_acceptance` 或 `access_confirmation` Human Action Request。每个请求必须提前展示选择后的 stage、remaining blockers、Owner 和 planned writes；它们不改变已经记录的正式批准，也不扩展批准范围。

`approved_design_only` 发布后进入 `completed_design_only`，不得生成 handoff。`approved_for_spec` 发布后才可按 R&D handoff reference 继续。

对已成为正式记录的 ADR 使用 supersede/revoke，不删除历史决定。回滚文档发布不等于回滚业务系统。
