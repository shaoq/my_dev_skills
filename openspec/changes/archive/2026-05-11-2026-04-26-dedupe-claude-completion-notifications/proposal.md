## Why

当前受管 Claude Code 通知方案同时安装了以下 hooks：

- `Stop`
- `Notification(permission_prompt)`
- `Notification(idle_prompt)`

这会让“本轮任务完成”和“完成后空闲等待下一条输入”落到两条提醒链路上。对用户来说，最常见的结果是：

1. Claude 完成当前任务时立即收到一次完成通知
2. 如果用户没有继续输入，约 60 秒后又收到一次 `idle_prompt` 通知

这两次通知虽然来自不同事件，但对“任务完成提醒”这个使用目标而言是重复的。当前运行时 helper 也没有 session 级状态或去重逻辑，因此无法保证“Claude 一轮任务完成只提醒一次”。

## What Changes

- 将受管 Claude hooks 的默认完成提醒模型调整为：
  - `Stop` 负责唯一的完成提醒
  - `Notification(permission_prompt)` 负责权限/确认提醒
  - 默认不再安装 `Notification(idle_prompt)` 的受管 hook
- 为运行时 helper 增加 Claude 专用的防重复状态，抑制异常重复的 `Stop` 投递，并兼容抑制遗留 `idle_prompt` 的重复提醒
- 将“升级自旧版受管配置”定义为正式迁移场景：重新安装时自动移除旧版受管 `idle_prompt` hook
- 扩展检查输出，使其能明确报告 Claude 当前是否仍存在受管 `idle_prompt` 配置

## Capabilities

### Modified Capabilities

- `agent-completion-notifications`: Claude 默认不再通过 `idle_prompt` 发送完成后空闲提醒，并要求完成场景只保留一次受管通知
- `managed-notification-config-merge`: Claude hooks 的受管合并逻辑需要支持“从旧版三事件模型迁移到新双事件模型”

## Impact

- 修改 `setup-iterm2-claude-notify.py`
- 修改 `agent-notify-runtime.py`
- 可能更新 `README.md` 的 Claude 通知行为说明
- 重新安装后会受管调整 `~/.claude/settings.json` 中的 Claude hooks
- 该提案只收紧 Claude 的受管默认通知行为，不改变 Codex 现有通知路径
