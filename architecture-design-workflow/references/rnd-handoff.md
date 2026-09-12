# R&D handoff

## Entry gate

要求 current ready packet ref/version/digest、准确绑定该 packet 的 `approved_for_spec` decision evidence、`design_maturity=spec_ready|implementation_ready`、已发布 ADR/详细设计，以及已确认的目标项目和仓库。`directional` 禁止生成 `approved_for_spec` handoff。缺一项就保持 `waiting_human` 或 `publishing`，不得创建授权性 handoff。

## Handoff content

- Architecture Issue、packet ref/version/digest、readiness/decision evidence refs、`ARCH-DESIGN`/`ARCH-REVIEW` digests、ADR/详细设计版本
- 目标项目、仓库、默认目标分支和 Owner
- 实施范围、明确非范围及禁止重新解释的架构决定
- 跨项目依赖、接口/数据契约和顺序
- 安全、可靠性、性能、容量、可观测性和成本验收条件
- 迁移、灰度、回滚/前滚与运行手册义务
- 未决决定、验证任务、阻塞项和升级路径
- `AUTHORIZATION_STATE=approved_for_spec`
- 批准图的 diagram ID/ref/digest；R&D 优先复用批准图，只在上游图不覆盖实现级流程/时序/数据/状态时增加一张 scope-local delta visual

多项目 handoff 为每个目标项目列独立范围、Owner、依赖和验收条件，并保留一个共同架构版本。

目标项目、R&D Owner 或必要交接风险尚需人类动作时，分别创建原子 `routing` 或 `risk_acceptance` Human Action Request。不同项目或 Owner 不合并授权；请求列明候选、有限备选、材料引用、准确回复以及回复后是否仍停留在 `waiting_human|publishing`。路由或风险回复不得扩大 packet-bound `approved_for_spec` 的范围。

Handoff 只授权目标 R&D Team 开始自身需求分析和 OpenSpec 流程，不代表 proposal、Issue、branch 或代码已经创建。Architecture workflow 不替目标 Team 执行这些动作。

handoff payload、continuation 和 readback 全部写入 `architecture_internal_evidence_v1`，不得创建 dedicated Agent handoff comment；人类时间线最多一次终态人类摘要。R&D 发现边界、接口、数据所有权、信任边界、NFR、风险或 maturity 改变时，必须返回 Architecture Team 并生成 `architecture_design_impact_v1`；不得在局部实现图中绕过批准 Design。

handoff 前再次确认 packet/design/review 原始 bytes 与 frozen digests；若不可用，保持 `publishing` 并设置 `approved_artifact_unavailable`，不得根据 decision brief 生成近似交接内容。
