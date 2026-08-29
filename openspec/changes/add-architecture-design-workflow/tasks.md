## 1. 基线与结构

- [ ] 1.1 记录并固化三类 RED 基线：紧急跨项目请求绕过路由与人工门禁、探索后直接创建 OpenSpec、通用 Reviewer 缺少标准报告契约
- [ ] 1.2 使用 `skill-creator` 初始化 `architecture-design-workflow/`，创建 `SKILL.md`、`agents/openai.yaml`、`references/` 和 `templates/` 目录
- [ ] 1.3 为 skill 编写精确的触发描述，覆盖复杂架构升级、新系统和混合型设计，并排除普通 bug 调查、进度跟进、实现和代码 Review

## 2. 核心工作流

- [ ] 2.1 在 `SKILL.md` 中实现 intake、项目路由、三类设计分类、阶段状态机、Owner 交接和 `ARCH-CONTROL` 更新规则
- [ ] 2.2 实现架构阶段禁止 OpenSpec artifacts 的硬门禁，并明确紧急措辞、Agent 推荐和模糊评论均不能构成授权
- [ ] 2.3 实现 conditional brainstorming → 冻结确认结论 → `openspec-explore` 思考模式的受控流程，阻止 brainstorming 的后续 planning/implementation 接管
- [ ] 2.4 实现 GitNexus-first 规则，覆盖代码理解、代码定位、执行链、影响分析和调试，并在索引陈旧时先重建
- [ ] 2.5 实现 `approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected` 的明确人工门禁和状态转换
- [ ] 2.6 实现单项目、多项目和缺少目标项目时的研发交接规则，同时禁止隐式创建仓库、Project、Issue、worktree 或提交

## 3. 分阶段参考资料

- [ ] 3.1 编写 `references/intake-and-project-routing.md`，定义适用性判断、Subject Project、动态标签、状态转换和等待人工规则
- [ ] 3.2 编写 evolution、greenfield、hybrid 三份 research reference，分别定义证据、非功能约束、迁移、成本和失败模式要求
- [ ] 3.3 编写 `references/solution-design.md`，定义候选方案、权衡矩阵、推荐方案和独立 `ARCH-DESIGN` 的完整性规则
- [ ] 3.4 编写 `references/architecture-review.md`，定义独立核验、finding 字段及四级 Review 结论
- [ ] 3.5 编写 ADR publication 与 R&D handoff references，固化批准证据、仓库沉淀和目标项目交接边界

## 4. 模板与元数据

- [ ] 4.1 创建 `ARCH-CONTROL`、`ARCH-RESEARCH`、`ARCH-DESIGN`、`ARCH-REVIEW` 和 `ARCH-RD-HANDOFF` 模板，保证中文、版本化、证据化且易读
- [ ] 4.2 创建 ADR 与 detailed-design 模板，包含状态、Issue、Subject Project、版本、评审、批准、取代关系和研发追踪字段
- [ ] 4.3 编写 `agents/openai.yaml`，提供以 `$architecture-design-workflow` 开头的默认提示和简洁的 Codex 展示信息
- [ ] 4.4 检查 `SKILL.md` 的渐进披露，确保只按当前阶段加载对应 reference/template，避免一次性注入全部内容

## 5. 验证与安装

- [ ] 5.1 运行 Codex skill validator、仓库 frontmatter/权限一致性检查和所有相对引用检查
- [ ] 5.2 使用 fresh Agent 重放 RED 基线，验证路由、OpenSpec 禁止、两阶段批准和 Review 契约全部转为 GREEN
- [ ] 5.3 分别验证 Claude Code 与 Codex 的显式调用、自然语言正向触发和普通工程任务负向不触发
- [ ] 5.4 在临时 HOME 运行现有 `setup-skills-env.py` 测试，确认双端创建、幂等、冲突保护、单端失败隔离和精确卸载
- [ ] 5.5 运行仓库完整测试、OpenSpec strict validate 和 GitNexus detect changes，确认变更仅涉及新增 skill、测试与必要文档
- [ ] 5.6 经用户执行正式安装后，核验 Claude Code 与 Codex 的两个链接都精确指向仓库源目录，不覆盖用户自有内容

## 6. 下游就绪

- [ ] 6.1 记录 skill 的稳定 canonical name、版本/提交和验证结果，供 `uni-architecture::bootstrap-architecture-design-team` 校验外部依赖
