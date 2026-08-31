## 1. RED 回归

- [x] 1.1 记录 UNIDRAG-12 latest-position reply 的真实 parent、mention、actor、revision 与 no-op 结果
- [x] 1.2 在现有 contract tests 增加 latest-position current Action success 与歧义/过期/编辑 failure fixtures
- [x] 1.3 运行测试并记录旧契约的预期 RED

## 2. Portable core

- [x] 2.1 定义 `current_action_reference_v1` 与 current/unique/Owner/version/digest/time/revision/supersession 规则
- [x] 2.2 从 portable required fields 移除平台 parent/thread 依赖并更新 Review 状态语义/模板

## 3. Multica adapter

- [x] 3.1 实施具名 Action ID 绑定并把 parent chain 降为审计证据，保留 token-only packet 兼容路径
- [x] 3.2 实施受限 current Agent mention 规范化与歧义失败关闭
- [x] 3.3 更新 manifest、decision evidence、Human Action 模板和 `in_progress` 自动投影

## 4. 验证与激活

- [x] 4.1 运行 GREEN contract/safety/quick validation、OpenSpec strict validation 与 diff 检查
- [x] 4.2 验证 portable core 无 Multica required fields；通过既有 symlink 激活本地 Skill，并将相同内容原 ID 同步到 Multica Workspace 的两个既有 Skill identity 后回读 digest
- [x] 4.3 重读 UNIDRAG-12 现有 latest-position reply；仅在新契约全部通过时自动恢复 `in_progress` 并处理决定
