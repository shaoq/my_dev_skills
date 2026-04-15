## ADDED Requirements

### Requirement: 通过正则提取合规要求

系统 SHALL 对 `CLAUDE_MD_FILES` 中每个文件逐行扫描，使用正则模式匹配提取合规要求。每个匹配项生成一条 `{ type, description, source_file }` 记录。

#### Scenario: 提取 test-sync 要求

- **WHEN** CLAUDE.md 包含 "must update tests when changing source code"
- **THEN** 系统提取一条 `{ type: "test-sync", description: "must update tests when changing source code", source_file: "CLAUDE.md" }`

#### Scenario: 提取中文合规要求

- **WHEN** CLAUDE.md 包含 "每次修改源码必须更新测试用例"
- **THEN** 系统提取一条 `{ type: "test-sync", description: "每次修改源码必须更新测试用例", source_file: "CLAUDE.md" }`

#### Scenario: 提取 api-schema-sync 要求

- **WHEN** CLAUDE.md 包含 "API 变更必须更新 OpenAPI schema"
- **THEN** 系统提取一条 `{ type: "api-schema-sync", description: "API 变更必须更新 OpenAPI schema", source_file: "CLAUDE.md" }`

### Requirement: 支持四种内置合规类型

系统 SHALL 支持以下内置类型及其匹配模式：

| 类型 | 匹配模式（case-insensitive） |
|------|------------------------------|
| `test-sync` | `must update.*(test\|spec\|测试\|用例)`, `必须更新.*(test\|测试\|用例)`, `每次变更后.*(test\|测试)`, `always (run\|write\|update).*(test\|spec)` |
| `doc-sync` | `must update.*(doc\|文档\|readme)`, `必须更新.*(doc\|文档)`, `always include.*(doc\|文档)` |
| `api-schema-sync` | `must update.*(api\|schema\|接口\|openapi)`, `必须更新.*(api\|schema\|接口)` |
| `changelog-sync` | `must update.*(changelog\|变更日志)` |

#### Scenario: 匹配 doc-sync 要求

- **WHEN** CLAUDE.md 包含 "always include documentation updates with code changes"
- **THEN** 系统提取 `{ type: "doc-sync", ... }`

#### Scenario: 同一行匹配多个模式

- **WHEN** CLAUDE.md 包含 "must update tests and docs after changes"
- **THEN** 系统提取 `test-sync` 和 `doc-sync` 各一条（首次匹配优先）

### Requirement: 按类型去重

系统 SHALL 对提取结果按 `type` 字段去重。多个 CLAUDE.md 文件中相同 type 的要求，仅保留最具体的描述。

#### Scenario: 多个 CLAUDE.md 有相同类型要求

- **WHEN** 根目录 CLAUDE.md 有 "must update tests" 且 `src/auth/CLAUDE.md` 有 "must update unit and integration tests for auth module"
- **THEN** 系统保留 "must update unit and integration tests for auth module"（更具体的描述）

#### Scenario: 无匹配的合规要求

- **WHEN** CLAUDE.md 存在但不包含任何合规关键词
- **THEN** D5 返回 `✓ (无合规要求)`
