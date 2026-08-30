## ARCH-DESIGN v4 有两项风险需要各自 Owner 决定

这两项风险属于不同 authority scope，必须拆成两个原子动作；当前仍在 `reviewing`，不会形成 approvable conclusion 或创建 packet。两份回复都是非批准信息。

### `RISK-PRIVACY-1`

- `action_type=risk_acceptance`
- Action ID：`HAR-RISK-PRIVACY-1-V4`
- Decision Owner：Privacy Owner
- 决定：接受 30 天 derived retention、修改条件或拒绝。
- Candidate recommendation：在删除、审计和复核控制成立时接受 30 天条件。
- Stable human-accessible evidence refs：`{{design_v4_privacy_ref}}`、`{{review_v4_privacy_ref}}`、`{{privacy_control_ref}}`

Option consequences：

| Option | After response |
|---|---|
| `accept` | stage 保持 `reviewing`；记录本 Risk ID 的 evidence；仍等待 SRE Owner；Next Owner=Architecture Lead；planned writes=`issue:ARCH-CONTROL` |
| `modify` | stage=`designing`；Next Owner=Solution Architect；直接更新控制并启动新 `ARCH-DESIGN` 版本 |
| `reject` | stage=`designing`；寻找替代 retention 方案；当前 v4 不再继续当前评审路径 |

Exact response：

```text
ACTION HAR-RISK-PRIVACY-1-V4: accept risk=RISK-PRIVACY-1; conditions=<conditions>
ACTION HAR-RISK-PRIVACY-1-V4: modify risk=RISK-PRIVACY-1; conditions=<conditions>
ACTION HAR-RISK-PRIVACY-1-V4: reject risk=RISK-PRIVACY-1; reason=<reason>
```

### `RISK-SRE-2`

- `action_type=risk_acceptance`
- Action ID：`HAR-RISK-SRE-2-V4`
- Decision Owner：SRE Owner
- 决定：接受试点单区条件、修改条件或拒绝。
- Candidate recommendation：只在试点范围、退出条件和复核点明确时接受。
- Stable human-accessible evidence refs：`{{design_v4_sre_ref}}`、`{{review_v4_sre_ref}}`、`{{pilot_exit_ref}}`

Option consequences：

| Option | After response |
|---|---|
| `accept` | stage 保持 `reviewing`；记录本 Risk ID 的 evidence；仍等待 Privacy Owner；Next Owner=Architecture Lead；planned writes=`issue:ARCH-CONTROL` |
| `modify` | stage=`designing`；Next Owner=Solution Architect；直接更新控制并启动新 `ARCH-DESIGN` 版本 |
| `reject` | stage=`designing`；重新设计部署拓扑或取消试点 |

Exact response：

```text
ACTION HAR-RISK-SRE-2-V4: accept risk=RISK-SRE-2; conditions=<conditions>
ACTION HAR-RISK-SRE-2-V4: modify risk=RISK-SRE-2; conditions=<conditions>
ACTION HAR-RISK-SRE-2-V4: reject risk=RISK-SRE-2; reason=<reason>
```

每个 Owner 的回复只影响自己的 Risk ID，不能替代另一权限域、Review conclusion、packet readiness 或正式设计决定。

<!-- ARCH-TEST-RESULT
{"fixture_id":"reviewable-multi-owner-risk-acceptance","runtime":"codex","runtime_version":"codex-cli 0.151.0","selected":true,"stage":"reviewing","gate":"none","review_conclusion":"none","packet_readiness":"none","packet_ref":"none","packet_version":"none","packet_digest":"none","access_confirmation":"none","recommendation":"none","human_decision":"none","decision_evidence_status":"none","evidence_recorded_at":"none","wait_reason":"none","blocked_reason":"none","planned_writes":["issue:ARCH-CONTROL"],"evidence_fields":["review_version","owner","closure_condition","next_action"],"limitations":["独立只读前向验证，未记录真实风险接受证据","题面未提供具名人类与实际稳定 refs"]}
ARCH-TEST-RESULT -->
