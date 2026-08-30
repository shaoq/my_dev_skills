# Capability preflight and write authorization

## Authorization boundary

Issue delivery is permitted only when a current `operational_authorization` Human Action Request response explicitly names the existing Multica workspace and Issue, exact verified packet, planned comment/attachment/projection/sidecar writes and authorized input/final/temporary paths. Paths outside the exact scope require a separate new authorization. Build and verify its canonical digest with [the operational authorization protocol](operational-authorization.md), then render [the operational authorization template](../templates/multica-operational-authorization.md); a task request or architecture approval alone is not sufficient write authority.

The following are outside Issue delivery and are forbidden without separate explicit human authorization: Skill import, Agent binding, Team/Project/Issue creation, Runtime configuration, CLI installation or upgrade, private/undocumented API use, and creation of a missing workspace, Issue, Agent, Team, Project, Skill, independent attachment resource, or other platform resource. Do not use any of these to repair a failed preflight.

For an explicitly authorized delivery only, uploading the three verified frozen Markdown artifacts as `--attachment` inputs on the single packet-comment write is an allowed minimal Issue delivery write. It is not permission for an independent upload, an orphan attachment, a standalone attachment resource, or creation of an attachment to fill a missing platform resource. Any attachment write outside that packet-comment delivery needs separate explicit human authorization.

The operational request must show `Existing target identities`, `Exact planned writes`, `Authorized paths / scope`, `Retained objects`, `Failure behavior`, `Excluded operations`, `Risks`, the exact authorize/deny reply and After-response behavior before any write. It is not an architecture approval and must not contain or solicit architecture decision tokens.

## Two-phase, fail-closed delivery capability contract

The pre-write gate may use only no-side-effect Issue/workspace reads, installed CLI/profile identity, command-surface inspection, existing versioned capability certificates, authorized input-path/digest checks, and metadata reads. CLI help text, source text, or a remembered interface are not proof that a live write/postcondition will succeed. Record every pre-write check as `check`, `observed_command_or_profile`, `result`, `owner`, and `closing_condition`. A missing, unknown, malformed, unsupported, or non-reproducible result fails closed. The normalized failure is:

```text
evidence_type=review_packet_unavailable
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
| `metadata_read` | Read existing `arch.packet.current` and observe its bounded single-key representation. | Provide readable current metadata in the existing Issue. |

The authorized first packet-comment write is the live proof boundary. Its parseable JSON response, actual `--parent` result, attachment bindings, thread reread, attachment identity/stable ref/raw-byte re-download, and metadata write/read-back are **postconditions**, not pre-write assumptions. `--parent` must use the actual trigger-comment ID when the task is comment-triggered; never substitute a thread root. `--attachment` must refer to frozen local Markdown files after their raw-byte digests are verified. Any postcondition failure emits unavailable evidence and retains created objects; it never retroactively authorizes a repair write.

## Preflight result

Record the observed CLI/profile identity, workspace ID, Issue ID/ref, execution time in RFC3339 UTC, each pre-write check, and each postcondition. Only a completely passed pre-write gate plus matching current operational authorization permits the minimal first write: packet-comment creation with attachments. The later metadata projection and shared sidecar writes must be expressly listed in the same exact scope and remain gated by their preceding postconditions. This does not authorize activation, configuration, resource creation, platform repair, retry, overwrite/conflict resolution or writes after a final fence scan.

Use durable attachment identity and `markdown_url`/stable endpoint in evidence. Never persist a time-limited signed `download_url` as stable access evidence. If a target member's Issue/workspace scope cannot be confirmed, or only the Agent can download material, fail closed as unavailable.
