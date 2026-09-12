# Durable evidence records

## Evidence profiles

Two durable evidence profiles are supported. Both persist `architecture_internal_evidence_v1`: exact immutable request/current Action, one canonical Design attachment, internal Research/Control/Review/machine-only Packet digests, visual manifest/receipts/preview projection, task result, status timeline, continuation/handoff readback, reconciliation and supersession. `shared_workspace_sidecar_v1` is external shared-workspace evidence; `multica_issue_task_evidence_v1` is platform-managed. Neither metadata or an Agent statement alone satisfies either profile.

## `shared_workspace_sidecar_v1`

The only durable record profile in this adapter is `shared_workspace_sidecar_v1`. It is available only when a human has explicitly confirmed an **existing** durable, shared workspace scope for this task and the adapter can safely publish and re-read a stable relative-path ref in that scope. It never creates the scope, workspace, directory, project, or any external resource; it is never a local filesystem path, a Runtime HOME path, Issue metadata, a comment fragment, or an inferred platform location.

Use only stable refs of this form:

```text
workspace://<confirmed-scope>/<relative-path>
```

`<confirmed-scope>` is the user-confirmed shared-workspace identity. `<relative-path>` is a normalized relative path with no leading slash, `..`, drive prefix, home expansion, query string, or local absolute path. A recommended deterministic layout is:

```text
architecture-approval/<packet-ref-escaped>/<packet-version>/<packet-digest-hex>/<record-kind>.md
```

Every final sidecar is immutable/write-once. Compute its final relative path from a unique record identity: mapping uses packet identity plus binding-evidence ID; readiness uses packet identity plus delivery-attempt ID; decision uses packet identity plus decision comment ID plus revision (when present) or raw content digest. Write complete bytes to a sibling temporary relative path and atomically publish with **no-clobber** semantics. Never replace or overwrite a final ref. If that final ref already exists, reuse it only when its reread bytes are exactly identical; otherwise report a conflict and fail closed while retaining all historical records.

Before each temporary write, atomic publish, and reread, resolve the confirmed workspace real root and every path component. The resolved candidate must remain inside that real root; reject symlinks, a changed root, `..`, absolute paths, and every TOCTOU/symlink escape. The scope must provide safe no-clobber atomic publish; ordinary replace/overwrite is insufficient. The adapter records neither a temporary path nor a local absolute path. If the scope is unconfirmed, unavailable, non-durable, cannot prove this path safety, lacks no-clobber publish, or cannot be re-read, it creates no sidecar.

Each sidecar begins with:

```text
evidence_profile=shared_workspace_sidecar_v1
evidence_ref=workspace://<confirmed-scope>/<relative-path>
packet_ref=<exact current packet ref>
packet_version=<exact current packet version>
packet_digest=<exact current packet digest>
recorded_at=<RFC3339 UTC>
```

`evidence_ref` must equal the actual final `workspace://...` location byte-for-byte. A sidecar is durable evidence only after the final ref rereads successfully.

## `multica_issue_task_evidence_v1`

Use this profile only when every evidence object is in the same current Multica Issue and the current manifest freezes all of these readbacks:

```text
evidence_profile=multica_issue_task_evidence_v1
evidence_ref=multica://issues/<issue-id>/tasks/<task-id>#architecture-evidence-v1
request_comment_ref=<exact-current-request-comment>
request_revision=<exact-revision>
request_digest=sha256:<raw-utf8-digest>
packet_ref=<exact-current-packet-ref-or-none>
packet_version=<exact-current-packet-version-or-none>
packet_digest=<exact-current-packet-digest-or-none>
design_attachment_evidence=<exact-single-design-identity-size-and-raw-byte-digest>
internal_artifact_evidence=<research-control-review-machine-only-packet-identities-and-digests>
visual_evidence=<manifest-source-html-receipt-light-1440x900-preview-identities-digests-and-statuses>
target_member=<canonical-member-uuid>
candidate_comment_ref=<exact-decision-comment-or-none>
candidate_revision=<exact-revision-or-none>
candidate_digest=<raw-and-normalized-digests-or-none>
metadata_projection=<exact-arch.packet.current-value-or-not-applicable>
control_ref=<exact-ARCH-CONTROL-ref>
control_digest=sha256:<raw-utf8-digest>
continuation_handoff_readback=<multica_execution_handoff_v2-task-evidence>
status_timeline=<ordered-server-status-readbacks>
supersession_scan=<current-and-conflicting-identities>
task_result=<completed-platform-task-identity-and-result>
```

The task ID and Issue ID are read from the platform; never synthesize them. The evidence ref becomes valid only after the platform task result and Control projection are complete and reread. For `owner_attested architecture_approval`, the current request must expose one named Action, all material scopes remain `manual_check_required`, and the effective decision must include `materials_opened` plus one legal decision. Before every consumption, reread the request, packet, attachments, target Member, candidate, metadata, Control, status and supersession set. Any missing or changed value invalidates the evidence. An Issue comment fragment, metadata value alone, local file, download result or Agent claim is never sufficient.

## Mapping, readiness, and decision records

- Mapping, readiness and formal decision records may use a shared-workspace sidecar, or the same current `multica_issue_task_evidence_v1` task/control evidence for an owner-attested packet. The selected profile must be consistent across target-human mapping, readiness and decision consumption for that Action.
- Generate readiness evidence only after the delivery attempt's final platform-write scan. A delivery-comment fragment is pre-projection evidence and never readiness authority by itself.
- Generate formal decision evidence only after re-reading current readiness and the exact decision comment. `current_action_reference_v1` becomes effective only after the manifest-bound exact candidate/status/task/metadata/`ARCH-CONTROL` rereads pass.

Neither profile authorizes a Multica write, workspace creation, shared-storage configuration change or external resource. Any missing authority or readback is a fail-closed evidence condition, not a reason to fall back to metadata alone, a local file or an Agent claim.

Every mapping、readiness 或 decision sidecar write must appear in a current `architecture_operation_manifest_v1` with final/temporary relative paths、confirmed existing scope、no-clobber publish、reread and retained objects. One manifest item does not cover another record kind/path. If a final object exists with different bytes or retained set drifted, fail closed; bounded recovery derives a new attempt/new manifest, while overwrite or scope expansion requires a new task instruction—not an authorization token.
