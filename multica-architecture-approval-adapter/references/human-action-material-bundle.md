# Human action material bundle

## Profile and scope

`multica_human_action_material_bundle_v1` delivers a current core Architecture Decision Brief and the complete materials needed for one authorized human action before or after packet creation. It is separate from packet readiness and never creates a Review conclusion, recommendation, approval token or core state transition.

The route requires:

- one current core Human Action Request with one atomic decision, one Decision Owner and one authority scope;
- a uniquely bound current Multica member for that Owner, or a routing/owner-binding action instead of a content action;
- a complete standalone `ARCH-DESIGN-vN.md` with canonical UTF-8 Markdown bytes, artifact version and raw-byte digest;
- exact Research and Control identities and complete human-facing entries;
- one existing workspace and Issue; and
- current exact operational authorization for all input paths, one comment write, attachments and retained objects.

No approvable Review or packet is required for a design-input bundle. Conversely, this profile never substitutes for the separate immutable packet delivery/readiness route.

## Bundle contents

The required attachment is:

```text
ARCH-DESIGN-vN.md
```

Its filename, `text/markdown` media type, design version and SHA-256 over exact raw bytes are frozen before delivery. Do not reserialize, normalize newlines or rebuild it from Issue comments.

Research and Control use verified `multica_web_comment_permalink_v1` entries when their exact complete comments remain available. If either entry cannot pass the requested client checks, include its exact source as `ARCH-RESEARCH-vN.md` or `ARCH-CONTROL-vN.md` in the same authorized bundle.

When current capability evidence says canonical Markdown is not comfortably readable in a requested client, include:

```text
ARCH-DESIGN-vN.pdf
derived_non_authoritative=true
source_digest=sha256:<canonical-markdown-digest>
```

The PDF is a reading copy only. It cannot replace the Markdown attachment, design identity or approval digest. If a missing PDF is discovered only after delivery, the attempt is unavailable; a later superseding bundle requires a new authorization listing retained objects and the new one comment write. Never append or edit the old comment.

## Operational authorization

Use `operation_variant=delivery` in `multica_operational_scope_v1`. Set `bound_identity` to the current action ID, Design version/digest and opaque delivery attempt. `authorized_paths` lists every exact Decision Brief, canonical Markdown, optional PDF and fallback Markdown input. `planned_writes` contains the exact ordered state/comment lifecycle: current-work `in_progress --no-start` only when needed, one Issue comment with all selected attachments, postcondition-gated `in_review --no-start`, and one deferred `in_progress --no-start` bound to `valid_human_action_response_v1`. No status transition is implicit.

If the preparation task result will be automatically materialized as the authorization request, the bundle declares `authorization_request=multica_task_result_authorization_request_v1`, freezes its preparation task ID, trigger comment, request Agent, authorization ID, Issue/workspace, Owner, attempt and material digests, and lists `comment:multica_task_result_authorization_request_v1` as an expected retained object. After materialization, resolve exactly one request comment by `source_task_id`, parent, Agent, revision-1 unedited content, parsed canonical scope and uniqueness. Record the actual ID as observed evidence without changing the frozen payload.

When the human authorization response triggers execution, freeze `parent=multica_authorization_response_parent_v1` in that write. At runtime first resolve the authorization request above, require the response to be its direct child, then resolve the response selector only to the verified current task `trigger_comment_id` under the operational authorization rules. Do not freeze the earlier preparation comment as delivery parent. Do not include packet metadata projection or readiness sidecars for a pre-packet action.

Also freeze the command's execution working directory. Keep all paths relative to the authorized common material root when possible. If the content or any attachment is intentionally outside that directory, the authorized command profile must state `allow_external_file=true` and execution must add `--allow-external-file`; neither the cwd nor the flag may be changed after authorization.

The write is one comment, not an independent upload:

```bash
multica issue comment add <issue> \
  --content-file <architecture-decision-brief.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  [--attachment <ARCH-DESIGN-vN.pdf>] \
  [--attachment <ARCH-RESEARCH-vN.md>] \
  [--attachment <ARCH-CONTROL-vN.md>] \
  [--parent <actual-trigger-comment-id>] \
  --output json
```

The actual response trigger comment ID is mandatory for the executed CLI command. The request and response symbolic selectors exist only to bind future platform identities and MUST resolve in order—first `multica_task_result_authorization_request_v1`, then `multica_authorization_response_parent_v1`—before execution. A generated thread root, prior authorization response, latest-comment search, orphan attachment, later edit, append, relabel, delete or second unlisted write is outside the authorization.

The authorized status commands are public CLI writes and MUST be frozen exactly as applicable:

```bash
multica issue status <issue> in_progress --no-start
multica issue status <issue> in_review --no-start
```

While the Agent is preparing or consuming a valid response, the Issue is `in_progress`. After the exact comment, attachments, mention, parent, digest and requested access postconditions succeed, set the Issue to `in_review`; this is the visible “waiting for the mentioned human” state. A remaining `critical_evidence_gaps` record does not change that projection when the delivered request gives a unique Owner an executable closing action. Use `blocked` only when no executable Agent or human path exists, never as a synonym for waiting for confirmation.

The deferred response transition uses `selector=valid_human_action_response_v1`. It resolves only when one task trigger is a revision-1 unedited direct reply by the exact Decision Owner to the current delivery comment, contains the exact action-bound response, belongs to the same Issue/workspace, and matches task attribution. After that selector validates, set the Issue to `in_progress --no-start` and verify the status postcondition before processing the response. Invalid, superseded, wrong-owner or wrong-parent responses are no-write/fail-closed.

Status changes, Agent-invoked authorization-request comments and fail-closed diagnostic comments are separate writes. If the required status writes are absent from exact `planned_writes`, the delivery is not authorized as a complete Human Action lifecycle and the Agent performs no partial substitute. Multica may automatically expose a task result as a platform-managed task result comment; record that actual comment and say “未主动调用 Issue write；Multica 将 task result 自动投递为平台管理评论”，而不是声称没有平台评论。

## Postconditions

Parse the response and re-read the exact new comment. Require the expected agent author, actual parent, exact Decision Brief headings, exactly one actionable action for the bound member, and every selected attachment identity bound to that comment. Re-download canonical Markdown, hash raw bytes and match the frozen digest.

Require the first rendered line to contain `mention://member/<canonical-member-id>` for the same Decision Owner. After all delivery and access postconditions pass, execute the authorized `in_review --no-start` write and re-read the Issue; `status postcondition=in_review` is part of success. If the status cannot be verified, retain the comment/attachments, return partial-failure evidence and require a new incremental authorization; do not edit, delete, append or issue an unplanned repair comment.

Then apply [human-accessible evidence links](human-accessible-evidence-links.md) to each Design, Research and Control entry. Record `web|mobile` separately as `opened|unavailable|not_run`; a filename, attachment card presence or Agent download alone is insufficient. If the exact new entries lack complete requested-client evidence before publication, this bundle's one actionable request MUST be `action_type=access_confirmation`; the intended design input, risk acceptance or approval remains non-actionable pending context. If any required complete material cannot be opened for the requested scope, retain all objects, mark the material delivery unavailable and do not treat the content decision as ready.

After the exact access action succeeds and its evidence re-verifies, create a new current core Human Action Request version for the content decision. Delivering that later request is a new `multica_human_action_material_bundle_v1` attempt with a new exact operational authorization; it may repeat the canonical attachment but MUST list retained objects and must not edit or append to the access-confirmation comment. Access confirmation never becomes content-decision authority.

This profile never writes `arch.packet.current`. If a later Review becomes approvable, the packet delivery route performs its own compatibility, authorization, immutable three-attachment delivery and readiness checks.
