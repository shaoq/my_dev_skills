# Reconciliation, current projection, and readiness

## State machine and immutable audit objects

Each attempt has a unique, opaque `delivery_attempt_id` and follows only:

```text
absent → delivering → delivered_unverified → ready
                    ↘ unavailable
```

`absent` permits only preflight reads and reconciliation scans. `delivering` permits one new packet-comment write only after pre-write fence and current derived manifest pass. `delivered_unverified` permits re-reads、raw-byte checks and at most the manifest-listed `arch.packet.current` projection after complete canonical delivery verifies. `ready` is terminal for that attempt and permits no further platform write. `unavailable` is terminal for that attempt and permits no repair、deletion、editing or later write. Bounded recovery creates a new attempt/new manifest that freezes retained objects and the exact incremental write; it does not request human operational authorization.

Neither a comment nor metadata alone is delivery/readiness/approval authority. Preserve superseded, duplicate, partial, failed, and conflicting objects for audit; never auto-delete or edit them.

## Actionable blocker status reconciliation

`architecture_blocker_action_v3` 使用独立 single-consumption reconciliation；`architecture_blocker_action_v1|architecture_blocker_action_v2` 只作 audit-only。写前按 Action ID、attempt、instruction-owner Member、Issue 和 supersession 扫描既有 blocker comments/tasks，并验证 `automatic_before_human` discovery evidence、business question、human reply recipe 与 evidence derivation policy。完全匹配的 current comment 只复用并回读；冲突、重复或旧 attempt 保留审计，不编辑或删除。

唯一 verified binding 不发布人类 blocker，直接创建 resume continuation。多个候选或 `unavailable_with_evidence` 成功交付并回读唯一 Member mention、single action 与双 response mode 后，Issue 必须为 `blocked` 且 `BLOCKER_ACTION_STATE=awaiting_input`。有效 `provide_input` 记录 `received`，有效 `request_discovery` 记录 `discovery_needed`；只有 mapped resume/discovery task readback 为 accepted/active 后才写 `in_progress --no-start`。若 task 未入队、mapping 漂移、readback 失败或 status 回读不匹配，执行 blocked rollback；不得遗留 orphaned `in_progress`。

无法在任何写入前唯一解析 instruction owner 时不创建 projection/comment/task，返回 `needs_new_mandate_v1`，Issue unchanged、current task completed with non-success、downstream task none。

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

Before producing either envelope, re-read the exact canonical approval comment by comment ID (not just an Issue list result) and validate its marker and agent author binding. If no actual comment exists, record comment ID/ref as literal `none`, do not construct `comments/none`, and emit unavailable evidence. Otherwise confirm that it contains exactly one required canonical Design attachment with durable identity. Re-read Design bytes and calculate SHA-256; re-read Review/packet/Control/Research through `architecture_internal_evidence_v1` durable refs.

Only emit `review_packet_ready` using [the readiness template](../templates/multica-readiness-evidence.md) when all of the following are true:

1. pinned core identity/current delivered packet and real approvable Review conclusion still verify;
2. exact packet-comment marker and adapter author binding verify;
3. exactly one canonical Design attachment binds to that comment and its raw-byte digest equals the frozen core digest; internal Review/packet/Control/Research digests also match;
4. Design has a durable stable endpoint, and the canonical target member has confirmed access to it under the selected mode;
5. the brief still contains Design maturity, concise Review/findings, risks, recommendation, consequences, one Action and Design-opening guidance;
6. the target-human mapping evidence re-verifies for this exact packet/Issue/workspace; and
7. the projection read-back and final no-more-writes scan remain current and canonical.
8. after that final scan, the complete readiness envelope has been persisted and reread under one profile from [durable evidence records](durable-evidence-records.md): an atomic no-clobber `shared_workspace_sidecar_v1`, or for `owner_attested architecture_approval`, a completed manifest-bound `multica_issue_task_evidence_v1` with exact request/task/metadata/Control/status/supersession readbacks and a non-`none` self `evidence_ref`.

The readiness brief check additionally requires a current Human Action Request ref/version and the fixed `Architecture Decision Brief` order: one-paragraph solution summary, Design maturity, concise Review/findings, simplified view, recommendation/rationale/confidence, alternatives/consequences, one authorized decision, After-response projection, one clickable Design entry, exact response and minimal current/superseded binding. Review/Packet/Control/Research remain internal and their absence from human attachments is success, not a gap. In `automatic`, each requested Design/preview scope must be individually `opened`. In `owner_attested`, the stable same-Issue Design surface stays `manual_check_required`, and the named exact response requires `materials_opened`.

For the portable envelope, project `owner_attested -> owner_manual`; retain Multica task/Action/attestation evidence only in Adapter records. The core consumes the manual-inspection semantics and portable refs/digests without learning Issue, comment, attachment or task fields.

## Automatic bounded retry after partial failure

Before a later reconciliation attempt that may write, scan and list every retained comment、attachment、projection and sidecar. If the current mandate still covers the same Issue/stage and retry limit remains, automatically derive a new manifest containing those identities、current packet、no-clobber behavior、supersedes and the one incremental write. Ambiguity、scope drift、retry exhaustion or an unlisted repair keeps the attempt read-only and requires a new task instruction only when scope must expand; never edit、relabel、attach to or delete retained objects.

Any missing attachment、digest mismatch、durable-ref absence、selected evidence-profile readback failure、access or mapping uncertainty、metadata failure、marker/comment author mismatch (`marker_author_conflict`)、metadata/comment identity conflict (`identity_conflict`)、capability failure、stale writer or canonical-delivery change emits `review_packet_unavailable`. Preserve the supplied Review conclusion and all existing objects, name ordered failed checks plus Owner and an observable closing condition, and never modify the frozen packet to compensate.
