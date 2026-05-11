## Why

当前 `setup-iterm2-claude-notify.py` 安装出来的通知链路同时包含两种机制：

1. `BellTrigger` 与运行时脚本 `ring_bell()` 会产生 `bell` 类通知
2. iTerm2 / Codex 的终端通知能力会产生 `notify` 类通知

这会在 macOS 通知中心里为同一窗口事件同时出现 `bell` 和 `notify`，造成重复提醒。与此同时，现有实现还有两个结构性问题：

- Claude Code 的 hooks 虽然已具备结构化事件入口，但当前 helper 仍只会发 BEL，不会发 iTerm2 原生通知
- Codex 当前被接到顶层 `notify` 外部命令，而 Codex TUI 官方已支持更合适的 `tui.notifications` + `notification_method = "osc9"` 路径，并且覆盖 approval prompts 与 completed turns

如果要实现“Claude Code 和 Codex 都只保留 notify，不要 bell”，就必须把现有 Bell 方案整体切换为 iTerm2 原生通知方案，并把 tmux 兼容作为正式需求纳入设计。

## What Changes

- 将统一通知目标调整为“只保留 iTerm2 notify，不再依赖 bell”
- 将 Claude Code 的运行时 helper 从发送 BEL 改为发送 iTerm2 `OSC 9` 通知
- 将 Codex 从顶层 `notify` 外部命令迁移为 TUI 原生通知配置：
  - `tui.notifications = true`
  - `tui.notification_method = "osc9"`
  - `tui.notification_condition` 明确受管配置策略
- 移除由本工具管理的 `BellTrigger`、BEL 输出以及 bell 相关 profile 改写
- 为 Claude helper 增加 tmux passthrough，确保 iTerm2 内运行 tmux 时通知仍然有效
- 更新安装、检查、卸载逻辑，使其围绕“notify-only + tmux-aware”目标工作

## Capabilities

### New Capabilities

- `iterm2-notify-only-delivery`: 统一通过 iTerm2 原生通知投递 Claude Code 与 Codex 的提醒，并禁止受管 bell 提醒链路
- `tmux-aware-agent-notifications`: 在 iTerm2 内运行 tmux 时，通知链路仍可通过 passthrough 到达外层 iTerm2
- `managed-notification-mode-migration`: 将既有 Bell/BellTrigger/Codex notify 配置受管迁移为 notify-only 配置，并支持检查与卸载

## Impact

- 修改 `setup-iterm2-claude-notify.py`
- 修改 `agent-notify-runtime.py`
- 可能更新 `README.md` 的安装说明、行为说明与 tmux 说明
- 安装时会受管更新以下用户本地配置：
  - `~/Library/Preferences/com.googlecode.iterm2.plist`
  - `~/.claude/settings.json`
  - `~/.codex/config.toml`
- 卸载时仅移除本工具写入的 notify-only 配置，不移除用户自己的非受管通知配置
- 本提案将替换当前“bell + notify 并存”的受管行为定义
