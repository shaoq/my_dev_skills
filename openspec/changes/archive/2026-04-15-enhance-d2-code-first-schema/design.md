## Context

`verify-impl-consistency` skill 的 D2 维度（Schema ↔ API Code）当前设计为：扫描独立 schema 文件 → 提取 endpoint → 与代码路由匹配。当无 schema 文件时直接跳过。

这覆盖了"schema-first"项目（手写 openapi.yaml → 生成代码），但忽略了"code-first"项目（代码 → 运行时自动生成 schema）。FastAPI + Pydantic 是最常见的 code-first 组合：路由装饰器定义 endpoint，Pydantic model 定义 request/response 结构，FastAPI 在启动时自动生成完整 OpenAPI 文档。

问题：虽然 schema 是自动生成的，但代码中仍可能存在大量一致性问题（见 proposal），当前 skill 完全无法检测。

## Goals / Non-Goals

**Goals:**
- D2 在无独立 schema 文件时，若 TECH_STACK 为 FastAPI，执行 code-first 静态分析
- 覆盖 6 类核心不一致：response_model 缺失、response_model 与实际返回不一致、status_code 冲突、未文档化异常、include/exclude 失真、Field 质量不足
- 复用现有 SKILL.md 的两层验证架构（Layer 1 Grep + Layer 2 语义分析）
- 不影响独立 schema 文件模式的 4a-4c 逻辑

**Non-Goals:**
- 不运行应用程序、不启动 FastAPI server
- 不做 AST 级别精确解析（Grep + Read 够用，与现有 skill 风格一致）
- 不自动修复问题，只报告发现
- 不支持 TypeScript/Go/Java 的 code-first 框架（本轮仅 FastAPI + Pydantic）
- 不替代 mypy/pyright 等类型检查器

## Decisions

### D1: 分支策略 — 在 D2 Step 4 入口增加 else-if

**选择**: 在现有 `if SCHEMA_FILES empty → skip` 之后增加 `else if TECH_STACK contains fastapi → code-first 模式`

**替代方案**: 创建独立 D2.5 维度 — 增加复杂度，且逻辑仍属 schema↔code 一致性范畴

**理由**: 两种模式解决的是同一个问题（schema 与代码是否一致），只是数据源不同。保持同一维度更直观。

### D2: Code-first 分析拆分为 4d/4e/4f 三步

- **4d — Pydantic Model 注册表**: Grep 扫描所有 `BaseModel` 子类，提取字段名、类型、`Field()` 参数。构建 `MODEL_REGISTRY`。
- **4e — 路由元数据检查**: Grep 扫描所有路由装饰器，提取 `response_model`、`status_code`、`responses`、`tags` 等参数。对每个路由执行 6 项一致性检查。
- **4f — Model 质量检查**: 基于 `MODEL_REGISTRY` 检查 Field 完备性、类型引用有效性、循环依赖。

**理由**: 三步拆分与现有 4a/4b/4c 结构对称（提取 → 匹配 → 深入），保持 skill 的可读性。

### D3: 检查项严重度分级

| 严重度 | 检查项 | 理由 |
|--------|--------|------|
| CRITICAL | 无 | 独立 schema 模式才产生 CRITICAL（定义了但不存在），code-first 至少代码能运行 |
| WARNING | 无 response_model、status_code 冲突、未文档化异常、include/exclude 失真、response_model 与返回不一致、未知类型引用、循环依赖 | 影响文档准确性和运行时行为 |
| INFO | Field 缺 description/examples、无 tags、无 summary/description | 影响文档可读性但不影响功能 |

**理由**: code-first 项目至少有代码在运行，问题严重度低于"schema 声明了但代码不存在"的情况。

### D4: 复用 TECH_STACK 检测 — 不引入新配置

**选择**: 复用 Step 2d 已检测的 `TECH_STACK`，仅检查是否包含 `fastapi`

**替代方案**: 让用户通过参数指定 — 增加使用复杂度

**理由**: Step 2d 已扫描 `requirements.txt` / `pyproject.toml` 中的 `fastapi`，无需重复检测。

## Risks / Trade-offs

**[Grep 误匹配]** → Model 注册表和路由提取依赖正则，可能误识别（如注释中的 `class X(BaseModel)`）。缓解：Layer 1 结果由 Layer 2 语义分析确认，误匹配降级为 UNCERTAIN。

**[FastAPI 路由变体多]** → `APIRouter` 实例命名多样（router、api_router、user_router），装饰器参数写法不统一。缓解：Grep 模式匹配 `@\\w+\\.(get|post|put|delete|patch)` 而非硬编码 `@app`/`@router`。

**[Pydantic model 嵌套复杂]** → 嵌套 model、泛型（`List[Model]`、`Optional[Model]`）增加解析难度。缓解：本轮仅检测直接类型引用和简单嵌套，复杂场景标记为 UNCERTAIN 交由 Layer 2。

**[仅支持 FastAPI]** → Django Ninja、Flask-RESTX 等框架有类似问题但本轮不覆盖。缓解：架构设计为可扩展——后续增加新框架只需在 4d/4e 中增加对应的 Grep 模式和检查规则。
