# Approval packet and human gate

## Purpose

`ARCH-APPROVAL-PACKET vN` 是平台无关、面向人类裁决的不可变 payload。它冻结一个 Work Item 的准确 `ARCH-DESIGN`/`ARCH-REVIEW` 组合、审核简报和合法决定集合，但不包含验证自身 digest 的 post-finalization evidence。

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

只有准确 refs/versions/digests、confirmed access、完整审核简报和 approvable Review conclusion 同时成立才可生成。readiness 不等于人工批准。

`review_packet_unavailable` 使用同一 identity/digest fields，并增加 `failed_checks`、`owner`、`closing_condition`。缺少 readiness 或任一检查失败时保持 `reviewing`，保留真实 Review conclusion，设置 `BLOCKED_REASON=review_packet_unavailable`。

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

decision evidence 必须包含 decision、可识别 `human_actor`、当前 packet ref/version/digest、binding profile、evidence ref 和 RFC 3339 UTC recorded time。当前交互 profile 只接受 Runtime 标记为当前 user-role 的消息；引用文本、fixture、Agent 输出、推荐、Review conclusion、紧急措辞、任务分派或模糊肯定均不构成决定。

绑定 superseded packet 的合法决定保留审计但对当前 gate no-op。`revision_requested` 开始新 `ARCH-DESIGN`，并只在 replacement design/review 再次 approvable 后创建新 packet。`rejected` 仅在绑定 current ready packet 时进入终态。

## Compatibility and publication

升级前已持久化在 `waiting_human` 且本次没有新 design/review version 或显式 refresh 的记录保持原 stage；不得伪造 readiness 或自动降级。显式 refresh 后执行新 packet gate。

发布前重新读取 packet、design、review 原始 bytes 并核对 frozen digests。无法恢复时保持 `publishing` 和原批准/readiness，设置 `BLOCKED_REASON=approved_artifact_unavailable`，记录失败 artifact、Owner 和 closing condition；不得从审核简报重建近似正文。准确 bytes 恢复并重新验证后清除 blocker，继续同一批准的发布流程。
