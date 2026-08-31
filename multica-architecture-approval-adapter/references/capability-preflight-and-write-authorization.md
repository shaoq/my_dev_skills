# Capability preflight and manifest write fence

## Boundary

文件名为兼容既有引用保留；新契约不使用 human write authorization。Issue delivery 只在 current `architecture_workflow_mandate_v1` 与自动派生的 `architecture_operation_manifest_v1` 同时 current、匹配且可重验时执行。`AUTHORIZE OPERATION`、`multica_operational_scope_v1` 或历史 task-result authorization comment 不是 precondition。

Skill import、Agent binding、资源创建、Runtime 配置、CLI 安装/升级、私有 API、跨 Issue/workspace、overwrite/delete/edit 历史对象和业务实现不属于普通 Issue delivery。它们只有在明确的新任务指令建立对应 mandate 时才可进入新的 manifest；缺失资源永不自动创建。

## No-side-effect pre-write checks

在首笔写入前记录以下 ordered checks：

| Check | Required observed behavior | Failure result |
|---|---|---|
| `mandate_current` | mandate 精确绑定 current workspace/Issue/stage/attempt/Agent 与允许操作 | stop; request a new task instruction only if scope changed |
| `issue_workspace_identity` | 既有 Issue 属于准确 workspace | unavailable; no write |
| `command_profile_surface` | 当前 CLI/profile 和 scope-matched capability certificate 支持 planned comment/attachment/status/metadata writes | unavailable; no install/upgrade |
| `input_paths_and_frozen_digests` | 所有路径在 manifest root 内，raw-byte digest 匹配 | unavailable; no write |
| `target_human_and_action` | canonical member、current action/version、`requires_human_review` 唯一且匹配 | unavailable; no write |
| `retained_object_scan` | 历史 comments/attachments/projections/sidecars 与 supersession set 已冻结 | unavailable; no duplicate current delivery |
| `metadata_read` | packet route 可读取 bounded `arch.packet.current`；material route 为 `not_applicable` | unavailable; no repair |
| `manifest_revalidation` | manifest payload/digest、Skill aggregates、ordered writes 和 invalidation facts 无漂移 | unavailable; no write |

help/source 文本或记忆不是 live capability 证明。unknown、unsupported、malformed 或不可重验一律失败关闭。

## Live proof and postconditions

通过 fence 后，首个 comment write 是 live proof boundary。comment JSON、actual parent、author、canonical mention、attachment bindings、thread reread、stable entry、raw-byte re-download 和逐 client opening 都是 postconditions。每一步只在前一步 postcondition 通过后执行 manifest 的下一项。

`--attachment` 只引用冻结路径和 digest；禁止 independent upload/orphan resource。`--parent` 只能来自 current task attribution 或 current Review trigger 的准确 selector，不能猜 UUID、选 latest comment 或 thread root。packet-only metadata/sidecar 继续受其直接 postconditions 和 no-clobber 约束。

Human Review delivery 成功后自动执行 `in_review --no-start` 并重读；有效 Review reply 开始处理时自动执行 `in_progress --no-start` 并重读。非 Review 操作不等待用户授权。

## Failure evidence

失败证据通过 task result / machine audit 记录：manifest ref/digest、check、observed command/profile、result、retained objects、owner、closing condition 和 status timeline。除非 diagnostic comment 本身已列入 manifest，否则不得追加评论。平台自动 materialize task result 时如实记录 platform-managed comment identity，但不得把它变成 authorization request。

仍有 bounded deterministic recovery 时自动创建新 attempt/new manifest；否则停止。范围扩大用自然语言要求新的任务指令，不生成 operational token。
