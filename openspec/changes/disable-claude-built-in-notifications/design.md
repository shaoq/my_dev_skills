## Context

当前受管 Claude 通知方案把“即时完成提醒”建立在 Claude hooks 之上：

- `Stop` 负责完成提醒
- `Notification(permission_prompt)` 负责权限提醒
- `SessionEnd` 负责退出抑制语义

运行时由 `agent-notify` 直接向 iTerm2 发送 `OSC 9`，因此完成时会立即提醒一次。

但 Claude Code 本身还有另一层内建通知配置：`preferredNotifChannel`。当该值保持默认 `iterm2` 时，Claude 在 prompt 空闲 60 秒后仍会通过自身通知通道发送“等待输入”提醒。这个提醒不经过受管 helper，因此：

- 现有 `Stop` 去重逻辑无法抑制它
- 现有 `idle_prompt` hook 移除策略也无法消除它
- 用户会在“即时完成提醒”之后，再收到一条 60 秒后的延迟提醒

这说明当前“notify-only”只统一了受管 helper 路径，没有统一 Claude 的全部通知出口。

## Goals / Non-Goals

**Goals:**

- 保留现有基于 `Stop` 的即时完成提醒
- 禁用 Claude 内建的 iTerm2 通知通道，避免 60 秒 idle 再提醒
- 由安装器受管写入、检查并恢复 `preferredNotifChannel`
- 不覆盖用户在 `~/.claude/settings.json` 中的其他无关配置

**Non-Goals:**

- 不改变现有 Claude hooks 事件组合
- 不改变 Codex 通知路径
- 不处理用户自定义的非受管外部通知脚本
- 不尝试保留 Claude 内建 idle 提醒并与即时提醒共存

## Decisions

### Decision 1: 受管关闭 Claude 内建通知通道

**选择**：安装器在 `~/.claude/settings.json` 中受管设置 `preferredNotifChannel = "notifications_disabled"`。

**理由**：

- 这是唯一能稳定关闭 Claude 内建 60 秒 idle 提醒的配置入口
- hook 层去重无法拦截 Claude 内建通知
- 与“只保留即时提醒”目标完全一致

**备选方案**：

- 保留 `preferredNotifChannel=iterm2`，仅在 helper 中继续补去重：拒绝。因为内建通知不经过 helper，无法实现真正去重。
- 移除 `Stop` 即时提醒，只保留 Claude 内建通知：拒绝。因为用户明确需要即时提醒。

### Decision 2: 将 `preferredNotifChannel` 纳入受管合并与恢复模型

**选择**：沿用现有安装器对 `~/.claude/settings.json` 的“最小改写 + 状态保存 + 卸载恢复”模式，把 `preferredNotifChannel` 作为独立受管字段纳入 state。

**理由**：

- 当前脚本已经对 Claude hooks 做受管合并，新增一个顶层字符串字段属于同类问题
- 安装器必须可逆，不能把用户原有通知偏好永久覆盖
- 用户可能原本显式配置了 `terminal_bell`、`iterm2_with_bell` 或其他值，卸载后应恢复

**备选方案**：

- 直接无状态覆盖，卸载时一律删除该字段：拒绝。会丢失用户原有设置。
- 把该字段交给 README 手动配置：拒绝。无法保证实际安装结果与检查输出一致。

### Decision 3: 检查模式显式报告“双通道风险”

**选择**：`--check` 除了报告受管 hooks，还要报告 `preferredNotifChannel` 当前值；如果不是 `notifications_disabled`，则明确提示“Claude 内建通知仍开启，可能与受管即时通知重复”。

**理由**：

- 当前问题就是因为安装结果表面看起来正确，但实际还有第二通知出口
- 用户需要一个直接可见的诊断项，而不是靠行为猜测

### Decision 4: 继续保持即时提醒责任只在受管 helper

**选择**：不调整 `agent-notify-runtime.py` 的提醒语义，不把 60 秒 idle 语义重新接回受管链路。

**理由**：

- 本提案的问题在配置出口重叠，不在 helper 行为本身
- 收敛出口比重新建复杂状态机更简单、也更符合用户目标

## Risks / Trade-offs

- 用户原本依赖 Claude 内建等待输入提醒 → 通过 state 恢复原值，并在文档中明确本方案选择“只保留即时提醒”
- `~/.claude/settings.json` 顶层字段结构异常 → 延续现有安装器的结构校验策略，无法安全合并时显式报错，不做危险覆盖
- 仍存在用户自定义第三方通知脚本 → `--check` 只能保证受管路径，不能承诺消除所有非受管重复提醒
- 未来 Claude 官方新增通知通道语义 → 通过显式检查 `preferredNotifChannel` 降低隐性重复风险

## Migration Plan

1. 安装时读取 `~/.claude/settings.json` 当前 `preferredNotifChannel`
2. 若此前未记录原值，则把“是否存在”和“原始值”写入受管 state
3. 将该字段设置为 `notifications_disabled`
4. 保持现有受管 hooks 安装逻辑不变
5. `--check` 报告当前字段值与受管状态
6. 卸载时按 state 恢复原值；若原先不存在，则删除该字段

## Open Questions

- 是否需要在 README 中增加“为什么关闭 Claude 内建通知”的行为说明
- `--check` 对用户显式配置的其他值是仅报告，还是在文案中区分“与受管目标不一致”与“用户自定义覆盖”
