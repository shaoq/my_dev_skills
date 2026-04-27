## Context

当前实现的 Claude 受管 hooks 只有：

- `Stop`
- `Notification(permission_prompt)`

helper 在处理 `Stop` 时只知道“Claude 已停止当前轮响应”，并不知道这次停止是不是用户马上执行 `/exit` 的一部分。因此只要 Claude 在退出前仍投递 `Stop`，helper 就会发送“Claude Code 已完成当前任务”通知。

Claude 官方 hooks 模型里，退出语义不在 `Stop` 上，而在 `SessionEnd` 上：

- `Stop`: 主代理完成响应时触发
- `SessionEnd`: 会话结束时触发，`reason` 可能是 `prompt_input_exit`

因此，单靠当前 `Stop` payload，无法稳定判断“这是正常完成”还是“退出前最后一次 stop”。

同时，当前 helper 只负责向当前 tty 发 `OSC 9`，没有判断“这条通知对应的 terminal session 是否正是当前 iTerm2 焦点 session”。这会带来第二类体验问题：

- 用户正在操作某个 iTerm2 窗口/标签/分屏里的 Claude
- 这个同一个焦点 session 完成后，仍然弹出系统通知

对于单窗口用户，这只是轻微多余；但对多窗口用户，这个问题不能用“iTerm2 在前台就不提醒”来粗暴解决，因为那会误伤同一 app 内其他后台 session 的真正提醒需求。

## Goals / Non-Goals

**Goals:**

- 保留正常 Claude 完成提醒
- `/exit` 退出会话时不发送完成提醒
- 当前 iTerm2 焦点 session 完成时不发送系统通知
- 同一 iTerm2 app 下其他非焦点窗口、非焦点 tab、非焦点 pane 的完成事件仍发送系统通知
- 保持现有 iTerm2 内 tmux 通知链路可用，不因焦点 session 抑制破坏后台 pane/session 的提醒
- 保留 `Notification(permission_prompt)` 权限提醒
- 保持受管安装、卸载、检查逻辑的幂等性

**Non-Goals:**

- 不处理用户自定义的非受管 Claude hooks
- 不改变 Codex 的通知行为
- 不恢复 `Notification(idle_prompt)`
- 不尝试拦截所有可能的退出方式的 UI 行为，只基于 Claude 官方 hook 语义判断
- 不采用“只要 iTerm2 在前台就全部 suppress”的粗粒度前台抑制

## Options Considered

### Option 1: 仅在 `Stop` 上做文本或时间窗判断

**结论**：拒绝。

**原因**：

- `Stop` payload 没有稳定的“这是退出造成的”字段
- 依赖消息文本、时间窗或启发式摘要很脆弱
- 容易误伤真实完成通知，或者漏掉退出误通知

### Option 2: 新增 `SessionEnd`，用退出原因回写会话状态，再由 `Stop` 读取抑制

**结论**：采纳。

**原因**：

- `SessionEnd.reason` 提供官方支持的退出语义
- 可以把“完成事件”和“退出事件”分开建模
- 与现有 helper 的 session 状态文件模型兼容

### Option 3: 新增 `UserPromptSubmit`，在用户输入 `/exit` 时预先打标

**结论**：暂不采纳。

**原因**：

- 理论上可以更早知道 `/exit`
- 但 slash command 是否始终经过 `UserPromptSubmit` 不如 `SessionEnd.reason` 明确
- 需要额外处理“用户输入了 `/exit` 但未真正结束会话”的边缘状态

### Option 4: 只要 iTerm2 app 在前台就 suppress 所有 Claude 完成通知

**结论**：拒绝。

**原因**：

- 无法区分当前正在操作的 session 与同一 app 内其他后台 session
- 多窗口、多 tab、多 pane 用户会丢失本应保留的提醒
- 与“精确抑制当前焦点 session，但保留其他 session 通知”的目标冲突

### Option 5: 基于 iTerm2 当前焦点 session 的 tty 做精确抑制

**结论**：采纳。

**原因**：

- iTerm2 AppleScript / 变量模型可以拿到当前焦点 session 的 `tty`
- Claude hook 运行时也天然知道自己正运行在哪个 tty
- 可以把抑制粒度收敛到“同一个实际焦点 session”，不误伤同 app 其他 session

## Decision

采用 **Option 2**：

- 安装器为 Claude 增加受管 `SessionEnd` hook
- helper 为 Claude 增加“最近退出”状态
- `SessionEnd(reason=prompt_input_exit)` 到来时，记录该 session 最近进入退出流程
- `Stop` 在真正发完成通知前，先检查同 session 是否已有最近退出标记；若是，则抑制该通知

并同时采用 **精确焦点 session 抑制**：

- helper 在发送 Claude 完成提醒前，查询 iTerm2 当前焦点 session 的 tty
- 只有当“当前 hook 所在 tty”与“iTerm2 当前焦点 session tty”完全一致时，才 suppress
- 如果 iTerm2 在前台，但焦点位于另一个 tty，则当前后台 session 的提醒仍然发送

## Detailed Design

### 1. Claude hooks 目标模型

安装器在 `~/.claude/settings.json` 中维护以下受管事件：

- `Stop`
- `Notification(permission_prompt)`
- `SessionEnd`

其中：

- `Stop` 继续用于正常完成提醒
- `Notification(permission_prompt)` 继续用于权限确认提醒
- `SessionEnd` 只用于退出语义识别，不直接发用户通知

焦点 session 抑制不依赖新增 hook，而是在 helper 内基于当前 tty 与 iTerm2 焦点 session 的比对完成。

### 2. SessionEnd 退出状态

当 helper 以 `claude-session-end` 模式运行时：

- 从 stdin 读取 Claude `SessionEnd` payload
- 提取 `session_id`
- 读取 `reason`

如果 `reason == prompt_input_exit`：

- 为该 `session_id` 记录 `exit_requested_at`
- 记录 `last_session_end_reason = prompt_input_exit`

如果 `reason` 是 `clear`、`logout` 或 `other`：

- 可以记录最近结束原因，供调试或后续扩展
- 默认不把它们视为“应抑制完成提醒”的退出类型，除非后续验证发现也需要覆盖

### 3. Stop 抑制规则

`Stop` 事件处理改为两阶段：

1. 读取当前 Claude session 去重/状态文件
2. 在现有重复 `Stop` 去重判断前后，增加退出抑制判断
3. 在真正发送通知前，增加焦点 session 精确抑制判断

建议规则：

- 若同一 `session_id` 最近存在 `exit_requested_at`
- 且其时间戳落在短窗口内
- 且最近退出原因是 `prompt_input_exit`
- 则当前 `Stop` 视为退出流程的一部分，直接 suppress

该短窗口只用于连接“退出”与“紧随其后的 stop”，例如 2 到 10 秒；它不用于普通完成去重。

### 4. 焦点 session 精确抑制

helper 需要在 macOS + iTerm2 环境下做一次精确查询：

- 当前前台 app 是否为 iTerm2
- iTerm2 `current window` 的 `current session` 是哪个 tty
- 该 tty 是否等于当前 hook 所属 tty

推荐数据来源：

- 当前 hook 所属 tty：`/dev/tty` 或进程关联终端设备
- iTerm2 焦点 session：通过 AppleScript 查询 `current session of current window` 的 `tty`

抑制规则：

- 若前台 app 不是 iTerm2，则不因焦点规则 suppress
- 若前台 app 是 iTerm2，但当前焦点 session tty 与本次 hook 的 tty 不同，则不 suppress
- 仅当两者完全相同，才 suppress 本次 Claude 完成通知

这保证了：

- 当前正在操作的那个 session 不打扰用户
- 同一 iTerm2 app 内其他后台窗口、后台 tab、后台 pane 的完成仍然会提醒
- 当前前台 app 若已切到其他应用，Claude 所在 iTerm2 后台 session 的完成仍然会提醒

### 5. tmux 场景要求

当前仓库的 notify-only 方案已经把 tmux 兼容视为正式能力，因此本提案不能只在“非 tmux 直接 iTerm2 session”上成立。

实现阶段至少需要验证两类场景：

- 非 tmux：普通 iTerm2 session 的 tty 焦点判定
- iTerm2 内 tmux：当前可见 pane 与后台 pane / 后台 window 的提醒区分

设计约束：

- 如果能够稳定拿到“当前 hook 所属 tty”与“iTerm2 焦点 session tty”的对应关系，则继续沿用精确比较
- 如果 tmux 场景下 tty 语义与外层 iTerm2 session 映射存在偏差，实现不得贸然采用会误吞后台通知的策略
- 在 tmux 下如果无法可靠确认“当前完成的是焦点 pane 所属会话”，应按降级原则继续提醒，而不是 suppress

### 6. 焦点查询失败时的降级策略

精确焦点抑制依赖 AppleScript / macOS Automation。实现时必须避免“查询失败导致漏提醒”。

降级原则：

- 如果 AppleScript 执行失败
- 或无法确定当前前台 app
- 或无法读取 iTerm2 焦点 session tty

则默认 **不 suppress**，继续发送通知。

也就是说：

- 允许“偶发多提醒”
- 不允许“因为判断失败而静默吞掉本该保留的后台提醒”

### 7. 顺序不确定性的处理

这个方案有一个关键前提需要显式承认：`Stop` 与 `SessionEnd` 的先后顺序未必固定。

因此设计上需要支持两种情况：

- `SessionEnd` 先到：最简单，`Stop` 直接读取到退出标记并抑制
- `Stop` 先到：helper 需要为 `Stop` 增加一个很短的延迟确认窗口，等待 `SessionEnd` 是否马上到来

建议实现思路：

- `Stop` 命中“当前无退出标记”时，不立即无脑通知
- 先等待一个很短的窗口，例如 150ms 到 500ms
- 再次读取状态文件
- 若在窗口内出现了 `prompt_input_exit` 标记，则 suppress
- 否则按正常完成通知发送

这样可以兼容事件顺序不稳定的问题，同时把正常完成通知的额外延迟控制在可接受范围内。

### 8. 状态文件扩展

现有 Claude dedup 状态文件可为每个 session 扩展如下字段：

```json
{
  "sessions": {
    "<session_id>": {
      "last_completion_at": 1710000000.0,
      "last_completion_fingerprint": "abc",
      "last_event_type": "stop",
      "exit_requested_at": 1710000001.0,
      "last_session_end_reason": "prompt_input_exit"
    }
  }
}
```

语义要求：

- `exit_requested_at` 仅表示近期收到退出信号，不应长期保留
- 状态清理逻辑需要像现有 completion 状态一样定期过期
- 退出标记应在窗口结束后自动失效，避免误伤下一轮会话

焦点 session 抑制不需要持久化复杂状态；它是发送前的即时查询。

### 9. 检查输出

`--check` 需要新增一行，显示：

- `SessionEnd: 已安装受管 hook`
- 或 `SessionEnd: 未安装受管 hook`

这样用户能快速分辨当前安装是否具备“退出不提醒”能力。

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| `Stop` 与 `SessionEnd` 顺序不稳定 | 可能仍误发或误抑制 | 为 `Stop` 增加极短延迟窗口，再次检查退出状态 |
| 抑制窗口过长 | 误伤正常完成提醒 | 把退出关联窗口控制在几百毫秒到几秒内，并仅针对同 session + `prompt_input_exit` |
| Claude 某些退出路径不用 `prompt_input_exit` | `/exit` 外的退出类型可能仍提醒 | 本提案先精确覆盖 `/exit` 主路径，其他退出原因后续再评估 |
| 用户保留非受管 hook | 仍可能出现额外提醒 | 在 proposal、README、check 文案中明确仅保证受管链路 |
| 前台判断失败 | 可能仍出现当前 session 的多余提醒 | 查询失败时降级为“继续提醒”，避免误吞后台 session 的真实提醒 |
| tmux 或复杂会话结构导致 tty 映射偏差 | 可能误判是否为焦点 session | 实现阶段需把“非 tmux / iTerm2 内 tmux”都列为验收场景 |

## Acceptance Outline

需要覆盖以下验收场景：

1. Claude 正常完成一轮任务时，仍收到一次完成提醒
2. Claude 请求权限时，仍收到权限提醒
3. 用户在提示输入状态执行 `/exit` 时，不收到完成提醒
4. 当前 iTerm2 焦点 session 完成时，不收到系统通知
5. 同一 iTerm2 app 下另一个非焦点窗口、非焦点 tab 或非焦点 pane 完成时，仍收到系统通知
6. 当前前台 app 不是 iTerm2 时，Claude 所在后台 iTerm2 session 完成后仍收到系统通知
7. iTerm2 内 tmux 场景下，当前焦点 pane 不提醒，后台 pane 或后台 window 的完成仍提醒；若无法可靠判断，则按降级策略继续提醒
8. `SessionEnd(reason=prompt_input_exit)` 到来后，helper 能在短窗口内抑制同 session 的 `Stop`
9. `--check` 能显示 `SessionEnd` 受管 hook 是否已安装
