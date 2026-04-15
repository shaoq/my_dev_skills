## ADDED Requirements

### Requirement: 扫描所有 active changes
系统 SHALL 扫描 `openspec/changes/` 目录下所有子目录，排除 `archive/` 目录，识别所有 active changes。

#### Scenario: 存在多个 active changes
- **WHEN** 用户调用 check-changes-completed skill
- **THEN** 系统列出 `openspec/changes/` 下所有非 archive 子目录作为 active changes

#### Scenario: 无 active changes
- **WHEN** `openspec/changes/` 下无子目录（或仅有 archive/）
- **THEN** 系统输出 "无 active changes" 并退出

### Requirement: 检查 Tasks 完成度
系统 SHALL 读取每个 active change 的 `tasks.md`，统计 `[x]`（已完成）和 `[ ]`（未完成）的计数和比例。

#### Scenario: 全部 tasks 已完成
- **WHEN** 某个 change 的 tasks.md 中所有任务项均为 `- [x]`
- **THEN** 维度 1 标记为通过，显示完成数 "N/N"

#### Scenario: 存在未完成 tasks
- **WHEN** 某个 change 的 tasks.md 中存在 `- [ ]` 未完成任务
- **THEN** 维度 1 标记为未通过，显示 "X/N" 和未完成项列表

#### Scenario: 无 tasks.md 文件
- **WHEN** 某个 change 目录下不存在 tasks.md
- **THEN** 维度 1 标记为"缺失"，提示 tasks 文件不存在

### Requirement: 检查 Artifacts 齐全性
系统 SHALL 通过 `openspec status --change "<name>" --json` 检查每个 change 的所有 artifacts 是否状态为 done。

#### Scenario: 所有 artifacts 完成
- **WHEN** openspec status 返回的所有 artifacts 的 status 均为 "done"
- **THEN** 维度 2 标记为通过

#### Scenario: 存在未完成 artifacts
- **WHEN** openspec status 返回的 artifacts 中存在 status 不为 "done" 的项
- **THEN** 维度 2 标记为未通过，列出未完成的 artifact 名称

### Requirement: 检查 Code 落地验证
系统 SHALL 通过两种方式验证代码是否真正落地：(1) 检查设计文档中提及的产出文件是否存在，(2) 通过 git log 检查是否有实质提交。

#### Scenario: 产出文件存在且有提交
- **WHEN** change 的产出文件（如 SKILL.md）存在，且 `git log` 显示有与该 change 相关的提交
- **THEN** 维度 3 标记为通过

#### Scenario: 产出文件缺失
- **WHEN** change 的预期产出文件不存在
- **THEN** 维度 3 标记为未通过，列出缺失的文件

#### Scenario: 无相关 git 提交
- **WHEN** 产出文件存在但 git log 中无与该 change 相关的提交
- **THEN** 维度 3 标记为警告，提示"可能有未提交的变更"

### Requirement: 检查依赖完整性
系统 SHALL 读取每个 change 的 `proposal.md` 中的 `## Dependencies` 段，提取依赖名称列表，验证每个依赖 change 的完成状态。

#### Scenario: 无依赖
- **WHEN** change 的 proposal.md 中无 `## Dependencies` 段或该段为空
- **THEN** 维度 4 标记为通过（无依赖）

#### Scenario: 所有依赖已完成
- **WHEN** change 的所有依赖 changes 均通过四维检查
- **THEN** 维度 4 标记为通过

#### Scenario: 存在未完成的依赖
- **WHEN** change 的某个依赖 change 未通过四维检查
- **THEN** 维度 4 标记为未通过，列出阻塞的依赖名称及其未通过维度

#### Scenario: 依赖不存在
- **WHEN** Dependencies 段引用的 change 名称在 `openspec/changes/` 中不存在（也不在 archive 中）
- **THEN** 维度 4 标记为异常，提示依赖引用无效

### Requirement: 汇总表格输出
系统 SHALL 将所有 active changes 的四维检查结果汇总为表格输出。

#### Scenario: 多个 changes 的汇总表格
- **WHEN** 检查完成
- **THEN** 输出包含以下列的表格：Change 名称、Tasks、Artifacts、Code 落地、依赖、可存档?

#### Scenario: 可存档判断
- **WHEN** 某个 change 的四个维度全部通过
- **THEN** 该 change 标记为"可存档"

#### Scenario: 不可存档判断
- **WHEN** 某个 change 的任一维度未通过
- **THEN** 该 change 标记为"不可存档"，并列出阻塞原因
