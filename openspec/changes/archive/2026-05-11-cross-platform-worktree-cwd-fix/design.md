## Context

当前项目包含三个涉及 git worktree 操作的 skill：

1. **`new-worktree-apply`** — 创建 worktree 并实施 OpenSpec change
2. **`merge-worktree-return`** — 将 worktree 改动合并回主分支并退出
3. **`parall-new-worktree-apply`** — 并行执行多个 worktree apply

这些 skill 通过符号链接安装到 Claude Code（`~/.claude/skills/`）和 Codex CLI（`~/.codex/skills/`）。

**核心问题**：`new-worktree-apply` Step 5 使用 Claude Code 内置的 `EnterWorktree` 工具，`merge-worktree-return` Step 7 使用 `ExitWorktree`。这两个工具仅 Claude Code 可用。Codex CLI 中没有这些工具，agent 会退回到 `git worktree add`（通过 Bash），但 Bash 不会切换会话 CWD，导致后续操作在错误目录执行。

**平台差异**：

| 行为 | Claude Code | Codex CLI |
|------|-------------|-----------|
| `EnterWorktree` 工具 | 内置可用，自动切换 CWD | 不存在 |
| `ExitWorktree` 工具 | 内置可用，自动切换 CWD | 不存在 |
| `allowed-tools` 字段 | 生效，控制 Bash 权限 | 忽略 |
| 创建 worktree | `EnterWorktree` 或 `git worktree add` | 只能用 `git worktree add` + `cd` |
| 退出 worktree | `ExitWorktree` | `cd <main-dir>` + `git worktree remove` |

## Goals / Non-Goals

**Goals:**

- 让 worktree 操作在 Claude Code 和 Codex CLI 中都能正确执行
- 保持 Claude Code 环境下的最优路径（使用内置工具）
- 为非 Claude Code 环境提供等效的 fallback 方案
- 加入 CWD 验证步骤，确保目录切换成功

**Non-Goals:**

- 不改变 `parall-new-worktree-apply` 的并行调度逻辑
- 不引入新的外部依赖
- 不修改 `allowed-tools` 声明（Codex 忽略此字段，Claude Code 需要保持）
- 不修改 `setup-skills-env.py` 安装脚本

## Decisions

### Decision 1: 平台检测方式 — 指令式而非探测式

**选择**：在 Skill 指令文本中直接写出条件分支，而非运行时探测。

```markdown
**Claude Code 环境**: 使用 EnterWorktree 工具（自动切换 CWD）。
**其他环境（Codex 等）**: 使用 `git worktree add` + `cd` 切换到 worktree 目录。
判断方式：EnterWorktree 工具是否可用。
```

**理由**：Skill 是自然语言指令，agent 本身能感知当前环境有哪些工具可用。写清楚两条路径 + 判断依据即可，无需复杂的运行时检测脚本。

**备选方案**：用 Bash 运行时检测（如 `which claude-code`），但不可靠且增加复杂度。

### Decision 2: CWD 验证 — 切换后必须校验

**选择**：在每次 CWD 切换操作后增加验证步骤：

```bash
pwd
git branch --show-current
```

若 `pwd` 不在预期目录，或 `git branch --show-current` 不显示目标分支，则报错停止。

**理由**：这是防止 CWD 未切换问题再次发生的最后一道防线，且开销极小。

### Decision 3: merge-worktree-return 的退出路径

**选择**：Claude Code 用 `ExitWorktree`，其他环境用 `git worktree remove <worktree-path>`。

**理由**：Step 6 已通过 `cd <MAIN_DIR>` 切回主目录并完成合并验证，Step 7 的 `ExitWorktree` 仅做 worktree 目录清理。非 Claude Code 环境只需等效的 `git worktree remove` 即可，无需额外 CWD 切换。

### Decision 4: parall-new-worktree-apply 的 Agent prompt 适配

**选择**：在 Agent spawn prompt 的步骤 1 中加入平台适配指引。

**理由**：subagent 同样可能在不同平台上运行。在 prompt 中明确指出两条路径，确保 subagent 不会在错误目录操作。

## Risks / Trade-offs

- **[Agent 可能忽略条件分支]** → 用强制措辞（"MUST"/"禁止"）加强约束，并在 CWD 验证步骤作为兜底
- **[git worktree add 路径的目录位置可能不同]** → 使用与 `EnterWorktree` 一致的 `.claude/worktrees/<name>/` 路径模式，确保行为一致
- **[Codex 的 cd 命令可能不持久]** → Codex 中每条 Bash 命令可能需要独立 cd，或在同一命令链中执行 cd + 后续操作。在指令中注明这一点
