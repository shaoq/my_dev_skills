---
name: parall-new-proposal
description: 并行提案拆分 skill。根据用户综合需求描述，按功能切片维度拆解为多个带依赖声明的 OpenSpec 提案，通过三问判定控制颗粒度，复用 /opsx:propose 创建 artifacts，后注入 ## Dependencies 段，使得后续 /parall-new-worktree-apply 可最大化并行执行。
argument-hint: "<需求描述> (如: 给项目添加完整的认证系统)"
disable-model-invocation: true
---

并行提案拆分 — 将综合需求拆解为多个带依赖声明的 OpenSpec 提案。

**Input**: 用户提供需求描述文本。若未提供，将询问。

---

## Step 0: 前置检查与输入处理

### 0.1 参数处理

提取用户传入的需求描述文本。

若无参数或参数为空：
1. 使用 **AskUserQuestion** 工具（开放式，无预设选项）询问：
   > "请描述你想要构建的综合需求。例如：'给项目添加完整的认证系统'、'重构数据层并迁移到 PostgreSQL'"
2. 从用户描述中理解意图
3. **不要**在没有理解需求的情况下继续推进

### 0.2 输入验证

确认需求描述满足以下条件：
- 描述长度 > 10 个字符（避免过于简短的输入）
- 描述包含可识别的功能概念（非无意义文本）

若不满足，提示用户提供更详细的需求描述。

---

## Step 1: 需求分析

### 1.1 理解需求

仔细分析用户的需求描述，识别：
- 核心功能目标
- 涉及的技术领域
- 可能的子功能边界

### 1.2 扫描现有代码结构

使用 Glob/Grep/Read 工具快速扫描项目结构：
- 目录布局（`ls` 或 Glob `**/`）
- 现有相关模块（Grep 关键词）
- 配置文件（依赖、框架）

目的：理解现有代码边界，确保拆解方案与项目实际结构匹配。

---

## Step 2: 功能切片拆解

### 2.1 按功能切片维度拆分

将需求按**可独立交付的功能单元**（功能切片）拆分为多个候选子方案。每个候选子方案生成：
- **名称**: kebab-case（如 `auth-user-model`）
- **描述**: 一段清晰说明该子方案做什么的文本

### 2.2 三问判定框架

对每个候选子方案执行三问判定：

```
Q1: 能否独立测试？
    → 能跑测试套件并看到绿色，而不是"它改了一个文件"

Q2: 能否独立理解？
    → 看 proposal.md 就知道它在做什么，而不是"某个大功能的内部步骤"

Q3: 产出是否有独立价值？
    → 即使其他提案还没做完，这个提案完成后的产出对项目有增量价值
```

判定规则：
- **三问全 YES** → 保留为独立提案
- **任一 NO** → 合并到最相关的候选子方案中，不作为独立提案

合并时记录合并原因，在最终展示中说明。

### 2.3 颗粒度检测

对通过三问判定的子方案列表执行数量检测：

- **子方案数 ≤ 1**: 输出提示：
  > "需求规模较小（仅产生 N 个子方案），建议直接使用 `/opsx:propose` 逐个创建。"
  使用 AskUserQuestion 询问用户是否仍要继续使用本 skill。

- **子方案数 > 6**: 输出警告：
  > "⚠️ 拆分粒度可能过细（N 个子方案），建议检查是否可合并部分子方案。超过 6 个会导致 Wave 和 Batch 数增多，实际耗时反而更长。"

- **2-6 个**: 正常范围，继续执行。

---

## Step 3: 依赖图构建

### 3.1 分析子方案间依赖

对每个子方案，识别它依赖哪些其他子方案才能正常工作。

依赖关系来源：
- 数据依赖（A 需要 B 定义的数据模型）
- 接口依赖（A 调用 B 提供的 API）
- 顺序依赖（A 的测试需要 B 先实现）

### 3.2 循环依赖检测

对依赖图执行 DFS 检测环：

```
对每个节点执行 DFS:
  标记为 "visiting"
  对每个邻居 (依赖):
    若邻居为 "visiting" → 发现环
    若邻居为 "unvisited" → 递归访问
  标记为 "visited"
```

若检测到循环依赖，报错并提示：
```
错误: 检测到循环依赖
  涉及的子方案: <环中所有名称>
  请调整拆解方案消除循环（合并其中一个到另一个）。
```

### 3.3 Wave 分组（拓扑排序）

使用 Kahn 算法（BFS 拓扑排序）生成分层执行计划：

```
算法:
1. 计算每个子方案的入度（被依赖数）
2. 入度为 0 的放入 Wave 1
3. 移除 Wave 1 的节点，更新剩余入度
4. 新入度为 0 的放入 Wave 2
5. 重复直到所有节点分配完毕
```

同一 Wave 内的子方案无互相依赖，可并行执行。

### 3.4 Wave 内批次划分

对每个 Wave，按子方案名称（kebab-case）字母序排列，以每批最多 3 个切分为批次：

```
MAX_PARALLEL = 3
对每个 Wave:
  sorted_names = 按 kebab-case 名称字母序排列
  batches = [sorted_names[i:i+3] for i in range(0, len(sorted_names), 3)]
```

批次规则：
- 同一批次内的子方案并行执行（最多 3 个）
- 不同批次串行执行
- 每个批次完成后立即合并回主干，再执行下一个批次
- 在展示方案时（Step 4.1）标注批次信息

---

## Step 4: 用户确认

### 4.1 展示拆解方案

输出完整的拆解方案供用户审阅：

```
## 拆解方案

### 子方案列表

| # | 名称 | 描述 | 依赖 | Wave | Batch |
|---|------|------|------|------|-------|
| 1 | auth-acl | ... | (无) | 1 | 1 |
| 2 | auth-user-model | ... | (无) | 1 | 1 |
| 3 | auth-jwt-service | ... | (无) | 1 | 1 |
| 4 | auth-session | ... | (无) | 1 | 2 |
| 5 | auth-http-layer | ... | auth-user-model, auth-jwt-service | 2 | 1 |

### 执行计划

Wave 1 (4 个子方案):
  Batch 1 (并行: 3)
    ├─ auth-acl
    ├─ auth-jwt-service
    └─ auth-user-model
  Batch 2 (串行: 1, Batch 1 合并后执行)
    └─ auth-session

Wave 2 (依赖 Wave 1, 1 个子方案):
  Batch 1 (并行: 1)
    └─ auth-http-layer

### 依赖图

Wave 1                    Wave 2
┌───────────┐             ┌─────────────────┐
│ auth-acl  │             │                 │
└───────────┘             │ auth-http-layer │
┌─────────────────┐       │                 │
│ auth-user-model ├──────►└─────────────────┘
└─────────────────┘              ▲
┌─────────────────┐              │
│ auth-jwt-service├──────────────┘
└─────────────────┘
┌──────────────┐
│ auth-session │
└──────────────┘

### 合并记录
- "user-repository" 合并到 "auth-user-model" (Q2 未通过: 是内部步骤)
```

### 4.2 用户确认交互

使用 **AskUserQuestion** 工具，提供三个选项：
1. **确认执行** — 按方案创建所有提案
2. **调整方案** — 用户修改后重新展示
3. **取消** — 终止流程

### 4.3 方案调整

若用户选择"调整方案"，根据用户反馈：
- 合并/拆分子方案
- 调整依赖关系
- 重新执行 Step 2.2 三问判定（若数量变化）
- 重新执行 Step 3 依赖图构建
- 返回 Step 4.1 重新展示

---

## Step 5: 批量创建提案

### 5.1 准备子方案描述

对确认后的每个子方案，准备精确的描述文本。格式：

```
<子方案名称>: <功能描述>。

背景: 这是"<原始需求>"综合方案的一部分。
功能: <详细功能描述>。
产出: <预期产出文件/模块>。
```

### 5.2 循环调用 /opsx:propose

按确认后的子方案列表顺序，逐个创建：

对每个子方案：
1. 使用 **Skill** 工具调用 `opsx:propose`，参数为子方案的名称和描述
   ```
   Skill("opsx:propose", args="<name>: <description>")
   ```
2. 等待 Skill 调用完成
3. 验证 `openspec/changes/<name>/` 目录已创建
4. 记录创建状态（成功/失败）

### 5.3 错误处理

若某个 `/opsx:propose` 执行失败：
1. 记录失败的子方案名称和失败原因
2. 使用 **AskUserQuestion** 询问用户：
   > "子方案 '<name>' 创建失败: <reason>。是否跳过继续处理剩余子方案？"
3. 用户选择跳过 → 继续下一个子方案
4. 用户选择停止 → 终止批量创建，进入 Step 6 输出部分报告

---

## Step 6: 依赖注入

### 6.1 写入 dependencies.yaml

对每个成功创建的子方案：
1. 检查该子方案是否有依赖（来自 Step 3 的依赖图）
2. 若有依赖：使用 **Write** 工具创建 `openspec/changes/<name>/dependencies.yaml`：

```yaml
dependencies:
  - <dep-name-1>
  - <dep-name-2>
```

### 6.2 格式规范

格式严格遵循 `parall-new-worktree-apply` Step 2.1 的解析规则：
- 键名: `dependencies:`（无引号）
- 列表项: 缩进 2 空格后 `- <change-name>`（kebab-case 名称，每项一行）
- 文件位置: `openspec/changes/<name>/dependencies.yaml`

### 6.3 无依赖跳过

若子方案无任何依赖（Wave 1 的成员），不创建 `dependencies.yaml`，跳过此步骤。

---

## Step 7: 总结报告

### 7.1 全部成功时

```
## 并行提案创建完成

### 创建的提案

| # | 名称 | 位置 | 依赖 | Wave | Batch |
|---|------|------|------|------|-------|
| 1 | auth-acl | openspec/changes/auth-acl/ | (无) | 1 | 1 |
| 2 | auth-user-model | openspec/changes/auth-user-model/ | (无) | 1 | 1 |
| 3 | auth-jwt-service | openspec/changes/auth-jwt-service/ | (无) | 1 | 1 |
| 4 | auth-session | openspec/changes/auth-session/ | (无) | 1 | 2 |
| 5 | auth-http-layer | openspec/changes/auth-http-layer/ | auth-user-model, auth-jwt-service | 2 | 1 |

### 执行计划

Wave 1 (4 个子方案):
  Batch 1 (并行: 3)
    ├─ auth-acl
    ├─ auth-jwt-service
    └─ auth-user-model
  Batch 2 (串行: 1, Batch 1 合并后执行)
    └─ auth-session

Wave 2 (依赖 Wave 1, 1 个子方案):
  Batch 1 (并行: 1)
    └─ auth-http-layer

### 下一步

运行 `/parall-new-worktree-apply` 开始并行实施。
```

### 7.2 部分失败时

在报告中增加失败部分：
```
### 创建失败的提案

| 名称 | 失败原因 |
|------|---------|
| auth-ui-login | /opsx:propose 执行超时 |

### 建议
- 对失败的提案，可手动运行 `/opsx:propose <name>` 重试
- 成功创建的提案可先通过 `/parall-new-worktree-apply` 执行
- 失败提案创建成功后，检查其 `dependencies.yaml` 文件是否正确
```

---

## Guardrails

- 不自建 artifact 生成逻辑，完全通过 `/opsx:propose` Skill 调用
- 不修改 `/opsx:propose` skill 本身
- 拆解方案必须经用户确认后才创建提案
- 三问判定是硬约束：未通过的候选必须合并，不可保留为独立提案
- `dependencies.yaml` 格式必须与 `parall-new-worktree-apply` Step 2.1 解析规则兼容
- 需求 ≤ 1 个子方案时提示用户考虑直接使用 `/opsx:propose`
- 超过 6 个子方案时标注警告
- 每 Wave 并行上限为 3（由 `parall-new-worktree-apply` 执行时控制）
- 每个批次完成后立即合并回主干，再执行下一个批次
- 失败的子方案不阻塞其他子方案的创建
