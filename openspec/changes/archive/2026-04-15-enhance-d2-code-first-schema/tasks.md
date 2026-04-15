## 1. D2 入口守卫条件修改

- [x] 1.1 修改 SKILL.md Step 4 开头的守卫逻辑：从 `if SCHEMA_FILES empty → skip` 变更为三路分支（有 schema 文件 → 4a-4c；无 schema 但 TECH_STACK 含 fastapi → 4d-4f；否则 → skip）
- [x] 1.2 更新 Step 4 的说明文字，反映三种模式的存在

## 2. Step 4d — Pydantic Model 注册表构建

- [x] 2.1 在 SKILL.md 添加 4d 子步骤：使用 Grep 扫描所有 `class \w+\(.*BaseModel.*\):` 定义，收集 model name 和 source file
- [x] 2.2 为每个 model 读取文件内容，提取字段定义（`field_name: type = Field(...)` 或裸字段 `field_name: type`）
- [x] 2.3 提取 `Field()` 参数：description、examples、ge/gt/lt/le、min_length/max_length、pattern
- [x] 2.4 处理嵌套类型引用（`List[X]`、`Optional[X]`、`Dict[str, X]`）提取内部 model 引用
- [x] 2.5 构建 `MODEL_REGISTRY` 结构体说明（model_name, file, fields[], nested_refs[]）

## 3. Step 4e — 路由元数据提取与一致性检查

- [x] 3.1 添加 Grep 模式扫描 FastAPI 路由装饰器：`@\w+\.(get|post|put|delete|patch)\(.*\)` 及 `add_api_route`
- [x] 3.2 从装饰器提取元数据：HTTP method、URL path、response_model、status_code、responses、tags、summary、description
- [x] 3.3 从 handler 函数提取返回类型注解（`-> Type`）和 docstring
- [x] 3.4 实现检查：无 response_model 且无返回类型注解 → WARNING
- [x] 3.5 实现检查：status_code 为 204/304 搭配非空 response_model → ERROR
- [x] 3.6 实现检查：handler 中 raise HTTPException(status_code=N) 但 responses 未含 N → WARNING
- [x] 3.7 实现检查：response_model_include/exclude/exclude_unset 参数 → WARNING（schema 将失真）
- [x] 3.8 实现检查：无 tags → INFO、无 summary/description 且无 docstring → INFO

## 4. Step 4f — Pydantic Model 质量检查

- [x] 4.1 实现检查：Field() 缺少 description → INFO
- [x] 4.2 实现检查：Field() 缺少 examples → INFO
- [x] 4.3 实现检查：字段类型引用不存在于 MODEL_REGISTRY 或非内置类型 → WARNING
- [x] 4.4 实现检查：model 间循环依赖检测（A→B→A） → WARNING

## 5. 报告格式更新

- [x] 5.1 在 Step 7 报告模板中确保 code-first 模式的发现项能正确归入 D2 维度输出
- [x] 5.2 在 D2 摘要中标注检查模式（schema-file / code-first）以便用户理解上下文

## 6. 验证

- [x] 6.1 对照 code-first-schema-analysis spec 中的所有 Scenario 逐一验证 SKILL.md 中的指令覆盖度
- [x] 6.2 对照 schema-api-consistency delta spec 验证守卫条件修改的正确性
- [x] 6.3 通读修改后的完整 SKILL.md，确认无逻辑断裂或重复
