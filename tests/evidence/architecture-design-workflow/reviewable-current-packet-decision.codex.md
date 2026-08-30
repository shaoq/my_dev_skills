## 需要对 current ready ARCH-APPROVAL-PACKET v19 作决定

### Action summary

- `action_type=design_approval`
- Action ID：`HAR-DESIGN-APPROVAL-V19`
- Decision Owner：`{{review_packet_ready.human_actor}}`
- 当前建议：`recommend_approved_for_spec`；建议不是批准。
- 为什么现在可决定：Design、Review、Packet 及人类访问均已验证，Review conclusion=`APPROVABLE_WITH_WARNINGS`，两项 accepted risks 有各自 Owner 和 evidence。

### 四种决定及后果

| 决定 | 含义 | After response / 直接写入 | 边界与不可逆影响 |
|---|---|---|---|
| `approved_design_only` | 只发布 ADR 与详细设计 | 进入 `publishing`；Next Owner=Architecture Lead；写 `ARCH-CONTROL`、ADR、详细设计 | 不生成 R&D handoff；发布历史只能 supersede/revoke |
| `approved_for_spec` | 发布批准文档并在目标存在时形成 R&D handoff | 进入 `publishing`；目标缺失则保留决定并等待 routing | R&D Team 独立分析；不自动创建 OpenSpec、Issue、branch、commit 或代码 |
| `revision_requested` | 进入新设计迭代 | stage=`designing`；写 `ARCH-CONTROL` 和新 `ARCH-DESIGN` | revision brief 不是批准；旧 packet 不改写 |
| `rejected` | 拒绝 current work item | stage=`rejected`；写 `ARCH-CONTROL` | `rejected` 为终态；继续需要新的明确工作 |

### Evidence

- Stable human-accessible evidence refs：`{{design_v19_ref}}`、`{{review_v19_ref}}`、`{{packet_v19_ref}}`、`{{risk_acceptance_refs}}`、`{{readiness_ref}}`
- Access confirmation / verifier：`{{access_evidence_refs}}` / `{{verifier}}`

### Exact response

复制其中一条，并保留完整 binding：

```text
ACTION HAR-DESIGN-APPROVAL-V19: approved_design_only packet_ref={{packet_v19_ref}}; packet_version=v19; packet_digest=sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
ACTION HAR-DESIGN-APPROVAL-V19: approved_for_spec packet_ref={{packet_v19_ref}}; packet_version=v19; packet_digest=sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
ACTION HAR-DESIGN-APPROVAL-V19: revision_requested packet_ref={{packet_v19_ref}}; packet_version=v19; packet_digest=sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
ACTION HAR-DESIGN-APPROVAL-V19: rejected packet_ref={{packet_v19_ref}}; packet_version=v19; packet_digest=sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

说明文字、readiness 和 recommendation 都不能替代上述 token 与 current packet binding。当前 Human decision 仍为 `none`，因此保持 `waiting_human`。

<!-- ARCH-TEST-RESULT
{"fixture_id":"reviewable-current-packet-decision","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"waiting_human","gate":"APPROVABLE_WITH_WARNINGS","review_conclusion":"APPROVABLE_WITH_WARNINGS","packet_readiness":"review_packet_ready","packet_ref":"ARCH-APPROVAL-PACKET","packet_version":"v19","packet_digest":"sha256:e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855","access_confirmation":"confirmed","recommendation":"recommend_approved_for_spec","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"design_approval","blocked_reason":"none","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["packet_ref","packet_version","packet_digest","packet_readiness","access_confirmation","recommendation","next_action"],"limitations":["独立只读前向验证，尚无真实 human decision","题面声明 refs 稳定可访问，但未提供可重读的实际 ref 字符串"]}
ARCH-TEST-RESULT -->
