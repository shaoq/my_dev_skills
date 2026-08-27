## MODIFIED Requirements

### Requirement: 通过 git diff 验证配套产出同步

系统 SHALL 只对本次调用一个或多个显式 `--change <active-change>` 选择项检查合规要求，并通过显式 `--target <target-branch>` 所解析的冻结 `<BASE_HEAD>..<CURRENT_HEAD>` 文件差异检查配套产出是否已随变更同步更新。系统 MUST 先证明 `BASE_HEAD` 是 `CURRENT_HEAD` 的祖先；D5 MUST 与 D3 使用同一对冻结 commits，并且 MUST NOT 固定或回退到 `main..HEAD`、自动选择未声明 change 或改用 merge-base。

#### Scenario: test-sync 合规通过

- **WHEN** 合规要求 `test-sync` 被触发，且冻结的目标分支差异中包含 `tests/test_auth.py`
- **THEN** 该要求合规检查通过

#### Scenario: test-sync 合规失败

- **WHEN** 合规要求 `test-sync` 被触发，但冻结的目标分支差异中无任何 test/spec 相关文件
- **THEN** 该要求被记录到 `D5_GAPS` 列表

#### Scenario: doc-sync 合规检查

- **WHEN** 合规要求 `doc-sync` 被触发
- **THEN** 系统 SHALL 在冻结的目标分支差异中搜索 `doc`、`.md`、`README` 模式的文件

#### Scenario: api-schema-sync 合规检查

- **WHEN** 合规要求 `api-schema-sync` 被触发
- **THEN** 系统 SHALL 在冻结的目标分支差异中搜索 `schema`、`openapi`、`swagger`、`.proto` 模式的文件

#### Scenario: D3 与 D5 基线一致

- **WHEN** `check-changes-completed --target develop --change change-a` 同时执行代码交付与配套合规检查
- **THEN** D3 的 commit 查询和 D5 的文件查询 SHALL 使用同一个冻结 `develop` commit

#### Scenario: 多目标 changes 按显式选择集隔离

- **WHEN** 调用为 `check-changes-completed --target develop --change change-a --change change-b`，且另一个 active `change-c` 面向 `release`
- **THEN** D3、D5、blocking reasons 和任务回填 SHALL 只处理 `change-a` 与 `change-b`，并且 MUST NOT 修改 `change-c/tasks.md`

#### Scenario: 基线不是当前提交的祖先

- **WHEN** 冻结的 `BASE_HEAD` 不是 `CURRENT_HEAD` 的祖先
- **THEN** D3 与 D5 SHALL 标记为未执行或阻塞，系统 MUST NOT 回填、stage 或 commit 任何所选 change 的任务标记

#### Scenario: 快照在写回前漂移

- **WHEN** 目标 ref 或当前 HEAD 在最终复检时不再等于冻结的 `BASE_HEAD` 或 `CURRENT_HEAD`
- **THEN** 报告 SHALL 显示冻结结果为 stale evidence、可存档状态为 unknown/blocked，并且系统 MUST NOT 执行任务写回
