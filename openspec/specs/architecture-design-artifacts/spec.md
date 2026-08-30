# architecture-design-artifacts Specification

## Purpose
TBD - created by archiving change add-architecture-design-workflow. Update Purpose after archive.
## Requirements
### Requirement: Every architecture stage has a structured report contract
The skill SHALL provide readable templates for `ARCH-CONTROL`, `ARCH-RESEARCH`, `ARCH-DESIGN`, `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET`, `ARCH-RD-HANDOFF`, ADR, and detailed design, and each report MUST identify the Work Item or Issue, version, owner, status, evidence, and next action applicable to that artifact. `ARCH-CONTROL` SHALL separately record Review conclusion, current packet ref/version/digest, external readiness or unavailable evidence ref, human decision evidence, `WAIT_REASON`, and `BLOCKED_REASON`.

#### Scenario: Architecture work begins
- **WHEN** an architecture request is accepted and routed
- **THEN** the Lead creates or updates `ARCH-CONTROL` with design type, Subject Project, current stage, owners, expected artifacts, human gates, and next action

#### Scenario: Architecture review becomes approvable
- **WHEN** Reviewer completes an approvable review for an exact design version
- **THEN** the workflow creates or references an immutable versioned `ARCH-APPROVAL-PACKET`, computes its raw-byte digest, and records external readiness evidence separately from both packet payload and Review conclusion before computing the next stage

### Requirement: Research is evidence-backed and type-aware
`ARCH-RESEARCH` MUST distinguish facts, assumptions, constraints, unknowns, and recommendations, and MUST include the evidence required by the selected design type.

#### Scenario: Evolution research cites code evidence
- **WHEN** an Analyst investigates an existing system
- **THEN** `ARCH-RESEARCH` links relevant repositories, commits, GitNexus flows or symbols, current interfaces, constraints, and observed risks

#### Scenario: Greenfield research compares external choices
- **WHEN** an Analyst investigates a new system
- **THEN** `ARCH-RESEARCH` compares viable technologies or services using current authoritative sources and records cost, operations, maturity, lock-in, and security assumptions

### Requirement: Design output is independently reviewable
`ARCH-DESIGN vN` SHALL be understandable without an OpenSpec change and MUST contain goals, non-goals, context, boundaries, alternatives, recommendation, non-functional design, failure modes, migration or rollout, rollback, cost and operations, open questions, and validation plan.

#### Scenario: Solution Architect completes a candidate design
- **WHEN** sufficient research evidence exists to recommend a solution
- **THEN** the Solution Architect publishes a versioned `ARCH-DESIGN` linked to its `ARCH-RESEARCH` inputs and does not create OpenSpec artifacts

### Requirement: Architecture review is independent and deterministic
`ARCH-REVIEW` MUST bind to one `ARCH-DESIGN` version, remain read-only, list evidence-backed findings with owner and closure condition, and conclude with `BLOCKED`, `NEEDS_REVISION`, `APPROVABLE_WITH_WARNINGS`, or `APPROVABLE`.

#### Scenario: Critical evidence is missing
- **WHEN** the reviewed design lacks required current-state, boundary, security, migration, rollback, operational, or cost evidence
- **THEN** the Reviewer reports a blocking or major finding and does not mark the design approvable

#### Scenario: Review passes
- **WHEN** all mandatory evidence and decisions are complete and only explicitly accepted non-blocking risks remain
- **THEN** the Reviewer emits the corresponding approvable conclusion and identifies the exact design version eligible for human approval

### Requirement: Repository publication follows human approval
The skill SHALL keep exploration and iteration history in the Work Item and MUST publish ADR and detailed design to the architecture repository only after an explicit recognizable-human decision binds the current ready approval packet. Published documents MUST record packet ref/version/digest, design/review digests, readiness evidence ref, decision evidence ref and existing traceability fields.

#### Scenario: Design is not yet approved
- **WHEN** a design is still reviewing, packet readiness is unavailable, the workflow is waiting for a decision, or the decision binds a superseded packet
- **THEN** no ADR or detailed design is written to the repository

#### Scenario: Design is approved
- **WHEN** a recognizable human explicitly approves the current ready packet
- **THEN** the workflow creates an ADR that records the decision and a detailed design that preserves the exact approved technical content, packet evidence and traceability

#### Scenario: Approved artifact digest cannot be verified
- **WHEN** publication cannot recover packet, design or review bytes matching the current packet and its frozen digests
- **THEN** publication remains at `publishing`, preserves the valid human decision and packet readiness, records `BLOCKED_REASON=approved_artifact_unavailable` with failed artifact, Owner and closing condition, and MUST NOT reconstruct approximate content from the decision brief

#### Scenario: Approved artifact bytes are restored
- **WHEN** every failed packet, design and review ref again yields raw bytes matching the frozen digests
- **THEN** the workflow clears `approved_artifact_unavailable` and resumes publication without changing the approved packet or human decision

### Requirement: Development handoff is self-contained
`ARCH-RD-HANDOFF` MUST identify the approved design and ADR, target project and repository, implementation boundaries, cross-project dependencies, non-functional acceptance criteria, rollout and rollback obligations, unresolved decisions, and the authorization state.

#### Scenario: Handoff is authorized
- **WHEN** the user records `approved_for_spec` and a target project exists
- **THEN** the handoff contains enough information for the target R&D Team to begin its own requirement analysis and OpenSpec proposal without reinterpreting architecture intent

### Requirement: Blocking human clarification requests are reviewable
When architecture work cannot progress until a recognizable human supplies one or more decisions, the skill SHALL make the clarification request independently reviewable in the Work Item. For every decision item it MUST state the decision required, a concrete candidate recommendation or explicit `no_recommendation`, the factual or principled basis, material risks or consequences, missing evidence with Owner and closure condition, and an editable accept/modify/reject response form. The request MUST distinguish facts, inferences, recommendations and unresolved evidence, and MUST NOT merely state that confirmation is required.

#### Scenario: Critical evidence gaps need human input
- **WHEN** an `ARCH-DESIGN` remains at `researching` or `designing` with `BLOCKED_REASON=critical_evidence_gaps` and asks a human to choose governance, SLO, deployment, ownership or product-contract inputs
- **THEN** the corresponding `ARCH-CONTROL` update or linked clarification comment contains the complete reviewable clarification structure for each requested decision

#### Scenario: No defensible candidate value exists
- **WHEN** available evidence cannot support a safe candidate value for a requested decision
- **THEN** the item records `no_recommendation`, explains which missing evidence changes the choice, and provides bounded options or a deterministic evidence-gathering path with Owner and closure condition
