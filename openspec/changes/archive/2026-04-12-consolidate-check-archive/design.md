## Context

项目有两个高度重叠的 skill：`check-changes-completed`（4D 诊断 + 归档引导）和 `archived-all-completed-changes`（3D 诊断 + 批量归档）。两者的检查逻辑 ~80% 相同，归档流程也几乎一致。用户明确希望职责分离：诊断工具不执行归档，归档由用户自行调用 `opsx:archive`。

## Goals / Non-Goals

**Goals:**
- 将 `check-changes-completed` 简化为纯诊断工具，只负责检查和报告
- 删除冗余的 `archived-all-completed-changes` skill
- 保持清晰的职责边界：诊断 → 用户判断 → `opsx:archive`

**Non-Goals:**
- 不增强 `opsx:archive` 的功能
- 不修改其他 skill
- 不引入新的 skill 替代 `archived-all-completed-changes`

## Decisions

### D1: 删除归档引导而非抽取为独立 skill

从 `check-changes-completed` 直接删除 Step 6（归档引导三选项流程），不将其抽取为新的独立 skill。

**理由**: 归档操作已有 `opsx:archive`。用户根据诊断报告自行决定归档哪些 change，不需要中间引导层。减少 skill 数量比增加新 skill 更好。

**替代方案**: 将归档引导抽取为 `batch-archive` skill → 增加了复杂度，且 `opsx:archive` 已经足够。

### D2: 报告末尾加归档提示

在诊断报告末尾添加一行提示，引导用户使用 `opsx:archive`。

**理由**: 删除归档引导后，用户需要一个从诊断到行动的桥梁。一句提示足矣，不需要交互式引导。

### D3: 直接删除 archived-all-completed-changes 而非归档

直接删除 `archived-all-completed-changes/SKILL.md` 文件，不通过 `opsx:archive` 归档该 change。

**理由**: 该 skill 刚创建不久，未经过实际使用验证，没有保留历史的价值。直接删除更干净。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 用户习惯了在 check 后直接归档，删除引导后体验变化 | 报告末尾提供明确的 `opsx:archive` 提示 |
| 未来可能需要批量归档能力 | 可通过 `parall-new-worktree-apply` 并行调用 `opsx:archive`，或创建新 proposal |
