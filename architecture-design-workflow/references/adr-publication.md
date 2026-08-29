# ADR publication

## Entry gate

仅当当前 Issue 中可识别的人类针对准确 `ARCH-DESIGN` 和 `ARCH-REVIEW` 版本明确记录 `approved_design_only` 或 `approved_for_spec` 时进入。

## Publication

1. 冻结批准证据、设计版本和 Review 版本。
2. 确认目标架构仓库、ADR/详细设计目录与写入权限；目标不明确则等待人工路由。
3. 用模板生成 ADR 和 detailed design，保留批准技术内容，不在发布时重新设计。
4. 写入后记录路径、版本、取代关系和提交/发布证据；无写入能力时输出完整待发布内容，不声称已落库。

`approved_design_only` 发布后进入 `completed_design_only`，不得生成 handoff。`approved_for_spec` 发布后才可按 R&D handoff reference 继续。

对已成为正式记录的 ADR 使用 supersede/revoke，不删除历史决定。回滚文档发布不等于回滚业务系统。
