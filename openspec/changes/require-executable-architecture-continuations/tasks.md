## 1. RED 契约测试

- [x] 1.1 为 orphaned `in_progress`、普通 ARCH-CONTROL 自 mention 和未入队 handoff 添加失败 fixtures/assertions
- [x] 1.2 为有效 cross-member handoff、独立 self-handoff、single-consumption reconciliation 和 fail-closed 状态添加通过 fixtures/assertions
- [x] 1.3 运行 targeted contract test，确认旧 Skill 缺少 continuation contract 时失败

## 2. Portable core

- [x] 2.1 在 `architecture-design-workflow` 增加平台无关 `execution_continuation_v1` 字段和完成门禁
- [x] 2.2 更新 workflow mandate/control template，禁止用 Next Owner 文字替代 accepted/active evidence
- [x] 2.3 扩展 core safety contract，证明 standalone profile 不依赖 Multica required fields

## 3. Multica adapter

- [x] 3.1 增加独立 `multica_execution_handoff_v1` reference 和 manifest planned write/postcondition
- [x] 3.2 实施 cross-member 与 self-handoff 的准确 mention、唯一 ID、single-consumption 和 task readback 规则
- [x] 3.3 更新 status projection，禁止无 accepted/active task 的 orphaned `in_progress + WAIT_REASON=none`

## 4. 验证与同步准备

- [x] 4.1 运行 targeted/full unit tests、architecture workflow safety 和两个 Skill quick validation
- [x] 4.2 运行 OpenSpec strict validation、`git diff --check` 与 GitNexus change analysis
- [x] 4.3 输出可供既有 Multica Skill overwrite 同步和 readback 的 package
