## Context

`check-changes-completed` 是一个 Claude Code skill，用于检查 OpenSpec changes 的完成度。当前采用四维模型（D1-D4），覆盖 OpenSpec 内部交付物，但不检查项目级规范合规性。

Claude Code 项目通过 `CLAUDE.md` 文件定义项目级规范（测试策略、文档要求、API schema 管理等）。这些规范以自然语言编写，无固定格式。

当前 D1-D4 检查流程已形成成熟的模式：收集维度结果 → 矛盾检测 → 汇总表 → 阻塞原因 → 归档提示。D5 需要融入这个既有模式。

## Goals / Non-Goals

**Goals:**

- 自动发现并载入项目 CLAUDE.md（根目录 + 变更相关子目录）
- 从 CLAUDE.md 提取合规要求（test-sync / doc-sync / api-schema-sync / changelog-sync / 自定义）
- 根据变更范围判断是否触发合规要求
- 验证配套产出是否已同步（通过 git diff）
- 在汇总表中展示合规状态，在阻塞原因中展示完整缺失内容
- 缺失时建议用户运行 `/opsx:explore`，不自动补全

**Non-Goals:**

- 不解析 CLAUDE.md 的全部内容，仅提取合规相关要求
- 不自动创建或修改配套产出（测试文件、文档、schema 等）
- 不引入外部 NLP/AST 解析依赖
- 不改变 D1-D4 的现有行为
- 不改变回填（backfill）逻辑 — D5 不参与回填

## Decisions

### Decision 1: D5 作为纯诊断维度

**选择**: D5 仅报告缺失，不自动修复。

**理由**: 配套产出的缺失需要人工判断范围和内容（如"哪些测试需要更新"），自动创建可能导致不准确的产出。

**备选方案**: 自动生成配套产出的骨架 → 否决，因为不同项目的配套产出差异极大。

### Decision 2: CLAUDE.md 解析采用正则关键词匹配

**选择**: 逐行正则匹配，匹配常见中英文表达模式。

**理由**: CLAUDE.md 是自然语言，无标准格式。正则匹配简单、确定性强、可扩展。覆盖以下关键词族：

| 类型 | 触发关键词 |
|------|-----------|
| test-sync | must update tests, 必须更新测试, 每次变更后更新测试, always run tests |
| doc-sync | must update docs, 必须更新文档, always include doc updates |
| api-schema-sync | must update API/schema, 必须更新接口/schema |
| changelog-sync | must update changelog, 必须更新变更日志 |

**备选方案**: LLM 提取 → 否决，skill 内不应依赖额外的 LLM 调用。

### Decision 3: 触发判断基于变更范围

**选择**: 使用 D3 已收集的 EXPECTED_FILES 和 design.md 内容判断触发。

| 合规要求 | 触发条件 |
|---------|---------|
| test-sync | EXPECTED_FILES 包含源码文件（排除测试文件自身） |
| doc-sync | EXPECTED_FILES 包含源码文件或 SKILL.md |
| api-schema-sync | design.md 提及 API/endpoint/route/schema |
| changelog-sync | EXPECTED_FILES 非空 |

**理由**: 复用 D3 已有数据，避免重复分析。

### Decision 4: 合规检查通过 git diff 验证

**选择**: `git diff main..HEAD --name-only` 匹配文件名模式。

| 合规要求 | 匹配模式 |
|---------|---------|
| test-sync | `test`, `spec`, `_test.` |
| doc-sync | `doc`, `.md`, `README` |
| api-schema-sync | `schema`, `openapi`, `swagger`, `.proto` |
| changelog-sync | `CHANGELOG`, `HISTORY` |

**备选方案**: 仅检查文件存在性 → 否决，因为文件可能存在但未随本次变更更新。

### Decision 5: 无 CLAUDE.md 不阻塞归档

**选择**: 无 CLAUDE.md 时 D5 = `✓ (无项目规范)`，不阻塞。

**理由**: 不是所有项目都有 CLAUDE.md，不应因此惩罚。

## Risks / Trade-offs

- **[正则误匹配]** → 使用精确的关键词模式（"must update"、"必须更新"、"每次变更后"等高确定性短语），降低误报。若 CLAUDE.md 语句不在模式表中，不会触发。
- **[合规要求未覆盖]** → D5 仅检查已知模式。用户可在 CLAUDE.md 中使用标准表述来确保被识别。
- **[git diff 范围局限]** → 依赖 `main..HEAD` 范围。若 main 分支名不同，D3 已处理了分支检测逻辑，D5 复用同一范围。
- **[子目录 CLAUDE.md 可能过多]** → 仅检查 D3 EXPECTED_FILES 涉及的子目录，不递归扫描全项目。
