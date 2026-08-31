# Reconciliation, current projection, and readiness

## State machine and immutable audit objects

Each attempt has a unique, opaque `delivery_attempt_id` and follows only:

```text
absent → delivering → delivered_unverified → ready
                    ↘ unavailable
```

`absent` permits only preflight reads and reconciliation scans. `delivering` permits the one new packet-comment write only after the pre-write fence and exact operational authorization pass. `delivered_unverified` permits re-reads, raw-byte checks, and at most the one expressly authorized `arch.packet.current` projection replacement after a complete canonical delivery verifies. `ready` is terminal for that attempt and permits no further platform write. `unavailable` is terminal for that attempt and permits no repair, deletion, editing, or later write. A later attempt requires a new operational authorization that lists retained objects and only the exact incremental write.

Neither a comment nor metadata alone is delivery/readiness/approval authority. Preserve superseded, duplicate, partial, failed, and conflicting objects for audit; never auto-delete or edit them.

## Reconciliation before every write

Start with an Issue thread scan and read `arch.packet.current`. First parse every syntactically legal profile marker as defined in [delivery mapping and marker](delivery-mapping-and-marker.md), before author eligibility. For the current packet ref/version, a different digest is terminal `identity_conflict`; an exact identity on a wrong/non-agent author is terminal `marker_author_conflict`. Neither outcome may write `arch.packet.current`, even if metadata points at an apparently exact delivery. Only unrelated packet refs are audit-only; same-ref higher/lower versions remain relevant to stale/supersession handling. Then classify eligible exact-author comments by current packet identity and reread attachment completeness.

1. Reject an invalid version (anything other than `v[1-9][0-9]*`) and stop unavailable.
2. If any current-ref marker has the same packet version but a different digest, stop unavailable with `fence_outcome=identity_conflict`; do not write comment or projection. If an exact current identity marker has a mismatched/non-agent author, stop unavailable with `fence_outcome=marker_author_conflict`; do not write comment or projection.
3. If any marker has a strictly higher version, stop as `stale_writer`; emit unavailable with a superseded closing condition and do no further writes.
4. For one exact, complete, raw-byte-verifiable delivery, reuse it; do not create another comment.
5. For multiple exact complete deliveries, choose the earliest by `(created_at, comment_id)` as canonical, report every other comment as a duplicate, and do not delete any. Reuse/reconcile only the canonical one.
6. A marker comment missing one required attachment, an attachment detached from the comment, or an orphan/upload record is partial and isolated. It cannot become ready. A later authorized attempt may create a new complete single-comment delivery, but must not attach to or relabel the partial object.
7. If a complete canonical delivery exists but its projection is missing/lost, repair **only** the projection after all required verification; `reconciliation_outcome=repaired_projection`.
8. A higher version is a new immutable delivery. Leave older delivery objects intact and move only the current projection after the new packet reaches the required verification point.

The `delivering` state begins after the first clean pre-write scan. Repeat the scan immediately before the command in the delivery mapping reference. Any newly observed higher version or same-version conflicting digest changes this attempt to terminal unavailable before a write.

## `arch.packet.current` bounded primitive projection

Use exactly one atomic metadata key, `arch.packet.current`; do not split current identity across keys. Its entire value has this fixed semicolon-delimited field order:

```text
profile=v1;version=vN;digest=sha256:<64-lowercase-hex>;comment_id=<escaped>;status=<escaped>;evidence_ref=<escaped>;core_revision=<escaped>;attempt_id=<escaped>;updated_at=<RFC3339-UTC-Z>
```

`profile` must be `v1`; version and digest use the same strict grammar as the marker. `status` is one of `delivered_unverified|ready|unavailable`. The remaining escaped fields use the same canonical UTF-8 percent encoding and strict parser from the delivery-marker reference. Reject unknown, missing, duplicate, reordered, malformed, or over-limit fields. `comment_id`, `evidence_ref`, `core_revision`, and `attempt_id` must be nonempty after decoding. `updated_at` is exact RFC3339 UTC `YYYY-MM-DDTHH:MM:SSZ`. Reject a value that exceeds the observed preflight-supported primitive limit; no truncation or alternate key is allowed.

Before an actual projection write, `evidence_ref` is deterministically fixed as `multica://issues/<issue-id>/comments/<packet-comment-id>#adapter-delivery-evidence-v1`. It is available only after resolving that actual comment and validating its marker, adapter author, and required attachment bindings; with no such successful reread it is the literal `none` and no projection write is permitted. It does not claim raw-byte readiness and creates no resource, so it breaks the projection/readiness cycle: the projection records this pre-existing delivery evidence, then readiness becomes eligible only after projection read-back and the final scan. The readiness envelope's `delivery_evidence_ref` must equal this exact string byte-for-byte when present. Its `projection_evidence_ref` must equal it only after actual projection write/read-back; without a projection write it is the literal `none`. Never synthesize `comments/none`.

Projection procedure:

1. Read metadata and scan all markers before the write; apply the same higher-version/conflict fence.
2. Atomically replace the single key with the fixed value for the verified canonical delivery.
3. Read the key back and rescan all marker comments and candidate attachments.
4. If the read-back differs, a higher version appears, a same-version digest conflict appears, a current-marker author conflict appears, or the earliest complete canonical delivery changes, end unavailable with no readiness.
5. Perform one final complete scan of comment, attachments, and projection. From completion of this final scan, this attempt must make **no further platform write**.

Metadata only accelerates discovery. It never carries full packet bytes, authorizes a human, overrides current core identity, or repairs a packet/comment identity conflict. Metadata write/read-back failure leaves objects intact, reports unavailable now, and permits a future reconciliation attempt to repair the projection.

## Re-read verification and readiness

Before producing either envelope, re-read the exact canonical packet comment by comment ID (not just an Issue list result) and validate its marker and agent author binding. If no actual packet comment exists, record packet-comment ID/ref as literal `none`, do not construct `comments/none`, and emit unavailable evidence. Otherwise confirm that it contains exactly the required design/review/packet attachments, each bound to that comment and each with durable identity. Re-read each attachment through that identity, obtain raw bytes using a fresh transient URL only if needed, and calculate SHA-256 over those bytes.

Only emit `review_packet_ready` using [the readiness template](../templates/multica-readiness-evidence.md) when all of the following are true:

1. pinned core identity/current delivered packet and real approvable Review conclusion still verify;
2. exact packet-comment marker and adapter author binding verify;
3. exactly three required attachment identities bind to that comment, and every raw-byte digest equals its frozen core digest;
4. each has a durable `markdown_url`/stable endpoint, and the canonical target member has confirmed workspace/Issue access to it;
5. the brief still contains all required non-authoritative recommendation and attachment-opening guidance;
6. the target-human mapping evidence re-verifies for this exact packet/Issue/workspace; and
7. the projection read-back and final no-more-writes scan remain current and canonical.
8. after that final scan, the complete readiness envelope has been atomically written and reread as a `shared_workspace_sidecar_v1` record with a non-`none` self `evidence_ref`, as defined in [durable evidence records](durable-evidence-records.md).

The readiness brief check additionally requires a current Human Action Request ref/version and the fixed `Architecture Decision Brief` order: one-paragraph solution summary, simplified architecture, Team recommendation/rationale/confidence, determined/undetermined matters, alternatives/consequences, the one authorized decision, After-response projection, clickable complete materials, exact response and minimal current/superseded binding. The packet gate adds stable Review/Packet entries and accepted-risk summary or explicit `none`. Validate every user-facing entry using [human-accessible evidence links](human-accessible-evidence-links.md); an internal `multica://issues/...` audit identity is never sufficient. Each artifact's requested desktop/mobile access confirmation must be individually `opened`; an incomplete or superseded rendering closes as unavailable with `failed_checks=brief_rendering_status|per_artifact_access_confirmation` as applicable.

## Retry authorization after partial failure

Before any later reconciliation attempt that may write, scan and list every retained comment, attachment, projection and sidecar from earlier attempts. Render a new `operational_authorization` request containing those exact identities, current canonical packet, no-clobber behavior and the one incremental write that remains possible. The old authority is insufficient because the observed object set changed. Denial, ambiguity, stale scope or any unlisted repair keeps the new attempt read-only; never edit, relabel, attach to or delete retained objects.

Any missing attachment, digest mismatch, durable-ref absence, shared-sidecar authorization/readback failure, access or mapping uncertainty, metadata failure, marker/comment author mismatch (`marker_author_conflict`), metadata/comment identity conflict (`identity_conflict`), capability failure, stale writer, or canonical-delivery change emits `review_packet_unavailable`. Preserve the supplied Review conclusion and all existing objects, name ordered failed checks plus Owner and an observable closing condition, and never modify the frozen packet to compensate.
