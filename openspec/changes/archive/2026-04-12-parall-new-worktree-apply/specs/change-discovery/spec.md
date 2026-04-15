## ADDED Requirements

### Requirement: Scan pending OpenSpec changes
系统 SHALL 扫描 `openspec/changes/` 目录下的所有子目录（排除 `archive/`），检查每个 change 的 `tasks.md` 文件中是否存在 `[ ]` 未完成项，仅将含有未完成项的 changes 列入待执行列表。

#### Scenario: Multiple pending changes found
- **WHEN** `openspec/changes/` 下有 3 个 change 目录，其中 2 个的 tasks.md 含有 `[ ]` 项
- **THEN** 系统将这 2 个 change 列入待执行列表，跳过已完成的那个

#### Scenario: No pending changes
- **WHEN** 所有 change 的 tasks.md 中所有项均为 `[x]`
- **THEN** 系统报告"无可执行的 changes"并退出

### Requirement: Parse dependencies from proposal
系统 SHALL 读取每个待执行 change 的 `proposal.md` 文件，解析 `## Dependencies` 段中的无序列表项作为依赖的 change 名称。无此段或段为空视为无依赖。

#### Scenario: Dependencies declared
- **WHEN** change-a 的 proposal.md 包含 `## Dependencies` 段且列出 `change-b` 和 `change-c`
- **THEN** 系统记录 change-a 依赖于 change-b 和 change-c

#### Scenario: No dependencies section
- **WHEN** change-x 的 proposal.md 不包含 `## Dependencies` 段
- **THEN** 系统将 change-x 视为无依赖

### Requirement: Build dependency graph and topological sort
系统 SHALL 基于解析出的依赖关系构建有向图，执行拓扑排序生成分波次执行计划（Wave 列表）。同一 Wave 内的 changes 无互相依赖，可并行执行。

#### Scenario: Linear dependency chain
- **WHEN** change-a 无依赖，change-b 依赖 change-a，change-c 依赖 change-b
- **THEN** 生成 3 个 Wave：Wave 1=[a], Wave 2=[b], Wave 3=[c]

#### Scenario: Independent changes
- **WHEN** change-a、change-b、change-c 均无依赖
- **THEN** 生成 1 个 Wave：Wave 1=[a, b, c]，全部可并行

#### Scenario: Mixed dependencies
- **WHEN** change-a 和 change-c 无依赖，change-b 依赖 change-a，change-d 依赖 change-b 和 change-c
- **THEN** 生成 3 个 Wave：Wave 1=[a, c], Wave 2=[b], Wave 3=[d]

### Requirement: Detect circular dependencies
系统 SHALL 检测依赖图中的循环依赖，若存在则报告错误并列出涉及的 change 名称，不执行任何操作。

#### Scenario: Circular dependency detected
- **WHEN** change-a 依赖 change-b，change-b 依赖 change-a
- **THEN** 系统报告循环依赖错误，列出 "change-a ↔ change-b"，并退出

### Requirement: Validate dependency references
系统 SHALL 验证每个依赖声明对应的 change 名称在 `openspec/changes/` 目录中存在。若引用了不存在的 change，报告错误并退出。

#### Scenario: Invalid dependency reference
- **WHEN** change-a 声明依赖 change-nonexistent，但该 change 目录不存在
- **THEN** 系统报告 "change-nonexistent 不存在"，并退出
