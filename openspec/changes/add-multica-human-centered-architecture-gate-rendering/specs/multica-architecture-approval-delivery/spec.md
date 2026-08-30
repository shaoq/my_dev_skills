## ADDED Requirements

### Requirement: Approval delivery explains decisions before technical bindings
The packet comment SHALL present the current review object, Team recommendation with Chinese rationale/conditions/risks, accepted warning summary and four legal human decisions with their Chinese consequences before marker or audit detail. It MUST instruct the target human to open the exact complete Design, Review and Packet attachments and MUST state that recommendation, access, status and operational authorization are not approval.

#### Scenario: Current packet is delivered for approval
- **WHEN** delivery and readiness preconditions pass for an approvable current packet
- **THEN** the target member can distinguish documentation-only approval, R&D handoff authorization, revision and terminal rejection before replying

### Requirement: Delivery and shared-scope writes have reviewable authorization
Explicit delivery authorization and every required `shared_workspace_sidecar_v1` write authorization SHALL be represented by an operational Human Action Request that identifies the exact existing target, final/temporary relative-path scope, planned object writes, no-clobber behavior, excluded resource creation and failure retention. The adapter MUST stop before writes when that request is absent, ambiguous, stale or does not cover the exact path scope.

#### Scenario: Shared sidecar scope is not authorized
- **WHEN** packet delivery objects could be created but no current request authorizes the mapping/readiness sidecar paths in an existing durable scope
- **THEN** the adapter performs no write, reports the specific authorization closing condition and does not treat local path knowledge as permission

### Requirement: Readiness verifies the rendered human entry point
In addition to existing marker, attachment, digest, mapping, projection and sidecar checks, readiness SHALL verify that the approval comment contains the current Human Action Request summary, option consequences, accepted-risk summary or `none`, exact stable attachment access guidance and non-approval boundary. A technically complete but unreadable or stale brief MUST close as `review_packet_unavailable` without changing Review conclusion.

#### Scenario: Comment omits decision consequences
- **WHEN** all three attachments and digests verify but the visible comment only lists legal tokens without explaining their effects
- **THEN** readiness is unavailable and the adapter identifies the brief-rendering closing condition
