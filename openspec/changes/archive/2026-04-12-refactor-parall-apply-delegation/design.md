## Context

当前 `new-worktree-apply` SKILL.md 的步骤 7-10 包含完整的 apply 后处理逻辑：Artifact 校验、Task Backfill（自动检测文件存在性并标记 `[x]`）、Force-add tasks.md 并 commit。

`parall-new-worktree-apply` 的 Agent prompt 中步骤 2-3 重复了完全相同的逻辑，导致：
1. 维护成本翻倍 — 修改一处必须同步另一处
2. 行为不一致风险 — 忘记同步时两边行为出现差异

## Goals / Non-Goals

**Goals:**
- parall Agent prompt 中不再内联后处理逻辑，改为引用 new-worktree-apply 的步骤 7-10
- 修改 new-worktree-apply 步骤 7-10 时，parall 自动获得更新
- 最小化改动范围 — 只修改 parall-new-worktree-apply/SKILL.md

**Non-Goals:**
- 不重构 new-worktree-apply 本身
- 不提取共享 snippet/include 机制
- 不处理前置检查逻辑的重复（git 检查、auto-commit、主分支检测）——这些在两个 skill 中的语义不同

## Decisions

### D1: Agent 通过 Read 工具实时读取 new-worktree-apply SKILL.md

**选择**: parall Agent prompt 中指示 Agent 用 Read 工具读取 `new-worktree-apply/SKILL.md`，按其中的步骤 7-10 执行。

**替代方案**:
- 方案 B: 拆分为独立 skill（如 `opsx:apply-and-finalize`）——增加 skill 数量，过度抽象
- 方案 C: 提取共享 markdown 片段 —— Claude Code 没有 snippet include 机制

**理由**: Read 工具是子代理默认可用的工具，每次执行时实时读取最新内容，修改 new-worktree-apply 后立即生效，无需引入新机制。

### D2: 引用路径使用相对于项目根目录的路径

**选择**: `new-worktree-apply/SKILL.md`

**理由**: Agent 的 `isolation: "worktree"` 创建的 worktree 是项目仓库的完整副本，目录结构与主仓库一致。`new-worktree-apply/SKILL.md` 位于项目根目录，在 worktree 中同样可访问。

### D3: 不改变 parall 中单 change 简化路径

**选择**: parall 的 Step 3.1（单个 change 时）仍然直接调用 `opsx:apply`，不委托 new-worktree-apply。

**理由**: 单 change 路径在主会话中执行，没有 Agent 隔离，与 new-worktree-apply 的 EnterWorktree 流程不兼容。这个路径的重复已在之前的分析中确认是合理的。

## Risks / Trade-offs

- **[Read 失败]** → 若 new-worktree-apply/SKILL.md 不存在或路径错误，Agent 会报错。缓解：prompt 中明确路径，并在 parall 的前置步骤中验证该文件存在。
- **[步骤编号变更]** → 若 new-worktree-apply 重构导致步骤 7-10 编号变化，parall prompt 中的引用失效。缓解：在 prompt 中用功能描述而非仅编号引用（如"步骤 7-10（Artifact 校验、Task Backfill、Force-add commit）"）。
