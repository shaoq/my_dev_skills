## Context

当前项目已有完整的 OpenSpec 工具链：`/opsx:propose` 创建单个提案、`/opsx:apply` 实施提案、`/parall-new-worktree-apply` 并行执行多个待实施提案。但规划阶段缺少一个编排层：用户提出大型综合需求时，需要手动逐个创建提案并手动管理依赖关系。`parall-new-worktree-apply` 已支持解析 `proposal.md` 中的 `## Dependencies` 段并进行拓扑排序，但这个段目前只能手动编写。

核心约束：不自建 artifact 生成逻辑，完全复用 `/opsx:propose` Skill。这避免了代码重复和漂移风险。

## Goals / Non-Goals

**Goals:**
- 接收用户综合需求描述，自动分析功能边界并拆解为多个独立子方案
- 构建依赖图并预览 Wave 分组，让用户在创建前确认拆解方案
- 循环调用 `/opsx:propose` 为每个子方案创建完整 OpenSpec artifacts
- 后注入 `## Dependencies` 段到每个子方案的 `proposal.md`，格式兼容 `parall-new-worktree-apply`
- 输出总结报告，展示依赖图和预估 Wave 分组

**Non-Goals:**
- 不实施任何代码变更（纯规划工具）
- 不替代 `/opsx:propose` 的 artifact 生成逻辑
- 不处理已有提案的依赖更新（仅处理新创建的提案）
- 不处理提案间的代码冲突检测（由执行阶段的 `parall-new-worktree-apply` 负责）

## Decisions

### Decision 1: 通过 Skill 工具调用 `/opsx:propose`，而非直接操作 openspec CLI

**选择**: 使用 `Skill` 工具调用 `/opsx:propose <name>`，传入子方案描述

**替代方案**: 直接调用 `openspec new change` + 读取 `openspec instructions` + 手动生成 artifacts

**理由**:
- `/opsx:propose` 已封装了完整的 artifact 生成流程（proposal → design → specs → tasks）
- 零代码重复，单一维护点
- Skill 调用虽然串行，但规划阶段速度要求不高

**代价**: 串行创建，N 个提案需要 N 次串行 Skill 调用。对于规划阶段可接受。

### Decision 2: 后注入 Dependencies 段，而非在 Skill 调用中预设

**选择**: `/opsx:propose` 完成后，用 `Read` + `Edit` 工具在 `proposal.md` 末尾追加 `## Dependencies` 段

**替代方案**: 修改 `/opsx:propose` 模板以支持预设 Dependencies 段

**理由**:
- 不修改 `/opsx:propose`，遵守"只使用不修改"原则
- 后注入操作简单：定位文件末尾，追加标准格式段落
- `parall-new-worktree-apply` 的解析规则只做 `## Dependencies` 标题 + 列表项匹配，追加不影响其他段落

### Decision 3: 拆解策略采用"功能切片"维度 + 三问判定框架

**选择**: 按**功能切片**（可独立交付的功能单元）拆分，而非按文件或模块拆分。每个候选子方案需通过三问判定，不通过则合并。

**三问判定框架**:

```
Q1: 能否独立测试？
    → 能跑测试套件并看到绿色，而不是"它改了一个文件"

Q2: 能否独立理解？
    → 看 proposal.md 就知道它在做什么，而不是"某个大功能的内部步骤"

Q3: 产出是否有独立价值？
    → 即使其他提案还没做完，这个提案完成后的产出对项目有增量价值
```

三问全 YES → 值得独立提案。任一 NO → 合并到相关提案。

**数量参考**（非硬限制，供 skill 内部参考）:
- 1-2 个提案 → 不需要本 skill，直接用 `/opsx:propose`
- 3-5 个提案 → 合理区间
- 5-8 个提案 → 上限，超过 8 个大概率过度拆分

**替代方案 A: 按文件拆分**
- 问题: 每个提案只改几个文件，缺乏可验证的完整功能，管理开销大

**替代方案 B: 按模块拆分**
- 问题: 可能过粗，一个大模块内仍有可并行的功能切片

**替代方案 C: 纯并行度优先**
- 问题: 为了最大化并行而过度拆分，提案间依赖关系爆炸，合并冲突概率反而升高

**理由**:
- 功能切片是自然的交付边界，团队日常也是按功能而非按文件组织工作
- 三问判定确保每个提案都有存在意义，不为并行而拆
- 合并后的提案数通常在 3-5 个区间，兼顾并行效率和管理成本

## Risks / Trade-offs

- **[拆解质量依赖 AI 推理]** → 拆解方案需经用户确认后再执行，用户可调整子方案数量和依赖关系
- **[Dependencies 段位置]** → `/opsx:propose` 生成的 `proposal.md` 格式由 openspec 模板控制，后注入的 `## Dependencies` 段可能出现在非标准位置。但 `parall-new-worktree-apply` 的解析规则只匹配标题行，位置不影响解析。
- **[串行创建耗时]** → 5 个提案可能需要 5-10 分钟。规划阶段可接受，且相比手动创建节省更多时间。
