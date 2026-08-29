## Why

现有 skills 能分别完成需求脑暴、代码探索、影响分析与 OpenSpec 调研，但缺少一套面向复杂架构设计的统一编排契约。没有该契约时，Agent 容易把架构探索直接推进为 OpenSpec 提案、混淆架构项目与实施项目，或产出无法独立评审、无法安全交接给研发 Team 的方案。

## What Changes

- 新增 `architecture-design-workflow` skill，统一复杂架构议题从接收、项目路由、事实调研、方案设计、独立评审、人工批准、ADR 发布到研发交接的阶段、产物和门禁。
- 支持 `evolution`、`greenfield`、`hybrid` 三类架构设计，并为不同类型定义证据要求、系统边界、迁移与回滚检查。
- 架构设计阶段允许按条件使用 `superpowers:brainstorming`，随后只以 `openspec-explore` 的思考模式开展分析；禁止创建 proposal、design、specs、tasks 等 OpenSpec artifacts。
- 使用结构化的 `ARCH-CONTROL`、`ARCH-RESEARCH`、`ARCH-DESIGN`、`ARCH-REVIEW`、`ARCH-RD-HANDOFF` 与 ADR/详细设计模板，使 Issue 内过程和仓库内批准方案可独立审阅。
- 明确 `approved_design_only` 与 `approved_for_spec` 两个人工门禁；只有后者才授权目标研发项目按既有 R&D Team 流程创建 OpenSpec change。
- 强制中文回复，并要求代码理解、代码定位、变更影响分析和架构事实核验优先使用 GitNexus；索引过期时先重建。
- 使用现有 `setup-skills-env.py` 的根目录 skill 扫描与双运行时链接机制，将同一源目录安装到 Claude Code 与 Codex。
- 为 skill 增加 Codex 元数据、参考文档、模板、静态校验及基于已记录基线失败的行为压力测试。

## Capabilities

### New Capabilities

- `architecture-design-governance`: 定义复杂架构议题的分类、项目路由、阶段产物、人工门禁、跨项目交接和禁止事项。
- `architecture-design-artifacts`: 定义可读、可审阅且可追踪的架构研究、独立方案、评审、ADR、详细设计和研发交接报告契约。
- `architecture-skill-runtime-installation`: 定义 `architecture-design-workflow` 在 Claude Code 与 Codex 中共享单一源码、可验证安装和安全冲突处理的行为。

### Modified Capabilities

无。

## Impact

- 在仓库根目录新增 `architecture-design-workflow/`，包括 `SKILL.md`、`agents/openai.yaml`、`references/` 和 `templates/`。
- 复用现有 `setup-skills-env.py`，原则上无需修改安装器；若实现阶段发现扫描或跨端发现不兼容，必须先补充失败测试并将任何修改限制在安装兼容范围内。
- 实施完成后会在 `~/.claude/skills/architecture-design-workflow` 与 `~/.codex/skills/architecture-design-workflow` 创建指向仓库源目录的受管软链接；不得覆盖同名普通文件或目录。
- 不修改 Multica 应用代码、现有 R&D Team、现有 OpenSpec skills 或用户项目数据；Architecture Team 的创建与绑定由独立项目提案负责。
