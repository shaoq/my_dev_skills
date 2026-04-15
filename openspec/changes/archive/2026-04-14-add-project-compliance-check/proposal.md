## Why

当前 `check-changes-completed` 技能的四维检查模型（D1-D4：任务/artifacts/代码落地/依赖）只检查 OpenSpec 自身的交付完整性，但忽略了项目级规范（CLAUDE.md）定义的合规要求。例如 CLAUDE.md 可能要求"每次修改源码必须同步更新测试"、"API 变更必须更新 schema"等。目前这些要求完全不被检查，导致变更虽然通过了四维检查但可能违反了项目规范。

## What Changes

- 在 `check-changes-completed/SKILL.md` 中新增 **Dimension 5 — Project Compliance** 维度
- 自动载入项目根目录及子目录中的 `CLAUDE.md` 文件
- 通过关键词正则从 CLAUDE.md 中提取合规要求（test-sync、doc-sync、api-schema-sync、changelog-sync 等）
- 根据变更的范围（EXPECTED_FILES + design.md 内容）判断是否触发合规要求
- 通过 `git diff` 检查配套产出是否已同步
- 缺失时在报告中输出完整的缺失提示，建议用户运行 `/opsx:explore` 分析，**不自动补全**
- 更新汇总表增加"合规"列、更新 blocking reasons 和 archive hint
- 同步更新 `README.md` 中的维度描述

## Capabilities

### New Capabilities

- `claudemd-loading`: 定位并载入项目根目录和变更相关子目录中的 CLAUDE.md 文件
- `compliance-extraction`: 通过正则匹配从 CLAUDE.md 内容中提取合规要求（类型、描述、来源）
- `compliance-check`: 判断变更是否触发合规要求，并验证配套产出是否已同步

### Modified Capabilities

## Impact

- `check-changes-completed/SKILL.md` — 新增 D5 维度、更新汇总表/阻塞原因/存档提示/Guardrails
- `README.md` — 更新 Skills 一览表和详解中的维度描述
- 无新增依赖或工具权限（已有 `Read`、`Grep`、`Bash(grep *)`、`Bash(git diff *)` 等足够）
- 无 API 变更
