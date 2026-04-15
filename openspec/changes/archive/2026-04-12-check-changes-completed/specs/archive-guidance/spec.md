## ADDED Requirements

### Requirement: 识别可存档 changes
系统 SHALL 从检查结果中筛选出四维全部通过的 changes，作为可存档候选列表。

#### Scenario: 存在可存档 changes
- **WHEN** 检查完成且至少有一个 change 四维全部通过
- **THEN** 系统列出可存档 changes 并进入存档引导流程

#### Scenario: 无可存档 changes
- **WHEN** 检查完成但没有任何 change 四维全部通过
- **THEN** 系统显示"当前无可存档的 changes"并列出各 change 的阻塞原因

### Requirement: 提供存档策略选择
系统 SHALL 使用 AskUserQuestion 工具让用户选择存档策略。

#### Scenario: 用户选择全部存档
- **WHEN** 用户选择"全部存档"
- **THEN** 系统对每个可存档 change 依次调用 `/opsx:archive <name>` 完成存档

#### Scenario: 用户选择逐个确认
- **WHEN** 用户选择"逐个确认"
- **THEN** 系统对每个可存档 change 使用 AskUserQuestion 询问是否存档，确认后调用 `/opsx:archive <name>`

#### Scenario: 用户选择仅查看
- **WHEN** 用户选择"仅查看，不存档"
- **THEN** 系统结束检查流程，不执行任何存档操作

### Requirement: 存档执行与状态更新
系统 SHALL 逐个执行存档操作，并显示每个存档操作的结果。

#### Scenario: 存档成功
- **WHEN** 调用 `/opsx:archive <name>` 成功完成
- **THEN** 显示存档成功摘要，继续下一个

#### Scenario: 存档失败
- **WHEN** 调用 `/opsx:archive <name>` 失败
- **THEN** 显示失败原因，询问用户是否跳过继续
