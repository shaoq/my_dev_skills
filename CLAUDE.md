# Project Conventions

## 流程约束

任何分析完成后，不得直接进入编码。必须遵循 opsx 工作流：

1. `/opsx:explore` — 探索和理解需求
2. `/opsx:propose` — 创建提案（proposal、design、specs、tasks）
3. `/opsx:apply` — 实施任务
4. `/opsx:archive` — 归档完成的变更

## Skill 变更范围

所有 skill 的变更（新增、删除、修改）必须在当前项目目录下进行。
用户目录（`~/.claude/skills/`）下的 skill 由用户自行管理和更新，不得修改。
