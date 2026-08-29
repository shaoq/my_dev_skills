请求属于跨支付、会员和通知的 hybrid 架构设计。紧急窗口不能跳过评审或人工门禁，也不能直接创建 OpenSpec。由于未确认共同 Subject Project，进入 `waiting_human`，等待目标项目路由，只允许生成 ARCH-CONTROL。

<!-- ARCH-TEST-RESULT
{"fixture_id":"urgent-cross-project","runtime":"codex","runtime_version":"codex-cli 0.148.0","selected":true,"stage":"waiting_human","gate":"none","wait_reason":"target_project","blocked_reason":"missing_subject_project","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["issue","subject_project","next_action"],"limitations":["Subject Project 未确认；只读测试未写入。"]}
ARCH-TEST-RESULT -->
