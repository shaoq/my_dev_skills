## 1. Skill 基础结构

- [x] 1.1 创建 `verify-impl-consistency/SKILL.md` 文件，写入 frontmatter（name, description, argument-hint, allowed-tools），不设置 disable-model-invocation
- [x] 1.2 编写 Step 1: 项目级发现逻辑 — 扫描 docs/schema/tests/source 文件，启发式过滤文档优先级
- [x] 1.3 编写 Step 5: OpenSpec 增量检测 — openspec list 检测活跃 change，读取 proposal/design/specs

## 2. D1 — Doc ↔ Code 一致性

- [x] 2.1 编写文档声明提取逻辑 — 从 HIGH/MEDIUM 优先级文档中提取端点路径、文件路径、函数名、参数定义、配置值、技术栈声明
- [x] 2.2 编写 Layer 1 精确验证 — 对每个提取的声明用 Grep 匹配源码，分类 FOUND/NOT_FOUND/UNCERTAIN
- [x] 2.3 编写 Layer 2 语义分析 — 对 UNCERTAIN 项 Read 相关代码段，判定 ALIGNED/DRIFTED/CONFLICT
- [x] 2.4 编写 OpenSpec 增量验证 — 读取 change 的 proposal/design/specs，逐条验证声明与 git diff 范围内的代码

## 3. D2 — Schema ↔ API Code 一致性

- [x] 3.1 编写 schema 文件发现 — 扫描 OpenAPI/Swagger/Proto/GraphQL 文件
- [x] 3.2 编写 schema 端点提取 — 解析 schema 文件提取端点路径+方法、请求/响应字段+类型、状态码
- [x] 3.3 编写多语言路由匹配 — 内嵌框架路由模式参考表（Express, Fastify, NestJS, FastAPI, Flask, Django, Gin, Echo, Spring），Grep 匹配路由定义
- [x] 3.4 编写请求/响应字段对比 — Layer 1 检查字段名存在性，Layer 2 检查类型语义一致性

## 4. D3 — Tests ↔ Code 一致性

- [x] 4.1 编写测试文件发现 — 扫描 *test*/*spec* 文件和 __tests__/test/tests/ 目录
- [x] 4.2 编写测试目标提取 — 从测试文件中提取被测端点路径、函数名、预期状态码、断言值
- [x] 4.3 编写测试目标存在性验证 — Grep 验证被测端点/函数在源码中是否存在，标记孤立测试
- [x] 4.4 编写场景覆盖评估 — 从 spec.md 的 WHEN/THEN 场景评估测试覆盖情况
- [x] 4.5 编写 OpenSpec 增量测试验证 — 检查 git diff 中的测试文件覆盖 change 的 spec 场景

## 5. 报告与输出

- [x] 5.1 编写报告生成逻辑 — 概要表（维度/发现数/CRITICAL/WARNING/INFO）+ 详细发现（严重性/来源/验证过程/建议）
- [x] 5.2 编写 Output On Success 模板 — 完整诊断报告 markdown 格式
- [x] 5.3 编写 Error Output Format 模板 — Step/Reason/Recovery 格式
- [x] 5.4 编写 Guardrails — 纯诊断不修改文件、不做 pass/fail 判定、不自动修复

## 6. README 同步更新

- [x] 6.1 更新 README.md Skills 一览表 — 添加 verify-impl-consistency 行（名称、调用方式、用途、参数）
- [x] 6.2 更新 README.md 使用流程图 — 在 check-changes-completed 后添加可选的 verify-impl-consistency 步骤
- [x] 6.3 添加 README.md verify-impl-consistency 详解章节 — 核心机制、三维模型、注意事项
- [x] 6.4 更新 README.md 目录结构 — 添加 `verify-impl-consistency/SKILL.md` 条目
