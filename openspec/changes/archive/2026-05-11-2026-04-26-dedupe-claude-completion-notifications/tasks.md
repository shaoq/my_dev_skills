## 1. Claude hooks 模型收紧

- [x] 1.1 调整受管 Claude hooks 构造逻辑，默认仅安装 `Stop` 与 `Notification(permission_prompt)`
- [x] 1.2 确认重新安装时可自动移除旧版受管 `Notification(idle_prompt)` group
- [x] 1.3 更新检查输出，显式报告受管 `idle_prompt` 是否仍存在

## 2. Runtime Helper 去重

- [x] 2.1 为 helper 定义 Claude session 状态结构与版本迁移策略
- [x] 2.2 实现 `Stop` 的短时间重复投递抑制
- [x] 2.3 实现遗留 `idle_prompt` 在”同 session 已完成”后的抑制逻辑
- [x] 2.4 保证 `permission_prompt` 不受完成类去重影响

## 3. 文档与迁移说明

- [x] 3.1 更新脚本帮助文案与 README，说明 Claude 默认不再安装 `idle_prompt`
- [x] 3.2 补充升级说明：需重启 Claude Code 会话以清除旧 hooks 缓存
- [x] 3.3 补充验收步骤，覆盖”完成一次””权限提醒””旧版残留 idle 抑制”
