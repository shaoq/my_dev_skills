## Why

现有 OpenSpec 工作流能够生成并校验提案 artifact 的结构，但在进入实施前缺少针对目标清晰度、方案完整性、跨 artifact 一致性和任务可执行性的语义审查。结构校验通过的提案仍可能包含互相冲突的决策、需求覆盖缺口或不可验证的任务；同时当前自定义 skills 虽已在本机同时链接给 Claude Code 与 Codex，仓库安装器却只管理 Claude Code，新增 skill 无法被两个运行时一致、可重复地发现。

## What Changes

- 新增 `openspec-review-change` skill，用于审查一个刚创建或尚未归档的 active OpenSpec change，并输出实施就绪结论。
- 审查覆盖 Schema 合规、目标与范围、项目事实基础、设计完整性、Spec 可测试性、跨 artifact 一致性、需求追踪性和任务实施就绪度。
- 首版完整支持 `spec-driven` Schema，动态读取 change 状态、artifact instructions、输出路径和依赖；遇到其他 Schema 时明确报告不支持并以 `BLOCKED` 结束，避免产生虚假的实施就绪结论。
- 支持可选 `--openspec-root <repo-relative-directory>`，与现有单 change worktree skill 使用相同的嵌套 OpenSpec 项目定位语义。
- 使用 `BLOCKED`、`NEEDS_REVISION`、`READY_WITH_WARNINGS`、`READY` 四级门禁结论，并为每个发现提供严重度、证据、影响和修改建议。
- 默认保持纯诊断、只读；不自动修改 change artifacts 或应用代码。
- 在 GitNexus 可用时增强代码库事实和影响范围核验，不可用时退化为常规文件与文本检索。
- 识别 pre-apply、部分实施和 tasks 全部完成的 change 阶段；后两种情况下仍可审查 artifacts，但必须声明当前工作树证据不能视为实施前基线，也不替代实现一致性检查。
- 使用同一份 `SKILL.md` 同时兼容 Claude Code 与 Codex：公共 frontmatter 保持两端可解析，Codex UI 元数据放入 `agents/openai.yaml`，两端调用与触发行为分别验证。
- 扩展 `setup-skills-env.py`，将根目录自定义 skills 安装和卸载到 `~/.claude/skills/` 与 `~/.codex/skills/`，并保持已有链接冲突和保护规则。
- 为 Claude Code 标准权限补充 `openspec validate`，使严格预检无需额外权限缺口。
- 增加审查规则和报告契约参考文件，并更新项目使用文档。

## Capabilities

### New Capabilities

- `openspec-proposal-review`: 在 OpenSpec change 进入 apply 前，对其 artifacts 执行结构、语义、事实、追踪性和任务就绪度审查，并输出可操作的门禁报告。
- `cross-runtime-skill-installation`: 使用同一份仓库 skill 源目录，为 Claude Code 和 Codex 安装、核验和卸载独立的全局发现链接，同时保持非本项目路径不被误删或覆盖。

### Modified Capabilities

无。

## Impact

- 新增 `openspec-review-change/` skill 目录，包括跨端公共 `SKILL.md`、Codex `agents/openai.yaml` 和 `references/` 下的审查规则与报告契约。
- 修改 `setup-skills-env.py` 的安装、卸载、摘要和标准权限，使其同时管理 Claude Code 与 Codex skill 目录，并加入 `openspec validate` 权限。
- 新增双端安装回归测试，使用临时 `HOME` 验证安装、重复安装、冲突保护、部分失败和卸载，不触碰真实用户目录。
- 更新 `README.md`，将项目定位更新为 Claude Code + Codex Skills 集合，并补充两端安装、调用方式和工作流位置。
- 复用现有 `openspec` CLI；不修改 OpenSpec 核心 skills、Schema、应用代码或其他现有 change artifacts。
- GitNexus 是可选增强能力，不新增强制外部依赖。
- `setup-skills-env.py` 现有 `scan_custom_skills()` 继续作为单一发现源；计划修改的安装与卸载函数经 GitNexus upstream impact 检查均为 LOW 风险，并只进入现有 main 安装流程。
