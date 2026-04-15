## ADDED Requirements

### Requirement: 定位项目根目录 CLAUDE.md

系统 SHALL 检查项目根目录是否存在 `CLAUDE.md` 文件。若存在，将其内容载入待解析列表。

#### Scenario: 项目根目录有 CLAUDE.md

- **WHEN** 项目根目录存在 `CLAUDE.md` 文件
- **THEN** 系统将该文件路径加入 `CLAUDE_MD_FILES` 列表

#### Scenario: 项目根目录无 CLAUDE.md

- **WHEN** 项目根目录不存在 `CLAUDE.md` 文件
- **THEN** `CLAUDE_MD_FILES` 列表为空，D5 返回 `✓ (无项目规范)`

### Requirement: 定位变更相关子目录 CLAUDE.md

系统 SHALL 检查 D3 已识别的 `EXPECTED_FILES` 涉及的子目录中是否存在 `CLAUDE.md`，并加入待解析列表。

#### Scenario: 产出文件所在子目录有 CLAUDE.md

- **WHEN** D3 的 EXPECTED_FILES 包含 `src/auth/login.py` 且 `src/auth/CLAUDE.md` 存在
- **THEN** 系统将 `src/auth/CLAUDE.md` 加入 `CLAUDE_MD_FILES` 列表

#### Scenario: 产出文件所在子目录无 CLAUDE.md

- **WHEN** D3 的 EXPECTED_FILES 包含 `src/auth/login.py` 但 `src/auth/CLAUDE.md` 不存在
- **THEN** 系统不添加额外文件，仅使用根目录的 `CLAUDE.md`（若存在）

### Requirement: 跳过不可读的 CLAUDE.md

系统 SHALL 在 CLAUDE.md 无法读取（编码问题、二进制内容）时跳过该文件，不阻塞归档。

#### Scenario: CLAUDE.md 为二进制或编码异常

- **WHEN** `CLAUDE.md` 文件存在但读取失败
- **THEN** D5 返回 `✓ (无法解析)`，不阻塞归档
