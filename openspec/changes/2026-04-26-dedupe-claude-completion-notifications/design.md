## Context

经过 explore，当前重复提醒问题并不在 iTerm2 `OSC 9` 输出层，而在 Claude hooks 的事件建模层：

- `Stop` 表示 Claude 已完成当前响应
- `Notification(permission_prompt)` 表示 Claude 需要用户确认
- `Notification(idle_prompt)` 表示 Claude 已空闲一段时间，等待用户继续输入

其中 `Stop` 和 `idle_prompt` 在“任务完成后，用户暂时没有继续输入”的场景中会先后发生。当前安装器把两者都接到统一 helper，因此同一轮任务会出现两次通知。

如果目标是“Claude Code 一轮任务完成时只会有一次通知”，则不能仅靠短时间窗节流。因为 `idle_prompt` 与 `Stop` 的间隔通常远大于普通 debounce 窗口。

## Goals / Non-Goals

**Goals:**

- 保证受管 Claude 完成提醒在默认配置下每轮任务只发一次
- 保留 `permission_prompt` 提醒能力
- 让重新安装具备迁移能力，能移除先前安装过的受管 `idle_prompt`
- 增加运行时防御逻辑，降低旧配置残留或重复投递导致的双通知风险

**Non-Goals:**

- 本提案不为 Claude 保留默认 `idle_prompt` 提醒能力
- 本提案不试图清理用户自定义的非受管 Claude hooks
- 本提案不改变 Codex 的通知策略
- 本提案不引入新的 Claude hook 事件类型，例如 `UserPromptSubmit`

## Options Considered

### Option 1: 保留 `idle_prompt`，只做时间窗去重

**结论**：拒绝。

**原因**：

- `idle_prompt` 常在 `Stop` 之后约 60 秒才触发
- 普通 3 秒、10 秒、30 秒时间窗都无法覆盖这种重复
- 若把时间窗拉得过长，又会误伤真正独立的后续通知

### Option 2: 默认移除 `idle_prompt`，并在 helper 中增加防御性去重

**结论**：采纳。

**原因**：

- 直接消除“完成通知”和“空闲提醒”语义重叠的根源
- 与“任务完成只提醒一次”的目标完全一致
- 安装器实现简单，迁移路径清晰
- helper 额外去重可覆盖异常重复投递和旧配置残留

### Option 3: 保留 `idle_prompt`，引入 `UserPromptSubmit` 做 turn 状态机

**结论**：暂不采纳。

**原因**：

- 可以同时保留 idle 语义和完成单次提醒
- 但需要新增事件、状态恢复逻辑和更复杂的 session 状态机
- 对当前“先确保完成只通知一次”的目标来说复杂度过高

## Decision

采用 **Option 2**：

- 受管默认 Claude hooks 仅保留 `Stop` 与 `Notification(permission_prompt)`
- 不再安装受管 `Notification(idle_prompt)`
- helper 增加 Claude 专用去重逻辑，确保受管默认路径下完成提醒只有一次，并尽量抑制混合旧配置场景下的重复

## Detailed Design

### 1. Claude hooks 目标模型

安装器在 `~/.claude/settings.json` 中维护以下受管事件：

- `Stop`
- `Notification(permission_prompt)`

不再写入：

- `Notification(idle_prompt)`

对旧版受管安装的迁移方式：

- 继续沿用现有“按 managed tag 过滤后重建”的策略
- 重新安装时，旧版受管 `idle_prompt` group 会被识别为受管条目并删除
- 然后仅回写 `Stop` 与 `permission_prompt` 两组受管配置

这意味着迁移后的默认行为天然不会再在完成后 60 秒产生第二次空闲提醒。

### 2. Helper 去重策略

虽然默认路径已去掉 `idle_prompt`，helper 仍需要 Claude 专用防御逻辑，原因有二：

1. 可能存在旧进程尚未重启，继续按旧 hooks 触发
2. 用户可能保留了历史受管配置副本，或 Claude 在异常情况下重复投递同一 `Stop`

helper 需要维护轻量状态文件，建议结构如下：

```json
{
  "version": 3,
  "claude": {
    "sessions": {
      "<session_id>": {
        "last_completion_at": "2026-04-26T12:34:56Z",
        "last_completion_fingerprint": "<derived>",
        "last_event_type": "stop"
      }
    }
  }
}
```

状态语义：

- `session_id` 来自 Claude hook payload；若缺失，则退化为“无 session”分支，只做短时间去重
- `last_completion_fingerprint` 用于识别同一完成事件的重复投递
- `last_completion_at` 用于短时间重复 `Stop` 抑制，以及遗留 `idle_prompt` 抑制

### 3. 事件处理规则

#### `Stop`

- 构造 completion fingerprint，优先使用 payload 中稳定字段；若字段不足，则使用 `session_id + 标题/消息摘要` 的组合退化
- 若同一 `session_id` 下在短时间窗口内收到相同 fingerprint，则视为重复投递并丢弃
- 否则发送完成通知，并更新该 session 的 completion 状态

建议的短窗口：5 秒到 15 秒，仅用于拦截重复 `Stop`，不用于处理 `idle_prompt`

#### `Notification(permission_prompt)`

- 始终允许发送
- 不参与完成类去重状态

#### 遗留 `Notification(idle_prompt)`

默认新配置不会再安装它，但 helper 仍需兼容：

- 如果同一 `session_id` 最近已经发送过完成通知，则直接丢弃该 `idle_prompt`
- 若拿不到 `session_id`，则按更保守策略处理：仅当最近的 Claude 完成通知极近时才抑制，避免误伤完全独立的提醒

这里的目的不是继续支持 idle 功能，而是避免旧配置残留时再次通知用户。

### 4. 检查与诊断输出

`--check` 需要明确区分以下状态：

- `Stop`: 受管 hooks 已安装
- `Notification(permission_prompt)`: 受管 hooks 已安装
- `Notification(idle_prompt)`: 受管 hooks 未安装

如果检测到受管 `idle_prompt` 仍存在，应输出“检测到旧版受管 idle_prompt，需要重装当前配置”的提示。

### 5. 回滚语义

卸载仍只移除受管条目，不处理非受管 hooks。

需要特别说明：

- 本提案的“确保只一次”范围仅覆盖受管 Claude 通知链路
- 若用户自行额外配置其他 Claude 通知 hooks，仍可能出现重复提醒

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| 移除 `idle_prompt` 后，用户失去“Claude 空闲太久”提醒 | 功能收缩 | 该提案明确以“完成只提醒一次”为优先目标；如后续需要，可用单独提案恢复为可选功能 |
| Claude payload 缺少稳定唯一字段，fingerprint 退化 | 去重精度下降 | 优先用 `session_id`，并把去重窗口限制在短时间范围，避免跨轮误伤 |
| 用户存在非受管 hooks | 仍可能重复 | 在 proposal 与 `--check` 文案中明确“仅保证受管链路” |
| 旧会话未重启仍按旧 hooks 运行 | 短时间内可能继续看到第二次通知 | helper 对遗留 `idle_prompt` 做抑制，安装说明继续要求重启 Claude Code 会话 |

## Acceptance Outline

需要覆盖以下验收场景：

1. 新装后，Claude 完成一轮任务，仅在 `Stop` 时收到一次通知
2. 完成后 60 秒不输入，不再收到受管 `idle_prompt` 通知
3. Claude 请求权限时，仍能收到 `permission_prompt` 通知
4. 从旧版受管安装升级后，`idle_prompt` group 被移除
5. 若旧会话残留触发一次 `idle_prompt`，helper 会在最近已完成的同 session 下抑制该通知
