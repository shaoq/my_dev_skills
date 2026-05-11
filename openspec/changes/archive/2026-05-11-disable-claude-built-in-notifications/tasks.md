## 1. Claude 设置受管合并

- [x] 1.1 为 `~/.claude/settings.json` 的 `preferredNotifChannel` 增加受管读取与结构校验逻辑
- [x] 1.2 在安装路径中保存 `preferredNotifChannel` 的原始存在性与原始值
- [x] 1.3 在安装路径中将 `preferredNotifChannel` 受管设置为 `notifications_disabled`
- [x] 1.4 在卸载路径中按受管 state 精确恢复 `preferredNotifChannel`，或在原先不存在时移除该字段

## 2. 检查与诊断输出

- [x] 2.1 扩展 `--check` 输出，显式报告当前 `preferredNotifChannel` 值
- [x] 2.2 当 `preferredNotifChannel` 不是 `notifications_disabled` 时，输出“可能与受管即时通知重复”的诊断提示
- [x] 2.3 验证该检查输出与现有 Claude hooks 状态报告可以同时工作，不影响其他检查项

## 3. 文档与验收说明

- [x] 3.1 更新 README 或脚本帮助文案，说明受管方案会关闭 Claude 内建通知通道以保留即时提醒
- [x] 3.2 补充受管边界说明：仅消除 Claude 内建通知与受管 helper 的重复，不保证消除所有非受管第三方通知
- [x] 3.3 补充验收步骤，覆盖“任务完成立即提醒”“60 秒后不再出现第二次 idle 提醒”“卸载后恢复原始 `preferredNotifChannel`”“check 能显示内建通知通道状态”
