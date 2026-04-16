## Context

`verify-impl-consistency` 的 D3 维度（Tests ↔ Code）当前有三层检查：
1. 5a — 提取测试目标（端点、函数、断言值）
2. 5b — 验证测试目标在代码中存在（防孤立测试）
3. 5c — 评估 spec 场景覆盖（WHEN/THEN 是否有对应测试）

问题：5c 只检查"是否有测试覆盖该场景"，不检查"测试断言是否验证了 spec 期望的值"。当代码和测试同时偏离 spec 时，D3 不会报告。

涉及文件：
- `verify-impl-consistency/SKILL.md`（唯一需要修改的文件）

## Goals / Non-Goals

**Goals:**
- 当 spec 存在时，新增一步将测试断言与 spec 期望值对比
- 从 spec WHEN/THEN 中提取可量化的期望值（状态码、返回字段、错误类型等）
- 将测试文件中的实际断言与 spec 期望值对比，报告偏离
- 无 spec 时保持当前行为不变

**Non-Goals:**
- 不修改 D1、D2 维度的现有逻辑
- 不做 AST 级精确断言解析（Grep + Read 够用）
- 不自动修复测试或代码
- 不引入新的 spec 格式要求（复用现有 WHEN/THEN 结构）

## Decisions

### D1: 新增独立步骤 5d，而非修改 5c

**选择**: 在 5c（场景覆盖评估）之后新增 5d（Spec-grounded 断言验证）

**备选方案**: 将断言对比逻辑合并进 5c — 增加单个步骤的复杂度，且两者的关注点不同（5c 关注"有没有"，5d 关注"对不对"）

**理由**: 5c 回答"这个场景有没有测试覆盖"，5d 回答"测试是否验证了正确的期望值"。职责清晰，且 5d 只在有 spec 时执行。

### D2: 期望值提取策略 — 结构化匹配 + 回退

**选择**: 优先从 THEN 子句提取结构化期望值，回退到自然语言语义分析

**提取规则**:
- `THEN returns <N>` / `THEN 返回 <N>` → expected_status = N
- `THEN returns <Type>` / `THEN field <name> is <value>` → expected_response
- `THEN throws <Exception>` / `THEN raises <Error>` → expected_error
- 无法结构化提取时 → 交给 Layer 2 语义分析

**理由**: 大多数 spec 的 THEN 子句包含可结构化提取的期望值。回退策略确保不遗漏非标准写法。

### D3: 跳过条件 — 无 spec 或无可提取期望值

**选择**: 5d 的前置条件为 `DOC_FILES` 或 spec 文件存在且包含 WHEN/THEN 场景

**理由**: 无 spec 时没有 ground truth，无法判断"正确"行为。此时保持当前 D3 行为（仅 5a→5b→5c）完全合理。

### D4: 偏离严重度分级

| 严重度 | 条件 |
|--------|------|
| CRITICAL | 测试断言与 spec 期望直接矛盾（spec 说 201，测试断言 200） |
| WARNING | 测试断言覆盖了部分 spec 期望但遗漏了关键断言（spec 说返回 {id, name}，测试只断言了 {id}） |
| INFO | 测试断言包含了 spec 未提及的额外验证（不报告为问题，仅记录） |

**理由**: CRITICAL 表示测试验证了错误行为；WARNING 表示测试验证了部分正确行为但不够完整；INFO 是测试比 spec 更严格，不是问题。

## Risks / Trade-offs

- **[THEN 子句表达多样]** → 缓解：结构化匹配覆盖 80% 常见模式，剩余交给 Layer 2
- **[Spec 本身可能有错]** → 缓解：报告中标明 "根据 spec `<source>` 的期望"，用户可判断是 spec 还是测试的问题
- **[多 spec 来源优先级]** → 缓解：OpenSpec change spec > 项目 spec > 通用文档，取最具体的来源
