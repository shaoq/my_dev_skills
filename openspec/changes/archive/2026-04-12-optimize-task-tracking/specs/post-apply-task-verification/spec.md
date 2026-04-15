## ADDED Requirements

### Requirement: Post-apply task status verification

`new-worktree-apply` 在 `opsx:apply` 执行完成后 SHALL 读取 `tasks.md`，检查是否存在仍为 `[ ]` 的 task 项。

#### Scenario: All tasks marked complete
- **WHEN** `opsx:apply` 执行后 tasks.md 中所有 task 均为 `[x]`
- **THEN** 输出 "所有 N 个任务已标记完成"，跳过补标记步骤

#### Scenario: Some tasks remain unmarked
- **WHEN** `opsx:apply` 执行后 tasks.md 中仍有 `[ ]` 项
- **THEN** 进入自动补标记流程

### Requirement: Automatic task backfill based on file existence

对每个仍为 `[ ]` 的 task，系统 SHALL 解析其描述文本，提取文件路径模式，检查对应产出文件是否存在。若存在则自动将 `[ ]` 改为 `[x]`。

解析规则：
- 反引号内的路径（如 `` `xxx/SKILL.md` ``）→ 检查该路径文件存在性
- "创建 `xxx/` 目录" → 检查目录存在性
- "编写 frontmatter" → 检查对应文件包含 frontmatter 标记（`---`）
- "实现 xxx" 类描述 → 检查相关代码文件存在

#### Scenario: Task references file that exists
- **WHEN** task 描述中引用的文件路径在磁盘上存在
- **THEN** 自动将 `[ ]` 改为 `[x]`，记录到补标记报告

#### Scenario: Task references file that does not exist
- **WHEN** task 描述中引用的文件路径在磁盘上不存在
- **THEN** 保留 `[ ]` 状态不变

### Requirement: Post-apply verification report

补标记完成后 SHALL 输出报告，包含：
- 自动标记的 task 数量及列表
- 仍为 `[ ]` 的 task 数量及列表（如有）
- 总完成度 X/N

#### Scenario: Some tasks auto-marked
- **WHEN** 补标记流程完成，有部分 task 被自动标记
- **THEN** 输出报告: "自动标记: X 个，仍缺失: Y 个，总计: N 个"

#### Scenario: No tasks needed backfill
- **WHEN** 所有 task 已在 apply 过程中被正确标记
- **THEN** 输出报告: "无需补标记，所有 N 个任务已完成"

### Requirement: Parallel agent post-apply verification

`parall-new-worktree-apply` 在合并所有分支后 SHALL 对每个已执行的 change 重新读取 `tasks.md`，执行相同的文件存在性检测与补标记。

#### Scenario: Merge completed with task gaps
- **WHEN** 合并完成后发现某 change 的 tasks.md 有未标记项但产出文件已存在
- **THEN** 在主目录中直接修改 tasks.md 补标记

#### Scenario: All tasks verified after merge
- **WHEN** 合并完成后所有 tasks.md 均正确标记
- **THEN** 验证通过，进入最终报告
