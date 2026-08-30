# R&D handoff

## Entry gate

要求 current ready packet ref/version/digest、准确绑定该 packet 的 `approved_for_spec` decision evidence、已发布 ADR/详细设计，以及已确认的目标项目和仓库。缺一项就保持 `waiting_human` 或 `publishing`，不得创建授权性 handoff。

## Handoff content

- Architecture Issue、packet ref/version/digest、readiness/decision evidence refs、`ARCH-DESIGN`/`ARCH-REVIEW` digests、ADR/详细设计版本
- 目标项目、仓库、默认目标分支和 Owner
- 实施范围、明确非范围及禁止重新解释的架构决定
- 跨项目依赖、接口/数据契约和顺序
- 安全、可靠性、性能、容量、可观测性和成本验收条件
- 迁移、灰度、回滚/前滚与运行手册义务
- 未决决定、验证任务、阻塞项和升级路径
- `AUTHORIZATION_STATE=approved_for_spec`

多项目 handoff 为每个目标项目列独立范围、Owner、依赖和验收条件，并保留一个共同架构版本。

Handoff 只授权目标 R&D Team 开始自身需求分析和 OpenSpec 流程，不代表 proposal、Issue、branch 或代码已经创建。Architecture workflow 不替目标 Team 执行这些动作。

handoff 前再次确认 packet/design/review 原始 bytes 与 frozen digests；若不可用，保持 `publishing` 并设置 `approved_artifact_unavailable`，不得根据 decision brief 生成近似交接内容。
