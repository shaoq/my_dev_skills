## Why

当前架构小组虽然能够产生严谨、可审计的设计与审批证据，但把 `ARCH-CONTROL`、Research、Review、Approval Packet 和 Agent handoff 大量投影到面向人的 Issue 时间线，并要求审批人同时打开多份材料。结果是过程审计压过总体方案，评审人难以确认哪一份才是完整结论，后续研发也容易从分散评论而不是批准设计继续工作。

本次变更将“人类评审面”与“Agent 执行/审计面”分离：保留严格的版本、digest、独立评审、批准和 supersession 门禁，但让一份完整 `ARCH-DESIGN-vN.md` 成为唯一必读、可独立评审并指导下一步的总体方案。同时引入 Archify 作为受控的方案可视化能力，使复杂边界、关键时序、数据流和生命周期能够以可复现、可验证的派生图呈现，而不把图或生成回执变成第二份总体方案。

## What Changes

- **BREAKING**：把 `ARCH-DESIGN-vN.md` 定义为架构阶段唯一必须交付给人类阅读的 canonical 总体方案；审批入口不得再要求人类同时阅读 `ARCH-REVIEW`、`ARCH-APPROVAL-PACKET`、`ARCH-CONTROL` 或 Research 才能作出决定。
- 保留 `ARCH-APPROVAL-PACKET`，但将其改为机器使用的 immutable approval manifest：它继续绑定准确 Design/Review 版本、digest、Owner、合法决定和 supersession，不再作为独立的人类附件或正文。
- 将 `ARCH-REVIEW` 收敛为独立评审的简短 findings/verdict；完整论证、方案正文和已关闭结论必须回写到新版本 Design，Review 不复制 Design。
- 将 `ARCH-CONTROL`、Research、readiness evidence、continuation、handoff/readback 和 reconciliation 视为内部控制/证据对象；默认不得逐步发布为普通人类 Issue 评论。
- Multica 的正式审批交付改为“一份 Design 附件 + 一段简短 Reviewer/决策摘要 + 一个具名 Action”。机器 manifest、digest、readback 和状态投影保存在 task evidence、metadata 或其他耐久审计记录中。
- Agent 间流转改用 runtime task payload/result 或耐久内部 evidence；只有发生真正的人类内容决定、无法自动解除的依赖输入、最终架构方案交付或终态摘要时才进入人类时间线。
- 为 Design 增加 `directional|spec_ready|implementation_ready` 成熟度，明确当前方案能指导到哪一阶段；未达到 `implementation_ready` 时必须在同一 Design 中列出剩余决策、Owner、关闭条件和研发前置项。
- 引入 impact-based revision：输入变化先判断是否影响已批准/待审设计；无实质影响时只更新内部证据，只有改变架构结论、风险、接口、约束或成熟度时才生成新 Design/Review 版本。
- 为 `ARCH-DESIGN` 引入可选但受规则约束的 Archify visual companion：复杂架构设计默认提供一张总览 Architecture 图，关键 Workflow、Sequence、Data Flow 或 Lifecycle 图按方案语义触发；Typed JSON、HTML、最新成功 `visual-check` 回执中的 light/1440×900 PNG 静态预览与验证回执均绑定准确 Design 版本和 digest。
- 明确 Archify 的三层质量声明和 fail-closed 门禁：`deliver` 只证明确定性交付，`visual-check` 只证明自动浏览器证据，独立 Reviewer 才能给出视觉与架构语义判断；required diagram 只有在 `deliver=passed`、`browser_evidence=passed`、`visual_review=passed`、当前语义评审通过且静态预览 digest/客户端投影验证完成时才可进入 packet readiness，`failed|skipped` 均不得由人工浏览或其他声明升级替代。
- 对当前两个 Team 采用最小角色绑定：Solution Architect 和 Product & Spec Engineer 可按职责创作，Architecture Reviewer 和 Solution Review Architect 仅按 review-only profile 核验；Lead、Analyst、Development、Code Review、QA、Integration 与 Watchdog 默认不绑定。
- R&D 必须优先引用已批准 Design 的图，仅在 OpenSpec 出现实现级流程、时序、数据或状态细节时补充差异图；任何会改变批准架构边界或结论的视觉变化都必须返回 Architecture Team 形成新 Design 版本。
- 同步更新核心 Skill、Multica Adapter、templates、references、fixtures、契约测试与激活/导入说明；新契约只作用于新 attempt，历史 Issue、附件、决定与旧 attempt 保持不可变。

## Capabilities

### New Capabilities

- `architecture-diagram-artifacts`: 定义从图表需要性判断、Typed JSON 创作、确定性交付、浏览器证据、独立语义评审到 Design 版本绑定的完整视觉产物契约。

### Modified Capabilities

- `architecture-design-artifacts`: 重新定义人类 canonical Design、精简 Review、内部控制产物、设计成熟度、visual companion manifest 与 impact-based revision。
- `architecture-approval-packets`: 将 packet 从人类必读材料改为机器 approval manifest，同时保持不可变绑定、readiness、决定与 supersession 安全性。
- `architecture-design-governance`: 将正式人类决定绑定到 current Action 与准确 Design/Review/manifest snapshot，并约束新旧 attempt 的版本迁移。
- `architecture-human-action-requests`: 将人类请求收敛为单一 Design 入口、简短评审摘要和一个原子决定。
- `architecture-workflow-operation-automation`: 将 Agent continuation、handoff、readback、Control 与状态投影从普通人类时间线移入内部执行/证据通道。
- `architecture-skill-runtime-installation`: 要求 core 与 adapter 作为兼容版本一起激活，并将外部 Archify 版本、来源和归档 digest 作为独立依赖冻结，验证新 attempt 使用新契约、旧 attempt 不被重解释。
- `multica-architecture-approval-delivery`: 将三附件审批交付改为单 Design canonical attachment、非权威视觉伴随资源和机器 manifest/readiness 记录。
- `multica-architecture-human-action-rendering`: 减少人类评论内容，只保留总体方案入口、必要的静态视觉预览、关键结论、风险和当前 Action。
- `multica-architecture-adapter-activation`: 更新导入、角色级 additive binding 和 sandbox acceptance，使新的人类/内部双通道契约及 Archify 创作/评审边界在两个 Team 上原子启用。

## Impact

- 核心 Skill：`architecture-design-workflow/SKILL.md` 及其 solution design、review、packet、human action、continuation、handoff references/templates。
- 外部视觉依赖：Archify `v2.17` 的 Typed JSON、`validate`、`deliver`、`visual-check` 与 review-only 命令边界；当前候选归档 SHA-256 为 `ed178d2ddd8861db1b8e867f32be7764bdec221d44568c37b6ae157c5e7f111c`，实施激活前必须重新回读并冻结实际来源、版本和 digest。
- 平台适配：`multica-architecture-approval-adapter/SKILL.md` 及 approval comment、human action、material bundle、manifest、readiness、durable evidence、handoff/readback references/templates。
- 仓库使用说明：`README.md` 中 core/adapter 的审批材料、Action binding、单 Design 人类入口、内部 evidence 和 Archify 角色边界说明。
- 规范：上述十项 OpenSpec capabilities 的 delta requirements。
- 验证：架构 workflow safety/runner、execution continuation、Multica adapter contract、fixtures/schema 和跨 runtime 激活验证。
- 运行时：仓库 core/adapter Skill 源保持唯一来源；Archify 保持独立外部来源，不复制进本仓库。部署时需刷新 Claude/Codex 链接或 Multica workspace import/binding，并通过新 sandbox Issue 验证四个目标 Agent 的创作/评审约束。已有运行中 attempt 必须继续使用其冻结 revision，或由显式新 attempt supersede。
- 依赖：以 `allow-owner-attested-formal-architecture-approval` 的完成内容为兼容基线；本变更不撤销其 Owner attestation、安全 readback 或 decision binding，只改变人类材料表面。
