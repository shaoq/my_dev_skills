## ADDED Requirements

### Requirement: Wave 内批次划分上限

`parall-new-worktree-apply` SHALL 对每个 Wave 的 changes 按目录名字母序排列后，以每批最多 3 个切分为多个 Batch。同 Batch 内并行 spawn Agent，不同 Batch 串行执行。

#### Scenario: Wave 有 3 个或更少 changes

- **WHEN** Wave 内有 3 个 changes（alpha、beta、gamma）
- **THEN** 生成 1 个 Batch，3 个 Agent 在同一消息中并行 spawn

#### Scenario: Wave 有 5 个 changes

- **WHEN** Wave 内有 5 个 changes（alpha、beta、gamma、delta、epsilon）
- **THEN** 生成 2 个 Batch：Batch 1 含 alpha/beta/gamma，Batch 2 含 delta/epsilon

#### Scenario: Wave 有 6 个 changes

- **WHEN** Wave 内有 6 个 changes
- **THEN** 生成 2 个 Batch，每 Batch 各 3 个

### Requirement: 每 Batch 完成后立即合并

`parall-new-worktree-apply` SHALL 在每个 Batch 的所有 Agent 完成后，立即执行串行合并流程（rebase + merge），再开始下一个 Batch。

#### Scenario: 两个 Batch 的 Wave 执行顺序

- **WHEN** Wave 1 有 Batch 1（3 个 change）和 Batch 2（2 个 change）
- **THEN** 先并行执行 Batch 1 的 3 个 Agent → 等待完成 → 串行合并 Batch 1 成功分支 → 再并行执行 Batch 2 的 2 个 Agent → 等待完成 → 串行合并 Batch 2 成功分支

#### Scenario: Batch 1 有 Agent 失败

- **WHEN** Batch 1 中有 1 个 Agent 失败
- **THEN** 仍然执行 Batch 1 的合并（仅合并成功的分支），然后继续执行 Batch 2

### Requirement: 规划阶段预览 Batch 划分

`parall-new-proposal` SHALL 在 Step 3 依赖图构建后新增 Step 3.4（批次划分），按每批最多 3 个预计算 Batch，并在 Step 4.1 展示方案中标注每个子方案的 Wave 和 Batch 信息。

#### Scenario: 展示含 Batch 信息的拆解方案

- **WHEN** 拆解产生 4 个 Wave 1 子方案和 1 个 Wave 2 子方案
- **THEN** 展示表格含 Batch 列：Wave 1 Batch 1 含前 3 个、Batch 2 含第 4 个，Wave 2 Batch 1 含 1 个

#### Scenario: 总结报告含 Batch 信息

- **WHEN** 所有提案创建成功
- **THEN** Step 7.1 总结报告中的表格 SHALL 包含 Batch 列，依赖图 SHALL 标注 Batch 边界

### Requirement: 颗粒度阈值调整

`parall-new-proposal` Step 2.3 颗粒度检测 SHALL 使用新阈值：`≤1 建议 /opsx:propose`、`2-6 正常`、`>6 警告`。

#### Scenario: 产生 2 个子方案

- **WHEN** 三问判定后保留 2 个子方案
- **THEN** 进入正常范围，继续执行（不提示使用 /opsx:propose）

#### Scenario: 产生 7 个子方案

- **WHEN** 三问判定后保留 7 个子方案
- **THEN** 输出警告"拆分粒度可能过细，超过 6 个会导致 Wave 和 Batch 数增多"

### Requirement: 执行计划展示含 Batch

`parall-new-worktree-apply` Step 2.5 展示执行计划时 SHALL 标注每 Wave 的 Batch 划分。

#### Scenario: 展示含 5 个 changes 的执行计划

- **WHEN** 发现 5 个无依赖的 changes
- **THEN** 展示：Wave 1 Batch 1（并行: 3）含前 3 个、Batch 2（并行: 2）含后 2 个

### Requirement: Guardrails 同步更新

`parall-new-proposal` 和 `parall-new-worktree-apply` 的 Guardrails 段 SHALL 反映并发上限为 3 的约束。`README.md` SHALL 同步更新注意事项描述。

#### Scenario: Guardrails 包含并发上限

- **WHEN** 读取任一 SKILL.md 的 Guardrails 段
- **THEN** 包含"每 Wave 并行上限为 3"或"MAX_PARALLEL = 3"的明确声明

#### Scenario: README 注意事项准确

- **WHEN** 读取 README.md 中 parall-new-proposal 的注意事项
- **THEN** 显示"超过 6 个时会警告"和"每 Wave 并行上限为 3"
