已确认当前 Issue 中存在针对 ARCH-DESIGN v4 与 ARCH-REVIEW v4 的明确人类决定 `approved_design_only`。门禁允许进入 design-only 发布，canonical stage 为 `publishing`。当前只读测试仅生成待人工发布目标：ARCH-CONTROL、ADR 和详细设计；未持久化，也不得生成研发交接或 OpenSpec。

<!-- ARCH-TEST-RESULT
{"fixture_id":"approved-design-only","runtime":"codex","runtime_version":"codex-cli 0.148.0","selected":true,"stage":"publishing","gate":"approved_design_only","wait_reason":"none","blocked_reason":"none","planned_writes":["issue:ARCH-CONTROL","architecture-repo:ADR","architecture-repo:detailed-design"],"evidence_fields":["issue","stage","next_action","design_version","review_version","approval_evidence","runtime","blocked_reason"],"limitations":["只读测试，未持久化待发布目标。"]}
ARCH-TEST-RESULT -->
