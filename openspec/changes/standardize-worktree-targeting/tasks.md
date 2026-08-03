## 1. 共享契约与影响预检

- [x] 1.1 对 `new-worktree-apply/SKILL.md`、`merge-worktree-return/SKILL.md` 和 `parall-new-worktree-apply/SKILL.md` 分别运行 GitNexus upstream impact，向用户报告直接影响、相关流程和风险后再编辑
- [x] 1.2 在三个 skill 的 description、argument-hint、Input 和示例中统一使用可选 `--target <target-branch>` 与 `TARGET_BRANCH` 术语
- [x] 1.3 定义三个命令各自的位置参数约束和统一 `--target` 解析错误；让 `new-worktree-apply --branch` 在零写操作下返回可复制的迁移命令
- [x] 1.4 在三个 skill 中统一目标选择顺序为“显式 `--target` → 主工作树当前分支 → `origin/HEAD` 本地同名分支 → `main`/`master`/`trunk`”，并记录选择依据
- [x] 1.5 使用 `git worktree list --porcelain` 和精确本地 ref 统一解析主工作树、调用目录、目标工作树及来源 worktree，拒绝不可用目标和必要的 detached HEAD

## 2. 共享确认与复检门槛

- [x] 2.1 为三个 skill 构建只读预检摘要，显示命令范围、目标及选择依据、工作树路径、待提交状态、计划写操作和风险警告
- [x] 2.2 使用当前平台可用的交互机制请求无默认值、无超时自动同意的明确确认；拒绝、取消或模糊回答时不修改 Git 且不调用 apply
- [x] 2.3 将所有 `git add`、commit、checkout/switch、worktree add/remove、rebase、merge 和 OpenSpec apply 移到确认之后
- [x] 2.4 在首次写操作前重新验证目标 ref/HEAD、worktree 映射、状态、checkout 需求和警告；实质事实变化时使旧确认失效并重新展示

## 3. `new-worktree-apply` 目标基线修复

- [x] 3.1 将 `MAIN_BRANCH`/`MAIN_HEAD` 改为 `TARGET_BRANCH`/`TARGET_HEAD`，并通过 `git rev-parse "$TARGET_BRANCH"` 记录真实目标 HEAD
- [x] 3.2 在确认后按摘要处理目标工作树待提交改动，刷新 `TARGET_HEAD`，并确保所有后续创建步骤使用该快照
- [x] 3.3 在 Codex 路径为 `git worktree add` 增加显式 `<TARGET_BRANCH>` start-point；在 Claude Code 路径确保 `EnterWorktree` 从目标 checkout 上下文创建，否则安全停止
- [x] 3.4 创建后验证 `WORKTREE_HEAD == TARGET_HEAD`，不再用 `git merge <target>` 掩盖错误起点；失败时停止 apply 并给出恢复建议
- [x] 3.5 保留 artifact 校验、apply、任务回填和提交逻辑，同时确保它们只在正确的 proposal worktree 中运行

## 4. `merge-worktree-return` 目标回收流程

- [x] 4.1 解析 `SOURCE_BRANCH`、`SOURCE_WORKTREE_DIR`、`TARGET_WORKTREE_DIR`，验证来源与目标不同且目标工作树干净
- [x] 4.2 将来源自动提交、rebase、冲突处理、目标 checkout 和 merge 全部绑定到已确认 `TARGET_BRANCH`
- [x] 4.3 将 OpenSpec 未完成任务清单并入统一风险确认，避免重复确认并保持明确授权
- [x] 4.4 使用 `git log <target>..<source>` 验证目标包含全部来源提交；任何失败都阻止 `ExitWorktree` 或 `git worktree remove`
- [x] 4.5 更新成功/错误输出、退出前清单和跨平台清理流程，统一显示 `SOURCE_BRANCH → TARGET_BRANCH`

## 5. `parall-new-worktree-apply` 目标批量流程

- [x] 5.1 将参数处理从“忽略所有参数”改为仅接受可选 `--target`，并把 Discovery、artifact 检查和依赖图构建保留在只读预检阶段
- [x] 5.2 把现有 Auto-commit 移到执行计划确认和复检之后，提交后刷新批量创建所用目标 HEAD
- [x] 5.3 让每个 agent/手动 child worktree 从同一个已确认目标快照创建，并在 agent 提示中传递目标和 CWD/HEAD 验证要求
- [x] 5.4 将每个 Batch 的 rebase、checkout、merge、tasks 回填和验证从 `MAIN_BRANCH` 改为 `TARGET_BRANCH`
- [x] 5.5 修复单 change 路径，使其也在隔离 worktree 中 apply、提交并通过相同目标合并流程返回
- [x] 5.6 更新冲突恢复、失败保留、最终报告和 Guardrails，显示目标选择依据及每个分支的目标包含验证

## 6. 跨 Skill 验证

- [x] 6.1 检查三个 `SKILL.md` 的 frontmatter、Markdown、参数提示、允许工具与实际流程一致，且不存在残留的错误 `MAIN_BRANCH`/`MAIN_DIR` 语义
- [x] 6.2 在隔离临时仓库对三个 skill 验证显式目标、主工作树分支、`origin/HEAD`、传统分支回退和无可用目标场景
- [x] 6.3 验证旧 `--branch`、缺失/重复目标、目标不存在、detached HEAD、取消/模糊确认及确认后状态变化均不会在授权前产生写操作
- [x] 6.4 验证 `new-worktree-apply` 在当前分支不同于目标时仍精确从目标 HEAD 创建，且错误基线会阻止 apply
- [x] 6.5 验证 `merge-worktree-return` 对非 `main` 目标的 rebase、merge、包含检查和清理，以及目标脏状态和不完整 proposal 的失败路径
- [x] 6.6 验证 `parall-new-worktree-apply` 的单 change、多个 wave/batch、取消计划、Auto-commit 时机、串行目标合并和失败 worktree 保留
- [x] 6.7 运行适用的 skill/OpenSpec 校验，并在提交前执行 `gitnexus_detect_changes()`，确认只影响三个预期 skill 和 `worktree-targeting` 流程
