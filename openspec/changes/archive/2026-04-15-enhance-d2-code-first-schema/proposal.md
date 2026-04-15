## Why

D2 (Schema ↔ API Code) 当前仅检查独立 schema 文件（openapi.yaml、swagger.json、*.proto、*.graphql）。当项目无此类文件时直接跳过整个 D2 维度。但对于 FastAPI + Pydantic 等"代码即 schema"框架，API schema 由运行时自动生成，永远不会有独立文件——然而代码中仍可能存在 response_model 缺失、类型注解不一致、未文档化异常等大量一致性问题。跳过检查导致这些项目缺少关键的 schema 完备性验证。

## What Changes

- 在 D2 增加分支逻辑：当 `SCHEMA_FILES` 为空但 `TECH_STACK` 检测到 code-first 框架时，不跳过，而是执行基于代码的 schema 一致性分析
- 新增 Pydantic Model 注册表构建（扫描所有 `BaseModel` 子类及其字段元数据）
- 新增路由元数据提取与一致性检查（response_model 缺失、status_code 冲突、未文档化 HTTPException、response_model_include/exclude 失真等）
- 新增 Pydantic Model 质量检查（Field 缺少 description/examples、未知类型引用、循环依赖）
- 首批支持 FastAPI + Pydantic，后续可扩展至 Django Ninja、Flask-RESTX 等 code-first 框架

## Capabilities

### New Capabilities
- `code-first-schema-analysis`: 基于 code-first 框架源码的 API schema 完备性静态分析，包括路由元数据提取、Pydantic model 注册表构建、以及 schema 质量检查

### Modified Capabilities
- `schema-api-consistency`: D2 的入口守卫条件从"无 schema 文件则跳过"变更为"无 schema 文件时检查 TECH_STACK 是否为 code-first 框架，若是则走 code-first 分支"

## Impact

- **SKILL.md**: Step 2b（发现逻辑不变）、Step 4（D2 主逻辑增加分支，新增 4d/4e/4f 三个子步骤，约 80-100 行新增内容）
- **报告输出**: D2 维度在 code-first 项目中不再为空，会产生 WARNING/INFO 级别的发现项
- **无破坏性变更**: 独立 schema 文件模式的 4a-4c 逻辑完全不变，仅在其后增加 else-if 分支
