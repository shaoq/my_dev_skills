## Why

当前受管 Claude 通知链路已经把“任务完成提醒”收敛到 `Stop`，并通过 `agent-notify` 立即发出 iTerm2 `OSC 9` 通知。但 Claude Code 自带的内建通知通道默认仍为 `preferredNotifChannel=iterm2`，因此同一会话在 60 秒未输入时还会再触发一次等待输入提醒。

这导致用户在“需要即时完成提醒”的目标下，仍然会收到一条延迟 60 秒的第二次通知。对于希望只保留即时提醒的用户，这不是补充提醒，而是重复提醒。

## What Changes

- 在受管 Claude 安装路径中增加 `preferredNotifChannel` 管理能力，将 Claude 内建通知通道显式切换为 `notifications_disabled`
- 为安装器增加该字段的受管备份与恢复语义：安装时保存原值，卸载时精确恢复
- 扩展检查输出，显式报告 Claude 当前 `preferredNotifChannel` 状态，并在未禁用时提示可能与受管即时通知重复
- 保持现有受管 `Stop`、`Notification(permission_prompt)`、`SessionEnd` hooks 不变，由 `agent-notify` 继续负责即时完成提醒与权限提醒
- 明确受管 Claude 完成提醒的单一路径语义：完成提醒应只由受管 helper 发出，不应与 Claude 内建 iTerm2 通知并存

## Capabilities

### Modified Capabilities

- `agent-completion-notifications`: Claude 的完成提醒需要保持单一路径语义；当受管即时提醒启用时，不得再由 Claude 内建通知通道补发 60 秒 idle 提醒
- `managed-notification-config-merge`: 安装器对 `~/.claude/settings.json` 的受管合并逻辑需要新增 `preferredNotifChannel` 管理、检查与恢复能力

## Impact

- 修改 `setup-iterm2-claude-notify.py`
- 可能更新 `README.md` 中关于 Claude 通知来源与行为边界的说明
- 重新安装后会受管调整 `~/.claude/settings.json` 中的 `preferredNotifChannel`
- 卸载时需要恢复安装前的 `preferredNotifChannel` 原始状态
- 该提案不改变 Codex 通知路径，也不改变现有 Claude hooks 事件组合
