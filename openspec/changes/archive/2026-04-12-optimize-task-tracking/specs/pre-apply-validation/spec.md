## ADDED Requirements

### Requirement: Artifact completeness check before apply

`new-worktree-apply` 在调用 `opsx:apply` 之前 SHALL 执行 artifact 完整性校验，通过 `openspec status --change "<name>" --json` 确认所有 artifacts 的 `status` 为 `"done"`。

#### Scenario: All artifacts done
- **WHEN** `openspec status --change "<name>" --json` 返回所有 artifacts `status: "done"`
- **THEN** 输出 "Artifacts 校验通过" 并继续执行 apply

#### Scenario: Some artifacts incomplete
- **WHEN** 有 artifact 的 `status` 不是 `"done"`
- **THEN** 输出错误信息列出未完成的 artifact 名称，停止执行，建议用户先完成 artifact

### Requirement: Key files existence verification

`new-worktree-apply` SHALL 验证以下关键文件在 worktree 中存在：
- `openspec/changes/<name>/proposal.md`
- `openspec/changes/<name>/design.md`
- `openspec/changes/<name>/tasks.md`
- `openspec/changes/<name>/specs/` 目录下至少一个 spec 文件

#### Scenario: All key files present
- **WHEN** 上述文件全部存在
- **THEN** 校验通过，继续执行

#### Scenario: Key file missing
- **WHEN** 任一关键文件不存在
- **THEN** 输出错误信息指明缺失文件，停止执行

### Requirement: Pre-apply validation for parallel execution

`parall-new-worktree-apply` SHALL 在 Step 1 Discovery 阶段对每个待执行 change 进行相同的 artifact 校验，跳过 artifacts 不完整的 change 并在执行计划中标注。

#### Scenario: Change has incomplete artifacts
- **WHEN** Discovery 阶段检测到某 change 的 artifacts 不完整
- **THEN** 将该 change 从待执行列表中排除，在执行计划输出中标注为 "跳过: artifacts 未完成"

#### Scenario: All changes have complete artifacts
- **WHEN** 所有待执行 changes 的 artifacts 均完整
- **THEN** 正常进入依赖解析和执行阶段
