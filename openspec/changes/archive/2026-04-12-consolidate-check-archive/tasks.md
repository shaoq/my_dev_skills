## 1. 修改 check-changes-completed

- [x] 1.1 删除 Step 6（归档引导三选项流程）及其相关 Guardrail
- [x] 1.2 在报告末尾添加归档提示：列出可存档 changes 并提示使用 `opsx:archive <name>`
- [x] 1.3 调整 Output On Success 格式，移除归档相关输出，加入归档提示

## 2. 删除冗余 skill

- [x] 2.1 删除 `archived-all-completed-changes/SKILL.md` 文件

## 3. 验证

- [x] 3.1 确认 `check-changes-completed` 保留完整的 4D 检查 + 报告 + 阻塞原因功能
- [x] 3.2 确认 `archived-all-completed-changes/` 目录已不存在
