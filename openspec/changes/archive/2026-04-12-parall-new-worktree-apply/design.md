## Context

项目使用 OpenSpec 管理变更提案，每个提案通过 worktree 隔离实施。目前已有的 `new-worktree-apply` 和 `merge-worktree-return` 两个 skill 处理单个提案的完整生命周期。但当多个提案同时待实施时，需要手动逐个调用，效率低且无法利用并行能力。

Claude Code 的 `Agent` 工具支持 `isolation: "worktree"` 参数，可以为每个子代理创建独立的 git worktree 副本，实现真正的并行工作。子代理完成后返回分支名，主会话负责合并。

## Goals / Non-Goals

**Goals:**
- 自动发现所有待执行的 OpenSpec changes
- 解析提案间的依赖关系，构建执行图
- 无依赖的 changes 并行执行，有依赖的按序执行
- 每轮并行完成后串行合并回主干
- 冲突时智能分析并自动解决
- 全部完成后验证所有 changes 状态

**Non-Goals:**
- 不处理跨仓库的依赖关系
- 不实现 proposal 依赖声明的语法校验工具（依赖人工书写正确）
- 不支持部分失败后自动重试（报告失败由用户决定）

## Decisions

### D1: 并行执行使用 Agent + isolation: "worktree"

**选择**: 使用 `Agent` 工具的 `isolation: "worktree"` 参数为每个 change 创建独立 worktree。

**替代方案**: 主会话串行使用 `EnterWorktree` / `ExitWorktree`。

**理由**: Agent isolation 方案实现真正的并行，子代理各自独立工作互不干扰。`EnterWorktree` 限制主会话同一时间只能在一个 worktree 中，无法并行。

### D2: 单个 change 时委托 new-worktree-apply

**选择**: 当待执行 changes 数量为 1 时，直接调用 Skill "opsx:apply" 并走完整的 new-worktree-apply 流程。

**理由**: 复用现有 skill 的完整逻辑（EnterWorktree + apply + merge + exit），避免重复实现。

### D3: 依赖声明在 proposal.md 的 ## Dependencies 段

**选择**: 在 proposal.md 中用 `## Dependencies` 段 + 无序列表声明依赖。

**格式**:
```markdown
## Dependencies
- change-a
- change-b
```

**理由**: 简单直观，与 proposal.md 的现有格式一致。无此段视为无依赖。

### D4: Wave 内合并采用 rebase + merge

**选择**: 每个 Wave 完成后，对每个分支先 `git rebase main`，再 `git merge <branch>`。

**理由**: rebase 确保分支基于最新的 main（包含之前 Wave 的合并），减少冲突。merge 保留完整的提交历史。

### D5: 冲突智能解决策略

**选择**: rebase 冲突时，Claude 读取冲突文件标记，分析语义后尝试自动合并。

**层级**:
1. 非重叠区域 → 双方都保留
2. 重叠但语义可合并 → 智能合并
3. 无法自动解决 → `git rebase --abort` 并报告

**理由**: 大多数并行 changes 修改不同文件，冲突较少。对于少量冲突，智能解决比直接放弃更高效。

## Risks / Trade-offs

- **[Agent 权限问题]** → 子代理可能因权限不足无法执行某些操作。缓解：使用 `mode: "bypassPermissions"` 或 `"auto"` 模式，并在 prompt 中明确要求 commit。
- **[多 changes 修改同一文件]** → 并行执行后合并必然冲突。缓解：智能冲突解决，失败时报告给用户。
- **[子代理 apply 超时]** → 单个子代理执行时间可能很长。缓解：设置合理的 timeout，Wave 内等待不设限。
- **[依赖声明错误]** → 用户可能声明不存在的依赖名或产生循环依赖。缓解：启动时校验依赖图的合法性。
