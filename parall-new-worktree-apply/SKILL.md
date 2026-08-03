---
name: parall-new-worktree-apply
description: 并行执行多个待实施的 OpenSpec changes。自动发现 pending changes，解析依赖图，无依赖的并行在隔离 worktree 中实施（均从同一个已确认目标分支创建），有依赖的按序执行，完成后串行合并回目标分支并验证。所有 Git 写操作只在显式预检确认之后执行。
argument-hint: "[--target <target-branch>]"
disable-model-invocation: true
---

并行执行多个待实施的 OpenSpec changes。

**Input**: 无位置参数。可选 `--target <target-branch>` 指定所有 change 的目标分支。无参数时自动发现所有待执行 changes。

示例:
- `/parall-new-worktree-apply`
- `/parall-new-worktree-apply --target develop`

**BREAKING**: 不再忽略所有参数。仅接受可选 `--target`；任何其他参数（含旧的位置参数）→ 参数错误，零写操作。

**Invariant（确认前只读）**: Step 0–4 为只读，不产生任何 Git 写操作，不 spawn 实施 agent，不调用 apply。`git add`/`commit`/`checkout`/`switch`/`rebase`/`merge`、`git worktree add`/remove、`EnterWorktree`/`ExitWorktree` 及 apply 仅在 Step 5 起执行——即确认（Step 3）与复检（Step 4）之后。

---

## Step 0: 前置检查与目标选择（只读）

### 0.1 参数处理

仅接受可选 `--target <target-branch>`（至多一次）。

- 出现任何位置参数、未知选项、`--target` 缺值、重复 `--target` → 报参数错误，零写操作：
  ```
  错误: 参数无效
    parall-new-worktree-apply 只接受可选 --target <target-branch>。
    示例: /parall-new-worktree-apply --target develop
    未执行任何 Git 写操作。
  ```

### 0.2 Git 仓库检查

```bash
git rev-parse --is-inside-work-tree
```

若不是 git 仓库，报错退出：`错误: 当前目录不是 git 仓库。`

### 0.3 目标分支选择

按统一优先级选择 `TARGET_BRANCH`，并记录 `TARGET_SOURCE`（用于确认摘要与最终报告）：

1. **显式 `--target`** — 必须存在于本地 `refs/heads/`：
   ```bash
   git rev-parse --verify --quiet refs/heads/<target-branch>
   ```
   不存在 → `错误: 目标分支 '<name>' 本地不存在。` 不 fetch、不创建、不回退，零写操作。`TARGET_SOURCE="explicit --target"`。
2. **主工作树当前分支** — 从 `git worktree list --porcelain`（0.4）读取；若是有效本地 ref → `TARGET_SOURCE="primary worktree current branch"`。
3. **`origin/HEAD` 本地同名分支**：
   ```bash
   git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's#^origin/##'
   ```
   结果存在于 `refs/heads/` → `TARGET_SOURCE="origin/HEAD local branch"`。
4. **传统回退** — `main`、`master`、`trunk` 中首个存在的本地分支 → `TARGET_SOURCE="conventional fallback"`。

无可用候选 → `错误: 无法选择目标分支。请使用 --target <branch> 指定。` 零写操作。

后续所有 Step 使用 `<TARGET_BRANCH>` 替代硬编码分支名。

### 0.4 Worktree 拓扑解析

```bash
git worktree list --porcelain
git rev-parse --show-toplevel
git -C <PRIMARY_WORKTREE_DIR> branch --show-current
```

记录：
- `PRIMARY_WORKTREE_DIR`（主工作树）
- `INVOCATION_WORKTREE_DIR`（调用目录）
- `TARGET_WORKTREE_DIR`（`TARGET_BRANCH` 已检出的 worktree；可能等于主工作树）

**拓扑规则**：
- 若 `TARGET_BRANCH` 已在某 worktree 检出 → 记为 `TARGET_WORKTREE_DIR`，不计划重复 checkout。
- 若未检出 → 记录"需在确认后将干净主工作树 checkout 到 `TARGET_BRANCH`"，并将计划中的 `TARGET_WORKTREE_DIR=<PRIMARY_WORKTREE_DIR>`；若主工作树不干净或不能安全切换 → 报错，确认前停止。
- 若主工作树处于 detached HEAD 且未显式指定 `--target` → `错误: 主工作树为 detached HEAD。请使用 --target <branch>。` 零写操作。
- 状态快照、确认后复检和 Auto-commit MUST 始终针对同一个 `TARGET_WORKTREE_DIR`；不能因为命令从主工作树或其他 worktree 调用，就改查 `PRIMARY_WORKTREE_DIR` 或调用 CWD。
- 记录控制器是否需要从 `INVOCATION_WORKTREE_DIR` 持久切换到 `TARGET_WORKTREE_DIR`。若平台无法让后续 Agent spawn 与主控命令保持该执行上下文，则在只读预检阶段停止并要求用户从目标工作树重新运行；单条 `git -C` 不算切换控制器上下文。

解析出实际或计划中的 `TARGET_WORKTREE_DIR` 后，再读取目标状态：
```bash
git -C <TARGET_WORKTREE_DIR> status --porcelain
```

---

## Step 1: Discovery — 扫描待执行 Changes（只读）

### 1.1 列出所有 change 目录

```bash
ls -d openspec/changes/*/ 2>/dev/null | grep -v '/archive/'
```

对每个目录，提取 change 名称（目录名）。

### 1.2 检测未完成任务

```bash
grep -c '^\- \[ \]' openspec/changes/<name>/tasks.md 2>/dev/null
```

- 返回值 > 0：列入待执行列表
- 返回值 = 0 或文件不存在：跳过

### 1.2.1 Artifact 完整性校验

```bash
openspec status --change "<name>" --json
test -f openspec/changes/<name>/proposal.md
test -f openspec/changes/<name>/design.md
test -f openspec/changes/<name>/tasks.md
ls openspec/changes/<name>/specs/*.md 2>/dev/null
```

所有 artifacts done 且文件齐全 → 列入待执行列表；否则标记"跳过: artifacts 未完成"，不列入。

### 1.3 待执行列表为空

输出并退出（零写操作）：
```
## 无可执行的 Changes

所有 changes 的任务均已完成，或没有找到 changes 目录。
运行 /opsx:propose 创建新的 change。
```

---

## Step 2: 依赖解析与图构建（只读）

### 2.1 解析依赖声明

```bash
test -f openspec/changes/<name>/dependencies.yaml
```

解析规则: 不存在或空列表 → 无依赖；存在 → 读取 dependencies 列表。

### 2.2 校验依赖引用

```bash
ls openspec/changes/<dep-name>/ 2>/dev/null
```

引用不存在的 change → 报错退出：`错误: 依赖引用无效`。

### 2.3 循环依赖检测

DFS 检测有向图中的环；发现环 → 报错退出，列出环中 changes。

### 2.4 拓扑排序生成 Wave 列表

Kahn 算法（BFS 拓扑排序）生成分层执行计划。同一 Wave 内的 changes 互相无依赖，可并行执行。

### 2.5 展示执行计划

输出执行计划（标注每 Wave 的 Batch 划分）：
```
## 执行计划（待确认）

目标分支: <TARGET_BRANCH>（选择依据: <TARGET_SOURCE>）
目标工作树: <TARGET_WORKTREE_DIR 或 "确认后 checkout 到主工作树">

发现 <N> 个待执行的 Changes，分为 <W> 个 Wave，每 Wave 最多 3 个并行：

Wave 1:
  Batch 1 (并行: 3)
    ├─ <change-a>
    ├─ <change-b>
    └─ <change-c>
  Batch 2 (并行: 2, Batch 1 合并后执行)
    ├─ <change-d>
    └─ <change-e>

Wave 2 (依赖 Wave 1):
  Batch 1 (并行: 1)
    └─ <change-f>

### 已跳过
  ├─ <change-g> — 跳过: artifacts 未完成

### 将执行的写操作（确认后）
  - Auto-commit 目标工作树待提交改动（若有）并刷新目标 HEAD
  - 每个 change 从 <TARGET_BRANCH> 创建隔离 worktree、apply、提交
  - 每个 Batch 后将成功分支串行 rebase + merge 进 <TARGET_BRANCH>
  - 失败/冲突分支保留 worktree 待人工处理
```

---

## Step 3: 只读预检摘要与强制确认（只读；无写操作）

在 Step 2.5 计划基础上，使用 **AskUserQuestion 工具** 请求**明确**确认，**无默认值、无超时自动同意**。

确认摘要 MUST 包含：
- 命令范围: `parall-new-worktree-apply`
- 目标分支、`TARGET_SOURCE`、`TARGET_HEAD`、`TARGET_WORKTREE_DIR`（或计划中的 checkout）
- Wave/Batch 结构与每 Batch 串行合并说明
- 目标工作树待提交改动清单（若有），或"无待提交改动"
- 计划写操作: Auto-commit、每个 change 的隔离 worktree 创建/apply/提交、每 Batch 串行 rebase+merge 到 `TARGET_BRANCH`、失败保留策略
- 风险警告: 主工作树是否需要 checkout 目标；控制器是否需要持久切换到 `TARGET_WORKTREE_DIR`；单 change 也将走隔离 worktree；冲突分支不阻塞其他分支

**确认处理**：
- **确认** → 进入 Step 4（复检）。
- **拒绝/取消** → 不创建任何 worktree、不 spawn 任何 agent、不调用 apply、不 commit，零写操作。
- **缺失/模糊** → 暂停等待明确输入，零写操作。
- **无交互工具** → 在响应中输出问题，结束当前执行，等待下一条消息。零写操作。

---

## Step 4: 确认后快照复检（只读，首次写操作前）

重新验证: 参数、`TARGET_BRANCH` ref 与 `TARGET_HEAD`、worktree 映射、`git -C <TARGET_WORKTREE_DIR> status --porcelain` 的目标状态、所需 checkout、控制器上下文切换能力、展示过的风险警告。

**任一实质事实变化** → 使确认失效，展示更新摘要并重新请求确认（回到 Step 3）。零写操作直到重新确认。

**全部一致** → 进入 Step 5。

---

## Step 5: 执行写操作（Auto-commit + Wave/Batch）

### 5.1 Auto-commit（确认后）

**仅此时**处理目标工作树待提交改动（之前在 Step 0.4 记录）：

若主工作树需 checkout 到 `TARGET_BRANCH`（目标未检出且主工作树已确认干净）：
```bash
git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>
```
checkout 成功后设置 `TARGET_WORKTREE_DIR=<PRIMARY_WORKTREE_DIR>`，并验证该目录位于 `TARGET_BRANCH`。

若 `TARGET_WORKTREE_DIR` 有待提交改动（按已确认计划）：
```bash
git -C <TARGET_WORKTREE_DIR> add -A
git -C <TARGET_WORKTREE_DIR> commit -m "chore: auto-commit before parallel worktree apply"
```

**刷新批量创建所用的目标 HEAD**：
```bash
TARGET_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse refs/heads/<TARGET_BRANCH>)
```

将控制器的**持久执行上下文**切换到已确认目标工作树；单条 `git -C` 不能替代此步骤：
```bash
cd <TARGET_WORKTREE_DIR>
test "$(pwd -P)" = "<TARGET_WORKTREE_DIR>"
test "$(git rev-parse --show-toplevel)" = "<TARGET_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<TARGET_BRANCH>"
test "$(git rev-parse HEAD)" = "<TARGET_HEAD>"
```

只有四项检查都通过，才可 spawn 第一个 Agent。若后续 Agent 工具调用不能继承该目标上下文，停止且不 spawn；不得从 `INVOCATION_WORKTREE_DIR` 的 HEAD 创建隔离 worktree。

若无待提交改动 → 跳过 commit，仍记录 `TARGET_HEAD`。

### 5.2 单 Change 也走隔离 worktree（无简化路径）

**即使只发现 1 个 change**，也必须走下方 Wave/Batch 流程（隔离 worktree 创建、apply、提交、串行合并），**禁止**直接在目标工作树调用 apply。1 个 change 等价于 1 Wave / 1 Batch / 1 agent。

### 5.3 Wave 执行循环

对每个 Wave 按顺序执行：

在当前 Wave 开始时，从目标工作树读取合并完上一 Wave 后的最新 HEAD：
```bash
TARGET_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse refs/heads/<TARGET_BRANCH>)
WAVE_TARGET_HEAD=$TARGET_HEAD
```

`WAVE_TARGET_HEAD` 用于记录该 Wave 的进入基线；禁止复用首次确认时的旧 HEAD 作为后续 Wave 基线。

#### 5.3.1 批次划分

当前 Wave 的 changes 按目录名字母序，每批最多 3 个切分为多个 Batch（满足 `batch-concurrency-control` 规格的并发上限 3）。

#### 5.3.2 Batch 执行循环

对当前 Wave 的每个 Batch 按顺序执行：

每个 Batch spawn 前再次读取当前目标 HEAD，使前一 Batch 已合并的结果也可见；同一 Batch 的所有 Agent 共享该快照：
```bash
BATCH_TARGET_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse refs/heads/<TARGET_BRANCH>)
test "$(pwd -P)" = "<TARGET_WORKTREE_DIR>"
test "$(git branch --show-current)" = "<TARGET_BRANCH>"
test "$(git rev-parse HEAD)" = "<BATCH_TARGET_HEAD>"
```

任一控制器上下文检查失败 → 本 Batch 不 spawn Agent，报告目标上下文漂移并停止；不能让隔离机制从调用 worktree 的 HEAD 创建。

##### 5.3.2.1 并行 Spawn Agent（同一消息内并行）

为 Batch 内每个 change spawn 一个 Agent，**在同一消息中并行 spawn**。每个 Agent **从当前 Batch 的同一个 `BATCH_TARGET_HEAD` 创建**。

Agent 配置：
- `subagent_type`: "general-purpose"
- `isolation`: "worktree"
- `mode`: "auto"
- `name`: "<change-name>"
- `description`: "apply <change-name>"
- `prompt`（必须在提示中传递目标与 CWD/HEAD 验证要求）:
  ```
  你正在一个隔离的 git worktree 中实施 OpenSpec change "<change-name>"。
  目标分支（基线）: <TARGET_BRANCH>
  当前 Wave 进入基线: <WAVE_TARGET_HEAD>
  当前 Batch 预期基线 HEAD: <BATCH_TARGET_HEAD>

  **平台适配（必须遵守）**:
  判断 EnterWorktree 工具是否可用：
  - 可用（Claude Code，isolation: "worktree" 已生效）: worktree 已从 <TARGET_BRANCH> HEAD 创建并切换 CWD，直接开始。
  - 不可用（Codex 等，isolation 未生效）: 手动创建，**必须使用显式 start-point**:
    git worktree add .claude/worktrees/<change-name> -b <change-name> <BATCH_TARGET_HEAD>
    cd .claude/worktrees/<change-name>
    必须在后续所有操作前显式 cd 到该 worktree。

  **基线验证（必须执行，不可跳过）**:
    WORKTREE_HEAD=$(git rev-parse HEAD)
    若 WORKTREE_HEAD != <BATCH_TARGET_HEAD> → 停止，报告基线错误，不进入 apply。

  **CWD 验证（必须执行）**:
    pwd; git branch --show-current
    确认目录包含 "<change-name>" 且分支正确，否则停止并报告。

  请严格按以下步骤执行:
  1. Skill 工具执行 opsx:apply，参数 "<change-name>"（读取 proposal/specs/design/tasks 逐个实施）
  2. Post-apply 后处理:
     Step A — Task Backfill: 读取 tasks.md 的 "- [ ]" 行，按四规则（反引号路径 test -f / 目录创建 test -d / frontmatter / 实现关键词）检测，通过则改 "- [x]"，输出报告。
     Step B — CWD 复验: pwd; git branch --show-current，不符则先 cd 回 worktree。
     Step C — Force-add + Commit:
       git add -A
       git add -f openspec/changes/<change-name>/tasks.md
       DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<change-name>/tasks.md)
       TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<change-name>/tasks.md)
       有变更时: DONE==TOTAL → "feat: implement <change-name> (DONE/TOTAL tasks)"; 否则 partial。
       无变更: 跳过 commit。
  3. apply 遇到问题: 仍执行步骤 2 后处理，并在返回中说明失败原因。

  返回: 实施状态、DONE/TOTAL、补标记详情、错误信息。
  ```

##### 5.3.2.2 等待 Agent 完成

耐心等待当前 Batch 内所有 Agent 完成。记录每个 Agent 的状态、分支名、错误信息。

##### 5.3.2.3 记录失败

失败 Agent 记录到结果列表，后续跳过其分支合并。失败不阻塞同 Batch 其他 Agent 的等待。

##### 5.3.2.4 合并当前 Batch

当前 Batch 所有 Agent 完成后，**立即执行 Step 6 合并流程**，将成功分支逐个合并进 `TARGET_BRANCH`。

合并后 `TARGET_BRANCH` HEAD 推进；下一个 Batch 的 worktree 虽基于更早 HEAD 创建，但 rebase 时同步到最新 `TARGET_BRANCH`，合并基线准确。

### 5.4 Wave 完成

当前 Wave 所有 Batch 执行并合并完毕后，立即刷新供下一 Wave 使用的目标基线：
```bash
TARGET_HEAD=$(git -C <TARGET_WORKTREE_DIR> rev-parse refs/heads/<TARGET_BRANCH>)
```

下一 Wave 必须从此最新 `TARGET_HEAD` 开始，并在其首个 Batch 记录新的 `BATCH_TARGET_HEAD`；依赖 change 因而能在实施期间看到上一 Wave 的代码，而不是只在事后 rebase。

---

## Step 6: 串行合并（`TARGET_BRANCH`）

由 Step 5.3.2.4 调用。**每个 Batch 完成后**，按目录名字母序逐个合并成功分支。

### 6.1 合并前控制器验证

**对每个成功分支，合并前验证主控状态**：
```bash
pwd -P
git rev-parse --show-toplevel
git branch --show-current
```
- `pwd -P` 和 `git rev-parse --show-toplevel` 都必须是 `TARGET_WORKTREE_DIR`（不包含 worktree 子目录）
- `git branch --show-current` 必须等于 `<TARGET_BRANCH>`

**CWD 验证失败** → 报告并**跳过该分支合并**：
```
错误: 主控 CWD 验证失败
  当前目录: <pwd>
  期望目标工作树: <TARGET_WORKTREE_DIR>
  当前分支: <branch>
  期望分支: <TARGET_BRANCH>
  合并已中止。
```

**分支验证失败** → 尝试恢复：
```bash
git checkout <TARGET_BRANCH>
```
恢复后仍失败 → 报告并**跳过该分支合并**。

### 6.2 合并单个分支（绑定 `TARGET_BRANCH`）

```
Step A: Rebase 到最新 <TARGET_BRANCH>
  git rebase <TARGET_BRANCH> <branch>

Step B: 冲突 → 转 Step 7（冲突解决）

Step C: 切换到 <TARGET_BRANCH> 并合并
  git checkout <TARGET_BRANCH>
  git merge <branch>

Step D: 验证目标包含全部来源提交
  git log <TARGET_BRANCH>..<branch>
  输出必须为空。

  不为空 → 合并验证失败:
    警告: 合并验证失败 — 分支 <branch> 仍有未合并提交
    该分支标记为未合并，保留 worktree/恢复状态，按失败策略处理，跳过该分支。

Step E: 验证合并后主控仍在 <TARGET_BRANCH>
  git branch --show-current
  不符则 git checkout <TARGET_BRANCH>，重新验证；仍失败则报告并停止串行合并。

Step F: 验证/回填 tasks.md 标记状态（在 <TARGET_BRANCH> 上）
  DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
  TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
  DONE < TOTAL → post-merge 补标记 + git add -f + commit "fix: backfill task markers for <name> (DONE/TOTAL tasks)"
```

### 6.3 合并顺序

按分支对应 change 的目录名字母序逐个合并。每合并一个，`<TARGET_BRANCH>` HEAD 推进，下一个分支 rebase 基于此新 HEAD。

---

## Step 7: 冲突智能解决

当 `git rebase <TARGET_BRANCH> <branch>` 产生冲突时执行。

### 7.1 检测冲突
```bash
git status --porcelain | grep "^UU"
```

### 7.2 分析冲突标记
对每个冲突文件：读取内容，解析 `<<<<<<< HEAD`、`=======`、`>>>>>>> <branch>` 标记，提取两方改动。

### 7.3 智能合并策略

**策略 1: 非重叠改动（自动解决）** — 两方修改不同区域（行号不重叠）→ 保留双方改动。

**策略 2: 语义可合并（智能解决）** — 两方修改同一区域但语义可合并（如两方都添加列表项）→ 合并。

**策略 3: 无法自动解决（放弃并报告）** — 同区域且语义冲突 → `git rebase --abort`，记录冲突详情，跳过该分支。

### 7.4 应用解决方案
```bash
git add <resolved-files>
git rebase --continue
```
若仍有冲突，重复 7.1–7.4。

---

## Step 8: 验证与最终报告

### 8.1 重新扫描 tasks.md（含文件存在性检测）

全部 Wave 完成后，重新扫描所有待执行 change。对每个:
```bash
DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
```
仍有 `[ ]` 的执行文件存在性检测，存在的自动标记 `[x]`，有变更则 `git add -f` + commit。

### 8.2 生成最终报告

```
## Parallel Worktree Apply 报告

**目标分支:** <TARGET_BRANCH>（选择依据: <TARGET_SOURCE>）
**待执行 Changes:** <total>
**执行 Waves:** <waves>
**成功:** <success_count>  **失败:** <fail_count>

### Wave 执行结果

Wave 1:
| Change | Agent 状态 | 合并状态 | CWD 验证 | 目标包含验证 | 备注 |
|--------|-----------|---------|---------|-------------|------|
| <name> | ✓ 成功    | ✓ 已合并 | ✓       | ✓           |      |
| <name> | ✓ 成功    | ✗ 跳过  | ✗ 失败  | —           | CWD 验证失败: <详情> |
| <name> | ✓ 成功    | ✗ 未验证| —       | ✗ 失败      | 目标仍有 <n> 个未合并提交 |
| <name> | ✗ 失败    | — 跳过  | —       | —           | Agent 执行失败: <原因> |
| <name> | ✓ 成功    | ✗ 冲突  | —       | —           | 冲突文件: <files> |

说明:
- "✗ 跳过 (CWD 验证失败)": 目标工作树或分支异常，合并未执行
- "✗ 未验证 (目标包含失败)": merge 已执行但 git log <TARGET_BRANCH>..<branch> 非空
- "— 跳过 (Agent 失败)": Agent 失败，分支不可合并
- "✗ 冲突": rebase 冲突且无法自动解决

### 验证结果

| Change | 任务完成 | 状态 |
|--------|---------|------|
| <name> | 7/7     | ✓    |
| <name> | 3/5     | ✗ 剩余 2 个任务 |

### 总结

全部 Changes 已成功实施并合并进 <TARGET_BRANCH>! ✓
（或: <fail_count> 个 Changes 存在问题，请查看上方详情。）

### 下一步

> 全部成功: 运行 `/check-changes-completed` 验证完整性，然后逐个 `/opsx:archive <name>` 归档。
> 部分失败: 对失败 change 运行 `/new-worktree-apply <name> --target <TARGET_BRANCH>` 重试，成功后 `/merge-worktree-return <name> --target <TARGET_BRANCH>` 合并。
```

### 8.3 失败项详情

对每个失败 change 输出: 失败阶段、原因、建议。

---

## 错误处理

### 通用错误格式
```
错误: <简要描述>
**上下文**: <步骤与参数>
**原因**: <具体原因>
**建议**:
  1. <恢复建议 1>
  2. <恢复建议 2>
```

### 各步骤错误处理

| 步骤 | 错误 | 处理 |
|------|------|------|
| 0.1 | 参数无效（非 --target） | 直接退出，零写操作 |
| 0.2 | 非 git 仓库 | 直接退出 |
| 0.3 | 目标无法选择/显式目标不存在 | 直接退出，零写操作，Discovery 前 |
| 2.2 | 依赖引用不存在 | 直接退出 |
| 2.3 | 循环依赖 | 直接退出，列出环 |
| 3 | 用户拒绝/取消 | 零写操作退出 |
| 5.3.2.1 | Agent 执行失败 | 记录失败，继续其他 |
| 6.1 | CWD/分支验证失败 | 跳过该分支 |
| 6.2 | Rebase 冲突 / 目标包含失败 | 智能解决，失败则跳过 |

---

## Guardrails

- Step 0–4 为只读：确认前不产生任何 Git 写操作、不 spawn 实施 agent、不调用 apply。
- 目标状态读取、复检和 Auto-commit 始终绑定同一个 `TARGET_WORKTREE_DIR`；Auto-commit 只在确认与复检之后执行。
- Agent spawn 前必须将控制器持久切换到 `TARGET_WORKTREE_DIR`；`git -C` 只约束单条命令，不能代替控制器 CWD 切换。
- 同一 Batch 的 child worktree 基于同一个最新 `BATCH_TARGET_HEAD`；每个 Batch spawn 前刷新，且每个 Wave 合并完成后刷新下一 Wave 的 `TARGET_HEAD`，创建后验证基线。
- 每 Wave 内并行 Agent 上限为 3，超出按字母序分 Batch 串行执行（满足 `batch-concurrency-control` 规格并发上限 3）。
- 同一 Batch 内 Agent spawn 必须在同一消息中并行。
- 合并必须串行绑定到 `TARGET_BRANCH`，每个分支合并后再处理下一个；每个 Batch 完成后立即合并。
- 失败的 Agent 或冲突分支不阻塞其他 Agent/分支；失败 worktree 保留待人工处理。
- 单个 change 也必须走隔离 worktree（创建/apply/提交/合并），禁止直接在目标工作树调用 apply。
- 最终验证必须重新扫描 tasks.md，不信任中间状态；报告显示目标选择依据与每个分支的目标包含验证。
- 待执行 changes 为 0 → 直接退出，零写操作。
- 确认无默认值、无超时自动同意；缺失/模糊回答保持 Git 不变。
