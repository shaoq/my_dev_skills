## Context

项目使用 OpenSpec 管理变更流程，changes 完成实施后需要归档到 `openspec/changes/archive/`。现有 `opsx:archive` 处理单个归档，`check-changes-completed` 做四维诊断但只可选引导归档。缺少一个"一键归档所有已完成 changes"的批量工具。

当前判定"已完成"的核心维度：tasks.md 任务全完成、代码文件已落地并 commit 到当前分支、依赖链无阻塞。

## Goals / Non-Goals

**Goals:**
- 自动扫描所有 active changes 并输出可归档性报告
- 通过三维模型（tasks + 代码落地 + 依赖）精确判定代码已完成的 changes
- 复用 `opsx:archive` 执行实际归档，不重复实现归档逻辑
- 提供三种确认策略，适应不同场景

**Non-Goals:**
- 不替代 `check-changes-completed` 的四维诊断功能
- 不检查 OpenSpec artifacts 完成状态（D2），由 `opsx:archive` 自行处理
- 不处理归档后的 spec sync 细节，委托给 `opsx:archive`

## Decisions

### D1: 三维模型而非四维

采用三维检查（tasks + 代码落地 + 依赖），去掉 artifacts 检查（D2）。

**理由**: `opsx:archive` 自身会检查 artifacts 状态并在需要时警告用户。重复检查没有意义，且可能导致判定不一致。

**替代方案**: 复用 `check-changes-completed` 的完整四维检查 → 过于重量级，且用户已明确只需要"代码已完成"判定。

### D2: 代码判定使用 git log + 当前分支

```bash
git log <current-branch> -- <expected-files>
```

**理由**: 用户明确要求确认代码已提交到当前分支。仅检查文件存在不够，因为文件可能只在 worktree 中未合并回来。

**预期文件来源**: 从 `design.md` 和 `proposal.md` 的 `## Impact` 段提取文件路径。若无明确路径，使用启发式：检查 `<change-name>/SKILL.md` 是否存在。

### D3: 复用 opsx:archive 而非自建归档

每个可归档 change 调用 `Skill("opsx:archive", args="<name>")`。

**理由**: `opsx:archive` 已处理 artifact 检查、delta spec sync、目录移动等完整流程。自建归档需要重复大量逻辑且容易与现有流程不一致。

**代价**: 每个 change 的归档有交互确认，批量体验略差。但可通过在 skill 中明确提示"批量模式"来改善。

### D4: 确认策略三选一

报告输出后，使用 AskUserQuestion 提供"全部归档 / 逐个确认 / 仅查看"三个选项。

**理由**: 用户在 explore 阶段已明确选择此方案。兼顾效率和安全性。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 代码文件路径提取不准确（design.md 中未明确列出） | 使用启发式 fallback：`<change-name>/SKILL.md`；同时检查 git diff 中该 change 相关的文件变更 |
| `opsx:archive` 批量调用时某个失败阻塞后续 | 失败不阻塞，记录错误继续下一个 |
| 归档过程中用户中断导致部分归档 | 已归档的不可回滚，未归档的保持原状；最终报告明确标注哪些成功哪些失败 |
| 依赖判定误判（依赖 change 已归档但代码未合入 main） | 检查依赖 change 是否在 archive/ 中存在即可，已归档视为完成 |
