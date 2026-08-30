该请求为常规缺陷定位与回归修复（订单服务偶发 502，已有明确复现步骤和批准的 OpenSpec change），属于普通工程，不触发 architecture-design-workflow。按稳定说明报告 stage=not_applicable、gate=not_applicable、planned_writes=[]，不创建 ARCH-CONTROL，路由到常规调试/实施流程（可用 GitNexus 定位错误调用链与最近提交中的回归）。

<!-- ARCH-TEST-RESULT
{"fixture_id":"routine-bug","runtime":"claude","runtime_version":"Claude Code 2.1.14","selected":false,"stage":"not_applicable","gate":"not_applicable","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"not_applicable","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"none","blocked_reason":"none","planned_writes":[],"evidence_fields":["routing_reason","runtime","next_action"],"limitations":["只读行为测试：未读取源码、未执行调试或任何写入","本 skill 不适用：常规缺陷修复应使用常规调试流程（如 GitNexus 定位调用链与回归提交）"]}
ARCH-TEST-RESULT -->
