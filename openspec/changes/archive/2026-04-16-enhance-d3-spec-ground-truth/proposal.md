## Why

`verify-impl-consistency` skill 的 D3 维度（Tests ↔ Code）当前只检查测试是否引用了存在的代码，不检查测试断言是否验证了 spec 期望的行为。当代码有 bug 且测试照着 bug 写时，D3 不会报告任何问题——形成"代码错、测试也错、但两者一致"的盲区。

需要新增：当 spec 存在时，以 spec 为 ground truth，交叉验证测试断言是否与 spec 期望一致，而不是仅与代码一致。

## What Changes

- D3 Step 5c（场景覆盖评估）增加"断言 vs spec 期望值"对比逻辑
- 从 spec 的 WHEN/THEN 场景中提取可量化的期望值（状态码、返回字段、错误消息等）
- 将测试文件中的实际断言与 spec 期望值对比，报告偏离
- 无 spec 时保持当前行为不变（仅做存在性检查）

## Capabilities

### New Capabilities

（无）

### Modified Capabilities

- `test-code-consistency`: 增加以 spec 为 ground truth 的断言验证：当 spec 存在时，对比测试断言与 spec 期望值，而非仅对比测试与代码

## Impact

- `verify-impl-consistency/SKILL.md` — D3 Step 5c 增强逻辑，Step 5a 增加期望值提取
- 不影响 D1、D2 维度的现有逻辑
- 不影响无 spec 项目的检查结果
