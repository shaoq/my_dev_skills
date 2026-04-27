## Context

当前仓库已有 `setup-iterm2-claude-notify.py`，它通过修改 iTerm2 的 plist，在所有 Profile 上安装 Trigger，并设置 `Flashing Bell=True`、`Silence Bell=True`。该脚本目前只处理“终端出现确认提示时如何提醒”，没有处理“agent 一轮任务结束后如何提醒”。

经过 explore，可确认：

- Claude Code 已存在可用的 hooks 入口：`Stop`、`Notification(permission_prompt)`、`Notification(idle_prompt)`
- Codex 已存在可用的完成提醒入口：`notify`
- Codex 当前文档也提供 `tui.notifications`，但首版若直接合并 `tui` 表，会显著增加 TOML 合并复杂度与破坏用户现有配置的风险

因此本提案需要把审批提醒与完成提醒拆成两条机制，并优先选择最小侵入的配置写入方案。

## Goals / Non-Goals

**Goals:**

- 保留当前已生效的 Claude Trigger 规则，不做替换或重写
- 为 Codex 增量追加审批提示匹配
- 新增 Claude 与 Codex 的完成提醒安装能力
- 为三类配置实现受管、幂等、可卸载的合并策略
- 让“审批提醒”和“完成提醒”在架构上分层，避免继续依赖单一 regex 方案

**Non-Goals:**

- 首版不重写现有 Trigger 命名、tag、通知文案
- 首版不依赖 Codex `tui.notifications` 作为主路径
- 首版不尝试拦截 Codex 的全部审批事件到 `notify`
- 不修改用户现有的非受管 Claude hooks、Codex 其他配置项、iTerm2 非本脚本 Trigger

## Decisions

### Decision 1: 现有 Claude Trigger 规则完全保留，仅做追加

**选择**：保留 `TRIGGER_PATTERNS` 中已有 3 条规则不变，只追加 Codex 审批提示规则。

**理由**：用户已经明确说明当前 Claude 规则在本机生效。首版升级必须向后兼容，而不是重写正则。

### Decision 2: 审批提醒继续由 iTerm2 Trigger 负责，完成提醒改走原生事件

**选择**：

- 审批提醒：iTerm2 Trigger
- 完成提醒：Claude hooks + Codex `notify`

**理由**：审批类事件通常已有稳定终端文本；完成类事件则更适合 lifecycle/hook 机制，不应继续主要依赖文本匹配。

### Decision 3: 引入统一运行时通知脚本

**选择**：新增统一通知脚本，Claude 与 Codex 都调用它，而不是分别写两套 `osascript` / `bell` 命令。

**理由**：

- 降低两套配置重复维护成本
- 统一去重、节流、标题文案和 BEL 行为
- 后续若需要扩展更多事件类型，只改一个脚本

### Decision 4: 统一通知脚本安装到稳定用户路径

**选择**：安装器将运行时通知脚本写入稳定的用户路径（如 `~/.local/bin/...`），并让 Claude/Codex 配置引用该稳定路径。

**替代方案**：

- 直接引用仓库绝对路径

**理由**：仓库路径可能变化。运行时脚本应独立于 repo 位置，否则移动仓库后用户配置会失效。

### Decision 5: Codex 首版只接入 `notify`，不强依赖 `tui.notifications`

**选择**：Codex 完成提醒首版采用 `notify` 调用统一脚本。统一脚本自身负责系统通知与 BEL 输出。

**替代方案**：

- 同时写入 `tui.notifications`
- 直接依赖 `tui.notification_method = "bel"`

**理由**：

- `notify` 已能覆盖 completed turn
- 合并一个顶层 `notify` 配置比修改 `[tui]` 表更安全
- 可以减少对现有 `config.toml` 结构的破坏风险

### Decision 6: Claude 使用 `Stop` + `Notification` 双入口

**选择**：

- `Stop` -> 即时完成提醒
- `Notification(permission_prompt)` -> 权限提醒
- `Notification(idle_prompt)` -> 空闲提醒

**理由**：这三个事件和用户需求一一对应，且由 Claude 官方明确支持。

### Decision 7: 配置写入必须是“受管合并”，卸载必须是“受管移除”

**选择**：

- iTerm2：继续以 `SCRIPT_TAG` 识别受管 Trigger
- Claude：受管 hooks 命令带固定标识参数，便于识别/移除
- Codex：受管 `notify` 命令带固定标识参数，便于识别/移除

**理由**：不能像当前 `remove_triggers()` 那样对未来所有配置做一刀切恢复。升级后必须只处理本工具管理的条目。

## Architecture

### 1. iTerm2 Trigger 层

负责审批类提醒：

- 保留现有 Claude 规则
- 追加 Codex 审批规则
- 继续触发 iTerm2 Notification + Bell

### 2. 统一运行时通知层

统一脚本负责：

- 接收来源：Claude hook / Codex notify
- 解析事件类型：`approval_needed` / `turn_completed` / `idle_waiting`
- 执行提醒动作：
  - macOS 通知
  - BEL（用于 iTerm2 tab 闪烁）
  - 可选的简短 stdout/stderr 说明（如有必要）

### 3. 配置安装层

安装器负责：

- 安装/更新 iTerm2 Trigger
- 安装统一通知脚本
- 合并 Claude hooks
- 合并 Codex `notify`
- 提供 `--check` 和 `--remove`

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| Codex `notify` 只覆盖 completed turn，不覆盖审批 | Codex 审批仍需依赖 Trigger | 将审批和完成提醒明确分层 |
| 统一脚本安装路径失效或不可执行 | Claude/Codex 运行时提醒失效 | 安装器检查可执行位，`--check` 验证路径 |
| `~/.codex/config.toml` 合并不当破坏用户配置 | 中高风险 | 首版只处理 `notify` 顶层项，避免广泛改写 `[tui]` |
| `~/.claude/settings.json` 已有 hooks | 覆盖风险 | 仅合并指定事件下的受管命令，不覆盖非受管 hooks |
| 当前卸载逻辑会重置 Bell 设置 | 可能影响用户原配置 | 升级时将 Bell 恢复策略改为“仅恢复本工具曾改动过的项”或记录前值 |

## Open Questions

- 统一通知脚本的最终安装路径是否固定为 `~/.local/bin/agent-notify`，还是使用更具体的工具名
- 升级时是否要为 iTerm2 Bell 设置记录前值，以实现更精细的卸载恢复
- `--check` 是否只检查存在性，还是要做一次完整端到端 dry-run 校验
