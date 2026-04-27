## Why

当前受管 Claude 通知链路已经移除了 `Notification(idle_prompt)`，并把完成提醒统一收敛到 `Stop`。这解决了“完成后 60 秒再次提醒”的重复问题，但仍存在一个新的误报场景：

- 用户在 Claude Code 提示输入状态下直接执行 `/exit`
- Claude 仍可能先触发一次 `Stop`
- 当前 `agent-notify` 会把这次 `Stop` 无条件当作“正常任务完成”并发出通知

从用户体验上看，这条通知并不是“任务完成提醒”，而是“会话退出前的尾声事件”。如果用户的目标是安静退出 Claude，会在 `/exit` 时收到一条完成提醒，属于误通知。

此外，当前 helper 对前台焦点没有做任何判断。结果是：

- 如果 Claude 所在的 iTerm2 session 正是用户当前正在使用的焦点 session
- 任务完成后仍会弹出系统通知

这对多窗口重度用户不合理。用户的真实需求不是“只要 iTerm2 在前台就不提醒”，而是：

- 当前正在操作的那个 iTerm2 session 不提醒
- 同一个 iTerm2 app 下其他后台窗口、其他 tab、其他 split pane 的完成事件仍然要提醒

## What Changes

- 为 Claude 受管通知链路增加“退出抑制”语义，使 `/exit` 触发的退出流程不会产生完成提醒
- 为 Claude 受管通知链路增加“焦点 session 抑制”语义：当前正在被用户操作的 iTerm2 session 完成时不提醒，但其他非焦点 session 仍提醒
- 在安装器中增加 Claude `SessionEnd` 受管 hook，用于识别退出原因并写入退出状态
- 在运行时 helper 中增加 Claude 会话级退出抑制状态，以及基于 iTerm2 焦点 session tty 的精确前台抑制判断
- 保持正常 `Stop` 完成提醒与 `Notification(permission_prompt)` 权限提醒不变
- 扩展检查输出，显式报告 `SessionEnd` 受管 hook 是否已安装

## Capabilities

### Modified Capabilities

- `agent-completion-notifications`: Claude 的完成提醒需要在“正常完成”与“用户退出会话”之间做区分，`/exit` 场景不得触发完成提醒
- `agent-completion-notifications`: Claude 的完成提醒还需要区分“当前焦点 session 完成”与“其他后台 session 完成”；仅前者应被抑制
- `managed-notification-config-merge`: Claude hooks 的受管合并逻辑需要新增 `SessionEnd`，并在检查模式中报告其安装状态

## Impact

- 修改 `setup-iterm2-claude-notify.py`
- 修改 `agent-notify-runtime.py`
- 可能更新 `README.md` 中关于 Claude 完成提醒的边界说明
- 重新安装后会受管调整 `~/.claude/settings.json` 中的 Claude hooks
- 该提案不改变 Codex 通知路径，也不尝试处理非受管 Claude hooks
- 该提案默认采用“精确焦点 session 抑制”，不会用“iTerm2 app 在前台就全部 suppress”的粗粒度策略
