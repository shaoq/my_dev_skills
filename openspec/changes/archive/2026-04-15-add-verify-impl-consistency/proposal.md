## Why

现有的 `check-changes-completed` skill 只做存在性/状态性检查（文件有没有、任务打勾没、有没有提交），无法发现文档描述与代码实现之间的**语义不一致**。项目缺少一个深度验证工具来检测：文档提到的功能在代码中是否真正实现、API Schema 定义是否与路由代码对齐、集成测试是否覆盖了实际功能。

## What Changes

- 新增 `verify-impl-consistency` skill，实现三维语义一致性诊断：
  - **D1 Doc ↔ Code**: 从文档提取可验证声明（端点路径、函数名、参数类型等），与代码实现精确匹配 + 语义分析
  - **D2 Schema ↔ API Code**: 解析 OpenAPI/Swagger/Proto/GraphQL schema，与多语言路由定义交叉验证
  - **D3 Tests ↔ Code**: 从测试文件提取被测目标，验证其存在性、场景覆盖和孤立测试
- 采用分层验证策略：Layer 1 精确模式匹配（Grep），Layer 2 语义分析（Claude 阅读）
- 自动检测运行模式：始终执行项目级扫描，检测到活跃 OpenSpec change 时追加精细验证
- 纯诊断输出（不做 pass/fail 判定），报告按 CRITICAL/WARNING/INFO 分级
- 多语言路由匹配支持：TS/JS (Express, Fastify, NestJS), Python (FastAPI, Flask, Django), Go (Gin, Echo), Java (Spring)
- 同步更新 README.md 文档（Skills 一览表、流程图、详解章节、目录结构）

## Capabilities

### New Capabilities
- `doc-code-consistency`: 从项目文档中提取可验证声明，与代码实现进行精确匹配和语义分析，报告不一致发现
- `schema-api-consistency`: 解析 API schema 文件（OpenAPI/Swagger/Proto/GraphQL），与多语言路由定义交叉验证端点、参数、类型和状态码
- `test-code-consistency`: 从集成测试中提取被测目标（端点、函数），验证其在源码中的存在性，评估场景覆盖和孤立测试

### Modified Capabilities
<!-- 无需修改现有 spec -->

## Impact

- **新文件**: `verify-impl-consistency/SKILL.md` — skill 主文件
- **修改文件**: `README.md` — Skills 一览表、使用流程图、详解章节、目录结构
- **自动生效**: `setup-skills-env.py` 的 `scan_custom_skills()` 会自动发现新 skill，无需修改安装脚本
- **依赖**: 需要 Claude 语义理解能力（`disable-model-invocation: false`），这是与现有 skills 的关键区别
