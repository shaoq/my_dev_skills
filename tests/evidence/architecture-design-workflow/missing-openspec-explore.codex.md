Subject Project 与输入已明确，但当前 Runtime 无法解析 `openspec-explore`。保持 `routed`，`BLOCKED_REASON=missing_openspec_explore`，gate 为 none；普通 planning 不能替代，当前唯一待发布目标是 ARCH-CONTROL。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-openspec-explore","runtime":"codex","runtime_version":"codex-cli 0.148.0","selected":true,"stage":"routed","gate":"none","wait_reason":"none","blocked_reason":"missing_openspec_explore","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["runtime","blocked_reason","next_action"],"limitations":["缺失必需依赖；未开展研究或写入。"]}
ARCH-TEST-RESULT -->
