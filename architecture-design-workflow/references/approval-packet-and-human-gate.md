# Approval packet and human gate

## Current surface contract

`ARCH-APPROVAL-PACKET` 是 `machine_only` immutable approval manifest，属于 `architecture_internal_evidence_v1`。它冻结 Design/Review identity、maturity、accepted risks、Owner、current Action、access/readiness 与 supersession，但不是人类阅读材料。`human_review_surface_v1` 只暴露一份 canonical Design、简短 Review/风险/推荐、决定后果和一个 current Action；不要求人类打开 Packet、完整 Review、Control 或 Research，也不要求复制 packet digest。current Action 从机器验证过的 packet snapshot 继承 ref/version/digest，回复只绑定 current Action。

旧 packet-bound、三附件或复制 digest 的 attempt 继续按冻结 reader 审计；新 writer 不改写、不消费为当前 surface，升级必须创建 superseding attempt。

## Purpose

`ARCH-APPROVAL-PACKET vN` 是平台无关、machine-only 的不可变 manifest。它冻结一个 Work Item 的准确 `ARCH-DESIGN`/`ARCH-REVIEW` 组合、maturity、Owner、current Action、审核摘要和合法决定集合，但不包含验证自身 digest 的 post-finalization evidence，也不作为人类附件。

## Packet lifecycle

- 可变 draft 不属于版本化 packet，也不能进入 gate。
- 同一 Work Item 的 delivered versions 从 `v1` 开始单调递增。
- delivered payload 固定 `payload_status=delivered`；交付后 bytes 永不改写。
- material revision 创建下一版本，并在新 payload 的 `supersedes` 中引用旧版本。
- `ARCH-CONTROL` 可以把旧版本投影为 superseded，但不得修改旧 payload 或 digest。
- `created_at`、`verified_at`、`recorded_at` 使用 RFC 3339 UTC `Z`。

## Raw-byte digest contract

每个 artifact 使用：

```text
digest_algorithm=sha256
digest_encoding=lowercase_hex
digest_value=sha256:<64 lowercase hex characters>
```

digest 输入是冻结后的原始文件 bytes。不得隐式转换字符编码、Unicode、空白或换行；文本 media type 必须声明 charset。packet 完成全部 payload 字段后才计算自身 digest。验证 packet 的 readiness/unavailable evidence 保存在 `ARCH-CONTROL`、standalone sidecar 或 durable record 中，只引用 packet ref/version/digest，不写回 packet。

## Access profiles

### `local_file`

只有以下条件全部满足时才证明目标人类可访问：

1. artifact 位于当前人类已选择或确认的 shared workspace scope；
2. ref 是该 scope 内的稳定相对路径；
3. evidence 记录 `human_actor`、scope、access confirmation ref、确认时间和 verifier；
4. verifier 从同一 ref 读取原始 bytes，并得到匹配 digest；
5. access confirmation 未撤回且 scope 未改变。

仅 Agent 进程能读取、本机绝对路径存在或没有目标 human actor confirmation 时必须失败关闭。

### `durable_platform_ref`

未来 adapter 可以提供等价的 durable access guarantee，但 core 只消费 portable ref/version/digest、actor、scope、verification time 和 verifier，不解释专有 ID。

## Readiness evidence envelope

`review_packet_ready` 至少包含：

```text
evidence_type=review_packet_ready
evidence_ref
packet_ref / packet_version / packet_digest
design_ref / design_version / design_digest
review_ref / review_version / review_digest / review_conclusion
human_actor / access_evidence_refs
verifier / verified_at
```

只有准确 refs/versions/digests、完整审核简报、approvable Review conclusion 和下述当前 access mode 条件同时成立才可生成。readiness 不等于人工批准。

- `automatic`：目标人类在每个 requested scope 的完整 human-readable rendering 均已由具名 verifier 实际打开并确认。
- `owner_manual`：唯一 Decision Owner 已通过 current mandate 或 deployment policy 明确选择自行检查；Runtime 已验证准确 artifact identity/type/version/digest、完整 raw bytes、current/superseded identity、同一 work item 的稳定可导航入口和 current Action。每个 requested scope 必须保持 `manual_check_required`，不得声称 `opened`。此时 content-decision activation gate 可以为 ready，但合法决定必须同时包含 Owner 对完整材料已打开的显式声明；材料打不开的准确回复只触发修复，不构成内容决定。

`review_packet_unavailable` 使用同一 identity/digest fields，并增加 `failed_checks`、`owner`、`closing_condition`。缺少 readiness 或任一检查失败时保持 `reviewing`，保留真实 Review conclusion，设置 `BLOCKED_REASON=review_packet_unavailable`。

`owner_manual` 绝不放宽机器完整性门禁。artifact identity、digest、稳定入口、唯一 Owner、current Action 或 durable readiness 任一缺失或漂移时仍生成 `review_packet_unavailable`。Owner 使用“材料打不开”的 exact response 时，当前内容决定必须保持 `none`，action 回到 preparation 并先修复或重新发布材料入口。

## Architecture recommendation

每个 packet 恰好包含一个：

- `recommend_approved_for_spec`
- `recommend_approved_design_only`
- `recommend_revision`
- `no_recommendation`

同时给出中文理由、适用条件和关键风险。recommendation 不是 human decision，不得改变 stage、gate 或授权状态。

## Human decision binding

合法决定只有：

- `approved_design_only`
- `approved_for_spec`
- `revision_requested`
- `rejected`

decision evidence 必须包含 decision、可识别 `human_actor`、current Action identity、继承的 manifest snapshot、binding profile、evidence ref 和 RFC 3339 UTC recorded time。当前交互 profile 只接受 Runtime 标记为当前 user-role 的消息；引用文本、fixture、Agent 输出、推荐、Review conclusion、紧急措辞、任务分派或模糊肯定均不构成决定。

绑定 superseded packet 的合法决定保留审计但对当前 gate no-op。`revision_requested` 开始新 `ARCH-DESIGN`，并只在 replacement design/review 再次 approvable 后创建新 packet。`rejected` 仅在绑定 current ready packet 时进入终态。

## Human-facing approval action

current ready manifest 等待决定时，生成一个 `action_type=architecture_approval` Human Action Request；历史 `design_approval` 仅作兼容读取。请求首屏先给 Decision Owner、Design maturity、简短 Review、关键风险、candidate recommendation（若有）和四个选项的中文对比；随后只放一份 canonical Design 的稳定入口，完整 internal refs/digests 后置或隐藏。

四个选项必须分别说明：

- `approved_design_only`：只发布 ADR/详细设计，进入 design-only 完成路径；不生成研发授权；
- `approved_for_spec`：发布批准文档，目标项目存在时生成 R&D handoff；不自动创建 OpenSpec、Issue、branch 或代码；
- `revision_requested`：进入新设计迭代，不修改旧 packet；修订说明作为独立非授权 context，缺失时另建 `design_input` 请求；
- `rejected`：current work item 进入 `rejected` 终态，具有明确不可逆流程影响。

每项同时列出立即 stage、remaining blockers、Next Owner、planned writes 和不可逆影响。新 writer 的 Exact response 必须包含 current Action ID 与一个决定值；`owner_manual` 还必须包含 Owner 对完整材料已打开的显式声明。Action 从 manifest 继承准确 ref/version/digest，Owner 不复制 packet digest。旧 packet-bound exact response 仅在 frozen legacy reader 中继续解析。

## Revision context

正式 decision evidence 与 revision brief 分开记录。有效 `revision_requested` 不因 brief 缺失而失效；状态进入新版本 `designing`，并记录 `revision_scope=missing`。随后由原决定人或明确的 Design Decision Owner 通过 `action_type=design_input` 补齐范围、优先级、约束和验收变化。旧 packet 永不改写，replacement packet 只能在新 design/review 再次 approvable 后创建。

## Compatibility and publication

升级前已持久化在 `waiting_human` 且本次没有新 design/review version 或显式 refresh 的记录保持原 stage；不得伪造 readiness 或自动降级。显式 refresh 后执行新 packet gate。

发布前重新读取 packet、design、review 原始 bytes 并核对 frozen digests。无法恢复时保持 `publishing` 和原批准/readiness，设置 `BLOCKED_REASON=approved_artifact_unavailable`，记录失败 artifact、Owner 和 closing condition；不得从审核简报重建近似正文。准确 bytes 恢复并重新验证后清除 blocker，继续同一批准的发布流程。
