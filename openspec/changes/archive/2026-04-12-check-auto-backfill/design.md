## Context

`check-changes-completed` 当前是纯只读诊断工具，检测到 D3(代码落地)✓ 但 D1(Tasks)✗ 的矛盾时，只报告阻塞原因。`new-worktree-apply` 已有 4规则解析器（反引号路径、目录创建、frontmatter、实现关键词），在 post-apply 阶段执行补标记。但该逻辑仅在 worktree apply 流程中运行，代码通过其他方式完成或 apply 流程中补标记失败时，无兜底机制。

当前 `check-changes-completed/SKILL.md` 的 Guardrail 明确写 "Never modify any change files — this is a read-only check"，需要放宽此约束。

## Goals / Non-Goals

**Goals:**
- 在 D3✓+D1✗ 矛盾时，自动或半自动将漏标 tasks 补标记为 `[x]`
- 分级策略：高置信度自动标记 + 低置信度确认后标记
- 保持最多 1 次用户交互的简洁体验
- 与现有 `git add -f` force-add 模式一致，确保 tasks.md 变更被 git 跟踪

**Non-Goals:**
- 不重构或修改 `new-worktree-apply` 的补标记逻辑
- 不增加对 D3 未通过的 change 的任何修改能力
- 不修改其他 skill
- 不处理 tasks.md 文件不存在的 change

## Decisions

### D1: 补标记逻辑复用 4规则解析器

**决策**: 直接在 `check-changes-completed/SKILL.md` 中内联 4规则解析逻辑（反引号路径、目录创建、frontmatter、实现关键词），与 `new-worktree-apply` Step 9 保持一致。

**理由**: SKILL.md 是 prompt 而非代码，无法共享模块。内联复用是最直接的方式，且逻辑稳定不会频繁变化。

**替代方案**: 让 `check-changes-completed` 调用 `new-worktree-apply` 的补标记步骤 → 两个 skill 职责耦合，不符合独立诊断工具的定位。

### D2: 分级策略的具体实现

**决策**:
- **第一级（高置信度）**: 4规则匹配到明确文件/目录路径且磁盘存在 → 自动标记为 `[x]`，无需确认
- **第二级（兜底）**: D3 完全通过（文件存在 + git commit 有记录）但仍有未标记项 → 一次性 AskUserQuestion 展示残余 `[ ]` 列表，用户确认后全部标记

**理由**: 第一级的文件路径匹配是确定性验证，无需人工干预；第二级缺少路径锚点，需要用户判断。最多 1 次交互保持流程简洁。

### D3: 补标记的触发时机

**决策**: 在 Step 4（汇总表格输出）之后、Step 5（阻塞原因）之前执行补标记。补标记完成后重新统计 D1，更新表格中的 Tasks 列。

**理由**: 先补标记再报告阻塞原因，使阻塞原因反映补标记后的真实状态，避免"刚报告完阻塞原因又发现可以自动修复"的冗余。

### D4: git commit 策略

**决策**: 对所有被补标记的 change 执行一次合并 commit：`git add -f openspec/changes/*/tasks.md` + `git commit -m "fix: auto-backfill task markers (N changes)"`。

**理由**: 每个改一行就 commit 太碎片化。一次性 commit 所有补标记更干净。使用 `git add -f` 绕过 `.gitignore` 中 `openspec/` 的排除规则。

**替代方案**: 每个 change 单独 commit → 过于冗余，且 check 流程不是按 change 逐个执行的。

## Risks / Trade-offs

| Risk | Mitigation |
|------|-----------|
| 第一级 4规则可能误标（文件存在但内容不完整） | tasks.md 只是进度跟踪，不影响代码正确性；误标风险低 |
| 第二级过度标记（D3 通过不等于每个 task 都完成） | 必须用户确认才执行，用户有最终决定权 |
| 角色变化：从纯只读变为可写，可能违背用户预期 | 更新 description 和 Guardrail 明确说明；D3✓ 是严格前提 |
| 内联 4规则逻辑导致与 new-worktree-apply 重复 | 逻辑稳定不常变，重复可接受；若未来频繁变化可考虑抽取 |
