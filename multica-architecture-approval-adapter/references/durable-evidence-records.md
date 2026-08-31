# Durable evidence records

## Evidence profiles

`shared_workspace_sidecar_v1` remains the only durable shared-workspace profile and is mandatory for formal packet approval evidence. A non-approval `current_action_reference_v1` (`design_input|architecture_review`) MAY instead use `multica_issue_task_evidence_v1`: the exact immutable member comment identity/content digests plus the platform-managed task result and `ARCH-CONTROL` projection listed in the current manifest. This profile does not create storage, metadata or a sidecar and cannot satisfy `architecture_approval`.

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

## Mapping, readiness, and decision records

- A mapping sidecar contains the complete `multica_target_human_v1` mapping record, exact packet identity, workspace/Issue scope, confirmer where applicable, verifier, and member-access result. Without an authorized and rereadable mapping sidecar, mapping is unavailable; delivery readiness is unavailable and a decision cannot be effective.
- A readiness sidecar contains the complete rendered [readiness envelope](../templates/multica-readiness-evidence.md), including its own `evidence_ref`. Generate it only after the delivery attempt's final no-more-platform-writes scan. A delivery-comment fragment is only pre-projection delivery evidence and is never a readiness sidecar or readiness authority. Without an authorized/re-readable readiness sidecar, emit `review_packet_unavailable`.
- A formal packet decision sidecar contains the complete rendered [decision record](../templates/multica-decision-evidence.md), including its own `evidence_ref`. Generate it only after re-reading current readiness and the exact decision comment, and only when current mandate/manifest lists this existing shared-scope no-clobber write and reread. A `current_action_reference_v1` design/review input instead records the same decision fields in `multica_issue_task_evidence_v1`; it becomes effective only after the manifest-bound exact candidate/status/task/ARCH-CONTROL rereads pass.

The sidecar rules do not authorize a Multica write, a workspace creation, a shared-storage configuration change, or a new external resource. They define how to use an already authorized, existing durable scope. Any missing authority is a fail-closed evidence condition, not a reason to fall back to metadata, a comment URL, a local file, or an Agent claim.

Every mapping、readiness 或 decision sidecar write must appear in a current `architecture_operation_manifest_v1` with final/temporary relative paths、confirmed existing scope、no-clobber publish、reread and retained objects. One manifest item does not cover another record kind/path. If a final object exists with different bytes or retained set drifted, fail closed; bounded recovery derives a new attempt/new manifest, while overwrite or scope expansion requires a new task instruction—not an authorization token.
