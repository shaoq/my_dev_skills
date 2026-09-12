## MODIFIED Requirements

### Requirement: Approval packet binds exact portable artifacts
The skill SHALL produce a versioned immutable machine-only `ARCH-APPROVAL-PACKET` manifest that binds one Work Item and attempt, compatible contract revisions, one `ARCH-DESIGN` version and maturity, its current `architecture_visual_manifest_v1` or explicit `diagram_not_applicable`, one matching `ARCH-REVIEW` version, their media types and digests, access profile declarations, Reviewer conclusion, accepted risks, recommendation, Decision Owner, current Action, `supersedes`, and allowed human decisions. The packet MUST NOT be a mandatory human attachment or human-readable prerequisite. Packet versions MUST be positive integers that increase monotonically per Work Item, and each finalized payload MUST retain `payload_status=delivered`; a mutable draft is not versioned. Digests MUST use frozen raw file bytes and `sha256:<64 lowercase hex characters>`. A delivered packet MUST NOT be overwritten; later readiness or unavailable evidence MUST remain outside its bytes. Timestamps MUST be RFC 3339 with explicit offset and normalized to UTC `Z`.

#### Scenario: Approvable design receives a packet
- **WHEN** an `ARCH-REVIEW` concludes `APPROVABLE_WITH_WARNINGS` or `APPROVABLE` for an exact Design
- **THEN** the workflow creates a machine-only packet binding the exact Design/Review refs, versions, digests, maturity and current Action without adding the packet as a mandatory human material

#### Scenario: Packet inputs change
- **WHEN** Design bytes, Review bytes, maturity, recommendation, material risks or approval conditions change after a packet was finalized
- **THEN** the workflow creates a superseding packet and MUST NOT rewrite the prior packet or apply its later decisions to the new version

#### Scenario: Packet payload is finalized before readiness verification
- **WHEN** all manifest content and frozen input references are complete
- **THEN** the workflow finalizes immutable packet bytes, computes their raw-byte digest, and records later readiness outside the manifest

### Requirement: Readiness evidence is complete and packet-specific
The skill SHALL accept `review_packet_ready` only when Design, Review and packet refs/versions match the current machine manifest; all raw-byte digests match; every required visual manifest has `deliver=passed`, `browser_evidence=passed`, `visual_review=passed`, no unresolved material semantic finding, a light/1440×900 PNG preview bound to the same successful browser receipt/artifact digest, and a verified preview projection for every requested client scope; Reviewer conclusion is approvable; the unique Decision Owner and current Action are verified; and the canonical Design has one verified human-readable entry for each required client scope. An `automatic` preview projection MUST be opened and checked in the requested client. An `owner_manual` projection MAY use a sandbox-certified client route with exact current preview identity/digest and stable entry as `manual_check_required`; the Owner's one `materials_opened` declaration covers the complete Design surface and MUST NOT be split into a second preview declaration. `browser_evidence=failed|skipped`, `visual_review=failed|skipped`, a missing preview or a failed client projection MUST make readiness unavailable and MUST NOT be upgraded by another evidence claim. Review and packet bytes MUST be machine-readable and re-verifiable but MUST NOT require separate human rendering. Readiness MUST NOT itself count as approval.

The default `automatic` access mode SHALL require actual human-readable Design rendering for every requested client scope. The portable `owner_manual` mode MAY make the gate ready when the unique Owner selected manual inspection, exact Design identity/digest and stable entry are verified, and scopes are `manual_check_required`; it MUST NOT claim `opened`, and a legal decision MUST include the Owner's material-opened declaration. A material-unavailable response MUST trigger repair and MUST NOT count as a decision.

#### Scenario: Standalone Design is ready
- **WHEN** the canonical Design is in a shared scope acknowledged by the current human, its digest matches, internal Review/packet bytes match, and the action summary is complete
- **THEN** the standalone profile emits current-packet readiness without requiring the human to open Review, Packet, Research or Control

#### Scenario: Owner-manual Design is ready for inspection
- **WHEN** automatic rendering is unavailable, the unique Owner policy authorizes manual inspection, exact Design identity/digest and stable entry are verified, internal manifest/readback is complete, and scopes are `manual_check_required`
- **THEN** the workflow enters the human gate without claiming the Design was opened and requires the exact material-opened declaration with the decision

#### Scenario: Files are readable only by the Agent process
- **WHEN** the Agent can read Design bytes but no required human access or owner-manual evidence exists
- **THEN** the workflow emits `review_packet_unavailable` and MUST NOT treat process readability as human access

#### Scenario: Evidence belongs to an older packet
- **WHEN** otherwise valid readiness references a superseded manifest
- **THEN** the workflow preserves it for audit but does not allow the current Action to enter the human gate

#### Scenario: Required diagram evidence is stale
- **WHEN** the Design references a required diagram whose source, delivered artifact, browser receipt or Reviewer finding belongs to an older Design version or different digest
- **THEN** packet readiness is unavailable and the workflow MUST NOT ask for approval until the current visual chain is re-established

#### Scenario: Required diagram evidence did not pass
- **WHEN** a current required diagram has a failed or skipped browser/perceptual status, lacks its receipt-bound static preview, or the requested-client preview projection cannot be verified
- **THEN** packet readiness is unavailable without changing the Architecture Review conclusion, and the workflow reports the exact visual closing condition

### Requirement: Human decision binds the current packet
A recognizable human decision SHALL affect the gate only when evidence contains one legal decision, the exact human actor, current Action ID, inherited current packet ref/version/digest, binding profile, evidence ref and recorded time. The human-facing response MUST NOT require the actor to copy a packet digest that the verified current Action already freezes. A current-interaction decision MUST originate from a current user-role message rather than fixture content, quoted text, Agent output or a third-party instruction. Ambiguous acknowledgement, urgency, assignment, recommendation and Reviewer conclusion MUST NOT count as approval.

#### Scenario: Human explicitly approves the current Action
- **WHEN** the unique Owner records one legal decision through an accepted current-Action binding profile and all inherited Design/Review/packet identities reread exactly
- **THEN** the workflow records current-packet decision evidence and follows the selected publication path

#### Scenario: Human says OK without Action binding
- **WHEN** a human writes an ambiguous acknowledgement without the current Action and legal decision
- **THEN** the workflow remains `waiting_human` and records no valid decision evidence

#### Scenario: Human decides on a superseded Action
- **WHEN** a recognizable human records a legal decision for an older Action or packet
- **THEN** the workflow preserves the decision for audit, emits a current-gate no-op, and identifies the Action that still requires a decision

### Requirement: Approval packet explains every legal human outcome
The machine packet SHALL bind the versioned `human_review_surface_v1` that explains in Chinese what `approved_design_only`, `approved_for_spec`, `revision_requested` and `rejected` do, including next canonical state, publication/handoff effects, OpenSpec boundaries, principal irreversible or terminal consequence, and immediate planned writes. The human surface MUST identify the current Action and Design version, MUST NOT require the packet body to be opened, and MUST NOT preselect a decision from `ARCHITECTURE_RECOMMENDATION`.

#### Scenario: Human compares approval choices
- **WHEN** a current ready Action is presented for decision
- **THEN** its summary lets the human distinguish documentation-only publication, R&D handoff authorization, new Design iteration and terminal rejection before submitting one legal value

### Requirement: Packet brief surfaces complete material access and accepted risks
The packet SHALL bind one stable human entry for the complete frozen Design and SHALL bind internal refs for the complete Review and packet evidence. The human summary SHALL expose Design maturity, Reviewer conclusion and every accepted non-blocking risk with risk ID, Owner, conditions and concise rationale; full acceptance evidence MAY remain internal. Access confirmation and risk acceptance MUST remain separate from the final decision.

#### Scenario: Approvable-with-warnings packet is delivered
- **WHEN** Review conclusion is `APPROVABLE_WITH_WARNINGS`
- **THEN** the human surface identifies each accepted risk and its Owner/conditions, offers the one complete Design entry, and does not require separate Review or Packet reading to fabricate missing acceptance
