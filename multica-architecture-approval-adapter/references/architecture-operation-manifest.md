# Architecture operation manifest and automatic execution

## Purpose

`architecture_operation_manifest_v1` 是 Adapter 从 current `architecture_workflow_mandate_v2` 派生的 immutable、single-consumption 执行证据。它保留旧 exact operational scope 的最小权限与可重验价值，但不是 Human Action，也不发布 `AUTHORIZE OPERATION` 请求。历史 `architecture_workflow_mandate_v1` 只作 dual-read 审计；新写入必须先建立 superseding v2 attempt。

只有用户已明确开始、继续、重试当前架构阶段，或明确要求实施并激活已审核的当前 Skill change 时，才能存在对应 workflow mandate。Adapter 不从 recommendation、Issue status、Agent 分派、旧 token 或模糊肯定推断 mandate。

## Canonical manifest

用固定字段顺序冻结 UTF-8/LF payload，并在末尾保留一个 LF：

```text
manifest_profile=architecture_operation_manifest_v1
manifest_id=<opaque-id>
mandate_ref=<stable-current-mandate-ref>
workspace_id=<existing-workspace-id>
issue_id=<existing-issue-id-or-none>
agent_id=<existing-agent-id>
workflow_actor_ref=<portable-actor-ref>
workflow_actor_authority_ref=<portable-authority-ref>
current_responsibility=<portable-responsibility>
portable_stage=<current-stage>
attempt_id=<opaque-attempt-id>
core_skill_identity=<name-and-aggregate-digest>
adapter_skill_identity=<name-and-aggregate-digest>
input_identities=<sorted-identities-and-raw-byte-digests>
human_surface_contract=human_review_surface_v1
internal_evidence_contract=architecture_internal_evidence_v1
output_identities=<one-design-human-output-and-ordered-internal-evidence-digests>
visual_manifest_identity=<current-ref-and-digest-or-diagram_not_applicable>
visual_receipt_identity=<current-deliver-and-visual-check-receipts-or-none>
static_preview_identity=<artifact-local-light-1440x900-ref-digest-and-platform-projection-or-none>
required_visual_status=<passed|unavailable|not_applicable>
handoff_id=<current-execution-handoff-id-or-none>
blocker_action_id=<current-portable-blocker-id-or-none>
blocker_profile=<architecture_blocker_action_v3|none>
blocker_response_mode=<provide_input|request_discovery|none>
discovery_actor_ref=<portable-actor-ref-or-none>
discovery_result=<unique_verified|multiple_verified|unavailable_with_evidence|none>
queued_task_id=<readback-task-id-or-none>
queued_task_status=<queued|waiting_local_directory|running|none>
predecessor_task_id=<current-task-id-or-none>
directory_lock_evidence_ref=<same-in-place-lock-ref-or-none>
planned_writes=<zero-padded-ordered-writes>
postconditions=<ordered-readback-checks>
retained_objects=<sorted-existing-object-identities-or-none>
retry_limit=<bounded-non-negative-integer>
supersedes=<legacy-request-or-attempt-identities-or-none>
invalidates_on=<frozen-drift-conditions>
```

字段值使用既有 canonical UTF-8 percent encoding；路径必须是已解析且位于 mandate 授权输入根下的相对路径。`planned_writes` 只允许当前 stage 所需的最小集合：work-start `in_progress --no-start`、一条 Decision Brief + exactly one Design attachment、一条 actionable blocker comment、internal task evidence、交付成功后的 `in_review --no-start`、必要状态投影。execution handoff 必须符合 `multica_execution_handoff_v2` 且 postconditions 包含准确 task/readback；不得规划 dedicated handoff comment。

## Derivation and pre-write fence

Adapter 必须从 mandate 和当前只读事实确定性生成 manifest，不接受用户手写或编辑 manifest。首笔写入前依次：

1. 重读 workspace/Issue/Agent、portable stage、attempt 和 current status；
2. 重算两个 Skill aggregate、全部输入/输出 raw-byte digest；
3. 重验唯一 Decision Owner、current action、`requires_human_review` 和 candidate/task attribution；`current_action_reference_v1` 的 parent chain 只作审计，packet/delivery parent selector 继续按各自 profile 校验；
4. 扫描 retained comments/attachments/projections/sidecars 与 current/superseded identity；
5. 证明 planned writes 是 mandate 允许操作的有序子集，且没有创建资源、跨 Issue/workspace、实现或部署；
6. 对 execution continuation 重验 internal task evidence、唯一 `handoff_id`、准确下一 Agent、task selector 和 single-consumption；dedicated handoff comment 与普通 `ARCH-CONTROL` 自 mention 不得进入 planned writes；
7. 对 actionable blocker 重验唯一 instruction-owner Member、`architecture_blocker_action_v3`、`automatic_before_human` discovery evidence、一个普通业务问题、single action、三类自然语言回复、reply-context evidence derivation、conditional formal-source policy、resume/discovery responsibility/Agent 与 blocked rollback；
8. 计算 manifest raw-byte SHA-256，并写入机器可读 task evidence。

Required visual preflight additionally requires current source/HTML/receipt/preview digests, `deliver=passed`、`browser_evidence=passed`、`visual_review=passed`、semantic findings closed and requested-client preview readability. Any failed/skipped/stale/mismatch is unavailable before approval readiness; an older HTML or preview cannot substitute.

任何 unknown、重复、漂移、缺失或额外写入使 manifest 不可消费。不得为了继续而请求 operational authorization、挑选最近评论、猜 UUID、编辑历史或补写诊断评论。

## Multica metadata capacity gate

Multica 当前 Issue metadata 使用一个聚合的 **8 KiB metadata bag**（8192 UTF-8 bytes，而不是每个 key 各 8 KiB）。每次 `metadata set` 前必须先读取完整 metadata bag，并执行 **pre-write byte budget**：使用平台返回的实际序列化/容量规则计算 `current bag - replaced current value + proposed value`；平台不能暴露精确序列化开销时，必须采用包含 key、value 与结构开销的保守上界，不能把单个 value 长度当作总预算。

若 verbose manifest/evidence 超过预算，必须先派生一个 **compact current projection**。紧凑投影仍须保留 profile、current work item/stage/attempt、current Action/manifest identity、actor 与 authority identity、state/status、输入/输出 evidence refs、supersedes 和恢复/关闭条件；完整命令、timeline、历史 retained objects 与冗长说明写入当前 task result 或既有 shared evidence，而不是塞入 metadata。只能原子替换已确认属于同一 Issue、已被 current attempt supersede 的 stale current metadata key；不得删除或编辑历史 comment、attachment、回复或其他审计对象。

平台拒绝写入时必须解析准确容量错误，重新读取整个 bag，并且 **do not retry the same oversized value**。只允许在同一 mandate/retry limit 内生成一次更小且字段完备的新 manifest/value，再重新执行预算与写后回读。若 current identity/evidence 无法在预算内无损表示，结果为 `metadata_capacity_exceeded`：保持/恢复准确 `blocked` 或写前状态，保留已创建对象，在 task result 中列出实际字节数、预算、未写 key、current evidence 与关闭条件；不得请求 operational authorization，也不得留下 orphaned `in_progress`。

## Single consumption and automatic writes

完全匹配后立即自动消费 manifest：

- 每一步写入前重读其直接 precondition；
- 每一步写入后重读 exact object/status/digest postcondition；
- 成功对象加入 retained set；
- 一个 manifest 只允许一个 current consumption record；重复触发先 reconciliation，不能重复发布 current delivery；
- 自动 retry 只能在 `retry_limit` 内生成新 attempt/new manifest，并必须冻结新的 retained set；旧 manifest 永不修改或再次消费。
- 当前 task 将结束且 portable intent 仍为 Agent working 时，必须按准确 handoff_id 回读 queued_task_id 与 queued_task_status；`queued` 满足 accepted，`running` 满足 active。`waiting_local_directory` 只有在 runtime 在线、attribution 准确、predecessor 是当前 task 且同一 `in_place` 目录锁 evidence 可重读时才满足 accepted，避免前序 task 等待下游 running、下游又等待前序释放目录的死锁。

Decision Brief 首行必须准确 mention 唯一 Decision Owner。只有 `requires_human_review=true` 且评论、附件、完整材料入口、mention 和当前 access verification mode 的 postconditions 全部通过后，才自动写 `in_review --no-start`。`automatic` 要求 client scopes=`opened`；显式 `owner_manual` 用于 `design_input|architecture_review`，要求 identity/digest/stable same-Issue entry/policy evidence；正式 packet 的 `owner_attested` 还要求 current named Action 与 manifest-bound `multica_issue_task_evidence_v1` request/task/`arch.packet.current`/`ARCH-CONTROL` readbacks。两种人工模式均记录 `manual_check_required`。非 Review 步骤自动进入下一 stage 或完成当前步骤，不停留等待用户。

有效 Review 回复使用 manifest-bound `valid_human_action_response_v1`。具名 `current_action_reference_v1` 必须匹配 actor、work item、唯一 current Action ID、从 request 继承的 version/design 或 packet digest、created-after-request、comment revision、raw/normalized digest、受限 current Architecture Agent edge mention、supersession 和 candidate task attribution；`owner_attested` 正式批准还必须精确包含 `materials_opened` 与一个 legal decision；direct parent 仅记录为 audit。automatic packet token-only/explicit profiles继续匹配其 packet identity 与 parent/profile 约束。匹配后自动写 `in_progress --no-start` 并重读，再处理内容决定；无效、编辑、错误 Owner/Action、非法 mention 或过期回复不改变状态。

## Failure and scope expansion

postcondition 失败时保留所有已创建对象，停止未执行写入，把完整 manifest、命令结果、digest、timeline 和失败检查放入 task evidence。用户可见结果只说明发生了什么、当前状态、影响、自动重试是否仍可用和可观察恢复路径。

仍有确定性恢复路径且未耗尽 retry 时自动重试并保持当前 task 执行。没有 Agent 自动路径但存在真正的方案决定时交付/保持 `in_review`。只有没有 Agent 或 human 可执行路径时使用 `blocked`。当前 task 已结束但没有可回读的 accepted/active 下一 task 时，不得保留 `in_progress + WAIT_REASON=none`。

需要新资源、跨范围目标、实现/部署、未在 activation mandate 中准确绑定的 overwrite/conflict strategy 或超出 retry limit 时停止并说明“需要新的任务指令”；不得生成 operational token。明确要求用新版 package 更新准确既有同名 Skill 的 activation mandate 可以冻结 exact existing Skill ID/package digest 与平台 `overwrite` operation，不再拆分 conflict 授权。其他新指令形成新 mandate 后才能生成新 manifest。

## Legacy supersession

`multica_operational_scope_v1`、`AUTHORIZE OPERATION`、delivery/retry/relay/status authorization request 及其回复仅作 legacy audit。新契约激活后：

- 不生成、不 relay、不消费旧 token；
- 旧 request/comment/attachment 保留原样；
- 新 manifest 的 `supersedes` 列出未消费旧 request 和旧 attempt；
- 用户可见评论只说明旧请求已由新自动流程取代，并指向审计 evidence；
- 旧请求的晚到回复不触发写入或状态变化。
