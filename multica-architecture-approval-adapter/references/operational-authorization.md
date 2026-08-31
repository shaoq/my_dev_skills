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

### Comment-triggered parent selector

When the operational authorization response itself will trigger a comment-delivery task, the response comment UUID does not exist while the scope payload is being frozen. In that one case, `planned_writes` MUST encode the canonical selector:

```text
parent=multica_authorization_response_parent_v1
```

This is a constrained runtime binding, not a wildcard. `bound_identity` MUST include the exact authorization request comment ID, authorization ID, expected response digest, Issue, workspace, operational Decision Owner and delivery attempt. Do not prebind a prior comment UUID, latest comment, thread root or guessed future UUID.

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

For `multica_authorization_response_parent_v1`, resolve the selector only to the current task's `trigger_comment_id` after verifying all of the following against frozen scope: same workspace and Issue; exact member author and operational Decision Owner; direct parent equals the authorization request comment; outer-whitespace-trimmed content equals the exact expected response; comment is revision 1 and unedited; and task attribution evidence ref equals the same trigger comment. The write then uses that resolved UUID as the actual CLI `--parent`, and reread must confirm it. Any mismatch is no-op/fail closed.

The authorization response is human evidence, not an adapter write. An authorization-request comment, failure diagnostic, repair note, Issue status change or any other Issue comment is forbidden unless it appears as its own exact `planned_writes` item. Without that authority, return the request or diagnostic in the task result only; do not create a comment to explain why no comment was allowed.
