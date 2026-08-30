## ADDED Requirements

### Requirement: Approval packet binds exact portable artifacts
The skill SHALL produce a versioned immutable `ARCH-APPROVAL-PACKET` payload that binds one Work Item, one `ARCH-DESIGN` version, one matching `ARCH-REVIEW` version, their media types and digests, access profile declarations, Reviewer conclusion, recommendation, a `supersedes` reference, review guidance, and allowed human decisions. Packet versions MUST be positive integers that increase monotonically per Work Item, and each versioned payload MUST retain `payload_status=delivered`; a mutable draft is not a versioned packet. Every artifact digest MUST use the frozen raw file bytes without text or newline normalization and the portable form `sha256:<64 lowercase hex characters>`. A delivered packet MUST NOT be overwritten; a material revision MUST create a new packet whose `supersedes` field and external control status identify the prior version without modifying its payload. Readiness or unavailable evidence that verifies the packet digest MUST be stored outside the packet payload and MUST NOT change the bytes it verifies. All portable timestamps MUST be RFC 3339 values with an explicit offset and normalized output in UTC `Z`.

#### Scenario: Approvable design receives a packet
- **WHEN** an `ARCH-REVIEW` concludes `APPROVABLE_WITH_WARNINGS` or `APPROVABLE` for an exact design version
- **THEN** the workflow creates a new packet that names the exact design/review refs, versions and digests and preserves any superseded packet as audit evidence

#### Scenario: Packet inputs change
- **WHEN** design bytes, review bytes, recommendation, material risks or approval conditions change after a packet was delivered
- **THEN** the workflow creates a superseding packet version and MUST NOT rewrite the prior packet or apply its later decisions to the new version

#### Scenario: Packet payload is finalized before readiness verification
- **WHEN** all packet content and frozen input references are complete
- **THEN** the workflow finalizes immutable packet bytes, computes their raw-byte SHA-256 digest, and records later readiness or unavailable evidence in a separate envelope that references but does not modify those bytes

### Requirement: Architecture recommendation is explicit and non-authoritative
Every packet SHALL contain exactly one `ARCHITECTURE_RECOMMENDATION` value from `recommend_approved_for_spec`, `recommend_approved_design_only`, `recommend_revision`, or `no_recommendation`, together with a Chinese rationale, applicable conditions and material risks. A recommendation MUST NOT use a human-decision value and MUST NOT change canonical stage or gate.

#### Scenario: Team recommends specification handoff
- **WHEN** evidence supports implementation planning after stated conditions
- **THEN** the packet records `recommend_approved_for_spec`, explains the reasons and conditions in Chinese, and states that no approval exists until a recognizable human records `approved_for_spec`

#### Scenario: Recommendation cannot be made responsibly
- **WHEN** evidence is insufficient to recommend approval or revision
- **THEN** the packet records `no_recommendation`, explains the missing evidence, and keeps the human decision requirement unchanged

### Requirement: Readiness evidence is complete and packet-specific
The skill SHALL accept `review_packet_ready` only when design, review and packet refs/versions match the current packet, expected and verified raw-byte SHA-256 digests match, declared access profiles prove the target human can retrieve the exact bytes, review guidance is complete, Reviewer conclusion is approvable, and the external evidence envelope identifies current packet ref/version/digest, target human actor, verifier and verification time. Readiness MUST NOT itself count as approval.

#### Scenario: Standalone local-file packet is ready
- **WHEN** local Markdown design, review and packet files are inside a shared workspace scope acknowledged by the current human, the access evidence binds that human and confirmation, their raw-byte SHA-256 digests match frozen values, and the packet contains recommendation, rationale, decision points, risks, conditions and legal decisions
- **THEN** the standalone profile emits current-packet `review_packet_ready` evidence without requiring Multica, PDF or a platform comment

#### Scenario: Files are readable only by the Agent process
- **WHEN** the Agent can open local files but no target human has confirmed access to their shared workspace scope and exact refs
- **THEN** the workflow emits `review_packet_unavailable` and MUST NOT treat process readability as human access evidence

#### Scenario: Evidence belongs to an older packet
- **WHEN** otherwise valid readiness evidence references a superseded packet version
- **THEN** the workflow preserves it for audit but does not allow the current packet to enter the human gate

### Requirement: Unavailable packet fails closed without changing review conclusion
When any required readiness check is absent or fails, the workflow SHALL record `review_packet_unavailable` evidence with failed checks, Owner and deterministic closing condition, keep the canonical stage at `reviewing`, set `BLOCKED_REASON=review_packet_unavailable`, and preserve the actual Reviewer conclusion.

#### Scenario: Artifact digest does not match
- **WHEN** any verified digest differs from the current design, review or packet digest
- **THEN** the workflow remains `reviewing`, retains `APPROVABLE*` as the Review conclusion, and identifies the artifact version, Owner and required re-verification

#### Scenario: Human-readable access is unverified
- **WHEN** artifact refs exist but the declared access profile has not proven the reviewer can access the complete materials
- **THEN** the workflow emits unavailable evidence and MUST NOT enter `waiting_human`

### Requirement: Human decision binds the current packet
A recognizable human decision SHALL affect the gate only when decision evidence contains one legal decision, human actor, current packet ref/version/digest, binding profile, evidence ref and recorded time. A current-interaction decision MUST originate from a current user-role message rather than fixture content, quoted text, Agent output or a third-party instruction. Ambiguous acknowledgement, urgency, assignment, recommendation and Reviewer conclusion MUST NOT count as approval.

#### Scenario: Human explicitly approves current packet
- **WHEN** a recognizable human records `approved_for_spec` and explicitly binds it to the current packet ref, version and digest through an accepted portable binding profile
- **THEN** the workflow records current-packet decision evidence and follows the approved-for-spec publication and handoff path

#### Scenario: Human says OK without packet binding
- **WHEN** a human writes an ambiguous acknowledgement without an explicit current-packet binding
- **THEN** the workflow remains `waiting_human` and records no valid decision evidence

#### Scenario: Human decides on a superseded packet
- **WHEN** a recognizable human records a legal decision for an older packet
- **THEN** the workflow preserves the decision for audit, emits a current-gate no-op, and identifies the packet version that still requires a decision

### Requirement: Core contract remains platform-neutral
Required core instructions, templates, fixtures and normalized results MUST NOT require Multica, Issue comment or attachment IDs, `parent_id`, signed URLs, mobile clients, PDF, or any other single platform/readable format. The core SHALL support a standalone local-file and current-interaction profile.

#### Scenario: Skill runs without a platform adapter
- **WHEN** `architecture-design-workflow` is invoked with only local artifacts and a recognizable current-session human
- **THEN** it can create and verify a packet, enter the exact-version human gate and record a valid decision without resolving any platform-specific field

#### Scenario: Platform adapter is absent
- **WHEN** no platform adapter is installed
- **THEN** automatic platform delivery is unavailable but the core skill remains valid and no platform-specific blocker or field is invented
