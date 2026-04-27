## Context

当前仓库中的通知方案由三部分组成：

- iTerm2 Trigger：安装 `BellTrigger`
- Claude Code：通过 hooks 调用 `agent-notify`
- Codex：通过顶层 `notify` 调用 `agent-notify`

而 `agent-notify-runtime.py` 当前只会：

- 构造标题与消息
- 调用 `ring_bell()`
- 对 `codex-notify` 可选链式调用原有 `notify`

这意味着当前 helper 并不直接发 iTerm2 原生通知。只要 iTerm2 仍开启 bell 相关通知，通知中心里就会出现 `bell` 条目；如果 Codex TUI 或 iTerm2 的其他通知链路也在工作，还会同时出现 `notify` 条目。

经过 explore，可确认：

- iTerm2 支持通过 `OSC 9` 专有转义序列直接 post notification
- iTerm2 的 Notification Center alerts 可以承接这类通知
- Codex TUI 官方支持 `notification_method = "osc9"`，并把 iTerm2 识别为支持 `osc9` 的终端
- Codex 官方 `osc9` 实现已处理 tmux 下的 DCS passthrough
- iTerm2 官方文档明确指出 proprietary escape code 在 tmux/screen 中可能无法直接工作，因此 Claude helper 必须显式做 tmux passthrough，不能只输出裸 `OSC 9`

因此，本提案需要把“通知能力”从 BEL 迁移为 iTerm2 `OSC 9`，并把 tmux 兼容定义为必选能力，而不是可选优化。

## Goals / Non-Goals

**Goals:**

- Claude Code 与 Codex 都只保留 `notify`，不再产生受管 `bell`
- 两者的通知统一由 iTerm2 发出，而不是脚本直接调用 macOS 通知 API
- 在普通 iTerm2 会话与 iTerm2 内 tmux 会话中都保持通知有效
- 保持安装、检查、卸载的受管与幂等特性
- 不破坏用户原有非受管 Claude/Codex/iTerm2 配置

**Non-Goals:**

- 不为非 iTerm2 终端提供同等通知承诺
- 不接管用户自定义的其他通知工具或第三方 notifier
- 不把任意泛 CLI 提示都继续保留为通知来源
- 不在本提案中直接实现代码，仅定义迁移方案与行为边界

## Decisions

### Decision 1: 统一通知出口为 iTerm2 `OSC 9`

**选择**：Claude helper 与 Codex TUI 都以 `OSC 9` 为通知出口，由 iTerm2 投递到 Notification Center。

**理由**：

- 满足“只保留 notify，不要 bell”
- 避免脚本直接依赖 `osascript` / `terminal-notifier`
- 与 iTerm2 原生通知模型对齐

### Decision 2: Claude 与 Codex 采用不同接入层，但共享同一通知语义

**选择**：

- Claude Code：继续使用 hooks 作为事件入口，但 helper 改为发 `OSC 9`
- Codex：不再把受管 helper 作为顶层 `notify` 主路径，改用 TUI `notification_method = "osc9"`

**理由**：

- Claude 已有明确 hooks 事件：`Stop`、`Notification(permission_prompt)`、`Notification(idle_prompt)`
- Codex 官方 TUI 通知覆盖 approval prompts 与 completed turns，语义更完整
- 如果 Codex 继续只靠顶层 `notify`，只能覆盖 completed turns，不足以满足统一 notify 目标

### Decision 3: 移除 BellTrigger 与运行时 BEL

**选择**：不再安装受管 `BellTrigger`，运行时 helper 也不再发送 BEL。

**理由**：

- 这是消除重复 `bell + notify` 的必要条件
- Bell 不是目标通知形态，保留只会继续制造重复

### Decision 4: Claude helper 必须支持 tmux passthrough

**选择**：helper 在检测到 tmux 时，对 `OSC 9` 做 DCS passthrough 包装；非 tmux 时输出普通 `OSC 9`。

**理由**：

- iTerm2 官方文档对 tmux/screen 下 proprietary escape code 的行为有保留
- Codex 官方已采用这一兼容策略
- 用户已明确要求 tmux 场景也保留通知

### Decision 5: Codex 受管配置迁移到 `[tui]`

**选择**：受管写入或合并以下配置，而不是继续主依赖顶层 `notify`：

- `tui.notifications = true`
- `tui.notification_method = "osc9"`
- `tui.notification_condition = "unfocused"` 或明确采用受管默认值

**理由**：

- 官方 TUI 路径才覆盖 approval prompts + completed turns
- 与 notify-only 目标一致
- 避免 helper 与 Codex 自带 TUI 通知叠加

### Decision 6: iTerm2 仅保留 notify 相关承载，不再受管改写 bell 行为

**选择**：

- 移除受管 `BellTrigger`
- 不再强制写入 `Flashing Bell` / `Silence Bell`
- `--check` 改为检查 iTerm2 是否具备承接 notify 的必要前提，而不是检查 Bell 配置

**理由**：

- bell 已不再是方案组成部分
- 不应继续修改与 bell 相关的 profile 行为

### Decision 7: 安装器执行受管迁移，而不是叠加第二套通知系统

**选择**：安装时应识别并迁移旧版受管配置，避免 Bell 时代的条目与 Notify 时代的条目并存。

**理由**：

- 如果只追加新配置，用户仍会看到重复提醒
- 迁移必须覆盖旧受管 trigger、旧 helper 行为、旧 Codex notify 注入方式

## Architecture

### 1. Claude Code 路径

事件入口：

- `Stop`
- `Notification(permission_prompt)`
- `Notification(idle_prompt)`

事件处理：

- hooks 调用受管 helper
- helper 根据 payload 构建消息
- helper 向当前终端输出 `OSC 9`
- 在 tmux 下对 `OSC 9` 做 passthrough 包装
- 由 iTerm2 将其显示为通知中心中的 `notify`

### 2. Codex 路径

事件入口：

- Codex TUI notifications

事件处理：

- 通过 `[tui]` 配置启用通知
- 指定 `notification_method = "osc9"`
- iTerm2 直接接收 `OSC 9` 并显示 `notify`
- 在 tmux 下依赖 Codex 官方内置 passthrough

### 3. 迁移与配置管理路径

安装器负责：

- 迁移并移除旧受管 `BellTrigger`
- 停止 bell 相关 profile 改写
- 更新 Claude hooks 到 notify-only helper 模式
- 迁移 Codex 配置到 `[tui]` notify-only 模式
- 检查当前配置是否仍遗留 bell 路径
- 卸载时仅移除受管 notify-only 条目

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| Claude helper 未正确处理 tmux passthrough | tmux 内 Claude 通知丢失 | 将 tmux 支持列为强制需求并纳入验收 |
| Codex `[tui]` 表已有用户配置 | 受管合并复杂度上升 | 仅最小改写受管字段，不覆写非目标字段 |
| 用户仍保留自定义 bell 配置 | 可能继续看到 bell | `--check` 明确区分“受管 bell 已移除”与“用户自定义 bell 仍存在” |
| 非 iTerm2 终端不支持 `OSC 9` | 通知不可达 | 文档中明确该方案仅承诺 iTerm2 |
| 旧版受管 `notify` / trigger 未正确迁移 | 重复通知残留 | 安装流程增加迁移检查，`--check` 给出遗留提示 |

## Open Questions

- Codex 受管默认的 `notification_condition` 最终取 `unfocused` 还是 `always`
- `--check` 是否需要检测当前会话是否在 tmux 中，并给出 passthrough 能力说明
- README 是否需要单独增加“tmux 场景排障”小节
