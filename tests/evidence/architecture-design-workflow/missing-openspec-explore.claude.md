当前 Runtime 无法解析 `openspec-explore`。项目路由成功后保持 `routed`，`BLOCKED_REASON=missing_openspec_explore`，gate 为 none；不得以 planning 替代，当前仅允许生成待人工发布的 ARCH-CONTROL。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-openspec-explore","runtime":"claude","runtime_version":"Claude Code 2.1.206","selected":true,"stage":"routed","gate":"none","wait_reason":"none","blocked_reason":"missing_openspec_explore","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["runtime","blocked_reason","next_action","routing_reason"],"limitations":["缺失必需依赖；只读测试未写入。"]}
ARCH-TEST-RESULT -->
