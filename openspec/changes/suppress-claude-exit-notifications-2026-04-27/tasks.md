## 1. Claude hooks 模型扩展

- [x] 1.1 在受管 Claude hooks 构造逻辑中新增 `SessionEnd` hook
- [x] 1.2 确保重新安装时仅刷新受管 `SessionEnd`，不影响非受管同名 hooks
- [x] 1.3 扩展检查输出，显式报告 `SessionEnd` 受管 hook 安装状态

## 2. Runtime Helper 退出抑制

- [x] 2.1 为 Claude session 状态增加退出语义字段与过期清理策略
- [x] 2.2 实现 `claude-session-end` 输入路径，并在 `reason=prompt_input_exit` 时记录退出标记
- [x] 2.3 在 `Stop` 通知前增加退出抑制判断
- [x] 2.4 处理 `Stop` / `SessionEnd` 顺序不稳定场景，加入短延迟确认窗口
- [x] 2.5 实现基于 iTerm2 焦点 session tty 的精确前台抑制，只 suppress 当前焦点 session
- [x] 2.6 为焦点查询失败定义降级策略，保证不误吞其他后台 session 的提醒
- [x] 2.7 明确并验证"前台 app 不是 iTerm2"时不触发焦点 suppress
- [x] 2.8 明确并验证 iTerm2 内 tmux 场景下的焦点 pane / 后台 pane 提醒边界
- [x] 2.9 保证正常完成提醒与 `permission_prompt` 提醒不被误抑制

## 3. 文档与验收说明

- [x] 3.1 更新 README 或脚本帮助文案，说明 `/exit` 不应触发完成提醒
- [x] 3.2 补充受管链路边界说明，仅保证受管 Claude hooks 的退出抑制与精确焦点 session 抑制
- [x] 3.3 补充验收步骤，覆盖"正常完成""权限提醒""/exit 不提醒""焦点 session 不提醒""非 iTerm2 前台 app 仍提醒""tmux 下后台 pane 仍提醒""check 显示 SessionEnd"
