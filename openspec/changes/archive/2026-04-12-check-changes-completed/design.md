## Context

OpenSpec 工作流中已有 `openspec-archive-change` skill 负责单个 change 的存档检查，但它是存档流程的一部分，不具备全局视角。`parall-new-worktree-apply` 在并行执行后做了验证，但仅限于它执行的 changes，且是执行流程的附属步骤。

需要一个独立的、可随时调用的全局检查 skill，覆盖所有 active changes，通过四维模型评估完成情况。

当前目录结构约定：
```
openspec/changes/
├── archive/           ← 已存档，扫描时排除
├── change-a/
│   ├── proposal.md    ← 含 ## Dependencies 段
│   ├── design.md
│   ├── specs/
│   ├── tasks.md       ← [x] / [ ] 勾选状态
│   └── .openspec.yaml
└── change-b/
```

## Goals / Non-Goals

**Goals:**
- 一次调用即可全局掌握所有 active changes 的完成情况
- 四维检查模型全面覆盖，不遗漏虚假完成
- 清晰的表格汇总输出，一目了然
- 可存档的 changes 提供存档引导，减少手动操作
- 与现有 skill 互补，不重复已有功能

**Non-Goals:**
- 不负责修复或实施未完成的 tasks
- 不负责解决依赖冲突
- 不替代 `openspec-archive-change` 的存档功能（仅引导调用）
- 不检查已存档的 changes

## Decisions

### D1: 四维检查的实现策略

**决策**: 维度 3（Code 落地验证）采用 **产出文件存在性检查 + git log 提交验证** 混合策略。

**理由**:
- 纯文件存在性检查简单但可能误判（空文件、占位文件）
- 纯 git log 检查无法确认具体产出物
- 混合策略：先检查 design.md 或 proposal.md 中提到的关键产出文件是否存在，再通过 `git log --oneline main..HEAD` 确认有实质提交

**替代方案**: 内容抽样（读 tasks 中关键项抽查对应函数/文件是否存在）— 可靠但复杂度高，不适合作为轻量检查工具。

### D2: 输出格式

**决策**: 使用 markdown 表格汇总 + 详细阻塞原因列表。

**理由**: 表格形式信息密度高，用户可快速扫描。阻塞原因列表提供行动指引。

### D3: 存档引导方式

**决策**: 检查完毕后，对可存档 changes 使用 AskUserQuestion 询问存档策略（全部存档 / 逐个确认 / 仅查看）。

**理由**: 存档是不可逆操作，需要用户确认。提供三种粒度满足不同场景。

### D4: 依赖检查逻辑

**决策**: 读取每个 change 的 `proposal.md` 的 `## Dependencies` 段，提取依赖名称列表，验证每个依赖 change 的四维状态。

**理由**: 与 `parall-new-worktree-apply` 使用相同的依赖来源，保持一致性。依赖链中的任一环节未完成，则该 change 标记为"依赖阻塞"。

## Risks / Trade-offs

- **[维度 3 误判风险]** → 缓解：git log 验证提供客观依据，不以 tasks.md 勾选为唯一标准
- **[大型项目中 git log 慢]** → 缓解：限定 git log 查询范围为 change 相关文件路径
- **[依赖图深度遍历可能循环]** → 缓解：记录已访问节点，检测到循环时标记异常
