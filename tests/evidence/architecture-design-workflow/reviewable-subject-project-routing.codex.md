## 需要 Architecture Sponsor 决定跨项目架构的长期归属

### Action summary

- `action_id=HAR-EVENT-ROUTING-001`
- `action_type=routing`
- Decision Owner：Architecture Sponsor
- Authority scope：只能从现有项目中选择本次架构决定的 Subject Project
- 为什么现在需要决定：支付拥有事件生产合同，会员和通知是消费者，`shared-platform` 已由 Platform Owner 管理共同协议，但长期架构归属尚未确定。

### Decision context

- Candidate recommendation：选择 `shared-platform`。这是路由建议，不是架构批准。
- Basis：事实是共同协议已经由 Platform Owner 管理；推断是将共同决定归属 `shared-platform` 能保留支付对生产合同的所有权，同时减少跨消费者项目的归档歧义。
- Bounded alternatives：

| Option | 主要后果 | Owner / 长期归档 | 风险 |
|---|---|---|---|
| `shared-platform`（建议） | 共同协议和跨项目决定集中管理 | Platform Owner / shared-platform | 需要持续维护三方追踪 |
| `payment` | 决定与生产合同归属同一项目 | Payment Owner / payment | 共同决定长期依附单一生产方 |

### Evidence and unresolved items

- Stable human-accessible evidence refs：`{{payment_contract_ref}}`、`{{shared_protocol_owner_ref}}`、`{{cross_project_owner_matrix_ref}}`
- 仍缺证据：目标人类对这些 refs 的访问确认；Owner=Architecture Lead；关闭条件=同一稳定 ref 可读取并记录 verifier。

### Exact response

```text
ACTION HAR-EVENT-ROUTING-001: select subject_project=shared-platform; reason=<reason>
```

或：

```text
ACTION HAR-EVENT-ROUTING-001: select subject_project=payment; reason=<reason>
```

### After response

任一合法选择都会使下一 stage=`routed`、remaining blockers=`none`、Next Owner=Architecture Lead，直接 `planned_writes=[issue:ARCH-CONTROL]`；不会创建设计、Review 或 packet。

### Authority boundary

Does not authorize：创建缺失 Project、仓库、Issue、Team、Agent、OpenSpec、branch、代码或实现，也不改变支付对生产合同的既有责任。

### Audit binding

- Routing context ref：`{{routing_context_ref}}`
- Current / superseded：`current`

<!-- ARCH-TEST-RESULT
{"fixture_id":"reviewable-subject-project-routing","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"waiting_human","gate":"none","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"target_project","blocked_reason":"missing_subject_project","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["subject_project","next_action","owner","closure_condition"],"limitations":["独立只读前向验证，未发布评论或执行写入","题面未提供实际 Issue、具名 Sponsor 与稳定 evidence refs，因此保留待注入变量"]}
ARCH-TEST-RESULT -->
