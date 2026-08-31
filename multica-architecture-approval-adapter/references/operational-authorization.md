# Legacy operational authorization protocol — audit only

## Status

`multica_operational_scope_v1` 是旧版 Adapter 的历史格式。新 `architecture_workflow_mandate_v1` 路径 MUST NOT 生成、渲染、relay、等待或消费该协议，也 MUST NOT 把它当作 preparation、delivery、attachment、status、retry、sidecar、verification、activation 或 conflict handling 的门禁。

本 reference 只允许：

- 识别和解析既有 audit records；
- 将未消费 request 标为 `superseded/audit-only`；
- 把旧 request/comment identity 写入新 `architecture_operation_manifest_v1.supersedes`；
- 证明晚到回复没有触发新写入或状态变化。

所有新自动操作使用 [architecture operation manifest](architecture-operation-manifest.md)。范围扩大时要求自然语言的新任务指令，不生成新的 authorization token。

## Legacy payload grammar

为保证历史记录可重验，解析器仍可读取固定十行 LF payload：

```text
scope_profile=multica_operational_scope_v1
authorization_id=<escaped-id>
operation_variant=<delivery|target_human_mapping|shared_sidecar|activation|conflict_strategy|sandbox|retry>
workspace_id=<escaped-existing-id>
issue_id=<escaped-existing-id-or-none>
agent_id=<escaped-existing-id-or-none>
bound_identity=<escaped-packet-skill-attempt-or-conflict-identity>
authorized_paths=<escaped-normalized-path-list-or-none>
planned_writes=<escaped-ordered-write-list-or-none>
retained_objects=<escaped-sorted-object-list-or-none>
```

历史 exact response 形态为：

```text
AUTHORIZE OPERATION <authorization_id> scope=<scope_digest>
DENY OPERATION <authorization_id> reason=<canonical-percent-escaped-reason>
```

解析成功只证明历史字节符合旧格式，不证明 current authority。新契约下一律：

```text
legacy_request_status=superseded|audit_only
effective_for_current_manifest=no
allowed_new_writes=none
```

## Legacy selectors

`multica_task_result_authorization_request_v1` 与 `multica_authorization_response_parent_v1` 可以为了审计重建 source task/direct-parent/author/revision/content 关系，但不得解析为新 delivery parent 或 current trigger。新路径只使用 current workflow trigger、Review delivery comment 和 `valid_human_action_response_v1` 的 manifest-bound selectors。

任何旧 request 的缺失、重复、编辑、错误 actor/parent、旧 attempt 或晚到回复都保留为审计事实。不得为“修复旧授权”编辑历史、追加评论、请求新 token 或恢复旧流程。
