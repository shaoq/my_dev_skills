## Context

复杂架构议题同时涉及需求澄清、现状代码证据、候选方案、非功能约束、人工裁决、知识沉淀和跨项目研发交接。现有 skills 覆盖其中的单点能力，但缺少共同的状态机与产物契约。

前置压力测试显示三个关键缺口：

1. 通用 Agent 可能把“很紧急、直接创建 proposal”解释为跳过项目路由和人工门禁的授权。
2. `openspec-explore` 能正确保持思考模式，但没有强制要求先产出可独立评审的 `ARCH-DESIGN`，也不区分“批准方案”与“批准进入 Spec”。
3. 通用架构评审能识别证据和迁移缺口，但报告名称、版本关联、门禁结论与研发交接字段不统一。

本 skill 的消费者包括 Architecture Lead、Architecture Analyst、Solution Architect 和 Architecture Reviewer。skill 是可复用的流程与报告契约，不负责创建具体 Multica Agent/Team。

## Goals / Non-Goals

**Goals:**

- 用一个明确状态机约束架构议题的阶段、责任人、输入、输出与人工门禁。
- 让架构研究、方案、评审、ADR 和研发交接均有稳定且易读的结构化模板。
- 支持现有系统演进、新建系统和混合型架构设计。
- 让 GitNexus、brainstorming 和 `openspec-explore` 在正确阶段、正确边界内组合使用。
- 保持 Claude Code 与 Codex 使用同一份 skill 源码。

**Non-Goals:**

- 不在架构设计阶段创建或修改 OpenSpec proposal、design、specs、tasks。
- 不实施业务代码，不创建 Git worktree，不合并分支，不归档 change。
- 不自动创建仓库、Multica Project、研发 Issue 或 Architecture Team。
- 不替代目标研发项目既有的 OpenSpec 与 R&D Team 流程。
- 不为 Architecture Team 创建 watchdog。

## Decisions

### 1. 采用显式阶段状态机，而非自由形式协作

skill 使用以下主流程：

```text
intake
  → routed
  → researching
  → designing
  → reviewing
  → waiting_human_design
  → approved_design_only | approved_for_spec | revision_requested | rejected
  → publishing
  → handed_off | completed_design_only
```

每次阶段转换必须记录在 `ARCH-CONTROL`，包括当前阶段、Owner、输入、产物版本、下一动作、阻塞原因和所需人工决定。`urgent`、`直接做` 等自然语言不能替代明确的批准状态。

备选方案是只提供一组报告模板。未选择，因为模板不能阻止 Agent 跳过项目路由或把探索直接升级为 OpenSpec。

### 2. 架构类型决定研究路径，但共享统一交付契约

- `evolution`：以现有系统为主体，必须包含现状调用链、影响半径、兼容性、迁移和回滚证据。
- `greenfield`：以新系统为主体，必须包含边界、能力模型、技术选型、Build-vs-Buy、部署与成本假设。
- `hybrid`：同时包含现有系统改造和新能力建设，必须明确两部分接口、迁移次序和跨系统失败模式。

三类路径最终都产出 `ARCH-RESEARCH`、`ARCH-DESIGN vN` 和 `ARCH-REVIEW`，避免不同类型出现不可比较的交付物。

### 3. brainstorming 只负责澄清，不拥有后续流程

Solution Architect 在目标、边界、关键约束或方案空间不清晰时调用 `superpowers:brainstorming`。brainstorming 完成后必须冻结结论摘要，再以该摘要作为 `openspec-explore` 思考模式的输入。

brainstorming 后续自带的 planning/implementation 逻辑不进入本工作流。`openspec-explore` 也只用于读代码、调查与比较，不得利用其“用户明确要求时可写 artifact”的通用能力创建任何 OpenSpec 文件。

### 4. GitNexus 是代码事实与影响分析的优先证据源

涉及现有代码的定位、调用链、变更影响、边界验证、缺陷追踪或重构可行性时，Agent 必须先确认索引状态；索引陈旧则优先重建。之后按目的使用 exploring、impact-analysis、debugging 等 GitNexus skills，并在报告中记录仓库、提交、索引时间、查询范围和证据位置。

若目标仓库没有 GitNexus 或工具不可用，允许退化为源码与官方文档调查，但必须标记证据限制，不能把“未发现”表述为“不存在”。

### 5. 架构设计必须先形成独立 `ARCH-DESIGN`

`ARCH-DESIGN vN` 不依附 OpenSpec Schema，至少包含：

- 摘要、目标与非目标
- 背景、假设和已确认约束
- 系统上下文与责任边界
- 候选方案和权衡矩阵
- 推荐方案与关键决策
- 数据、接口、安全、可靠性、性能和可观测性设计
- 失败模式、迁移、回滚和分阶段发布
- 成本、运维与组织影响
- 未决问题、验证计划与研发拆分建议
- 对应 `ARCH-RESEARCH` 版本和证据链接

该文档首先发布在 Issue 结构化报告中，允许 Reviewer 与用户在不进入研发流程的情况下完成审阅。

### 6. 评审者独立出具确定性门禁结论

Architecture Reviewer 不修改被审文档，并输出 `ARCH-REVIEW`：

- `BLOCKED`：存在证据缺失、关键边界未定或无法安全裁决的问题。
- `NEEDS_REVISION`：方向可行但存在必须修订的重要缺口。
- `APPROVABLE_WITH_WARNINGS`：仅有已显式接受的非阻断风险。
- `APPROVABLE`：证据、设计和交付路径完整。

每个 finding 必须包含严重度、证据、影响、建议、Owner 和关闭条件。Review 必须绑定准确的 `ARCH-DESIGN` 版本。

### 7. 使用两个互不替代的人工批准门禁

- `approved_design_only`：允许发布 ADR/详细设计并结束架构任务，但不授权创建 OpenSpec change 或研发 Issue。
- `approved_for_spec`：除发布批准方案外，授权生成 `ARCH-RD-HANDOFF`，并由目标项目既有 R&D Team 进入需求分析和 OpenSpec 流程。

批准必须来自当前架构 Issue 中可识别的人类决定；Agent 自己的推荐、Issue 的紧急级别、既有评论中的模糊肯定均不能推断为批准。

### 8. Issue 保留过程，仓库只沉淀批准后的稳定产物

`ARCH-CONTROL`、`ARCH-RESEARCH`、方案迭代、评审发现和人工决定保留在 Issue。只有人工批准后的最终方案才写入架构仓库的 ADR 与详细设计目录。

这样既保留完整决策过程，又避免把每轮探索噪声固化为长期文档。

### 9. 参考资料与模板按阶段拆分

skill 目录采用：

```text
architecture-design-workflow/
├── SKILL.md
├── agents/openai.yaml
├── references/
│   ├── intake-and-project-routing.md
│   ├── research-evolution.md
│   ├── research-greenfield.md
│   ├── research-hybrid.md
│   ├── solution-design.md
│   ├── architecture-review.md
│   ├── adr-publication.md
│   └── rnd-handoff.md
└── templates/
    ├── arch-control.md
    ├── arch-research.md
    ├── arch-design.md
    ├── arch-review.md
    ├── adr.md
    ├── detailed-design.md
    └── arch-rd-handoff.md
```

`SKILL.md` 只保留触发条件、状态机、硬门禁、角色路由和引用导航；详细规则与模板按需加载，降低上下文负担。

### 10. 复用现有双运行时安装器并执行行为测试

根目录 skill 会被 `scan_custom_skills()` 自动发现，现有安装器已具备 Claude Code/Codex 双端链接、幂等跳过、错误链接替换、普通目录保护和精确卸载能力。因此默认只需新增 skill 目录并运行安装器，不修改安装逻辑。

测试分三层：

1. 静态校验：frontmatter、目录结构、Codex 元数据和引用链接。
2. 触发测试：复杂架构设计应触发，普通 bug 修复或明确 OpenSpec 实施不应触发。
3. 压力测试：重放“紧急跨项目”“批准后直接 proposal”“评审证据不足”等基线案例，确认新 skill 阻止越权并生成正确报告契约。

## Risks / Trade-offs

- **[流程较重，不适合日常分析]** → 通过触发描述限定为复杂架构升级、新系统设计和跨系统方案；日常调查继续使用 Engineering Triage。
- **[模板过多增加上下文]** → 主 skill 使用渐进披露，只加载当前阶段对应 reference/template。
- **[Agent 将人类自然语言误判为批准]** → 只接受明确状态值，并在 `ARCH-CONTROL` 中记录批准证据。
- **[代码事实随目标仓库变化而过期]** → 报告固定记录提交与索引快照，交接前重新核验关键影响。
- **[跨运行时行为存在差异]** → 公共流程只使用共同可表达的字段，Codex UI 信息隔离到 `agents/openai.yaml`，分别做 smoke test。
- **[安装器扫描新增 skill 后影响用户环境]** → 实施阶段先在临时 HOME 验证，再由用户显式运行安装；不覆盖同名普通路径。

## Migration Plan

1. 按 skill-creator 规范创建目录、frontmatter、Codex 元数据、references 和 templates。
2. 将基线压力测试整理为可重复场景，先确认无 skill 时的失败行为，再验证新 skill 的门禁。
3. 运行静态校验、引用检查和 Claude Code/Codex 双端触发测试。
4. 在临时 HOME 验证安装器，再运行现有安装命令创建受管软链接。
5. 由 `uni-architecture` 项目提案同步并绑定该 skill；在依赖完成前不创建 Architecture Team。

回滚时移除两个运行时中精确指向本仓库的受管链接，并删除新增 skill 目录；不影响其他 skills。

## Open Questions

无。Architecture Team 的具体 Runtime、Agent 指令和 Multica 资源由依赖本 skill 的独立项目提案定义。
