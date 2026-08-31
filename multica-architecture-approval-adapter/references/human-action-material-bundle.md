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

Use `operation_variant=delivery` in `multica_operational_scope_v1`. Set `bound_identity` to the current action ID, Design version/digest and opaque delivery attempt. `authorized_paths` lists every exact Decision Brief, canonical Markdown, optional PDF and fallback Markdown input. `planned_writes` contains exactly one ordered Issue comment write with all selected attachments. When the human authorization response triggers execution, freeze `parent=multica_authorization_response_parent_v1` in that write and bind the exact authorization request identity; at runtime resolve it only to the verified current task `trigger_comment_id` under the operational authorization rules. Do not freeze the earlier preparation comment as delivery parent. Do not include packet metadata projection or readiness sidecars for a pre-packet action.

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

The actual trigger comment ID is mandatory for the executed CLI command. The symbolic selector exists only in the pre-response canonical authorization scope and MUST resolve to that exact ID before execution. A generated thread root, prior authorization response, latest-comment search, orphan attachment, later edit, append, relabel, delete or second unlisted write is outside the authorization.

Material preparation and delivery leave the Issue `in_progress`. Status changes, authorization-request comments and fail-closed diagnostic comments are separate writes and are not implied by this bundle. If they are absent from exact `planned_writes`, return their content in the task result only.

## Postconditions

Parse the response and re-read the exact new comment. Require the expected agent author, actual parent, exact Decision Brief headings, exactly one actionable action for the bound member, and every selected attachment identity bound to that comment. Re-download canonical Markdown, hash raw bytes and match the frozen digest.

Then apply [human-accessible evidence links](human-accessible-evidence-links.md) to each Design, Research and Control entry. Record `web|mobile` separately as `opened|unavailable|not_run`; a filename, attachment card presence or Agent download alone is insufficient. If the exact new entries lack complete requested-client evidence before publication, this bundle's one actionable request MUST be `action_type=access_confirmation`; the intended design input, risk acceptance or approval remains non-actionable pending context. If any required complete material cannot be opened for the requested scope, retain all objects, mark the material delivery unavailable and do not treat the content decision as ready.

After the exact access action succeeds and its evidence re-verifies, create a new current core Human Action Request version for the content decision. Delivering that later request is a new `multica_human_action_material_bundle_v1` attempt with a new exact operational authorization; it may repeat the canonical attachment but MUST list retained objects and must not edit or append to the access-confirmation comment. Access confirmation never becomes content-decision authority.

This profile never writes `arch.packet.current`. If a later Review becomes approvable, the packet delivery route performs its own compatibility, authorization, immutable three-attachment delivery and readiness checks.
