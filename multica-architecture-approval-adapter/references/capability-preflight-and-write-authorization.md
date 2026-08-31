# Capability preflight and write authorization

## Authorization boundary

Issue delivery is permitted only when a current `operational_authorization` Human Action Request response explicitly names the existing Multica workspace and Issue, the exact current architecture action or packet, planned comment/attachment/projection/sidecar writes, and authorized input/final/temporary paths. Paths outside the exact scope require a separate new authorization. Build and verify its canonical digest with [the operational authorization protocol](operational-authorization.md), then render [the operational authorization template](../templates/multica-operational-authorization.md); a task request or architecture approval alone is not sufficient write authority.

The following are outside Issue delivery and are forbidden without separate explicit human authorization: Skill import, Agent binding, Team/Project/Issue creation, Runtime configuration, CLI installation or upgrade, private/undocumented API use, and creation of a missing workspace, Issue, Agent, Team, Project, Skill, independent attachment resource, or other platform resource. Do not use any of these to repair a failed preflight.

For an explicitly authorized delivery only, passing verified frozen artifacts as `--attachment` inputs on the single comment write is an allowed minimal Issue delivery write. A pre-packet Human Action material route follows [the material bundle contract](human-action-material-bundle.md) and always carries canonical `ARCH-DESIGN-vN.md` plus any authorized PDF or Research/Control fallback. A packet route carries the three verified frozen Design/Review/Packet Markdown artifacts. Neither route permits an independent upload, orphan attachment, standalone attachment resource, or creation of an attachment to fill a missing platform resource. Any attachment write outside that exact comment delivery needs separate explicit human authorization.

The operational request must show `Existing target identities`, `Exact planned writes`, `Authorized paths / scope`, `Retained objects`, `Failure behavior`, `Excluded operations`, `Risks`, the exact authorize/deny reply and After-response behavior before any write. It is not an architecture approval and must not contain or solicit architecture decision tokens.

For a Human Action lifecycle, command-surface inspection and the current capability certificate must cover status readback plus both exact no-trigger commands:

```bash
multica issue status <issue> in_review --no-start
multica issue status <issue> in_progress --no-start
```

The authorization must list these status writes in their event order, including deferred response-start binding via `valid_human_action_response_v1`; mention, comment and status are not bundled as an unspecified side effect.

When a preparation task result will be automatically materialized as the authorization request, freeze `authorization_request=multica_task_result_authorization_request_v1` rather than a future request UUID. Bind the exact preparation task, preparation trigger, request Agent, authorization ID, Issue/workspace, Owner, attempt and material digests, and retain `comment:multica_task_result_authorization_request_v1` as a constrained expected object. After materialization, require exactly one revision-1 unedited request comment with matching `source_task_id`, direct parent, Agent, parsed authorization content and scope. Missing, duplicate, edited or mismatched candidates fail closed; never use a guessed UUID, latest comment or compact read that omits task attribution.

For a response-triggered delivery, the authorization also freezes `parent=multica_authorization_response_parent_v1` rather than a future response UUID. Immediately before the first write, first resolve the request selector above, then resolve the response selector only to the current task's `trigger_comment_id`. Require same workspace/Issue, exact operational-owner member author, direct reply to the resolved authorization request, exact expected token derived from the frozen authorization ID/scope digest after outer-whitespace trimming, revision 1 with no edit, and task attribution evidence pointing to that same trigger. A mismatch is an authorization failure, not a reason to select another comment.

Freeze the execution working directory and external-file mode with the command profile. Prefer a working directory equal to the authorized common input root and relative `--content-file` / `--attachment` paths. If any frozen input is intentionally outside that directory, `planned_writes` MUST explicitly include `allow_external_file=true` and the actual command MUST include `--allow-external-file`; adding the flag at runtime is forbidden. In either mode, resolve every path under the authorized root, reject symlink escape, and recheck raw-byte digests immediately before submission.

## Two-phase, fail-closed delivery capability contract

The pre-write gate may use only no-side-effect Issue/workspace reads, installed CLI/profile identity, command-surface inspection, existing versioned capability certificates, authorized input-path/digest checks, and route-required metadata reads. CLI help text, source text, or a remembered interface are not proof that a live write/postcondition will succeed. Record every pre-write check as `check`, `observed_command_or_profile`, `result`, `owner`, and `closing_condition`. A missing, unknown, malformed, unsupported, or non-reproducible result fails closed. The normalized failure is route-specific: `human_action_material_unavailable` for the pre-packet material route and `review_packet_unavailable` for the packet route. Preserve the actual action/Review state and use:

```text
evidence_type=<human_action_material_unavailable|review_packet_unavailable>
action_id=<actual action ID or none>
review_conclusion=<actual supplied conclusion>
failed_checks=<ordered failing check names>
owner=<platform owner or Architecture Lead>
closing_condition=<specific observable behavior to provide or authorize>
```

Preserve the real Review conclusion and do not claim delivery/readiness. Before preflight passes, perform no delivery write.

| Ordered check | Required observed behavior | Failure closing condition |
| --- | --- | --- |
| `issue_workspace_identity` | Resolve the supplied existing Issue and confirm it belongs to the explicitly supplied workspace. | Provide an existing, accessible Issue/workspace identity. |
| `command_profile_surface` | Read installed CLI/profile identity and command surface for the authorized comment/attachment/metadata operations; a prior, scope-matched capability certificate may support this gate. | Provide a current installed command/profile identity and a scope-matched capability certificate; help/source alone is insufficient. |
| `input_paths_and_frozen_digests` | Confirm authorized local input paths and raw-byte frozen digests before submission. | Provide authorized frozen input paths and matching raw-byte digests. |
| `metadata_read` | Packet route only: read existing `arch.packet.current` and observe its bounded single-key representation. Pre-packet material route records `not_applicable` and MUST NOT create or modify that key. | For packet delivery, provide readable current metadata in the existing Issue. |

The authorized first comment write is the live proof boundary. Its parseable JSON response, actual `--parent` result, attachment bindings, thread reread, attachment identity/stable entry/raw-byte re-download, and requested-client opening results are **postconditions**, not pre-write assumptions. Packet-only metadata write/read-back remains a later packet-route postcondition. `--parent` must use the actual response trigger-comment ID resolved through `multica_authorization_response_parent_v1`, after its direct parent has first been resolved through `multica_task_result_authorization_request_v1` when applicable; never substitute a thread root. `--attachment` must refer to frozen local files after their raw-byte digests are verified. Any postcondition failure emits route-specific unavailable evidence and retains created objects; it never retroactively authorizes a repair write.

For Human Action delivery, a canonical member mention and successful comment/attachment/access reread gate the authorized `in_review --no-start` command. Re-read the Issue and require `status postcondition=in_review`. For a later response task, validate `valid_human_action_response_v1` before the authorized `in_progress --no-start` command, then require `status postcondition=in_progress` before doing Agent work. A failure returns evidence in the task result, retains prior objects and performs no unplanned repair.

Fail-closed evidence is returned through the task result unless an exact diagnostic comment is separately listed in `planned_writes`. The same rule applies to asking for operational authorization: the Agent may prepare or return the request, but it must not invoke an unlisted Issue write. If Multica automatically materializes the task result as a platform-managed task result comment, record its identity and state truthfully that the Agent did not invoke the write but the platform produced the comment. Never spend an unlisted Agent-invoked comment write to explain a rejected trigger, failed preflight or failed postcondition.

## Preflight result

Record the observed CLI/profile identity, workspace ID, Issue ID/ref, execution time in RFC3339 UTC, each pre-write check, and each postcondition. Only a completely passed pre-write gate plus matching current operational authorization permits the minimal first write: one Decision Brief comment with its exact attachments. For the material route, that is the complete write and it never writes `arch.packet.current`; for the packet route, later metadata projection and shared sidecar writes must be expressly listed in the same exact scope and remain gated by their preceding postconditions. This does not authorize activation, configuration, resource creation, platform repair, retry, overwrite/conflict resolution or writes after a final fence scan.

Use durable attachment identity and a separately verified human-facing entry according to [human-accessible evidence links](human-accessible-evidence-links.md). Never persist a time-limited signed `download_url` as stable access evidence. If a target member's Issue/workspace scope cannot be confirmed, a requested client cannot open the exact complete material, or only the Agent can download it, fail closed as unavailable.
