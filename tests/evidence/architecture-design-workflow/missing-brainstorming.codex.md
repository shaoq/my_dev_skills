该 greenfield 请求存在目标用户、系统边界、预算、数据敏感级别及自建或采购偏好的实质歧义，必须先使用 superpowers:brainstorming；当前 Runtime 无法解析该依赖，故停止并记录 BLOCKED_REASON=missing_brainstorming。

<!-- ARCH-TEST-RESULT
{"fixture_id":"missing-brainstorming","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"routed","gate":"none","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"none","blocked_reason":"missing_brainstorming","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["issue","subject_project","design_type","stage","next_action","runtime","blocked_reason","routing_reason"],"limitations":["依赖预检未通过，不能开始研究、设计或评审。","不能用经验判断、普通 planning 或其他 skill 替代缺失依赖。"]}
ARCH-TEST-RESULT -->
