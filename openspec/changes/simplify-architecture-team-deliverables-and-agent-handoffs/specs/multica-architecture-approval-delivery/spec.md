## MODIFIED Requirements

### Requirement: Adapter consumes the portable core contract without redefining it
The `multica-architecture-approval-adapter` SHALL require a delivered current machine-only `ARCH-APPROVAL-PACKET` conforming to a compatible core revision and SHALL map evidence to portable fields without changing stages, Review conclusions, Design maturity, recommendation, packet bytes or legal decisions. The adapter MUST render `human_review_surface_v1` separately from `architecture_internal_evidence_v1` and MUST NOT expose internal evidence as mandatory human material.

#### Scenario: Core manifest is available
- **WHEN** a current packet, Design, Review and compatible surface contracts pass preflight
- **THEN** the adapter creates the one-Design human delivery while persisting packet/readback data internally

#### Scenario: Core and adapter revisions conflict
- **WHEN** the adapter cannot prove compatibility with the frozen core contract
- **THEN** it performs no platform write and reports the exact revision mismatch

### Requirement: Review comment stays concise while full content is attached
The adapter SHALL publish one human-readable approval comment that shows exact Design version/maturity, Reviewer conclusion, concise findings, Team recommendation with Chinese rationale/conditions/risks, legal decisions and a non-approval warning. It MUST attach exactly one complete canonical `ARCH-DESIGN-vN.md`. Complete Review and Packet bytes MUST remain internal evidence and MUST NOT be attached or copied into the comment. A derived Design PDF and interactive Archify HTML MAY be offered as non-authoritative supporting resources. When the Design has a required diagram, its receipt-bound light/1440×900 static preview SHALL be offered from the same canonical Design surface and its client-specific rendering MUST be verified separately from Design Markdown access. All such resources MUST be bound to the Design visual manifest, MUST NOT count as additional canonical architecture artifacts and MUST NOT become separate mandatory entries that the Owner must open.

#### Scenario: Approval comment is delivered
- **WHEN** preflight succeeds for a current approvable manifest
- **THEN** the comment contains the brief and adapter marker, has exactly one canonical Design Markdown attachment, and has no Review, Packet or Control attachment

#### Scenario: Work was triggered by a comment
- **WHEN** the current task requires the approval entry below a trigger
- **THEN** the adapter publishes the one approval comment with the trigger as parent and records its actual ID for Action binding

#### Scenario: Optional PDF rendering fails
- **WHEN** an optional PDF accessibility renderer fails
- **THEN** canonical Markdown remains authoritative, the limitation is internal evidence, and no digest or approval gate changes

#### Scenario: Optional interactive diagram cannot open on mobile
- **WHEN** the canonical Design and its static preview are readable but a derived Archify HTML viewer cannot run on the mobile client
- **THEN** the adapter records the interactive limitation, keeps the Design entry usable, and does not require the Owner to open the HTML before deciding

#### Scenario: Static preview cannot be read on mobile
- **WHEN** automatic mode opens the canonical Design but the required light/1440×900 preview projection is missing, has a mismatched digest, or its title, primary components/boundaries or critical labels cannot be distinguished in a requested mobile scope
- **THEN** readiness is unavailable for that scope and the adapter repairs the current preview projection without substituting an older image or requiring the interactive HTML

#### Scenario: Owner-manual preview uses the certified route
- **WHEN** automatic opening is unavailable but the selected Owner-manual profile verifies the current preview identity/digest, a sandbox-certified requested-client route and one stable Design-surface entry
- **THEN** preview access is `manual_check_required`, the exact Action's single `materials_opened` declaration covers the complete Design surface, and the adapter MUST NOT request a separate preview attestation

### Requirement: Multica attachments provide durable human-readable access
For the required canonical Design attachment the adapter MUST record a `durable_platform_ref` with Issue/comment/attachment identity, stable access ref, media type, availability scope, target human actor/binding evidence, expected digest, verifier and verification time. The Design and Review target actors MUST resolve uniquely to one canonical Member without fuzzy inference. Review, Packet, Control and Research SHALL use durable internal refs and MUST NOT require human attachment cards. Time-limited download URLs MUST NOT be stable refs.

#### Scenario: Target actor maps uniquely
- **WHEN** manifest-bound mapping identifies one current-workspace Member for the consistent Design/Review target actor
- **THEN** readiness records that UUID as the only actor permitted to decide

#### Scenario: Mapping is absent or ambiguous
- **WHEN** target actors differ or mapping resolves to zero/multiple Members
- **THEN** the adapter emits unavailable evidence and performs no approval request

#### Scenario: Target member opens the Design
- **WHEN** the approval comment belongs to an accessible Issue
- **THEN** the client exposes one canonical Design card whose stable path retrieves the complete Design bytes

#### Scenario: Only the Agent can read the Design
- **WHEN** the Agent can download the attachment but target-member access or owner-manual policy cannot be established
- **THEN** access remains unconfirmed and readiness is unavailable

#### Scenario: Only an expiring URL is returned
- **WHEN** the platform provides no stable attachment identity beyond an expiring URL
- **THEN** the adapter MUST NOT mark durable access or readiness confirmed

### Requirement: Readiness verifies the delivered platform bytes
After comment creation the adapter MUST re-read the approval comment, confirm exactly one canonical Design attachment, download it through stable identity and compare raw-byte SHA-256 with the manifest. It MUST also re-read internal Review/packet bytes, task result, `arch.packet.current`, `ARCH-CONTROL` evidence and supersession state. `review_packet_ready` SHALL be emitted only after brief, Design access, all digests, target human, current Action and projections verify.

The adapter SHALL support `automatic` and `owner_attested` evidence modes. `automatic` records actual per-client Design opening. `owner_attested` records `manual_check_required`, binds a unique current Action and requires `materials_opened`; it MUST NOT claim `opened`. Ready evidence SHALL use `shared_workspace_sidecar_v1` or `multica_issue_task_evidence_v1`; the latter binds immutable request/task result, Design attachment, internal Review/manifest digests, target Member, Control, projection, status and supersession readbacks. External sidecar remains optional.

#### Scenario: Complete one-Design delivery verifies
- **WHEN** comment marker, single Design attachment/digest/access, internal Review/packet digests, Owner, Action and projection all match
- **THEN** the adapter emits portable current-manifest readiness and the core may compute `waiting_human`

#### Scenario: Owner-attested delivery is ready
- **WHEN** automatic rendering is unavailable but unique Owner, exact Design attachment, stable entry and complete task/control evidence pass
- **THEN** the adapter emits ready evidence with `manual_check_required`, exposes one Action and requires `materials_opened`

#### Scenario: Downloaded Design differs
- **WHEN** re-downloaded Design digest differs from the manifest
- **THEN** the adapter preserves the Review conclusion, emits unavailable evidence and does not advance or rewrite the packet

#### Scenario: Internal evidence drifts
- **WHEN** Review bytes, packet bytes, task result, Control, projection or supersession readback differs
- **THEN** readiness is unavailable even though only the Design is human-facing

### Requirement: Approval delivery explains decisions before technical bindings
The approval comment SHALL present solution summary, Design maturity, Reviewer conclusion/findings, Team recommendation with Chinese rationale/conditions/risks, accepted warnings and legal decisions with consequences before marker/audit identity. It MUST instruct the Owner to open the one complete Design attachment and MUST state that recommendation, material access, status and internal packet readiness are not approval.

#### Scenario: Current approval is delivered
- **WHEN** delivery and readiness pass for an approvable current manifest
- **THEN** the Owner can understand the solution and distinguish documentation-only approval, R&D handoff, revision and rejection without opening Review, Packet, Research or Control

### Requirement: Readiness verifies the rendered human entry point
Readiness SHALL verify that the approval comment contains the current Human Action summary, Design maturity, Reviewer conclusion/findings, option consequences, accepted-risk summary or `none`, exact stable Design access guidance and non-approval boundary. In `automatic` mode every requested scope MUST actually open the canonical Design. In `owner_attested` mode the adapter MUST verify its stable same-Issue entry, mark scopes `manual_check_required`, and require `materials_opened` in the exact Action response. Complete Review, Packet, Research and Control remain machine evidence; their absence from the rendered comment or attachment list MUST NOT make an otherwise complete human entry unavailable.

#### Scenario: Comment omits decision consequences
- **WHEN** Design attachment and all internal digests verify but the visible comment lists only legal tokens
- **THEN** readiness is unavailable and identifies the brief-rendering closing condition

#### Scenario: Design entry is not readable
- **WHEN** the canonical Design card cannot be opened under automatic mode or has no stable owner-manual entry under owner-attested mode
- **THEN** readiness is unavailable without changing Review conclusion

#### Scenario: Internal artifacts are not rendered
- **WHEN** Design entry and human brief pass while Review, Packet, Research and Control are verified only through internal evidence
- **THEN** readiness may succeed because those artifacts are not mandatory human materials

### Requirement: Adapter preserves the visual companion evidence chain
When a Design declares `diagram_requirement=required`, the adapter SHALL persist and re-read the current `architecture_visual_manifest_v1`, Typed JSON and delivered HTML digests, Archify deterministic receipt, passed automated browser receipt, passed independent visual/semantic Review evidence, and the raw-byte digest of the light/1440×900 PNG selected from that same receipt. It MUST project that artifact-local preview identity to a stable platform ref outside the immutable Design, expose it from the canonical Design surface with an optional interactive link, and keep source JSON and receipts in internal evidence. Readiness MUST verify the preview bytes and requested-client readability. A missing, failed, skipped, stale or mismatched required visual chain MUST make readiness unavailable without changing the underlying Review conclusion.

#### Scenario: Visual resources match the current Design
- **WHEN** every required diagram ref, digest and review result matches the Design and packet snapshot
- **THEN** the adapter presents the canonical Design with its derived static preview, MAY offer the interactive link, and records the complete visual chain internally

#### Scenario: Static preview differs from its manifest
- **WHEN** the delivered preview bytes do not match the digest bound by the current visual manifest
- **THEN** readiness is unavailable and the adapter does not substitute an older preview or remove the diagram requirement

#### Scenario: Required visual status is not passed
- **WHEN** the current manifest records `browser_evidence=failed|skipped` or `visual_review=failed|skipped`
- **THEN** readiness is unavailable even if Design Markdown and interactive HTML are accessible, and no manual observation or older receipt upgrades the failed claim
