## Why

当前 `setup-iterm2-claude-notify.py` 只能通过 iTerm2 Trigger 匹配终端输出，为 Claude Code 的审批类提示提供提醒。这个方案有三个明显缺口：

1. 现有 Claude 规则虽然已在本机生效，但没有正式覆盖 Codex 当前版本的审批提示文案。
2. “等待用户确认”和“本轮任务已完成、等待下一条输入”是两类不同事件，但当前脚本只覆盖了前者。
3. 运行时提醒不应继续只依赖正则匹配；Claude Code 与 Codex 都有更适合的 hooks / notify 入口。

同时，本仓库现有脚本在卸载时会直接恢复 Bell 设置，未来如果继续扩展到 `~/.claude/settings.json` 与 `~/.codex/config.toml`，必须明确“仅移除本工具管理的条目，不破坏用户现有配置”。

## What Changes

- 升级 `setup-iterm2-claude-notify.py` 为统一安装器，但保留现有 Claude Trigger 规则不变
- 在 iTerm2 Trigger 层追加 Codex 当前版本的审批提示匹配规则
- 新增统一运行时通知脚本，供 Claude Code hooks 与 Codex `notify` 共用
- 为 Claude Code 安装受管 hooks：
  - `Stop` 用于即时完成提醒
  - `Notification(permission_prompt)` 用于权限提醒
  - `Notification(idle_prompt)` 用于空闲等待提醒
- 为 Codex 安装受管 `notify` 命令，用于 completed turn 的完成提醒
- 为安装、检查、卸载增加“受管配置合并”能力，仅增删本工具写入的配置

## Capabilities

### New Capabilities

- `agent-approval-notifications`: 在保留现有 Claude Trigger 规则的前提下，增量追加 Codex 审批提示匹配规则
- `agent-completion-notifications`: 通过 Claude hooks 与 Codex `notify` 安装完成提醒能力
- `managed-notification-config-merge`: 对 iTerm2、Claude、Codex 三类配置执行幂等合并与受管卸载

### Modified Capabilities

- `setup-iterm2-claude-notify.py` 从“仅安装 iTerm2 Trigger”扩展为“安装 Trigger + 运行时通知配置”

## Impact

- 修改 `setup-iterm2-claude-notify.py`
- 新增 1 个统一运行时通知脚本文件
- 可能更新 `README.md` 的安装/检查说明
- 安装时会受管更新以下用户本地配置：
  - `~/Library/Preferences/com.googlecode.iterm2.plist`
  - `~/.claude/settings.json`
  - `~/.codex/config.toml`
- 卸载时仅移除本工具管理的 Trigger、hooks、notify 配置，不覆盖用户已有其他配置
