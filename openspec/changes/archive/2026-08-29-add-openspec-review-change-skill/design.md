## Context

OpenSpec 的 `propose` 流程会按照当前 Schema 生成 proposal、design、specs 和 tasks，`openspec validate --strict` 能识别结构和格式错误，但不能判断自然语言目标是否清晰、artifact 之间是否矛盾、方案是否建立在真实代码库之上，或任务是否足够明确以供实施。现有 `verify-impl-consistency` 面向实施后的文档、Schema、测试与代码一致性，`check-changes-completed` 面向收尾和归档条件，均不覆盖实施前的提案质量门禁。

新 skill 作为独立诊断步骤位于 propose 与 apply 之间，主要使用者是希望在投入实施前发现需求、设计和任务缺口的提案作者与实施者。它需要遵守项目级指令，并与当前仓库其他根目录 skills 一样由同一份源目录同时提供给 Claude Code 和 Codex。

当前 `setup-skills-env.py` 已能扫描根目录 `*/SKILL.md`，但只为 `~/.claude/skills/` 创建链接和维护 Claude 权限；本机 `~/.codex/skills/` 下的现有项目 skill 链接并非该安装器管理。新增 skill 如果不补齐安装逻辑，就无法通过仓库文档中的标准安装流程被 Codex 发现。GitNexus upstream impact 显示计划修改的 `install_skill_symlinks`、`uninstall_skill_symlinks`、`install` 和 `uninstall` 均为 LOW 风险，各自只有一个直接调用方并集中在现有 main 流程。

## Goals / Non-Goals

**Goals:**

- 对一个指定或可唯一推断的 OpenSpec change 生成证据驱动的实施就绪审查报告。
- 同时覆盖结构校验、单 artifact 质量、跨 artifact 一致性、端到端追踪性和任务可执行性。
- 动态读取 OpenSpec 状态、artifact 路径和 instructions，避免在已支持的 `spec-driven` Schema 内硬编码 artifact 文件集合。
- 将代码库事实、项目约束和影响范围纳入审查，并在 GitNexus 不可用时可靠降级。
- 使用确定性的严重度和门禁规则，让结论可复核、可重复使用。
- 默认只读，不在审查过程中改变被审查证据。
- 让同一份 skill 源目录、核心工作流和 references 同时兼容 Claude Code 与 Codex。
- 使仓库安装器可重复地安装和卸载两个运行时的 skill 链接，并在隔离环境中验证安全行为。
- 支持仓库根和显式嵌套 OpenSpec 项目根。

**Non-Goals:**

- 不替代 `openspec validate --strict`，而是在其结果之上增加语义审查。
- 不验证已经实现的代码是否满足 Spec；该职责属于 `verify-impl-consistency`。
- 不检查 change 是否已经完成或可归档；该职责属于 `check-changes-completed`。
- 不自动重写 proposal、design、specs、tasks 或应用代码。
- 首版不批量审查全部 active changes、已归档 changes，也不自动挂接到 propose 或 apply。
- 首版不对 `spec-driven` 之外的自定义 Schema 作完整语义审查；检测到后失败关闭并说明不支持。
- 不提供百分制质量评分。
- 不在实施或测试中修改真实 `~/.claude`、`~/.codex` 或其他用户配置；双端安装测试只使用临时 `HOME`。

## Decisions

### 1. 使用独立 skill 作为显式预实施门禁

新增根目录 `openspec-review-change/`，由现有 skill 安装流程自动发现。首版由用户显式调用并审查单个 change，不修改 OpenSpec 核心 propose/apply skills。

备选方案是把审查自动嵌入 propose 末尾或 apply 开头。未选择该方案，因为自动嵌入会增加核心流程耗时、把诊断结果与创建或实施动作耦合，并使用户难以单独重跑审查。

### 2. 使用公共 SKILL.md 加运行时专属元数据实现双端兼容

`openspec-review-change/` 只维护一份 `SKILL.md` 和 references。公共 frontmatter 使用两个运行时均能解析且能通过现有 validators 的 `name`、`description` 和只读 `allowed-tools`；参数语法写入正文，不依赖 Claude 专属 `argument-hint`，也不使用会被 Codex validator 拒绝的 Claude 专属键。

Codex 专属的 `display_name`、`short_description` 和以 `$openspec-review-change` 开头的 `default_prompt` 放入 `agents/openai.yaml`。Claude Code 忽略该产品专属目录，通过 `/openspec-review-change` 调用公共 Skill。两端分别验证显式调用、自然语言触发和负向不触发场景。

备选方案是维护 Claude/Codex 两份 SKILL.md。未选择该方案，因为审查 rubric 和流程容易漂移，也违背当前项目所有自定义 skills 共用根目录源文件的模式。

### 3. 将现有安装器扩展为双运行时链接管理

保留 `scan_custom_skills()` 作为唯一 skill 发现源，将安装和卸载函数参数化为目标 skill 目录，并由 `install()`、`uninstall()` 分别处理 `~/.claude/skills/` 和 `~/.codex/skills/`。Claude 的 settings 合并仍只写入 `~/.claude/settings.json`；Codex 侧只管理 skill 链接，不复用 Claude 权限配置。

沿用现有安全语义：正确链接计为 skipped；指向错误目标的同名符号链接可替换；同名普通文件或目录不得覆盖并输出 warning；卸载只删除精确指向本仓库 skill 目录的链接。一端发生冲突或失败时继续检查另一端，并在摘要中分别报告 created、skipped、removed、not-found 和 warnings，不能把部分成功报告为全部成功。

新 skill 会调用 `openspec validate`，因此 `STANDARD_PERMISSIONS` 增加 `Bash(openspec validate:*)`。安装回归测试通过临时 `HOME` 覆盖双端首次安装、重复安装、错误链接替换、普通目录保护、单端冲突、精确卸载和用户配置隔离。

备选方案是要求用户手动创建 Codex 链接。未选择该方案，因为本机现有链接虽证明目录布局可行，但手工步骤不可重复，也与 README 的一键安装承诺不一致。

### 4. 显式解析 OpenSpec 项目根、change 和审查阶段

输入为可选 `<change-name>` 与可选 `--openspec-root <repo-relative-directory>`。项目根参数与现有 `new-worktree-apply` 保持一致：省略等价于 `.`；重复、缺值、绝对路径、`..` 逃逸、符号链接逃逸或目标下不存在 `openspec/` 时在任何审查前失败关闭。所有 OpenSpec 命令和 artifact 路径都相对确认后的项目根执行。

skill 先确认 Git 仓库、OpenSpec CLI 和项目结构，再运行 `openspec list --json`。显式名称必须存在于 active changes；没有 active change 时给出可恢复提示；省略名称且只有一个 active change 时自动选择；多个 change 且无法从会话唯一推断时请求用户选择。已归档 change 不属于首版审查范围。

从 `tasks.md` checkbox 和 OpenSpec 状态识别 `pre-apply`、`in-progress`、`all-tasks-done`。后两种阶段仍审查 artifacts，但报告必须声明代码库证据来自当前工作树，不能视为实施前基线，也不能替代 `verify-impl-consistency`。dirty worktree 同样进入证据范围说明，不直接改变门禁结论。

备选方案是只支持仓库根项目和纯 pre-apply change。未选择该方案，因为仓库已经存在嵌套 OpenSpec worktree 工作流，且 active change 可能在修订过程中出现部分实现；直接拒绝会让审查能力在真实使用中出现不必要断层。

### 5. 完整支持 spec-driven，并动态发现其 artifact 文件

skill 运行 `openspec status --change <name> --json` 获取 Schema、artifact 状态和 apply 要求。首版只对 `schemaName: spec-driven` 给出完整语义结论；其他 Schema 以明确 `BLOCKER` 报告不支持，避免在无法建立语义角色和追踪链时误报 `READY`。

对状态中声明的每个 artifact 调用 `openspec instructions <artifact-id> --change <name> --json`，以其 `outputPath`、`instruction`、`rules` 和依赖信息作为审查依据。`outputPath` 是 glob 时，必须相对 change 目录安全展开全部匹配文件；零匹配与 artifact 状态或 proposal capability 声明矛盾时形成 `BLOCKER`。如果 apply 所需 artifact 缺失，仍审查已存在内容，但总体结论为 `BLOCKED` 并列出缺失项。

备选方案是直接硬编码四个默认路径。未选择该方案，因为即使在 spec-driven 下，specs 也是多文件 glob，项目规则也可能调整 artifact 输出位置。

### 6. 采用“确定性检查 + 语义审查”两层模型

第一层执行可重复的结构检查，包括 OpenSpec 严格校验、artifact 状态、文件存在性、Capability 与 Spec 路径映射、Requirement/Scenario 格式和 task checkbox 格式。

第二层执行八维语义审查：

1. Schema 与结构合规
2. 目标和范围清晰度
3. 项目事实与影响范围
4. 设计完整性
5. Spec 可测试性
6. 跨 artifact 一致性
7. 端到端追踪性
8. 任务实施就绪度

详细判定规则放入 `references/review-rubric.md`，报告字段和示例放入 `references/report-contract.md`，保持主 `SKILL.md` 简洁。

备选方案是只依赖一次自由形式的模型审读。未选择该方案，因为缺少确定性预检会遗漏可机械发现的问题，也难以复核为何结构有效的提案仍被阻断。

### 7. 通过追踪矩阵检查覆盖闭环

审查过程中建立以下逻辑链路：

`问题/目标 → What Changes → Capability → Requirement/Scenario → Design Decision → Task → Verification`

矩阵不要求每个节点机械地一对一对应，但必须能解释每个范围内变更如何被需求定义、被方案支撑、被任务交付和被验证。孤立变更项、无来源任务、无任务覆盖的场景和缺少验证的任务均形成 findings。

备选方案是只分别审查四类 artifact。未选择该方案，因为单篇文档都写得合理时，跨文档遗漏和冲突仍可能存在。

### 8. 代码库核验优先使用项目能力并允许降级

skill 遵循当前运行时已经加载的项目指令层级：Codex 使用适用的 `AGENTS.md`，Claude Code 使用适用的 `CLAUDE.md`，不盲目合并两个运行时可能冲突的指令文件。若适用项目指令配置 GitNexus，则遵循约定使用 `query`、`context`，并只对提案明确要修改的现有公共符号或关键接口使用 `impact`；新增文件或无法解析为符号的范围使用文件和流程证据。若 GitNexus 不存在、索引陈旧或工具不可用，则使用文件检索和源码阅读验证提案声明。

任何降级都必须在报告中说明证据范围和置信度，不能把“未找到”直接等同于“事实不存在”。GitNexus 因此是增强能力而非硬依赖。

备选方案是把 GitNexus 设为强制依赖。未选择该方案，因为其他使用该 skill 的仓库可能没有索引或索引暂时陈旧，而文件与源码核验仍能提供受限但诚实的审查结果。

### 9. 使用严重度驱动的四级就绪结论

每个 finding 使用以下严重度：

- `BLOCKER`：缺失必要 artifact、结构无效、关键范围或决策无法确定，实施无法安全开始。
- `MAJOR`：需求覆盖缺口、跨 artifact 冲突、关键风险遗漏、任务不可执行等会显著增加错误实施概率的问题。
- `MINOR`：不阻止实施，但会降低清晰度、可维护性或验证质量的问题。
- `INFO`：非问题性的观察、已有优势或可选改进。

总体门禁规则固定为：存在 `BLOCKER` → `BLOCKED`；无 BLOCKER 但存在 `MAJOR` → `NEEDS_REVISION`；仅存在 `MINOR` → `READY_WITH_WARNINGS`；无 BLOCKER、MAJOR、MINOR → `READY`。

不使用百分制，因为不同提案的适用维度和风险不同，单一分数会掩盖少量但关键的阻断项。

备选方案是二元通过/失败或百分制评分。未选择该方案，因为二元结果无法区分可带 warning 实施与必须修订，百分制又可能用大量低风险得分掩盖单个阻断问题。

### 10. 报告必须证据化且默认只读

每个问题固定输出编号、严重度、维度、证据位置、问题说明、实施影响和修改建议；无法确定时补充置信度或待确认信息。编号按维度和证据位置稳定排序；同一根因跨多个维度时保留一个主 finding 并交叉标注受影响维度，避免重复报告。报告还包含运行时、OpenSpec 根、change 阶段、工作树证据范围、artifact 状态、维度摘要、追踪缺口和下一步建议。大型报告先输出门禁及 BLOCKER/MAJOR，再输出追踪缺口和低严重度观察。

skill 不提供隐式 auto-fix，也不在审查期间编辑 artifacts。用户明确要求修订时，应在后续独立操作中修改并重新运行审查，以保证每次报告对应稳定的证据快照。

备选方案是在 review 中直接自动修复 artifacts。未选择该方案，因为修改证据会使报告无法对应稳定快照，也会把诊断权限扩张为可能改变需求和架构决策的写入权限。

## Risks / Trade-offs

- **[自然语言审查存在判断差异]** → 使用固定 rubric、严重度条件、证据字段和门禁算法降低漂移，并用真实提案进行前向测试。
- **[大型提案产生过长报告]** → 先输出门禁和高严重度问题，完整 finding 按严重度排序；INFO 只保留有价值的观察。
- **[不同 Schema 的语义差异]** → 始终读取动态 instructions，以 Schema 声明为优先依据；首版只对 `spec-driven` 执行完整审查，其他 Schema 失败关闭。
- **[代码库核验工具不一致]** → GitNexus 可用时增强，否则降级到文件检索，并显式报告证据限制。
- **[只读模式不能立即消除问题]** → 提供精确修改建议，用户修订后重跑审查；保持诊断与修改职责分离。
- **[追踪矩阵可能过度机械化]** → 允许多对多和不适用关系，但要求所有范围内变更具有可解释的交付与验证路径。
- **[双运行时 frontmatter 能力不完全相同]** → 只使用两个 validators 都接受的公共字段，把 Codex UI 信息放入 `agents/openai.yaml`，参数说明放入正文并进行双端调用测试。
- **[安装器修改影响全部自定义 skills]** → GitNexus 风险为 LOW；保留单一扫描源和已有冲突保护，并用临时 HOME 覆盖两个运行时的安装与卸载回归。
- **[非 spec-driven Schema 暂不支持]** → 失败关闭并准确说明支持边界，待获得真实 Schema 和 fixture 后再扩展，不用未经验证的通用性换取虚假 READY。
- **[部分实施会污染实施前证据]** → 显示 change 阶段、dirty 状态和证据快照，仅审查 artifacts 质量，不把当前代码一致性当作提案质量证明。

## Migration Plan

1. 使用 Codex `skill-creator` 初始化并实现公共 `openspec-review-change/` 目录、Codex UI 元数据和 references。
2. 在 GitNexus impact 结果基础上扩展安装器和标准权限，并先用临时 HOME 完成 Claude Code/Codex 双端安装回归。
3. 更新 README 的项目定位、安装、调用和工作流说明，不执行真实用户目录安装。
4. 在隔离临时 OpenSpec 项目中准备完整冲突、缺失 artifact、无实质问题、部分实施、嵌套 root 和非 spec-driven 等 fixtures。
5. 使用 fresh Codex agent 与独立 Claude Code smoke run 分别验证显式调用、触发、报告契约和只读性；用 hash/Git diff 证明被审查文件未变化并清理 fixtures。
6. 通过带 PyYAML 的隔离解释器运行两端 skill validators，再运行 OpenSpec 严格校验、静态契约检查和 GitNexus 变更范围检测。

本变更只新增诊断能力，无数据迁移。回滚时删除新增 skill 目录并恢复 README；现有 propose、apply、verify 和 archive 流程不受影响。

## Open Questions

无。首版采用单 active change、spec-driven、只读、显式可调用且允许安全自然语言触发的范围；批量审查、归档 change 审查和其他 Schema 语义 profile 留待真实使用反馈后评估。
