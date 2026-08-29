请求属于 greenfield 架构设计，但关键输入存在实质歧义，当前 Runtime 又无法解析 `superpowers:brainstorming`。保持 `routed`，`BLOCKED_REASON=missing_brainstorming`，gate 为 none，仅生成待人工发布的 ARCH-CONTROL，停止研究和设计。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-brainstorming","runtime":"codex","runtime_version":"codex-cli 0.148.0","selected":true,"stage":"routed","gate":"none","wait_reason":"none","blocked_reason":"missing_brainstorming","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["runtime","blocked_reason","next_action"],"limitations":["缺失必需依赖；未开展研究或写入。"]}
ARCH-TEST-RESULT -->
