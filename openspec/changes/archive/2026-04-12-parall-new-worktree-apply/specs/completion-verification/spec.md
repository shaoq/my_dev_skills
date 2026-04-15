## ADDED Requirements

### Requirement: Re-scan tasks after all waves
全部 Wave 执行完成后，系统 SHALL 重新扫描 `openspec/changes/*/tasks.md`，检查每个之前标记为待执行的 change 的任务完成状态。

#### Scenario: All tasks completed
- **WHEN** 所有待执行 change 的 tasks.md 中所有项均为 `[x]`
- **THEN** 系统报告全部验证通过

#### Scenario: Some tasks remain incomplete
- **WHEN** 某个 change 的 tasks.md 中仍有 `[ ]` 未完成项
- **THEN** 系统列出该 change 名称和剩余未完成任务数量

### Requirement: Generate final report
系统 SHALL 在验证阶段生成最终报告，包含：执行总览（总 changes 数、Wave 数）、每个 Wave 的执行结果（change 名称、Agent 状态、合并状态）、验证结果、失败项详情（如有）。

#### Scenario: All successful
- **WHEN** 所有 changes 均成功执行并验证通过
- **THEN** 系统输出包含汇总表格的成功报告

#### Scenario: Partial failure
- **WHEN** 有 3 个 changes，其中 2 个成功、1 个失败
- **THEN** 系统输出报告标注 2 个成功和 1 个失败，并说明失败原因

### Requirement: Report dependency graph
系统 SHALL 在执行开始前显示解析后的依赖图和 Wave 分组计划，让用户确认执行计划。

#### Scenario: Show execution plan
- **WHEN** 依赖图构建完成
- **THEN** 系统显示 Wave 列表，每个 Wave 内包含 change 名称，标注依赖关系
