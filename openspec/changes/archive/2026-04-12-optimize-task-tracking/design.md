## Context

当前 `new-worktree-apply` 和 `parall-new-worktree-apply` 两个 skill 在 worktree 中执行 `opsx:apply` 时存在 task 状态丢失问题。根本原因：`.gitignore` 包含 `openspec/`，导致 worktree 中 `opsx:apply` 对 `tasks.md` 的 `[ ]→[x]` 标记被 git 忽略，`git add -A` 不会将其加入暂存区，`git merge` 无法传播变更，worktree 退出后标记永久丢失。

当前流程：
```
worktree 创建 → opsx:apply (标记 tasks.md) → git add -A (跳过 .gitignore) → merge → ExitWorktree (删除 worktree)
结果: main 上的 tasks.md 永远是全 [ ] 状态
```

两个 skill 都缺少：
1. apply 前对 OpenSpec artifact 完整性的校验
2. apply 后对 task 标记准确性的验证与补救
3. 绕过 .gitignore 将 tasks.md 纳入 git 跟踪的机制

## Goals / Non-Goals

**Goals:**
- 确保 `opsx:apply` 执行后 tasks.md 的 `[x]` 标记能随 worktree merge 回到 main
- apply 前校验 OpenSpec artifacts（proposal/design/specs/tasks）齐全且 status 为 done
- apply 后验证 task 标记准确性，对漏标任务自动补标记
- `parall-new-worktree-apply` 的并行 Agent 也具备同样的 task 标记保障
- 不修改 `.gitignore`，通过 `git add -f` 绕过

**Non-Goals:**
- 不修改 `.gitignore`（保持 openspec/ 被忽略的现状）
- 不修改 `openspec-apply-change` skill（它已正确标记 [x]，问题在传播）
- 不修改 `merge-worktree-return` skill（合并逻辑本身没问题，是 git 跟踪的问题）
- 不处理 openspec/ 下除 tasks.md 外的其他文件跟踪

## Decisions

### 1. 使用 `git add -f` 绕过 .gitignore

**选择**: `git add -f openspec/changes/<name>/tasks.md`
**备选**: 修改 .gitignore 移除 `openspec/`；使用 `git add --force` 对整个 openspec/ 目录

**理由**: `git add -f` 只 force-add tasks.md 一个文件，精准可控。修改 .gitignore 影响范围大，会将所有 openspec 文件纳入版本控制，可能包含大量迭代过程的临时文件。只跟踪 tasks.md 是最小干预原则。

### 2. Post-apply 验证策略：基于文件存在性检测

**选择**: 解析 tasks.md 中每个 `[ ]` task 的描述，匹配产出文件路径，检查文件是否存在
**备选**: 完全信任 opsx:apply 的标记（不验证）；要求用户手动确认

**理由**: opsx:apply 理论上会标记每个完成的 task，但实际执行中可能因中断、错误跳过等原因漏标。基于文件存在性的自动检测可以补标记大部分情况，减少人工干预。对于无法自动判断的 task，保留 `[ ]` 状态由用户后续确认。

### 3. Task 描述解析规则

**选择**: 用正则从 task 描述中提取文件路径模式，包括：
- 反引号内的路径：`` `xxx/SKILL.md` `` → 检查该路径
- "创建 xxx" → 检查目录或文件
- "实现 xxx 功能" → 检查关键词 grep
- "编写 frontmatter" → 检查对应文件中 frontmatter 存在

**备选**: 只做全量 force-add + 简单 grep 检测

**理由**: 结构化解析更准确，减少误标记。但规则不宜过于复杂，保持可维护性。

### 4. parall-new-worktree-apply 的修改方式

**选择**: 修改 Agent prompt 增加 force-add + post-verify 指令，合并后主进程再做一次验证
**备选**: 只修改 Agent prompt；只修改合并后验证

**理由**: Agent 在 worktree 中执行 force-add 确保变更被 commit；合并后主进程再验证是双重保险，防止 merge 冲突导致 tasks.md 丢失。

## Risks / Trade-offs

- **[force-add 后 tasks.md 成为 tracked file]** → 后续正常 `git add -A` 会包含它，这是期望行为。如果未来需要停止跟踪，需 `git rm --cached`。
- **[自动补标记可能误标]** → 匹配规则基于文件存在性，如果文件被创建但内容不完整可能误标。缓解：标记报告明确列出自动标记的项，用户可审查。
- **[parall Agent 可能不理解 force-add 指令]** → Agent prompt 需要明确写出完整命令，不依赖理解能力。
- **[merge 冲突可能导致 tasks.md 变更丢失]** → 合并后主进程验证步骤作为兜底，检测到丢失时重新标记。
