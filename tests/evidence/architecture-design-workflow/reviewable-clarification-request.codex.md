## ARCH-CONTROL｜`ARCH-DESIGN v1` 关键输入澄清请求

当前保持 `stage=designing`、`BLOCKED_REASON=critical_evidence_gaps`、Review conclusion=`none`、Human gate=`none`。以下内容是设计阶段候选输入，属于非批准信息，不构成 Review、packet readiness、`ARCHITECTURE_RECOMMENDATION`、OpenSpec 或实施授权。

### CR-01 内容治理

- 候选建议：默认只保存 trace、版本、时延、token、命中与评分等结构化元数据；原始问题、检索片段和回答默认不持久化。确需诊断时仅允许脱敏、授权、审计的受限采样，原文保留 7 天（provisional），禁止默认用于训练。
- 理由：现有技术事件不含正文；数据最小化和用途限制可降低泄露风险。
- 风险：降低逐例复现能力；受限采样增加脱敏、审计和删除成本。
- 待补证据 / Owner / 关闭条件：由 Privacy/Security 确认字段、用途、保留期和例外审批。

### CR-02 容量与 SLO

- 候选建议：`no_recommendation`。在没有真实峰值、payload 和增长数据时不制造 QPS、p95 或可用性数值；由 Product 与 SRE 提供现状基线，或指定 Owner 完成流量回放和故障演练。
- 理由：容量数字会直接改变组件、部署和成本选择。
- 风险：继续缺少基线会造成过度建设、容量不足或不可兑现的 SLO。
- 待补证据 / Owner / 关闭条件：补齐峰值 QPS、并发、payload 分布、增长率、延迟、loss、RPO/RTO、测量时间与证据位置。

### CR-03 部署与许可

- 候选建议：第一阶段 self-hosted，内容数据保留在受控环境，默认禁止向新的外部 SaaS 发送生产正文；许可证、DPA、预算和采购在生产前独立审查。
- 理由：沿用当前信任边界可降低数据外发与供应商锁定风险。
- 风险：自托管增加升级、备份和 on-call 成本。
- 待补证据 / Owner / 关闭条件：Security/Procurement/SRE 确认地域、网络出口、许可证、预算和运维能力。

### CR-04 持续运营 RACI

- 候选建议：Engineering 负责 collector/schema；SRE/Platform 负责平台、数据库、备份与 on-call；ML/Eval 负责 evaluator、gold set 与数据质量；Product 负责 KPI；Security/Privacy 负责采集、脱敏、删除和隐私事件。
- 理由：分离在线链路、平台运行、评测质量、业务口径和治理责任。
- 风险：只有角色域而没有可识别负责人时，升级路径仍不可执行。
- 待补证据 / Owner / 关闭条件：Subject Project Owner 补齐具体 A/R、替补、值守时段和升级路径。

### CR-05 Session 与 KPI

- 候选建议：服务端生成稳定 session ID；新增字段先保持可选并设置兼容窗口。首批 KPI 为请求成功率、证据校验通过率、引用覆盖率、端到端 P95 和负反馈率；gold set 由 ML/Eval 维护。
- 理由：覆盖可靠性、RAG 证据质量、性能与用户结果的最小闭环。
- 风险：错误 session 边界会扭曲漏斗与成本，未冻结的分母和分段会导致指标不可比较。
- 待补证据 / Owner / 关闭条件：Product/Data/API Owner 冻结 session 生命周期、指标公式、分母、排除项、分群、基线和目标。

### 可编辑回复

逐项使用：`接受 / 修改 / 拒绝`。例如：

```text
CR-01：接受 / 修改=<字段、用途、TTL> / 拒绝，原因=<...>
CR-02：测量证据=<ref> / Owner=@...，日期=<...> / 修改=<...> / 拒绝，原因=<...>
CR-03：接受 / 修改=<部署与许可边界> / 拒绝，原因=<...>
CR-04：接受，负责人映射=<...> / 修改=<...> / 拒绝，原因=<...>
CR-05：接受 / 修改=<session 与 KPI 口径> / 拒绝，原因=<...>
```

接受候选建议只改变其明确绑定的设计输入，不能替代测量证据、其他责任 Owner 的决定或准确 packet ref/version/digest 的 human decision。关键缺口实际关闭后，Lead 才重新计算 blocker；当前 `planned_writes=[issue:ARCH-CONTROL]`。

<!-- ARCH-TEST-RESULT
{"fixture_id":"reviewable-clarification-request","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"designing","gate":"none","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"none","blocked_reason":"critical_evidence_gaps","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["design_version","next_action","owner","closure_condition"],"limitations":["只读行为验证，未执行任何写入","真实容量、payload、预算和具体责任人仍需测量或由对应 Owner 确认"]}
ARCH-TEST-RESULT -->
