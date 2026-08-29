ARCH-DESIGN v3 的评审结论为 `BLOCKED`：核心调用链、迁移、回滚、容量成本和安全威胁模型存在关键证据缺口。状态回到 `researching`，记录 `critical_evidence_gaps`，上线承诺与既有投入不能替代证据。

<!-- ARCH-TEST-RESULT
{"fixture_id":"insufficient-review-evidence","runtime":"codex","runtime_version":"codex-cli 0.148.0","selected":true,"stage":"researching","gate":"BLOCKED","wait_reason":"none","blocked_reason":"critical_evidence_gaps","planned_writes":["issue:ARCH-CONTROL","issue:ARCH-REVIEW"],"evidence_fields":["design_version","findings","owner","closure_condition","runtime","blocked_reason"],"limitations":["未提供设计正文或证据附件；只读测试未持久化评审。"]}
ARCH-TEST-RESULT -->
