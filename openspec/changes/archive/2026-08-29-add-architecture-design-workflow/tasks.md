## 1. 基线与结构

- [x] 1.1 在 `tests/fixtures/architecture-design-workflow/` 固化 RED fixtures：紧急跨项目请求、探索后直接创建 OpenSpec、通用 Reviewer 缺少标准报告契约、依赖缺失和普通工程任务；每个 fixture 声明预期 stage、gate、required/forbidden markers、允许 write set 与 evidence fields
- [x] 1.2 使用 `skill-creator` 初始化 `architecture-design-workflow/`，创建 `SKILL.md`、`agents/openai.yaml`、`references/` 和 `templates/` 目录，并创建 `tests/architecture-design-workflow-safety.sh` contract runner
- [x] 1.3 为 skill 编写精确的触发描述，覆盖复杂架构升级、新系统和混合型设计，并排除普通 bug 调查、进度跟进、实现和代码 Review

## 2. 核心工作流

- [x] 2.1 在 `SKILL.md` 中实现 canonical stage 枚举与转换矩阵、`WAIT_REASON`、`BLOCKED_REASON`、项目路由、三类设计分类、Owner 交接和 `ARCH-CONTROL` 更新规则；禁止 `rejected`/`revision_requested` 错误进入 publishing
- [x] 2.2 实现架构阶段禁止 OpenSpec artifacts 的硬门禁，并明确紧急措辞、Agent 推荐和模糊评论均不能构成授权
- [x] 2.3 实现运行时依赖 preflight：`openspec-explore` 必需，`superpowers:brainstorming` 在存在歧义时必需；缺失时保持当前 stage、记录确定性 blocker、中文报告并零写停止，且不得自动安装或修改 Runtime 配置
- [x] 2.4 实现 conditional brainstorming → 冻结确认结论 → `openspec-explore` 思考模式的受控流程，阻止 brainstorming 的后续 planning/implementation 接管
- [x] 2.5 实现 GitNexus-first 规则，覆盖代码理解、代码定位、执行链、影响分析和调试，并在索引陈旧时先重建
- [x] 2.6 实现 `approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected` 的明确人工门禁和状态转换
- [x] 2.7 实现单项目、多项目和缺少目标项目时的研发交接规则，同时禁止隐式创建仓库、Project、Issue、worktree 或提交
- [x] 2.8 实现全部用户可见输出的中文契约，并保留命令、路径、状态枚举、代码标识符和引用原文的准确形式

## 3. 分阶段参考资料

- [x] 3.1 编写 `references/intake-and-project-routing.md`，定义适用性判断、Subject Project、canonical state、转换矩阵、`WAIT_REASON`、`BLOCKED_REASON` 和等待人工规则
- [x] 3.2 编写 evolution、greenfield、hybrid 三份 research reference，分别定义证据、非功能约束、迁移、成本和失败模式要求
- [x] 3.3 编写 `references/solution-design.md`，定义候选方案、权衡矩阵、推荐方案和独立 `ARCH-DESIGN` 的完整性规则
- [x] 3.4 编写 `references/architecture-review.md`，定义独立核验、finding 字段及四级 Review 结论
- [x] 3.5 编写 ADR publication 与 R&D handoff references，固化批准证据、仓库沉淀和目标项目交接边界
- [x] 3.6 编写 `references/runtime-and-validation.md`，记录依赖 preflight、临时 HOME 验证、正式安装命令、链接核验命令、canonical skill name 和下游按所选提交校验版本的方法

## 4. 模板与元数据

- [x] 4.1 创建 `ARCH-CONTROL`、`ARCH-RESEARCH`、`ARCH-DESIGN`、`ARCH-REVIEW` 和 `ARCH-RD-HANDOFF` 模板，保证中文、版本化、证据化且易读，并完整包含适用的 Issue、Owner、status、evidence、next action、`WAIT_REASON` 与 `BLOCKED_REASON`
- [x] 4.2 创建 ADR 与 detailed-design 模板，包含状态、Issue、Subject Project、版本、评审、批准、取代关系和研发追踪字段
- [x] 4.3 编写 `agents/openai.yaml`，提供以 `$architecture-design-workflow` 开头的默认提示和简洁的 Codex 展示信息
- [x] 4.4 检查 `SKILL.md` 的渐进披露，确保只按当前阶段加载对应 reference/template，避免一次性注入全部内容

## 5. 验证与安装

- [x] 5.1 运行 Codex skill validator、仓库 frontmatter/权限一致性检查和所有相对引用检查，并把精确命令写入 `references/runtime-and-validation.md`
- [x] 5.2 实现并运行 `tests/architecture-design-workflow-safety.sh`，对所有 fixtures 的 stage、gate、required/forbidden markers、write set、证据字段和中文输出执行归一化断言
- [x] 5.3 使用 fresh Claude Code 与 Codex Agent 重放同一组 fixtures，分别记录 Runtime 版本、fixture、归一化结果、证据位置与限制；验证显式调用、自然语言正向触发、依赖缺失失败关闭和普通工程任务负向不触发
- [x] 5.4 在临时 HOME 运行现有 `setup-skills-env.py` 测试，确认双端创建、幂等、冲突保护、单端失败隔离和精确卸载
- [x] 5.5 运行仓库完整测试、OpenSpec strict validate 和 GitNexus detect changes，确认变更仅涉及新增 skill、测试与必要文档
- [x] 5.6 生成并审核供用户选择执行的正式安装与双链接核验命令；自动实施不得执行这些命令或修改真实 `~/.claude`、`~/.codex`

## 6. 下游就绪

- [x] 6.1 在 `references/runtime-and-validation.md` 记录稳定 canonical name、验证矩阵和下游消费契约；要求 `uni-architecture::bootstrap-architecture-design-team` 在交接时记录并校验实际选用的仓库提交，避免在同一提交中写入自引用 commit hash
