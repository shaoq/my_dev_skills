## Why

Multica adapter 已能安全交付不可变 packet 并绑定准确人工 token，但面向人的评论仍以技术字段和 token 为主，delivery、target-human、shared sidecar、activation、conflict 和 retry 等显式授权也缺少统一的人类可读请求。Core 的平台无关 `Human Action Request` 需要一个不反向污染 core 的 Multica 投影。

## What Changes

- 依赖 `add-human-centered-architecture-decision-gates` 提供的平台无关契约，把 core 人工动作请求渲染为一屏优先、手机可读的 Multica 评论，并将完整 Markdown 继续作为稳定附件/链接交付。
- 正式审批评论逐项解释 `approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected` 的中文含义、状态后果和非授权边界，同时保持权威决定评论为准确 token。
- 为 `revision_requested` 增加独立、可引用的 revision brief；revision brief 只指导 replacement design，权威 token 仍由既有 decision binding profile 验证。
- 为 packet delivery、target-human mapping、shared sidecar 写入、Skill activation、conflict strategy、sandbox acceptance 和 retry 生成明确的运维授权请求，列出准确目标、计划写入、不会执行的动作、风险、失败保留对象和准确授权回复。
- 要求 access confirmation 显示并逐项验证 Design、Review、Packet 的稳定入口，桌面和手机均能打开完整内容；技术 ID/digest 保持审计准确但不挤占首屏决策摘要。
- 增加 adapter contract/fixture/sandbox 测试，验证 token 与说明分离、授权不被误认为架构批准、过期/superseded 请求不生效。
- 不修改 Multica 核心代码、CLI/API、Team/Project/Agent/Issue，也不执行真实 workspace import、binding 或 packet delivery。

## Capabilities

### New Capabilities

- `multica-architecture-human-action-rendering`: 定义 core Human Action Request 在 Multica 评论、附件、访问确认和运维授权中的投影契约。

### Modified Capabilities

- `multica-architecture-approval-delivery`: 使审批交付首屏可读、完整材料可打开，并为 delivery/access/shared-scope 写入提供明确授权请求。
- `multica-architecture-approval-decision-binding`: 保持纯 token 权威绑定，同时关联非权威 revision brief 和每种决定的可读后果。
- `multica-architecture-adapter-activation`: 使 activation、冲突策略、sandbox 和 retry 授权具备准确目标、风险、计划写入与回复格式。

## Impact

影响 `multica-architecture-approval-adapter` 的主说明、delivery/decision/target-human/durable-evidence/activation/sandbox references、评论与证据模板、adapter fixtures/contract tests 和主规格。它只消费 core portable contract，不改变 core stage、packet bytes、recommendation 或 human decision values；不修改 `uni-architecture`、`unidocs-rag` 或 Multica 核心。
