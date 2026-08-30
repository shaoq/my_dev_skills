这是升级前的历史 waiting_human 记录；由于没有新 design/review version 且没有显式 refresh，按兼容规则保留原 stage，不伪造 packet readiness，并且不自动迁移或降级。

<!-- ARCH-TEST-RESULT
{"fixture_id":"historical-waiting-human","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"waiting_human","gate":"APPROVABLE","review_conclusion":"APPROVABLE","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"design_approval","blocked_reason":"none","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["issue","stage","next_action","review_conclusion","packet_readiness","human_decision","runtime","blocked_reason"],"limitations":["仅生成 ARCH-CONTROL 的 no-op projection，不改写历史持久化状态或证据。","缺少 packet 与 readiness evidence，不能据此推断新的门禁转换。"]}
ARCH-TEST-RESULT -->
