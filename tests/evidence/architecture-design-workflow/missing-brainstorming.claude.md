请求需要 `superpowers:brainstorming` 澄清，但当前 Runtime 无法解析它。保持 `routed`，`BLOCKED_REASON=missing_brainstorming`，gate 为 none，只生成待人工发布的 ARCH-CONTROL，停止研究和设计。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-brainstorming","runtime":"claude","runtime_version":"Claude Code 2.1.206","selected":true,"stage":"routed","gate":"none","wait_reason":"none","blocked_reason":"missing_brainstorming","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["runtime","blocked_reason","next_action"],"limitations":["缺失必需依赖；只读测试未写入。"]}
ARCH-TEST-RESULT -->
