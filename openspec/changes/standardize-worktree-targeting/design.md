## Context

项目有三个组成 worktree 生命周期的高风险 Git skill：`new-worktree-apply` 创建并实施单个 change，`merge-worktree-return` 将单个 worktree 合并回目标，`parall-new-worktree-apply` 批量创建、实施和串行合并多个 change。当前三者对“主工作树”“主分支”“创建基线”和“合并目标”的定义不一致：两个 skill 优先检测 `main`，一个 skill 虽提供 `--branch`，却记录当前 HEAD 并从当前 HEAD 创建 worktree；批量 skill 还在展示所谓确认计划前自动提交，且没有真正等待用户回答。

这些不是三个独立功能，而是同一个跨工作流的目标分支契约。部分更新会保留不一致接口，并可能让创建基线与最终合并目标不同。因此本变更用一个 capability 同时约束三个 skill，同时保持每个 skill 的具体执行步骤独立。

## Goals / Non-Goals

**Goals:**

- 三个 skill 统一使用 `--target <target-branch>` 和 `TARGET_BRANCH`。
- 三个 skill 共享完全相同、可解释的目标选择优先级。
- 在任何 Git 写操作前展示目标和计划并取得明确确认。
- 确保单 worktree 创建基线、单 worktree 合并目标和批量合并目标一致。
- 修复 `new-worktree-apply` 的目标 HEAD 与 worktree 起点错误。
- 确保批量流程的单 change 路径仍在隔离 worktree 中实施。
- 保持 Claude Code 与 Codex CLI 等环境的能力适配和失败即停语义。

**Non-Goals:**

- 不自动 fetch、pull、push 或更新远程引用。
- 不自动创建用户指定的目标分支或远程跟踪分支。
- 不改变 OpenSpec apply、任务回填和归档的业务规则，除非它们必须移动到确认后的正确 worktree。
- 不改变 rebase 后串行 merge 的集成策略。
- 不抽取共享脚本、references 或新的运行时依赖；三个 skill 以一致的低自由度说明实现同一契约。

## Decisions

### 1. 使用一个原子提案覆盖完整 worktree 生命周期

三个 skill 修改不同文件，但共享同一个用户接口和安全不变量。将它们纳入 `standardize-worktree-targeting`，并以 `worktree-targeting` capability 定义统一规则。实施任务按 skill 分组，最终通过一个跨 skill 场景矩阵验收。

备选方案是三个独立提案，可以并行修改文件，但可能产生部分上线、参数不一致和规则漂移；两个额外提案也没有独立于统一契约的产品价值。

### 2. 三个命令只使用 `--target`

统一接口为：

```text
/new-worktree-apply <proposal-name> [--target <target-branch>]
/merge-worktree-return [proposal-name] [--target <target-branch>]
/parall-new-worktree-apply [--target <target-branch>]
```

每个命令最多接受一个 `--target`。`new-worktree-apply` 的 `--branch` 不作为兼容别名：检测到旧参数时在预检阶段停止，显示对应的 `--target` 迁移命令，不产生 Git 写操作。这样避免两个同义参数长期并存。

各 skill 仍保留自己的位置参数约束：`new-worktree-apply` 需要一个 proposal；`merge-worktree-return` 接受零或一个 proposal；批量 skill 不接受 proposal 位置参数。

### 3. 共用确定性目标选择算法

三个 skill 都使用 `git worktree list --porcelain`、精确本地 ref 和只读命令按以下顺序选择：

1. 显式 `--target`；
2. 主工作树当前检出的本地分支；
3. `refs/remotes/origin/HEAD` 指向的本地同名分支；
4. 依次存在的本地 `main`、`master`、`trunk`。

显式目标不存在时直接失败，不静默回退。自动候选为 detached HEAD、不存在于 `refs/heads/` 或在当前场景不可用时跳过；没有候选则要求显式传入 `--target`。每次都记录 `TARGET_SOURCE`，用于确认摘要和最终报告。

备选方案是强制每次传参，安全但破坏无参数便利性；继续优先 `main` 则无法解决本变更的根因。

### 4. 用 worktree 拓扑确定执行目录

统一记录：

- `PRIMARY_WORKTREE_DIR`
- `INVOCATION_WORKTREE_DIR`
- `TARGET_BRANCH`
- `TARGET_WORKTREE_DIR`（若目标已检出）
- `SOURCE_BRANCH`/`SOURCE_WORKTREE_DIR`（回收与批量合并场景）

目标已在某个 worktree 检出时，在该目录读取或更新目标；目标未检出时，仅在干净且可安全切换的主工作树中于确认后 checkout 目标。目标工作树必须满足各流程要求：回收流程要求干净；创建和批量流程若保留 Auto-commit，则必须在摘要中列出将被提交的目标工作树改动。

### 5. 建立共享的只读预检和确认门槛

确认前完成参数解析、目标选择、worktree 映射、分支存在性、状态读取、OpenSpec 状态读取和计划构建。摘要至少显示：

- 命令与 proposal/change 范围；
- 目标分支、选择依据与目标工作树；
- 来源分支和来源 worktree（适用时）；
- 将自动提交的文件状态；
- 将执行的 worktree 创建、apply、rebase、merge、验证和清理动作；
- 未完成任务、必要 checkout 或其他风险。

通过环境可用的交互能力取得无默认值、无超时自动同意的明确确认。Claude Code 使用 `AskUserQuestion`；其他环境使用等价工具，没有工具时输出问题并结束当前响应等待下一条消息。拒绝、取消或模糊回答保持 Git 状态不变。

确认前禁止 `git add`、`git commit`、`git checkout`/`git switch`、`git worktree add`/remove、`git rebase` 和 `git merge`，也不得调用会实施 change 的 apply skill。

### 6. 确认后复检关键快照

首次写操作前重新验证参数解析结果、目标 ref、目标 HEAD、worktree 映射、工作树状态、checkout 需求和风险警告。任一展示过的实质事实变化都使确认失效，返回预检并请求新确认，避免交互等待期间的检查时/使用时竞态。

### 7. `new-worktree-apply` 精确基于目标创建

将 `MAIN_HEAD=$(git rev-parse HEAD)` 改为从已确认目标读取 `TARGET_HEAD=$(git rev-parse "$TARGET_BRANCH")`。确认及复检通过后，先按摘要处理目标工作树待提交改动，再重新记录目标 HEAD。

Codex CLI 使用带显式起点的命令：

```bash
git worktree add <path> -b <proposal-name> <TARGET_BRANCH>
```

Claude Code 使用 `EnterWorktree` 时，必须从已确认目标的 checkout/HEAD 上下文创建；若平台能力不能指定起点，则先在确认后将干净的主工作树切换到目标，或停止并要求用户调整环境，不能从其他当前 HEAD 静默创建。

创建后要求 `WORKTREE_HEAD == TARGET_HEAD` 才能进入 apply。基线不一致时停止，不用 `git merge <TARGET_BRANCH>` 掩盖错误起点。原有 artifact 检查、apply、任务回填和提交在正确 worktree 中继续执行。

### 8. `merge-worktree-return` 围绕已确认目标回收

在来源 worktree 中确认后提交改动并 rebase 到 `TARGET_BRANCH`，然后在 `TARGET_WORKTREE_DIR` 合并 `SOURCE_BRANCH`。仅当 `git log <target>..<source>` 为空且其他退出条件通过时，才使用 `ExitWorktree` 或从非来源目录执行 `git worktree remove`。OpenSpec 未完成任务警告并入同一次风险确认。

### 9. `parall-new-worktree-apply` 围绕已确认目标批量执行

批量 skill 接受 `--target`，发现 changes、构建依赖图和读取状态属于确认前只读阶段。现有 Auto-commit 移到计划确认与复检之后。所有 agent worktree 必须从同一个已确认目标 HEAD 创建；每个 Batch 完成后，分支依次 rebase 并 merge 到同一个 `TARGET_BRANCH`。

即使只发现一个 change，也必须走隔离 worktree 的创建、apply、提交和合并流程，不能直接在目标工作树中调用 apply。最终报告显示目标分支、选择依据和每个分支的合并验证。

### 10. 保持 skill 自包含并以场景矩阵验证

不增加辅助资源。实施后在隔离临时 Git 仓库验证三个命令的显式目标、各级回退、旧参数迁移、取消确认、确认后状态变化、目标只存在远程、目标位于其他 worktree、错误基线、单/多 change 批量路径及成功清理。

## Risks / Trade-offs

- **[`--branch` 调用被破坏]** → 明确标记 BREAKING，并提供可复制的 `--target` 迁移命令。
- **[强制确认打断无人值守流程]** → 将交互作为高风险 Git 写操作的必要安全边界，并在三个 skill 的输入说明中明确。
- **[Claude Code 创建 API 无显式 start-point]** → 从目标 checkout 上下文调用；不能证明基线一致时停止，不静默回退。
- **[目标工作树含未提交改动]** → 在摘要中精确显示；只有明确授权的创建/批量流程才可确认后提交，回收流程要求目标干净。
- **[等待确认期间状态变化]** → 写操作前复检，变化即重新确认。
- **[批量 skill 文件较长、易规则漂移]** → tasks 按共享契约和三个 skill 分组，并用同一场景矩阵逐项核对。

## Migration Plan

1. 将 change 与 capability 重命名为 `standardize-worktree-targeting` 和 `worktree-targeting`。
2. 先在三个 skill 中统一参数解析、目标选择、预检摘要、确认和复检规则。
3. 分别更新单 worktree 创建、单 worktree 回收和批量 apply/merge 的目标驱动流程。
4. 更新 frontmatter、示例、成功/错误输出和 Guardrails，并移除 `MAIN_BRANCH`/`MAIN_DIR` 的错误语义。
5. 在隔离仓库运行静态校验和跨 skill 场景矩阵；通过后再提交。
6. 回滚时同时恢复三个 `SKILL.md`，避免留下混合参数或混合目标策略。

## Open Questions

无。单提案范围、统一 `--target`、选择优先级、旧参数迁移和强制确认边界均已由用户确认。
