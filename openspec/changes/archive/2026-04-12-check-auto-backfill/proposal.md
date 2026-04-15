## Why

`check-changes-completed` 是纯只读诊断工具，当检测到"代码已落地 (D3✓) 但 tasks 未标记 (D1✗)"的矛盾时，只会报告阻塞原因，不执行修复。用户需要手动编辑 tasks.md 将 `[ ]` 改为 `[x]`，这违背了自动化的初衷。现有的补标记逻辑仅存在于 `new-worktree-apply` 的 post-apply 流程中，如果代码是通过其他方式完成的，或 apply 流程中补标记失败，就没有任何兜底机制。

## What Changes

- 修改 `check-changes-completed/SKILL.md`：在 Step 5（阻塞原因）之后新增 Step 5.5（智能补标记），采用分级策略：
  - 第一级（高置信度）：复用 `new-worktree-apply` 的 4规则解析器逐项匹配，自动标记无需确认
  - 第二级（兜底）：D3 全通过后仍有残余 `[ ]` 时，一次性 AskUserQuestion 确认后标记
- 更新 Guardrail：从 "Never modify any change files" 改为允许在 D3✓+D1✗ 条件下修改 tasks.md
- 更新 skill description 反映新角色：诊断 + 修复
- 补标记后执行 `git add -f` + commit，与现有 force-add 模式一致

## Capabilities

### New Capabilities
- `smart-task-backfill`: 分级智能补标记能力 — 4规则精确匹配 + D3兜底确认，自动将代码已落地但漏标的 tasks 标记为完成

### Modified Capabilities
- `check-changes-completed`: 从纯只读诊断工具升级为诊断+修复工具，在检测到 D3✓+D1✗ 矛盾时触发补标记流程

## Impact

- 修改文件：`check-changes-completed/SKILL.md`
- 依赖：`new-worktree-apply` 的 4规则解析逻辑（复用模式，非代码依赖）、git（add -f, commit）
- 影响：`check-changes-completed` 角色从纯诊断变为诊断+修复，Skill 调用者需知晓此行为变化
