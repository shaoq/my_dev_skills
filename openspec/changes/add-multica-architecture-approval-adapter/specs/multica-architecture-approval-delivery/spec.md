## ADDED Requirements

### Requirement: Adapter consumes the portable core contract without redefining it
The `multica-architecture-approval-adapter` skill SHALL require a delivered current `ARCH-APPROVAL-PACKET` conforming to the pinned `architecture-design-workflow` core revision and MUST map platform evidence back to the portable fields without changing canonical stages, Review conclusions, recommendation enums, packet bytes or human decision values.

#### Scenario: Compatible current packet is supplied
- **WHEN** the adapter receives a delivered packet, exact design/review inputs and digests compatible with the consumed core revision
- **THEN** it may begin Multica capability preflight and delivery while leaving core artifacts unchanged

#### Scenario: Core packet is absent or incompatible
- **WHEN** no delivered current packet exists or its contract is incompatible with the pinned revision
- **THEN** the adapter refuses to synthesize platform state, emits deterministic unavailable evidence and identifies the core-contract closing condition

### Requirement: Delivery capability is preflighted and fails closed
Before the first platform write, the adapter MUST verify only no-side-effect Issue/workspace reads, installed CLI/profile/command surface, any existing scope-matched capability certificate, authorized frozen input paths/digests, and metadata reads. The first authorized comment+attachments response, actual reply parent/bindings, thread reread, attachment re-download and metadata write/read-back are fail-closed postconditions. CLI help or source text alone MUST NOT be treated as live behavior proof. It MUST NOT install or upgrade a CLI, call undocumented internal APIs or modify Multica source to repair a failed gate or postcondition.

#### Scenario: Required capabilities are available
- **WHEN** the target Issue resolves in the current workspace and every required CLI behavior satisfies the adapter contract
- **THEN** delivery may proceed and the preflight evidence records the observed CLI/profile identity

#### Scenario: A required capability is missing
- **WHEN** comment attachments, parent replies, thread reads, stable attachment retrieval or metadata behavior cannot be verified
- **THEN** no delivery is claimed ready, `review_packet_unavailable` identifies the failed check, Owner and closing condition, and the actual Review conclusion is preserved

### Requirement: Review comment stays concise while full content is attached
The adapter SHALL publish one human-readable packet comment that shows exact packet/design/review versions, Reviewer conclusion, Architecture Team recommendation with Chinese rationale, conditions and risks, review questions, legal decisions and a non-approval warning. It MUST attach the complete frozen design, review and packet Markdown bytes rather than copying their full bodies into the comment.

#### Scenario: Packet comment is delivered
- **WHEN** preflight succeeds for a current approvable packet
- **THEN** the comment contains the concise review brief and adapter marker, and its attachments contain the complete exact `ARCH-DESIGN`, `ARCH-REVIEW` and `ARCH-APPROVAL-PACKET` inputs

#### Scenario: Work was triggered by a comment
- **WHEN** the current Multica task requires replies to remain below a trigger comment
- **THEN** the adapter publishes the packet comment with that trigger as parent and records the actual packet comment ID for later descendant binding

#### Scenario: Optional PDF rendering fails
- **WHEN** a configured PDF renderer is absent or cannot render a non-authoritative derived preview
- **THEN** original Markdown delivery remains the authority, the PDF failure is reported as a limitation, and no canonical digest is replaced by a derived digest

### Requirement: Multica attachments provide durable human-readable access
For each required artifact the adapter MUST record a `durable_platform_ref` with Multica Issue/comment/attachment identity, stable access ref, media type, availability scope, target human actor, target-human binding evidence, expected digest, verifier and verification time. The design/review target actors MUST be non-empty and consistent, and the adapter MUST resolve them uniquely to one canonical Multica member UUID without fuzzy display-name, email, assignee or author inference. It MUST NOT persist a time-limited signed `download_url` as the stable ref.

#### Scenario: Packet actor maps uniquely to one member
- **WHEN** a packet-bound mapping identifies exactly one current-workspace Multica member for the consistent design/review target actor
- **THEN** readiness records the canonical member UUID and mapping evidence ref as the only actor permitted to decide

#### Scenario: Target-human mapping is absent or ambiguous
- **WHEN** design/review target actors differ, no exact member mapping exists, or more than one member matches
- **THEN** the adapter emits `review_packet_unavailable`, records the mapping closing condition and does not infer an actor from names, assignments or prior comments

#### Scenario: Target member opens material from mobile
- **WHEN** the packet comment and required attachments belong to an Issue accessible to the target member
- **THEN** the Multica mobile timeline exposes attachment cards whose canonical access path can retrieve the complete artifact bytes

#### Scenario: Only the Agent can read the attachment
- **WHEN** the Agent can download an attachment but target-member Issue scope or stable access cannot be established
- **THEN** access confirmation remains unconfirmed and the adapter emits `review_packet_unavailable`

#### Scenario: Only an expiring URL is returned
- **WHEN** the platform response provides no stable attachment identity or persistable access ref beyond a time-limited URL
- **THEN** the adapter MUST NOT mark durable access or readiness as confirmed

### Requirement: Readiness verifies the delivered platform bytes
After comment creation the adapter MUST re-read the packet comment, confirm all required attachment IDs are bound to it, download each attachment through its stable identity and compare raw-byte SHA-256 with the frozen design/review/packet digests. `review_packet_ready` SHALL be emitted only after comment brief, access, digests, target human and metadata projection all verify.

It MUST additionally write once and re-read a complete readiness `shared_workspace_sidecar_v1` record in an explicitly user-confirmed existing durable shared scope. The final sidecar ref is immutable and safe no-clobber published; it MUST use a unique packet-identity plus delivery-attempt path and fail closed on different existing bytes, symlink/TOCTOU escape, or absent safe scope. The adapter MUST NOT create that scope or treat a delivery-comment fragment as readiness evidence. Without this sidecar, readiness is unavailable.

#### Scenario: Complete delivery verifies
- **WHEN** marker identity, attachment bindings, downloaded bytes, stable access, human scope and metadata projection all match the current packet
- **THEN** the adapter emits a portable `review_packet_ready` envelope referencing the exact Multica delivery and the core may compute `waiting_human`

#### Scenario: Downloaded bytes differ
- **WHEN** any re-downloaded required attachment has a digest different from its frozen core input
- **THEN** the adapter preserves the approvable Review conclusion, emits `review_packet_unavailable`, and MUST NOT advance or rewrite the packet

#### Scenario: Metadata projection cannot be read back
- **WHEN** delivery objects verify but the current projection write or read-back fails
- **THEN** the current run remains unavailable and a later reconciliation may recover the delivery without claiming readiness now

### Requirement: Delivery retries reconcile instead of blindly duplicating
The adapter SHALL reconcile existing marker-bearing comments, attachments and metadata by Issue plus packet ref/version/digest before writing. It MUST reuse one exact complete delivery, preserve superseded deliveries, fail closed on same-version digest conflicts, prevent a stale lower-version attempt from overwriting a higher-version projection and avoid automatic deletion of duplicate or partial objects.

#### Scenario: Exact delivery already exists
- **WHEN** retry finds one adapter-authored comment whose marker and verified attachments exactly match the current packet
- **THEN** it reuses that delivery, refreshes verification and does not create another packet comment

#### Scenario: Comment exists after metadata failure
- **WHEN** a prior run created a complete packet comment but failed before metadata projection succeeded
- **THEN** reconciliation discovers the comment by marker and digest, verifies it and repairs only the projection needed for readiness

#### Scenario: Same packet version has a different digest
- **WHEN** an existing adapter marker uses the current packet version with a conflicting packet digest
- **THEN** delivery fails closed as an identity conflict and neither comment nor metadata is overwritten

#### Scenario: New packet supersedes an old packet
- **WHEN** the core supplies a higher packet version that supersedes the prior delivered version
- **THEN** the adapter creates a new immutable delivery, retains the old comment and attachments, and moves only the current metadata projection

#### Scenario: Lower-version attempt overlaps a newer delivery
- **WHEN** an older delivery attempt observes a higher packet version during any pre-write or post-write fence
- **THEN** the older attempt performs no further writes, emits no readiness, reports itself stale and leaves reconciliation to the higher-version delivery

#### Scenario: Two attempts interleave for the same packet
- **WHEN** concurrent attempts create more than one exact marker-bearing delivery before either finishes
- **THEN** both rescan, select the earliest complete verifiable delivery as canonical, preserve duplicate objects for audit and emit readiness only for the canonical identity after projection read-back

### Requirement: Issue metadata is a lightweight projection only
The adapter MUST use one bounded primitive Issue metadata value at `arch.packet.current` for a versioned, deterministically encoded current packet version/digest/comment/status/core revision/evidence ref/attempt/timestamp projection. It MUST atomically replace that single key, reject malformed or duplicate fields, perform pre-write and post-write monotonic fences, and keep complete packet, attachment bytes and human decision evidence outside metadata. Metadata MUST NOT independently count as delivery, readiness or approval.

#### Scenario: Projection is current
- **WHEN** a delivery has fully verified
- **THEN** metadata read-back points to the same packet digest and comment while canonical evidence remains recoverable from referenced comments, attachments and `ARCH-CONTROL`

#### Scenario: Metadata contains an approval-looking value
- **WHEN** metadata text resembles `approved_for_spec` without valid member comment evidence
- **THEN** the adapter ignores it as human approval and keeps the human gate unchanged

#### Scenario: Projection changes during final verification
- **WHEN** post-write read-back or the final marker scan finds a higher version, another digest or a changed canonical delivery
- **THEN** the current attempt emits `review_packet_unavailable`, performs no later platform writes and does not return readiness for its stale projection
