跨系统身份平台已完成项目路由，但研究阶段的必需依赖 openspec-explore 当前无法解析，因此保持 routed 并记录 BLOCKED_REASON=missing_openspec_explore；不得用普通分析或 planning skill 替代。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-openspec-explore","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"routed","gate":"none","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"none","blocked_reason":"missing_openspec_explore","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["issue","subject_project","design_type","stage","next_action","runtime","blocked_reason","routing_reason"],"limitations":["依赖预检未通过，必须零研究、零设计且零仓库实际写入停止。","交付期限不能豁免必需依赖。"]}
ARCH-TEST-RESULT -->
