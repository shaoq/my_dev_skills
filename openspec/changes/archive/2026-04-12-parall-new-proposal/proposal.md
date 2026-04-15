## Why

当用户提出一个综合性的大型需求时，当前的 `/opsx:propose` 只能创建单个提案，无法从规划阶段就考虑并行度优化。用户需要手动逐个创建提案并手动声明依赖关系，效率低下且容易遗漏依赖。需要一个编排层 skill，在规划阶段就分析功能边界和依赖关系，将大需求拆解为多个带依赖声明的独立提案，使得后续 `/parall-new-worktree-apply` 可以最大化并行执行。

## What Changes

- 新建 `parall-new-proposal` skill，作为规划阶段的编排层
- 支持接收用户综合需求描述，按**功能切片**维度（而非文件或模块维度）拆解为多个子方案
- 拆解颗粒度遵循**交付单元**原则：每个子方案 SHALL 通过三问判定（独立测试、独立理解、独立价值），不通过则合并到相关提案，避免为并行而过度拆分
- 支持构建依赖图，按拓扑序预览 Wave 分组方案
- 支持用户确认拆解方案后，循环调用 `/opsx:propose`（通过 Skill 工具）为每个子方案创建完整 OpenSpec artifacts
- 支持在每个子方案的 `proposal.md` 中后注入 `## Dependencies` 段，格式兼容 `parall-new-worktree-apply` 的解析规则
- 不自建 artifact 生成逻辑，完全复用 `/opsx:propose`，零代码重复

## Capabilities

### New Capabilities
- `requirement-decomposition`: 分析用户综合需求，识别功能边界，拆解为可独立并行的工作单元，构建依赖图并预览 Wave 分组
- `batch-proposal-creation`: 循环调用 /opsx:propose 为每个子方案创建完整 artifacts，并在 proposal.md 中后注入 ## Dependencies 段
- `dependency-injection`: 对已创建的 proposal.md 后注入依赖声明段，格式兼容 parall-new-worktree-apply 的 ## Dependencies 解析规则

### Modified Capabilities
（无）

## Impact

- 新增 skill 文件：`parall-new-proposal/SKILL.md`（项目根目录下）
- 依赖：`/opsx:propose`（通过 Skill 工具调用）、`openspec` CLI（`openspec new change`、`openspec status`、`openspec instructions`）
- 产出兼容：每个子方案的 `proposal.md` 中的 `## Dependencies` 段格式与 `parall-new-worktree-apply` Step 2.1 的解析规则完全一致
- 影响：用户工作流从"手动逐个创建提案 + 手动声明依赖"变为一条命令 `/parall-new-proposal` 自动完成全部分析和创建
