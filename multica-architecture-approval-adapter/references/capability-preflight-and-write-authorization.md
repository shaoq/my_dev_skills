# Capability preflight and write authorization

## Authorization boundary

Issue delivery is permitted only when a current `operational_authorization` Human Action Request response explicitly names the existing Multica workspace and Issue, the exact current architecture action or packet, planned comment/attachment/projection/sidecar writes, and authorized input/final/temporary paths. Paths outside the exact scope require a separate new authorization. Build and verify its canonical digest with [the operational authorization protocol](operational-authorization.md), then render [the operational authorization template](../templates/multica-operational-authorization.md); a task request or architecture approval alone is not sufficient write authority.

The following are outside Issue delivery and are forbidden without separate explicit human authorization: Skill import, Agent binding, Team/Project/Issue creation, Runtime configuration, CLI installation or upgrade, private/undocumented API use, and creation of a missing workspace, Issue, Agent, Team, Project, Skill, independent attachment resource, or other platform resource. Do not use any of these to repair a failed preflight.

For an explicitly authorized delivery only, passing verified frozen artifacts as `--attachment` inputs on the single comment write is an allowed minimal Issue delivery write. A pre-packet Human Action material route follows [the material bundle contract](human-action-material-bundle.md) and always carries canonical `ARCH-DESIGN-vN.md` plus any authorized PDF or Research/Control fallback. A packet route carries the three verified frozen Design/Review/Packet Markdown artifacts. Neither route permits an independent upload, orphan attachment, standalone attachment resource, or creation of an attachment to fill a missing platform resource. Any attachment write outside that exact comment delivery needs separate explicit human authorization.

The operational request must show `Existing target identities`, `Exact planned writes`, `Authorized paths / scope`, `Retained objects`, `Failure behavior`, `Excluded operations`, `Risks`, the exact authorize/deny reply and After-response behavior before any write. It is not an architecture approval and must not contain or solicit architecture decision tokens.

For a response-triggered delivery, the authorization freezes `parent=multica_authorization_response_parent_v1` rather than a future comment UUID. Immediately before the first write, resolve it only to the current task's `trigger_comment_id`. Require same workspace/Issue, exact operational-owner member author, direct reply to the frozen authorization request, exact expected token after outer-whitespace trimming, revision 1 with no edit, and task attribution evidence pointing to that same trigger. A mismatch is an authorization failure, not a reason to select another comment.

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

The authorized first comment write is the live proof boundary. Its parseable JSON response, actual `--parent` result, attachment bindings, thread reread, attachment identity/stable entry/raw-byte re-download, and requested-client opening results are **postconditions**, not pre-write assumptions. Packet-only metadata write/read-back remains a later packet-route postcondition. `--parent` must use the actual trigger-comment ID resolved through `multica_authorization_response_parent_v1` when the authorization response triggered the task; never substitute a thread root. `--attachment` must refer to frozen local files after their raw-byte digests are verified. Any postcondition failure emits route-specific unavailable evidence and retains created objects; it never retroactively authorizes a repair write.

Fail-closed evidence is returned through the task result unless an exact diagnostic comment is separately listed in `planned_writes`. The same rule applies to asking for operational authorization: preparing or returning the request is allowed, but publishing it as an Issue comment is a distinct write. Never spend an unlisted comment write to explain a rejected trigger, failed preflight or failed postcondition.

## Preflight result

Record the observed CLI/profile identity, workspace ID, Issue ID/ref, execution time in RFC3339 UTC, each pre-write check, and each postcondition. Only a completely passed pre-write gate plus matching current operational authorization permits the minimal first write: one Decision Brief comment with its exact attachments. For the material route, that is the complete write and it never writes `arch.packet.current`; for the packet route, later metadata projection and shared sidecar writes must be expressly listed in the same exact scope and remain gated by their preceding postconditions. This does not authorize activation, configuration, resource creation, platform repair, retry, overwrite/conflict resolution or writes after a final fence scan.

Use durable attachment identity and a separately verified human-facing entry according to [human-accessible evidence links](human-accessible-evidence-links.md). Never persist a time-limited signed `download_url` as stable access evidence. If a target member's Issue/workspace scope cannot be confirmed, a requested client cannot open the exact complete material, or only the Agent can download it, fail closed as unavailable.
