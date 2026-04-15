## ADDED Requirements

### Requirement: Detect rebase conflicts
系统 SHALL 在执行 `git rebase main <branch>` 后检测是否存在冲突（通过 `git status --porcelain` 检查 `UU` 状态的文件）。若检测到冲突，启动智能解决流程。

#### Scenario: Rebase without conflicts
- **WHEN** `git rebase main <branch>` 执行成功，无冲突文件
- **THEN** 系统继续执行 `git checkout main && git merge <branch>`

#### Scenario: Rebase with conflicts
- **WHEN** `git rebase main <branch>` 产生冲突文件
- **THEN** 系统读取冲突文件内容，分析冲突标记

### Requirement: Analyze conflict markers
系统 SHALL 读取每个冲突文件，解析 `<<<<<<<`、`=======`、`>>>>>>>` 标记，识别当前分支（HEAD）的改动和被 rebase 分支的改动，分析两个改动的区域是否重叠。

#### Scenario: Non-overlapping changes
- **WHEN** 冲突文件中两个分支的修改位于不同区域（如文件头部 vs 文件尾部）
- **THEN** 系统保留双方的改动，生成合并后的文件

#### Scenario: Overlapping changes with resolvable semantics
- **WHEN** 两个分支修改了同一区域，但语义上可以合并（如添加不同的列表项）
- **THEN** 系统智能合并双方内容，生成合并后的文件

#### Scenario: Irresolvable conflict
- **WHEN** 两个分支修改了同一区域且语义无法自动合并
- **THEN** 系统执行 `git rebase --abort`，报告冲突详情，跳过该分支

### Requirement: Apply conflict resolution
系统 SHALL 在解决冲突后执行 `git add <resolved-files> && git rebase --continue`，继续 rebase 流程。

#### Scenario: All conflicts resolved
- **WHEN** 所有冲突文件已解决并 `git add`
- **THEN** 系统执行 `git rebase --continue`，完成 rebase

### Requirement: Report unresolved conflicts
若冲突无法自动解决，系统 SHALL 报告以下信息：冲突的 change 名称、冲突文件路径、双方修改的摘要，并建议用户手动解决。

#### Scenario: Conflict abort report
- **WHEN** 冲突无法自动解决，执行了 `git rebase --abort`
- **THEN** 系统输出包含 change 名称、文件路径、冲突摘要的报告
