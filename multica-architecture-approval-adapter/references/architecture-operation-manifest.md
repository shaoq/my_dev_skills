# Architecture operation manifest and automatic execution

## Purpose

`architecture_operation_manifest_v1` 是 Adapter 从 current `architecture_workflow_mandate_v1` 派生的 immutable、single-consumption 执行证据。它保留旧 exact operational scope 的最小权限与可重验价值，但不是 Human Action，也不发布 `AUTHORIZE OPERATION` 请求。

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
portable_stage=<current-stage>
attempt_id=<opaque-attempt-id>
core_skill_identity=<name-and-aggregate-digest>
adapter_skill_identity=<name-and-aggregate-digest>
input_identities=<sorted-identities-and-raw-byte-digests>
output_identities=<ordered-filenames-and-raw-byte-digests>
planned_writes=<zero-padded-ordered-writes>
postconditions=<ordered-readback-checks>
retained_objects=<sorted-existing-object-identities-or-none>
retry_limit=<bounded-non-negative-integer>
supersedes=<legacy-request-or-attempt-identities-or-none>
invalidates_on=<frozen-drift-conditions>
```

字段值使用既有 canonical UTF-8 percent encoding；路径必须是已解析且位于 mandate 授权输入根下的相对路径。`planned_writes` 只允许当前 stage 所需的最小集合：work-start `in_progress --no-start`（当前状态不同时）、一条 Decision Brief+附件评论、task evidence、交付成功后的 `in_review --no-start`（仅 `requires_human_review=true`）、以及有效 current 回复后的 `in_progress --no-start`。packet route 还可包含既有 `arch.packet.current` projection 和既有 shared-scope sidecar no-clobber publish。

## Derivation and pre-write fence

Adapter 必须从 mandate 和当前只读事实确定性生成 manifest，不接受用户手写或编辑 manifest。首笔写入前依次：

1. 重读 workspace/Issue/Agent、portable stage、attempt 和 current status；
2. 重算两个 Skill aggregate、全部输入/输出 raw-byte digest；
3. 重验唯一 Decision Owner、current action、`requires_human_review` 和 parent/task attribution；
4. 扫描 retained comments/attachments/projections/sidecars 与 current/superseded identity；
5. 证明 planned writes 是 mandate 允许操作的有序子集，且没有创建资源、跨 Issue/workspace、实现或部署；
6. 计算 manifest raw-byte SHA-256，并写入机器可读 task evidence。

任何 unknown、重复、漂移、缺失或额外写入使 manifest 不可消费。不得为了继续而请求 operational authorization、挑选最近评论、猜 UUID、编辑历史或补写诊断评论。

## Single consumption and automatic writes

完全匹配后立即自动消费 manifest：

- 每一步写入前重读其直接 precondition；
- 每一步写入后重读 exact object/status/digest postcondition；
- 成功对象加入 retained set；
- 一个 manifest 只允许一个 current consumption record；重复触发先 reconciliation，不能重复发布 current delivery；
- 自动 retry 只能在 `retry_limit` 内生成新 attempt/new manifest，并必须冻结新的 retained set；旧 manifest 永不修改或再次消费。

Decision Brief 首行必须准确 mention 唯一 Decision Owner。只有 `requires_human_review=true` 且评论、附件、完整材料入口、mention 和 client access postconditions 全部通过后，才自动写 `in_review --no-start`。非 Review 步骤自动进入下一 stage 或完成当前步骤，不停留等待用户。

有效 Review 回复使用 manifest-bound `valid_human_action_response_v1`，必须精确匹配 actor、direct parent、action ref/version、packet/design digest、comment revision、supersession 和 task attribution。匹配后自动写 `in_progress --no-start` 并重读，再处理内容决定；无效、编辑、错误 Owner/parent 或过期回复不改变状态。

## Failure and scope expansion

postcondition 失败时保留所有已创建对象，停止未执行写入，把完整 manifest、命令结果、digest、timeline 和失败检查放入 task evidence。用户可见结果只说明发生了什么、当前状态、影响、自动重试是否仍可用和可观察恢复路径。

仍有确定性恢复路径且未耗尽 retry 时自动重试并保持 `in_progress`。没有 Agent 自动路径但存在真正的方案决定时交付/保持 `in_review`。只有没有 Agent 或 human 可执行路径时使用 `blocked`。

需要新资源、跨范围目标、实现/部署、未在 activation mandate 中准确绑定的 overwrite/conflict strategy 或超出 retry limit 时停止并说明“需要新的任务指令”；不得生成 operational token。明确要求用新版 package 更新准确既有同名 Skill 的 activation mandate 可以冻结 exact existing Skill ID/package digest 与平台 `overwrite` operation，不再拆分 conflict 授权。其他新指令形成新 mandate 后才能生成新 manifest。

## Legacy supersession

`multica_operational_scope_v1`、`AUTHORIZE OPERATION`、delivery/retry/relay/status authorization request 及其回复仅作 legacy audit。新契约激活后：

- 不生成、不 relay、不消费旧 token；
- 旧 request/comment/attachment 保留原样；
- 新 manifest 的 `supersedes` 列出未消费旧 request 和旧 attempt；
- 用户可见评论只说明旧请求已由新自动流程取代，并指向审计 evidence；
- 旧请求的晚到回复不触发写入或状态变化。
