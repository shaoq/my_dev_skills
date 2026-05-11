## 1. Notify-only 架构设计

- [x] 1.1 明确 notify-only 目标行为：Claude Code 与 Codex 都只保留 iTerm2 notify，不再保留 bell
- [x] 1.2 明确 Claude hooks 路径与 Codex TUI 路径的职责边界
- [x] 1.3 明确 iTerm2 在普通会话与 tmux 会话中的承接方式

## 2. Claude Notify 路径迁移

- [x] 2.1 定义 `agent-notify-runtime.py` 从 BEL 改为 `OSC 9` 的行为规范
- [x] 2.2 定义 Claude `Stop`、`permission_prompt`、`idle_prompt` 的 notify 文案与事件映射
- [x] 2.3 定义 Claude helper 的 tmux passthrough 规则

## 3. Codex Notify 路径迁移

- [x] 3.1 定义从顶层 `notify` 迁移到 `[tui]` 通知配置的受管策略
- [x] 3.2 明确 `tui.notifications`、`tui.notification_method = "osc9"`、`tui.notification_condition` 的受管默认值
- [x] 3.3 明确安装、检查、卸载时如何识别并处理旧版受管 Codex notify 配置

## 4. iTerm2 与遗留 Bell 迁移

- [x] 4.1 定义旧版受管 `BellTrigger` 的迁移与移除语义
- [x] 4.2 定义停止受管改写 `Flashing Bell` / `Silence Bell` 的策略
- [x] 4.3 定义 `--check` 如何识别受管 bell 已清除以及用户自定义 bell 仍存在

## 5. 文档与验收

- [x] 5.1 更新 README 中的安装目标、行为说明与限制条件
- [x] 5.2 补充验收场景：iTerm2 非 tmux 的 Claude/Codex notify-only
- [x] 5.3 补充验收场景：iTerm2 内 tmux 的 Claude/Codex notify-only
