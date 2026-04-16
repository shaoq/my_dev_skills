## 1. Step 5d 框架 — Spec-grounded 断言验证

- [x] 1.1 在 `verify-impl-consistency/SKILL.md` D3 Step 5c 之后新增 Step 5d 标题和前置条件：当 spec 文件包含 WHEN/THEN 场景时执行，否则 skip 并输出 informational note
- [x] 1.2 编写 Step 5d 整体流程描述：提取 spec 期望值 → 匹配测试断言 → 分级报告

## 2. Spec 期望值提取逻辑

- [x] 2.1 编写 THEN 子句结构化提取规则：状态码模式 `returns <N>` / `返回 <N>` → expected_status
- [x] 2.2 编写返回字段提取规则：`returns {field1, field2}` / `返回 {字段1, 字段2}` → expected_fields
- [x] 2.3 编写错误类型提取规则：`throws <Error>` / `raises <Exception>` → expected_error
- [x] 2.4 编写回退逻辑：无法结构化提取的 THEN 文本 → 传递给 Layer 2 语义分析

## 3. 断言匹配与偏离检测

- [x] 3.1 编写测试断言与 expected_status 对比逻辑：匹配 → ALIGNED，矛盾 → CRITICAL
- [x] 3.2 编写测试断言与 expected_fields 对比逻辑：全覆盖 → ALIGNED，部分覆盖 → WARNING 列出缺失字段
- [x] 3.3 编写测试断言与 expected_error 对比逻辑：匹配 → ALIGNED，不匹配 → CRITICAL
- [x] 3.4 编写额外断言记录逻辑：测试包含 spec 未提及的断言 → INFO（不报告为问题）

## 4. 报告输出集成

- [x] 4.1 更新 Step 7a 汇总表：D3 维度增加 "断言偏离" 计数列
- [x] 4.2 更新 Step 7b 详细发现：D3 区块新增 "Spec-grounded 断言验证" 子分类，按严重度排序
- [x] 4.3 更新 Output On Success 模板：D3 输出包含断言验证结果摘要
