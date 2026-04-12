---
name: parall-new-worktree-apply
description: 并行执行多个待实施的 OpenSpec changes。自动发现 pending changes，解析依赖图，无依赖的并行在隔离 worktree 中实施，有依赖的按序执行，完成后串行合并回主干并验证。
argument-hint: "[可选: 无参数则自动发现所有待执行 changes]"
disable-model-invocation: true
---

并行执行多个待实施的 OpenSpec changes。

**Input**: 无参数时自动发现所有待执行 changes。无需手动指定。

---

## Step 0: 前置检查与 Auto-commit

### 0.1 参数处理

无参数。若用户传入了参数，忽略并提示：本 skill 自动发现所有待执行 changes，无需参数。

### 0.2 Git 仓库检查

验证当前目录是 git 仓库：
```bash
git rev-parse --is-inside-work-tree
```

若不是 git 仓库，报错退出：
```
错误: 当前目录不是 git 仓库。请在 git 仓库中运行此命令。
```

### 0.3 确认在主分支

检测主分支名称（按优先级 main → master → trunk）：
```bash
git branch --list main master trunk
```

确认当前在主分支上：
```bash
git branch --show-current
```

若不在主分支，报错并提示切换：
```
错误: 当前不在主分支 (当前: <current-branch>)。
请先切换到主分支 (<main-branch>) 后再执行。
```

### 0.4 Auto-commit

检查工作区状态：
```bash
git status --porcelain
```

若有未提交文件，自动提交：
```bash
git add -A
git commit -m "chore: auto-commit before parallel worktree apply"
```

若无可提交文件（porcelain 输出为空），跳过此步。

---

## Step 1: Discovery — 扫描待执行 Changes

### 1.1 列出所有 change 目录

扫描 `openspec/changes/` 下的所有子目录，排除 `archive/`：
```bash
ls -d openspec/changes/*/ 2>/dev/null | grep -v '/archive/'
```

对每个目录，提取 change 名称（目录名）。

### 1.2 检测未完成任务

对每个 change，读取 `tasks.md`，检查是否存在 `[ ]` 未完成项：
```bash
grep -c '^\- \[ \]' openspec/changes/<name>/tasks.md 2>/dev/null
```

- 返回值 > 0：该 change 含未完成任务，列入待执行列表
- 返回值 = 0 或文件不存在：跳过该 change

### 1.2.1 Artifact 完整性校验

对每个含未完成任务的 change，校验其 OpenSpec artifacts 是否齐全：
```bash
openspec status --change "<name>" --json
```

解析 JSON，检查所有 artifacts 的 `status` 是否为 `"done"`。

同时验证关键文件存在：
```bash
test -f openspec/changes/<name>/proposal.md
test -f openspec/changes/<name>/design.md
test -f openspec/changes/<name>/tasks.md
ls openspec/changes/<name>/specs/*.md 2>/dev/null
```

- 所有 artifacts done 且文件齐全 → 列入待执行列表
- 任一不满足 → 将该 change 标记为 "跳过: artifacts 未完成"，不列入待执行列表，在执行计划中标注

### 1.3 待执行列表为空

若待执行列表为空，输出并退出：
```
## 无可执行的 Changes

所有 changes 的任务均已完成，或没有找到 changes 目录。

运行 /opsx:propose 创建新的 change。
```

---

## Step 2: 依赖解析与图构建

### 2.1 解析依赖声明

对每个待执行 change，检查是否存在 `dependencies.yaml` 文件：

```bash
test -f openspec/changes/<name>/dependencies.yaml
```

```
解析规则:
1. 若 dependencies.yaml 不存在 → 无依赖
2. 若存在 → 读取文件，解析 YAML 的 dependencies 列表
3. 每项的 change-name 为依赖名称
4. dependencies 为空列表 → 无依赖
```

### 2.2 校验依赖引用

验证每个依赖名称在 `openspec/changes/` 目录中存在：
```bash
ls openspec/changes/<dep-name>/ 2>/dev/null
```

若引用了不存在的 change，报错退出：
```
错误: 依赖引用无效
  Change "<change-name>" 声明依赖 "<dep-name>"，但该 change 不存在。
  请检查 dependencies.yaml 文件。
```

### 2.3 循环依赖检测

使用 DFS 算法检测有向图中的环：

```
对每个节点执行 DFS:
  标记为 "visiting"
  对每个邻居 (依赖):
    若邻居为 "visiting" → 发现环，报错退出
    若邻居为 "unvisited" → 递归访问
  标记为 "visited"
```

若检测到循环依赖，报错退出：
```
错误: 检测到循环依赖
  涉及的 changes: <cycle 中所有 change 名称>
  请修改 dependencies.yaml 消除循环。
```

### 2.4 拓扑排序生成 Wave 列表

使用 Kahn 算法（BFS 拓扑排序）生成分层执行计划：

```
算法:
1. 计算每个 change 的入度 (被依赖数)
2. 入度为 0 的 change 放入 Wave 1
3. 移除 Wave 1 的节点，更新剩余节点的入度
4. 新入度为 0 的放入 Wave 2
5. 重复直到所有节点分配完毕
```

同一 Wave 内的 changes 互相无依赖，可并行执行。

### 2.5 展示执行计划

输出执行计划供用户确认：
```
## 执行计划

发现 <N> 个待执行的 Changes，分为 <W> 个 Wave：

Wave 1 (并行: <count>)
  ├─ <change-a>
  └─ <change-b>

Wave 2 (依赖 Wave 1: <dep-list>)
  └─ <change-c>

### 已跳过
  ├─ <change-d> — 跳过: artifacts 未完成 (design, specs)
```

---

## Step 3: 决策 — 执行路径选择

### 3.1 单个 Change（数量 = 1）

若待执行 changes 数量为 1：

1. 直接在主会话中调用 Skill 工具执行 `opsx:apply <change-name>`
2. 等待 apply 完成
3. 执行合并回主干流程（Step 5）
4. 跳转到 Step 6（验证）

### 3.2 多个 Changes（数量 ≥ 2）

进入 Wave 执行循环（Step 4）。

---

## Step 4: Wave 执行循环

对每个 Wave 按顺序执行：

### 4.1 并行 Spawn Agent

为 Wave 内的每个 change spawn 一个 Agent，**在同一消息中并行 spawn** 以实现真正的并行：

每个 Agent 的配置：
- `subagent_type`: "general-purpose"
- `isolation`: "worktree"
- `mode`: "auto"
- `name`: "<change-name>"
- `description`: "apply <change-name>"
- `prompt`:
  ```
  你正在一个隔离的 git worktree 中实施 OpenSpec change "<change-name>"。

  请严格按照以下步骤执行:

  1. 调用 Skill 工具执行 opsx:apply，参数为 "<change-name>"
     这会自动读取 proposal、specs、design、tasks 并逐个实施任务

  2. Post-apply 后处理:
     opsx:apply 完成后，执行以下后处理步骤:

     Step A — Task Backfill:
       a. 读取 openspec/changes/<change-name>/tasks.md，收集所有 "- [ ]" 行
       b. 对每行按四规则检测:
          Rule 1: 反引号路径 → 提取 task 描述中 `path` 的文件路径，test -f <path>
          Rule 2: 目录创建模式 → 匹配 "创建 `xxx/` 目录"，test -d <dir>
          Rule 3: Frontmatter 模式 → 匹配 "编写 frontmatter"，test -f <path> && head -1 <path> | grep -q '^---'
          Rule 4: 实现关键词 → 匹配 "实现 xxx"，grep -rl <keyword> --include="*.md" . 2>/dev/null | head -3
       c. 检测通过的自动改为 "- [x]"
       d. 输出补标记报告

     Step B — Force-add + Commit:
       git add -A
       git add -f openspec/changes/<change-name>/tasks.md
       统计 DONE/TOTAL:
         DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<change-name>/tasks.md)
         TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<change-name>/tasks.md)
       若有变更:
         若 DONE == TOTAL: git commit -m "feat: implement <change-name> (DONE/TOTAL tasks)"
         若 DONE < TOTAL: git commit -m "feat: implement <change-name> (DONE/TOTAL tasks, partial)"
       若无变更: 跳过 commit

  3. 若 apply 过程中遇到问题:
     - 仍然执行步骤 2 的后处理（补标记 + 提交）
     - 在返回中说明失败原因

  完成后返回: 实施状态（成功/失败）、已完成/总任务数、补标记详情、任何错误信息。
  ```

### 4.2 等待 Agent 完成

等待当前 Wave 内所有 Agent 完成。

**重要**: 耐心等待。Agent 可能需要较长时间完成 apply。不要主动检查或中断。

每个 Agent 完成后会自动返回结果。记录每个 Agent 的：
- 状态（成功/失败）
- 分支名称（若 isolation: "worktree" 返回了 branch）
- 错误信息（若有）

### 4.3 记录失败

Agent 失败不阻塞其他 Agent 的等待。失败的 Agent 记录到结果列表中，后续跳过其分支的合并。

---

## Step 5: 串行合并

**每个 Wave 完成后**（所有 Agent 返回后），按目录名字母序逐个合并成功的分支。

### 5.1 合并单个分支

对每个成功的分支，按以下顺序操作：

```
Step A: Rebase 到最新 main
  git rebase main <branch>

Step B: 检查是否有冲突 → 转到 Step 6（冲突解决）

Step C: 切换到 main 并合并
  git checkout main
  git merge <branch>

Step D: 验证合并成功
  git log --oneline -1  # 确认 HEAD 已推进

Step E: 验证 tasks.md 标记状态
  对该 change 检查 main 上的 tasks.md:
  DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
  TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)

  若 DONE < TOTAL:
    执行 post-merge 补标记:
    - 读取 tasks.md，收集 [ ] 项
    - 解析 task 描述提取文件路径
    - 检查产出文件存在性
    - 自动标记 [x]
    - git add -f openspec/changes/<name>/tasks.md
    - git commit -m "fix: backfill task markers for <name> (DONE/TOTAL tasks)"
```

### 5.2 合并顺序

按分支对应 change 的目录名字母序逐个合并。每合并一个分支后，main HEAD 推进，下一个分支的 rebase 基于此新 HEAD。

---

## Step 6: 冲突智能解决

当 `git rebase main <branch>` 产生冲突时执行此步骤。

### 6.1 检测冲突

```bash
git status --porcelain | grep "^UU"
```

若有输出，说明存在未合并的冲突文件。

### 6.2 分析冲突标记

对每个冲突文件：
1. 读取文件内容
2. 解析 `<<<<<<< HEAD`、`=======`、`>>>>>>> <branch>` 标记
3. 提取两方的改动内容

### 6.3 智能合并策略

按以下优先级处理：

**策略 1: 非重叠改动（自动解决）**
```
若两方修改了文件的不同区域（行号不重叠）:
  → 保留双方的改动
  → 生成合并后的文件
```

**策略 2: 语义可合并（智能解决）**
```
若两方修改了同一区域，但语义上可以合并:
  例如: 两方都添加了列表项 → 合并两个列表项
  例如: 一方添加 import，一方修改函数 → 保留 import + 保留函数修改
  → 生成合并后的文件
```

**策略 3: 无法自动解决（放弃并报告）**
```
若两方修改了同一区域且语义冲突:
  → 执行 git rebase --abort
  → 记录冲突详情
  → 跳过该分支，继续处理下一个
```

### 6.4 应用解决方案

冲突解决后：
```bash
git add <resolved-files>
git rebase --continue
```

若 `rebase --continue` 后仍有冲突，重复 6.1–6.4。

---

## Step 7: 验证与最终报告

### 7.1 重新扫描 tasks.md（含文件存在性检测）

全部 Wave 完成后，重新扫描所有之前标记为待执行的 change：

对每个待执行 change：

**Step A: 统计 task 状态**
```bash
DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
```

**Step B: 若有未完成任务，执行文件存在性检测**

对每个仍为 `[ ]` 的 task，解析其描述提取文件路径，检查产出文件是否存在。存在的自动标记 `[x]`。

若补标记后 tasks.md 有变更：
```bash
git add -f openspec/changes/<name>/tasks.md
git commit -m "fix: backfill task markers for <name> (DONE/TOTAL tasks)"
```

**Step C: 最终统计**
- 所有 task 均为 `[x]` → 该 change 验证通过 ✓
- 仍有 `[ ]` → 标注剩余任务数

### 7.2 生成最终报告

```
## Parallel Worktree Apply 报告

**待执行 Changes:** <total>
**执行 Waves:** <waves>
**成功:** <success_count>  **失败:** <fail_count>

### Wave 执行结果

Wave 1:
| Change | Agent 状态 | 合并状态 | 备注 |
|--------|-----------|---------|------|
| <name> | ✓ 成功    | ✓ 已合并 |      |
| <name> | ✓ 成功    | ✗ 冲突  | 冲突文件: <files> |

Wave 2:
...

### 验证结果

| Change | 任务完成 | 状态 |
|--------|---------|------|
| <name> | 7/7     | ✓    |
| <name> | 3/5     | ✗ 剩余 2 个任务 |

### 总结

全部 Changes 已成功实施并验证! ✓
（或: <fail_count> 个 Changes 存在问题，请查看上方详情。）

### 下一步

> 全部成功: 运行 `/check-changes-completed` 验证完整性，然后逐个 `/opsx:archive <name>` 归档。
> 部分失败: 对失败的 change 运行 `/new-worktree-apply <name>` 单独重试，成功后 `/merge-worktree-return <name>` 合并。
```

### 7.3 失败项详情

对每个失败的 change，输出详细信息：
```
### 失败详情: <change-name>

- 失败阶段: [Agent 执行 / 合并冲突 / 验证]
- 原因: <详细描述>
- 建议: <恢复建议>
```

---

## 错误处理

### 通用错误格式

```
错误: <简要描述>

**上下文**: <正在执行的步骤和参数>
**原因**: <错误的具体原因>
**建议**:
  1. <恢复建议 1>
  2. <恢复建议 2>
```

### 各步骤错误处理

| 步骤 | 错误 | 处理 |
|------|------|------|
| 0.2 | 非 git 仓库 | 直接退出 |
| 0.3 | 不在主分支 | 直接退出，提示切换 |
| 2.2 | 依赖引用不存在 | 直接退出，提示检查 |
| 2.3 | 循环依赖 | 直接退出，列出环中 changes |
| 4.2 | Agent 执行失败 | 记录失败，继续其他 Agent |
| 5.1 | Rebase 冲突 | 尝试智能解决，失败则跳过该分支 |
| 7.1 | 验证未通过 | 在报告中标注，不阻塞 |

---

## Guardrails

- 始终确保 worktree 代码基于最新 HEAD（Agent isolation: "worktree" 自动保证）
- Agent spawn 必须在同一消息中并行，不要串行 spawn 同一 Wave 的 Agent
- 合并必须串行，每个分支合并后再处理下一个
- 失败的 Agent 或冲突的分支不阻塞其他 Agent/分支
- 最终验证必须重新扫描 tasks.md，不信任中间状态
- 若待执行 changes 为 0，直接退出不做任何操作
- 若待执行 changes 为 1，走简化路径（直接 apply），不 spawn Agent
