## 1. 运行时通知能力设计

- [x] 1.1 定义统一运行时通知脚本的安装位置、入参协议和受管标识
- [x] 1.2 定义统一脚本支持的事件模型：`approval_needed`、`turn_completed`、`idle_waiting`
- [x] 1.3 定义统一脚本的通知动作：macOS 通知、BEL、节流/去重策略

## 2. iTerm2 Trigger 升级

- [x] 2.1 保留现有 Claude Trigger 规则不变
- [x] 2.2 补充 Codex 当前版本的审批提示匹配规则
- [x] 2.3 明确 Trigger 安装、检查、卸载的受管识别方式

## 3. Claude / Codex 配置安装

- [x] 3.1 设计 Claude `Stop` 与 `Notification` hooks 的受管合并策略
- [x] 3.2 设计 Codex `notify` 的受管合并策略
- [x] 3.3 设计 `--check` 输出，覆盖 iTerm2 / Claude / Codex 三类配置

## 4. 配置保全与卸载

- [x] 4.1 设计不破坏现有 `~/.claude/settings.json` 的 JSON 合并策略
- [x] 4.2 设计不破坏现有 `~/.codex/config.toml` 的最小侵入写入策略
- [x] 4.3 设计“仅移除受管条目”的卸载语义

## 5. 文档与验证

- [x] 5.1 更新脚本帮助文案与 README 使用说明
- [x] 5.2 补充验收场景：Claude 审批、Claude 完成、Claude idle、Codex 审批、Codex 完成
