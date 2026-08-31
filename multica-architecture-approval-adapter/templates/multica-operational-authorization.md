# Legacy Multica Operational Authorization Record — audit only

> 禁止用于新请求。此模板只渲染历史 `multica_operational_scope_v1` 记录与 supersession 证据；current workflow 使用自动派生的 `architecture_operation_manifest_v1`，不得要求用户复制 `AUTHORIZE OPERATION`。

## 现在需要授权什么

- `action_type=operational_authorization`
- Authorization ID / current status：`{{authorization_id}}` / `current|superseded`
- Operation variant：`delivery|target_human_mapping|shared_sidecar|activation|conflict_strategy|sandbox|retry`
- Decision Owner：`{{authorized_human_actor}}`
- Why now：{{why_now_zh}}

## Existing target identities

- Workspace：`{{existing_workspace_identity}}`
- Issue：`{{existing_issue_identity_or_na}}`
- Agent：`{{existing_agent_identity_or_na}}`
- Skill / packet / attempt：`{{existing_bound_identities}}`

## Exact planned writes

| Order | Operation / command profile | Exact target | New or reused |
|---|---|---|---|
| {{order}} | {{operation_or_command_profile}} | {{exact_target}} | {{new_or_reused}} |

- Authorized paths / scope：`{{exact_authorized_paths_and_scope}}`
- Incremental retry scope：`{{incremental_writes_or_na}}`
- No-clobber / conflict strategy：`{{no_clobber_or_explicit_strategy}}`
- Scope profile：`scope_profile=multica_operational_scope_v1`
- Canonical scope payload ref：`{{canonical_scope_payload_ref}}`
- Scope digest：`scope_digest=sha256:{{canonical_scope_payload_raw_utf8_sha256}}`
- Task-result authorization-request selector：`{{multica_task_result_authorization_request_v1_or_na}}`
- Frozen request preparation：`source_task_id={{preparation_task_id_or_na}}`；trigger=`{{preparation_trigger_comment_id_or_na}}`；Agent=`{{request_agent_id_or_na}}`
- Expected / resolved request object：`authorization_request=multica_task_result_authorization_request_v1` / `{{resolved_request_comment_id_or_pending_or_na}}`；仅在 source task、parent、Agent、revision、准确授权内容和唯一性均匹配后解析。
- Comment-triggered response-parent selector：`{{multica_authorization_response_parent_v1_or_na}}`；先解析上述 request，再只解析为通过 exact Owner/direct-parent/content/revision/Issue/workspace/task-attribution 校验的当前 `trigger_comment_id`。

## Retained objects and failure behavior

- Retained objects：`{{existing_objects_preserved_on_success_or_failure}}`
- Failure behavior：{{fail_closed_behavior_zh}}
- Stop / rollback boundary：{{stop_or_rollback_boundary_zh}}

## Risks and exclusions

- Risks：{{operational_risks_zh}}
- Excluded operations：{{unlisted_writes_resource_creation_delete_overwrite_or_configuration}}
- Unlisted authorization/diagnostic/status comments：禁止；仅可通过 task result 返回。
- Platform materialization：Agent 未主动调用 Issue write 时，仍须记录 Multica 自动投递的 platform-managed task result comment；不得声称没有平台评论。
- Does not authorize：任何架构内容决定、Review conclusion、packet gate、发布范围扩大或未列出的写入。

## Exact authorize / deny response

授权：

```text
AUTHORIZE OPERATION {{authorization_id}} scope=sha256:{{canonical_scope_payload_raw_utf8_sha256}}
```

拒绝：

```text
DENY OPERATION {{authorization_id}} reason={{canonical_percent_escaped_reason}}
```

仅当前、由准确 Decision Owner 作出并绑定 exact scope 的回复有效；模糊肯定、旧请求回复或范围不完整的授权都不允许执行写入。

## After response

| Response | Allowed next operation | Remaining blockers | Next Owner | Evidence / planned writes |
|---|---|---|---|---|
| authorize | {{exact_allowed_next_operation}} | {{remaining_blockers}} | {{next_owner}} | {{authorization_evidence_and_writes}} |
| deny | no write | authorization denied | {{next_owner}} | retain existing objects |

## Audit binding

- Bound request / target digest：`{{bound_request_or_target_digest}}`
- Current / superseded：`current|superseded`
- Recorded evidence / time：`{{evidence_ref_or_pending}}` / `{{recorded_at_or_pending}}`
