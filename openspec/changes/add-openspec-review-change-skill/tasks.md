## 1. 固化 OpenSpec 与现有项目基线

- [x] 1.1 运行本 change 的 `openspec status` 及 proposal、design、specs、tasks 四类 `openspec instructions`，记录 `spec-driven` Schema、artifact 路径、依赖和内容要求，并逐项确认实现计划没有绕过当前 OpenSpec 契约
- [x] 1.2 记录 `setup-skills-env.py` 当前只管理 `~/.claude/skills`、本机双端链接由非安装器路径形成、`scan_custom_skills()` 是根目录 skill 单一发现源的基线证据
- [x] 1.3 在修改安装器前对 `install_skill_symlinks`、`uninstall_skill_symlinks`、`install` 和 `uninstall` 重新运行 GitNexus upstream impact；记录调用方、执行流程和风险，若结果升为 HIGH 或 CRITICAL 则先停止并告知用户

## 2. 初始化双运行时公共 Skill

- [x] 2.1 按 Codex 与 Claude Code 的 skill-creator 指引初始化仓库根目录 `openspec-review-change/`，创建公共 `SKILL.md`、`agents/openai.yaml` 和 `references/`，并删除全部模板占位符
- [x] 2.2 将 `SKILL.md` frontmatter 限定为两端 validators 接受的 `name`、`description`、`allowed-tools`，把 `[change-name] [--openspec-root <repo-relative-path>]` 参数契约写入正文
- [x] 2.3 配置只读 `allowed-tools`，覆盖 Git、OpenSpec 的 list/status/instructions/validate、文件检索和项目要求的只读代码智能命令，不加入文件写入或任务标记修改能力
- [x] 2.4 生成并核对 `agents/openai.yaml` 的带引号 `display_name`、`short_description` 和 `default_prompt`，确保 prompt 明确包含 `$openspec-review-change`
- [x] 2.5 编写 description 的正负触发边界：命中 OpenSpec 提案质量与实施就绪审查，不抢占 PR、源码 diff、实现一致性或归档完成度审查

## 3. 编写审查规则与报告契约

- [x] 3.1 创建 `openspec-review-change/references/review-rubric.md`，定义 Schema 合规、目标范围、项目事实、设计完整性、Spec 可测试性、跨 artifact 一致性、端到端追踪性和任务实施就绪度八个维度
- [x] 3.2 在 rubric 中列出每个维度的适用条件、正反例、`BLOCKER/MAJOR/MINOR/INFO` 边界，以及迁移、安全、兼容、性能和运维等条件项的“不适用”判定规则
- [x] 3.3 在 rubric 中定义 `问题/目标 → What Changes → Capability → Requirement/Scenario → Design Decision → Task → Verification` 的多对多追踪规则和缺口分类
- [x] 3.4 创建 `openspec-review-change/references/report-contract.md`，固定运行时、OpenSpec root、change 阶段、工作树证据范围、artifact 状态、维度摘要、finding 字段、追踪缺口和下一步结构
- [x] 3.5 在报告契约中定义稳定编号、严重度与证据位置排序、同根因去重、大型报告展开方式和不确定证据表达
- [x] 3.6 在报告契约中实现门禁算法：BLOCKER→`BLOCKED`、无 BLOCKER 且有 MAJOR→`NEEDS_REVISION`、仅 MINOR→`READY_WITH_WARNINGS`、无实质问题→`READY`

## 4. 实现项目、Change 与 Schema 预检

- [x] 4.1 在 `SKILL.md` 中解析 `[change-name] [--openspec-root <repo-relative-path>]`，拒绝重复参数、缺值、绝对路径、`..` 逃逸、符号链接逃逸和未初始化的 OpenSpec 根
- [x] 4.2 检查 Git 仓库与 `openspec` CLI 可用性，并将缺失前置条件报告为 `BLOCKED`，不得安装依赖或修改环境
- [x] 4.3 通过 active change 列表实现显式名称选择、唯一 active change 自动选择、无 active change 提示和多 change 歧义交互；拒绝缺失或仅归档的名称
- [x] 4.4 使用 `openspec status --change <name> --json` 识别 Schema、artifact 状态和 apply requirements；仅对 `spec-driven` 继续完整语义审查，其他 Schema 输出受支持边界并固定 `BLOCKED`
- [x] 4.5 对每个声明的 artifact 调用 `openspec instructions <artifact-id> --change <name> --json`，读取 instruction、规则、依赖和 outputPath，并把当前 Schema instructions 作为内容与结构审查契约
- [x] 4.6 相对 change 目录安全展开 artifact outputPath glob，按稳定路径顺序读取全部匹配文件；将 required/completed artifact 零匹配或越界路径记为 `BLOCKER`
- [x] 4.7 执行 `openspec validate <name> --type change --strict --json`；校验失败或 apply-required artifact 不完整时继续审查可读内容但固定总体结论为 `BLOCKED`
- [x] 4.8 根据 task checkbox 与可归属的仓库证据识别 `pre-apply`、`in-progress`、`all-tasks-done`，并在 dirty 或无法归属的工作树中标注基线限制

## 5. 实现语义、事实与任务就绪审查

- [x] 5.1 按当前运行时加载适用项目指令链：Codex 使用 `AGENTS.md`，Claude Code 使用 `CLAUDE.md`，记录实际采用的约束且不盲目合并冲突指令
- [x] 5.2 按项目要求使用 GitNexus `query/context` 核验现有逻辑，并只对提案计划修改的现有公共或关键 symbol 运行 upstream `impact`；新增文件使用文件和流程证据
- [x] 5.3 在 GitNexus 不可用或索引陈旧时降级到 `rg`、文件读取和源码核验，在报告中说明证据范围与置信度，不把“未找到”当作不存在
- [x] 5.4 依据 rubric 审查目标、范围、非目标、设计决策、备选方案、风险与迁移，核对提案声明与当前项目实现和既有工作流是否一致
- [x] 5.5 审查每个 Requirement/Scenario 的规范性、可观察 WHEN/THEN、边界与错误路径，并将 capability、design、task 和 verification 建立追踪关系
- [x] 5.6 审查 task 的依赖顺序、单次会话颗粒度、具体目标、完成证据和测试覆盖，将隐藏的架构选择报告为设计未决而非普通实现步骤
- [x] 5.7 按 report contract 合并同根因 finding、生成稳定编号和排序，并据严重度确定唯一总体门禁结论
- [x] 5.8 在 Guardrails 中禁止审查过程修改 artifacts、应用代码、项目配置、用户配置或 task markers；即使同一请求包含“review 并修复”，也先完成只读报告并要求独立后续修订

## 6. 扩展 Claude Code 与 Codex 双端安装

- [x] 6.1 在已记录 LOW 风险 impact 后，将 skill link 安装逻辑参数化为目标目录，并由 `install()` 独立处理 `~/.claude/skills` 和 `~/.codex/skills`
- [x] 6.2 保留正确链接跳过、错误符号链接替换、普通文件或目录保护的既有语义，使一端冲突或失败不阻止另一端及其他 skills
- [x] 6.3 将卸载逻辑参数化为两个运行时，仅删除解析后精确指向本仓库源目录的链接，并保留外部链接、普通文件和目录
- [x] 6.4 分别输出 Claude Code 与 Codex 的 created、skipped、replaced、removed、not-found 和 warnings 摘要，避免把部分成功显示为全部成功
- [x] 6.5 向 `STANDARD_PERMISSIONS` 增加 `Bash(openspec validate:*)`，继续只合并 Claude settings，安装 Codex 链接时不创建或覆盖任何 Codex 配置文件
- [x] 6.6 新增临时 HOME 回归测试，覆盖双端首次安装、幂等跳过、错误链接替换、普通目标保护、单端冲突继续和分端摘要
- [x] 6.7 扩展临时 HOME 回归测试，覆盖双端 owned link 卸载和 foreign link、普通文件、目录保留，并断言真实 `~/.claude`、`~/.codex` 未发生变化

## 7. 更新双端文档

- [x] 7.1 更新 `README.md` 的项目定位、依赖和安装说明，明确同一安装器管理 Claude Code 与 Codex skill 链接且只维护 Claude Code 命令权限
- [x] 7.2 在核心 Skills 表和使用示例中分别记录 Claude Code 的 `/openspec-review-change`、Codex 的 `$openspec-review-change`、可选 change 名称和 `--openspec-root`
- [x] 7.3 更新工作流说明，将只读 Review 放在 propose/parall-new-proposal 与 apply/worktree-apply 之间，并说明四级门禁、支持 Schema、部分实施提示及与实现一致性/归档检查的职责边界

## 8. 隔离验证与前向测试

- [x] 8.1 使用临时 HOME 运行双端安装与卸载回归套件，并保存真实 Claude Code/Codex 目录测试前后 hash 或等价只读快照作为隔离证据
- [x] 8.2 使用带 PyYAML 的隔离环境分别运行 Codex 与 Claude Code 的 `quick_validate.py`，修复公共 frontmatter、目录、命名和元数据错误
- [x] 8.3 校验 `agents/openai.yaml` 的字段类型、引号、description 长度和 `$openspec-review-change` default prompt 契约
- [x] 8.4 在隔离临时 Git/OpenSpec 项目中创建严格校验通过但跨 artifact 冲突的 `spec-driven` fixture，确认引用冲突双方、去重并输出 `NEEDS_REVISION`
- [x] 8.5 创建缺少 apply-required artifact 的 fixture，确认仍审查可读内容、引用当前 OpenSpec instruction 且总体固定为 `BLOCKED`
- [x] 8.6 创建无实质问题的完整 fixture，确认条件项无误报并输出 `READY` 或仅由证据支持的 `READY_WITH_WARNINGS`
- [x] 8.7 创建部分实施、all-tasks-done、dirty worktree 和无法归属改动 fixture，确认阶段及基线限制正确且不冒充实现一致性结论
- [x] 8.8 创建嵌套 OpenSpec root、越界 root 与非 `spec-driven` Schema fixture，确认嵌套定位、路径保护和不支持 Schema 的失败关闭行为
- [x] 8.9 对所有 fixture 在审查前后比较 tracked/untracked 文件 hash 与 Git 状态，确认 review 未修改 artifacts、代码、配置或 task markers，并清理临时目录
- [x] 8.10 使用 fresh Codex agent 与独立 Claude Code 会话分别 smoke test 显式调用、自然语言正向触发和 PR/code review 负向场景，确保两端从原始 fixture 独立得出符合契约的报告
- [x] 8.11 重新运行本 change 的四类 `openspec instructions` 并逐项复核 proposal、design、两个 capability Specs 和 tasks，随后运行 `openspec validate add-openspec-review-change-skill --type change --strict --json`
- [x] 8.12 在提交前运行 GitNexus `detect_changes`（相对 `main`），确认实现只影响新 skill、双端安装器与测试、README 和本 change artifacts，并核对受影响执行流程符合已评估范围
