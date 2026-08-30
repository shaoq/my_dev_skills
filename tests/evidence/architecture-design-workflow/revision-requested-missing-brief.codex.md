## `revision_requested` 已生效；现在需要补齐修订范围

有效决定已使 stage=`designing`。当前 `revision_scope=missing`；缺少 brief 不撤销正式决定，也不能从 token 或 recommendation 推断具体修改内容。旧 packet 保持不变，只有 replacement design/review 再次 approvable 并交付新 packet 后才会产生 supersession。

### Action summary

- `action_type=design_input`
- Action ID：`HAR-REVISION-SCOPE-V20`
- Decision Owner：原决定人 `{{human_actor}}` 或明确的 Design Decision Owner
- Authority scope：只补充新设计迭代的修订范围、优先级、约束和验收变化
- Candidate recommendation：`no_recommendation`，因为现有证据不含任何可执行范围。

### Bounded alternatives

| Option | Option consequences / After response |
|---|---|
| `inline_scope` | `revision_scope=provided`，stage 保持 `designing`，Next Owner=Solution Architect，继续新 `ARCH-DESIGN` 版本，不创建 packet |
| `revision_brief_ref` | Architecture Lead 先验证稳定 ref；通过后 `revision_scope=provided`，再交给 Solution Architect |
| `reject` | stage 保持 `designing`，`revision_scope=missing`，不凭空生成修订内容 |

### Evidence

- Stable human-accessible evidence refs：`{{design_v20_ref}}`、`{{review_v20_ref}}`、`{{packet_v20_ref}}`、`{{revision_decision_evidence_ref}}`
- Missing evidence / Owner / closure condition：缺具体范围；Owner=Decision Owner；关闭条件=提供 inline scope 或经验证的 stable brief ref。

### Exact response

```text
ACTION HAR-REVISION-SCOPE-V20: modify revision_scope=<章节或问题>; priority=<优先级>; constraints=<约束>; acceptance_changes=<验收变化>; reason=<原因>
ACTION HAR-REVISION-SCOPE-V20: modify revision_brief_ref=<stable ref>; reason=<与packet v20的关系>
ACTION HAR-REVISION-SCOPE-V20: reject; reason=<暂不提供原因>
```

### Authority boundary

该 brief 是 non-authoritative context：不修改或替换 `revision_requested`，不改写 packet v20，不批准新设计，不形成 Review conclusion，不创建 replacement packet、OpenSpec 或实现。

<!-- ARCH-TEST-RESULT
{"fixture_id":"revision-requested-missing-brief","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"designing","gate":"revision_requested","review_conclusion":"APPROVABLE","packet_readiness":"review_packet_ready","packet_ref":"ARCH-APPROVAL-PACKET","packet_version":"v20","packet_digest":"sha256:ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad","access_confirmation":"confirmed","recommendation":"recommend_revision","human_decision":"revision_requested","decision_evidence_status":"valid","evidence_recorded_at":"2026-08-30T15:30:00Z","wait_reason":"none","blocked_reason":"none","planned_writes":["issue:ARCH-CONTROL","issue:ARCH-DESIGN"],"evidence_fields":["packet_version","packet_digest","human_decision","decision_evidence","next_action","owner","closure_condition"],"limitations":["独立只读前向验证，未持久化 revision brief 或新设计版本","题面未提供具名 actor 与实际 stable refs"]}
ARCH-TEST-RESULT -->
