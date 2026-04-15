## ADDED Requirements

### Requirement: 后注入 Dependencies 段到 proposal.md
系统 SHALL 在 `/opsx:propose` 完成后，对有依赖的子方案使用 Read + Edit 工具在其 `proposal.md` 中注入 `## Dependencies` 段。

#### Scenario: 为有依赖的子方案注入 Dependencies 段
- **WHEN** 子方案 "auth-middleware" 依赖 "auth-core-model" 且 `/opsx:propose` 已完成
- **THEN** 系统 SHALL 读取 `openspec/changes/auth-middleware/proposal.md`，在文件末尾追加：
  ```
  ## Dependencies

  - auth-core-model
  ```

#### Scenario: 无依赖的子方案跳过注入
- **WHEN** 子方案 "auth-core-model" 无任何依赖
- **THEN** 系统 SHALL 不修改其 `proposal.md`，跳过依赖注入步骤

### Requirement: Dependencies 段格式兼容 parall-new-worktree-apply
系统 SHALL 确保 `## Dependencies` 段的格式与 `parall-new-worktree-apply` Step 2.1 的解析规则完全一致。

#### Scenario: 格式兼容性验证
- **WHEN** 系统 注入 Dependencies 段
- **THEN** 段格式 SHALL 为 `## Dependencies` 标题行 + 后续 `- <change-name>` 无序列表项，与 parall-new-worktree-apply 的 grep 解析规则匹配

### Requirement: 生成总结报告
系统 SHALL 在所有子方案创建和依赖注入完成后，输出总结报告。

#### Scenario: 输出完整总结
- **WHEN** 所有子方案的 `/opsx:propose` 和依赖注入均已完成
- **THEN** 系统 SHALL 输出包含以下内容的总结报告：
  - 创建的提案列表（名称 + 位置）
  - 依赖关系可视化（ASCII 图）
  - 预估 Wave 分组
  - 提示用户执行 `/parall-new-worktree-apply`

#### Scenario: 部分子方案失败
- **WHEN** 5 个子方案中有 2 个创建失败
- **THEN** 系统 SHALL 在报告中标注失败项及原因，展示成功项的完整总结，并提供后续建议
