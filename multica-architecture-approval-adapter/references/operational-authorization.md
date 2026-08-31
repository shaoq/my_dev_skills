# Operational authorization protocol

## Authority boundary

`multica_operational_scope_v1` is the only adapter profile for authorizing a new Multica or shared-scope write. It is operational authority only: it cannot decide architecture content, change core state, or expand beyond the exact current request.

## Canonical scope payload

Build exactly these ten LF-separated lines in fixed order, including one final LF after the last line:

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

Every placeholder is encoded using canonical percent encoding of UTF-8 bytes: preserve only `A-Z`, `a-z`, `0-9`, `.`, `_`, `-`, and `~`; encode every other byte as `%` plus two uppercase hexadecimal digits. The parser rejects lowercase/non-canonical escapes, invalid UTF-8, unknown/duplicate/reordered fields and an absent final LF.

Normalize path/object lists before escaping. Paths are relative to the explicitly confirmed scope, contain no leading slash、`..`、home expansion、drive prefix、query string or symlink escape, are sorted by raw UTF-8 byte order and joined with ASCII comma. Retained object identities use the same sorting. `planned_writes` preserves execution order and prefixes each entry with a zero-padded ordinal such as `01:` before joining with ASCII comma; no duplicate target is allowed.

For a Human Action delivery, `planned_writes` MUST explicitly freeze every applicable status write as a distinct ordinal: work-start `in_progress --no-start` when the observed status differs, the comment/attachments, postcondition-gated `in_review --no-start`, and deferred response-start `in_progress --no-start` with `selector=valid_human_action_response_v1`. The selector is bound to the current action ref, delivery comment, Decision Owner, exact response grammar, Issue/workspace and task attribution. It is single-use and cannot match an edited, superseded, wrong-parent or wrong-author reply. Status writes omitted from the scope are forbidden; a delivery authorization that omits required lifecycle writes is incomplete and causes no delivery write.

### Platform-managed task-result authorization-request selector

When Multica automatically materializes a preparation task result as the authorization-request comment, that comment UUID does not exist while the scope payload is being frozen. In that one case, the canonical authorization bundle MUST declare:

```text
authorization_request=multica_task_result_authorization_request_v1
```

This is a constrained expected retained-object selector, not a wildcard and not an additional Agent-invoked write. `bound_identity` MUST freeze the exact preparation task ID, preparation trigger comment ID, request Agent ID, authorization ID, Issue, workspace, operational Decision Owner, delivery attempt and material identities/digests. `retained_objects` MUST include `comment:multica_task_result_authorization_request_v1`.

After platform materialization and before consuming any response, resolve the selector to exactly one current comment that satisfies every frozen fact: `source_task_id` equals the preparation task ID; direct parent equals the preparation trigger; author type and ID equal the request Agent; revision is 1 and unedited; the parsed authorization ID, canonical scope payload and scope digest equal the frozen request; and the comment belongs to the same Issue/workspace. Use a read surface that preserves `source_task_id`; a compact view that omits it is insufficient. Missing, duplicate, edited, malformed or mismatched candidates fail closed and require a new preparation attempt. Never guess a future UUID or select the latest comment or thread root.

Multica's automatic materialization is a platform-managed task result comment. It is not an Agent invocation of an Issue write, but it is still an observable platform comment and MUST be reported truthfully: “未主动调用 Issue write；Multica 将 task result 自动投递为平台管理评论”. Do not claim that no platform comment was produced.

### Comment-triggered response-parent selector

When the operational authorization response itself will trigger a comment-delivery task, the response comment UUID does not exist while the scope payload is being frozen. In that one case, `planned_writes` MUST encode the canonical selector:

```text
parent=multica_authorization_response_parent_v1
```

This is a constrained runtime binding, not a wildcard. `bound_identity` MUST include the authorization-request binding (either an already exact comment ID or `multica_task_result_authorization_request_v1` with its frozen preparation identity), authorization ID, Issue, workspace, operational Decision Owner and delivery attempt. The expected one-line response is derived from the frozen authorization ID and canonical scope digest; do not place a self-referential future response digest in `bound_identity`. Do not prebind a prior response UUID, latest comment, thread root or guessed future UUID.

Compute `scope_digest=sha256:<64 lowercase hex>` over the canonical payload's exact raw UTF-8 bytes, including the final LF. Do not normalize Unicode, whitespace or line endings after construction.

## Exact response

The authorize response is exactly one line after trimming outer whitespace:

```text
AUTHORIZE OPERATION <authorization_id> scope=<scope_digest>
```

The deny response is exactly:

```text
DENY OPERATION <authorization_id> reason=<canonical-percent-escaped-reason>
```

The current recognizable operational Decision Owner must author the response. Recompute the payload and digest immediately before the first write; any changed target, path, retained object, planned write, conflict or attempt supersedes the request and requires a new authorization. A response bound to a superseded digest is audit-only/no-op.

## Consumption and evidence

Record authorization comment/ref, actor, scope payload/digest, current/superseded, created/updated/recorded times and reread result. Before every write, confirm the operation is the next exact `planned_writes` item and all prior postconditions passed. Authorization never bypasses preflight, no-clobber, stale-writer, identity-conflict or final no-more-writes rules.

The delivery comment/attachment postconditions gate the `in_review` write. Re-read the Issue after the command and require `status postcondition=in_review`. At a later valid response task, resolve `valid_human_action_response_v1`, execute only its frozen deferred `in_progress --no-start` item, re-read, and require `status postcondition=in_progress` before processing the response. A failed status postcondition retains prior objects and fails closed; it does not authorize repair, edit, delete, diagnostic comment or another status write.

When `multica_task_result_authorization_request_v1` is present, first resolve and record its actual request comment ID using the preparation-task rules above; this observed evidence does not alter the frozen scope payload. Only then resolve `multica_authorization_response_parent_v1` to the current task's `trigger_comment_id` after verifying all of the following against frozen scope: same workspace and Issue; exact member author and operational Decision Owner; direct parent equals the resolved authorization request comment; outer-whitespace-trimmed content equals the exact response derived from the frozen authorization ID and scope digest; comment is revision 1 and unedited; and task attribution evidence ref equals the same trigger comment. The write then uses that resolved response UUID as the actual CLI `--parent`, and reread must confirm it. Any missing, duplicate, edited or mismatched request/response is no-op/fail closed and MUST NOT cause a diagnostic Issue comment.

The authorization response is human evidence, not an adapter write. An Agent-invoked authorization-request comment, failure diagnostic, repair note, Issue status change or any other Agent-invoked Issue comment is forbidden unless it appears as its own exact `planned_writes` item. Without that authority, return the request or diagnostic in the task result only; do not call an Issue write to explain why no comment was allowed. If the platform automatically materializes that task result, record the platform-managed comment identity and do not misreport it as “no platform comment”.
