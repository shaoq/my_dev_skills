## Context

my_dev_skills 是一个 Claude Code Skills 集合，基于 OpenSpec 工作流。现有 5 个 skills 中，`check-changes-completed` 提供五维完成度检查（存在性/状态级），但缺少语义层面的深度验证。项目需要一个新的独立 skill 来补充这一空白。

该 skill 的定位是**纯诊断工具**，不需要 `disable-model-invocation`（与现有 skills 不同），因为 Layer 2 语义分析需要 Claude 的理解能力。

## Goals / Non-Goals

**Goals:**
- 实现三维一致性检查：Doc↔Code、Schema↔API Code、Tests↔Code
- 采用分层验证策略：Layer 1 精确匹配 + Layer 2 语义分析
- 支持双模式运行：始终项目级扫描，有活跃 OpenSpec change 时追加增量验证
- 多语言路由匹配（TS/JS, Python, Go, Java）
- 纯诊断输出，CRITICAL/WARNING/INFO 三级分级

**Non-Goals:**
- 不做 pass/fail 判定（不是门禁工具）
- 不自动修复不一致（只报告）
- 不做 AST 级精确分析（保持语言无关性）
- 不替代 `check-changes-completed`（两者互补）
- 不支持单语言深度框架集成（如 NestJS 装饰器解析、Spring Bean 分析）

## Decisions

### D1: 模型驱动 vs 纯脚本驱动

**决策**: 模型驱动（`disable-model-invocation: false`）

**理由**: Layer 2 语义分析需要理解"文档说校验邮箱格式，代码只校验非空"这类语义差异，纯 bash/regex 无法实现。现有 `check-changes-completed` 使用 `disable-model-invocation: true` 是因为它的逻辑完全程序化（计数文件、检查状态），不需要语义理解。

**替代方案**: 纯脚本驱动 — 只做 Layer 1 精确匹配。被否决因为缺少语义层面的价值。

### D2: 双模式策略 — 项目优先

**决策**: 始终执行项目级扫描（D1/D2/D3），检测到活跃 OpenSpec change 时追加 change 级精细验证。

**理由**: 项目级扫描提供基线健康视图，OpenSpec 增量提供 focused 验证。两者合并到一份报告中，用户无需思考"该用哪个模式"。

**替代方案**:
- 参数驱动模式切换 — 用户可能忘记选择正确的模式
- 仅 OpenSpec 模式 — 无法服务非 OpenSpec 项目

### D3: 分层验证策略

**决策**: Layer 1 精确模式匹配（Grep）→ Layer 2 语义分析（Claude Read）

**理由**: Layer 1 快速过滤掉明确匹配和明确不匹配的项，只把不确定的交给 Layer 2。这平衡了速度和准确性。

**替代方案**:
- 纯语义分析 — 全部交给 Claude 阅读，速度慢且成本高
- 纯精确匹配 — 无法发现语义层面的不一致

### D4: 文档扫描启发式过滤

**决策**: 按文件名/路径启发式分级（HIGH/MEDIUM/SKIP），优先读取含代码声明的文档。

**理由**: 大型项目可能有大量 .md 文件（CHANGELOG、翻译文件等），全量读取不实际。启发式过滤平衡覆盖率和效率。

### D5: 多语言路由匹配模式表

**决策**: 在 SKILL.md 中内嵌多语言路由模式参考表，Claude 根据项目实际使用的语言和框架选择匹配模式。

**理由**: Claude 能自动识别项目的技术栈（通过 package.json/requirements.txt/go.mod/pom.xml 等），无需用户指定。模式表提供 Grep 搜索的 pattern 参考。

## Risks / Trade-offs

- **[模型依赖]** Layer 2 依赖 Claude 的语义理解能力，结果可能因模型版本不同而有差异 → 限定 Layer 2 只处理 Layer 1 无法判定的 UNCERTAIN 项，减少模型参与比例
- **[大项目性能]** 项目级全扫描在大项目中可能耗时 → 启发式过滤减少读取量；D2 无 schema 文件时直接跳过
- **[提取准确性]** 从自由文本文档中提取声明可能遗漏或误提取 → Layer 1 做快速验证，Layer 2 做二次确认
- **[跨框架路由变体]** 同一语言不同框架的路由定义差异大 → 模式表覆盖主流框架，无法匹配时归入 UNCERTAIN 交 Layer 2
- **[Monorepo 复杂度]** 多包项目可能需要按子目录分组 → 报告按子目录分组展示
