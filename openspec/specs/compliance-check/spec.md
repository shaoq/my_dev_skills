## ADDED Requirements

### Requirement: 判断变更是否触发合规要求

系统 SHALL 根据变更的范围（D3 的 EXPECTED_FILES 和 design.md 内容）判断每条合规要求是否被触发。

#### Scenario: test-sync 被源码变更触发

- **WHEN** EXPECTED_FILES 包含 `src/auth/login.py`（非测试文件）且合规要求为 `test-sync`
- **THEN** 该要求被标记为"已触发"

#### Scenario: test-sync 不被纯文档变更触发

- **WHEN** EXPECTED_FILES 仅包含 `README.md` 且合规要求为 `test-sync`
- **THEN** 该要求被标记为"不适用"

#### Scenario: api-schema-sync 被 design.md 中的 API 描述触发

- **WHEN** design.md 提及 "新增 API 端点 POST /api/v2/users" 且合规要求为 `api-schema-sync`
- **THEN** 该要求被标记为"已触发"

#### Scenario: 无要求被触发

- **WHEN** 变更范围不触发任何合规要求
- **THEN** D5 返回 `✓ (不适用)`

### Requirement: 通过 git diff 验证配套产出同步

系统 SHALL 对每条已触发的合规要求，通过 `git diff main..HEAD --name-only` 检查配套产出是否已随变更同步更新。

#### Scenario: test-sync 合规通过

- **WHEN** 合规要求 `test-sync` 被触发，且 git diff 中包含 `tests/test_auth.py`
- **THEN** 该要求合规检查通过

#### Scenario: test-sync 合规失败

- **WHEN** 合规要求 `test-sync` 被触发，但 git diff 中无任何 test/spec 相关文件
- **THEN** 该要求被记录到 `D5_GAPS` 列表

#### Scenario: doc-sync 合规检查

- **WHEN** 合规要求 `doc-sync` 被触发
- **THEN** 系统 SHALL 在 git diff 中搜索 `doc`、`.md`、`README` 模式的文件

#### Scenario: api-schema-sync 合规检查

- **WHEN** 合规要求 `api-schema-sync` 被触发
- **THEN** 系统 SHALL 在 git diff 中搜索 `schema`、`openapi`、`swagger`、`.proto` 模式的文件

### Requirement: 汇总 D5 检查结果

系统 SHALL 将 D5 结果汇总为以下格式之一：

- 所有已触发要求均通过 → `✓`
- 存在未通过的要求 → `✗ 缺失: <type-list>`（如 `✗ 缺失: test-sync, doc-sync`）

#### Scenario: 全部合规

- **WHEN** 所有已触发的合规要求均通过验证
- **THEN** D5 = `✓`

#### Scenario: 部分缺失

- **WHEN** test-sync 通过但 doc-sync 失败
- **THEN** D5 = `✗ 缺失: doc-sync`

### Requirement: D5 不自动补全

系统 SHALL NOT 自动创建或修改任何配套产出文件。缺失时仅在报告中提示，并建议用户运行 `/opsx:explore` 分析。

#### Scenario: 发现合规缺失时的行为

- **WHEN** D5 检测到 `test-sync` 缺失
- **THEN** 系统在 blocking reasons 中输出完整缺失内容和建议，不创建任何测试文件

### Requirement: D5 影响可存档判定

系统 SHALL 将 D5 纳入可存档逻辑。变更仅在所有五个维度（D1-D5）通过时才可存档。

#### Scenario: D5 失败阻塞归档

- **WHEN** D1-D4 均通过但 D5 失败
- **THEN** 该变更不可存档，blocking reasons 中显示合规缺失详情

#### Scenario: 无 CLAUDE.md 不阻塞归档

- **WHEN** D5 返回 `✓ (无项目规范)` 或 `✓ (无合规要求)` 或 `✓ (不适用)`
- **THEN** D5 视为通过，不阻塞归档
