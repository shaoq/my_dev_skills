## Why

`check-changes-completed` 和 `archived-all-completed-changes` 两个 skill 有 ~80% 逻辑重叠（前置检查、扫描、D1/D3/D4 三维检查、报告表格、阻塞原因、归档三选项）。`archived-all-completed-changes` 本质上是 `check-changes-completed` 的子集（少了 D2 artifacts 检查），加上一个归档后汇总表。维护两份近乎相同的逻辑会导致漂移风险和维护负担。同时 `check-changes-completed` 内嵌的归档引导步骤模糊了职责边界——诊断工具不应承担执行动作。

## What Changes

- **BREAKING**: 从 `check-changes-completed` 删除归档引导步骤（Step 6），使其成为纯诊断工具
- 删除 `archived-all-completed-changes/SKILL.md`，该 skill 完全冗余
- 归档动作由用户根据诊断报告自行调用 `opsx:archive` 完成

## Capabilities

### New Capabilities
（无）

### Modified Capabilities
- `check-changes-completed`: 移除归档引导步骤，强化纯诊断定位，在报告末尾提示用户使用 `opsx:archive` 归档

## Impact

- 修改文件：`check-changes-completed/SKILL.md`（删除 Step 6 归档引导，调整结尾提示）
- 删除文件：`archived-all-completed-changes/SKILL.md`
- 依赖关系不变：`opsx:archive` 独立可用
