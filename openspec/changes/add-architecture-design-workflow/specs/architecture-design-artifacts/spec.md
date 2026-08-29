## ADDED Requirements

### Requirement: Every architecture stage has a structured report contract
The skill SHALL provide readable templates for `ARCH-CONTROL`, `ARCH-RESEARCH`, `ARCH-DESIGN`, `ARCH-REVIEW`, `ARCH-RD-HANDOFF`, ADR, and detailed design, and each report MUST identify the Issue, version, owner, status, evidence, and next action applicable to that artifact.

#### Scenario: Architecture work begins
- **WHEN** an architecture request is accepted and routed
- **THEN** the Lead creates or updates `ARCH-CONTROL` with design type, Subject Project, current stage, owners, expected artifacts, human gates, and next action

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
The skill SHALL keep exploration and iteration history in the Issue and MUST publish ADR and detailed design to the architecture repository only after explicit human approval.

#### Scenario: Design is not yet approved
- **WHEN** a design is still reviewing, blocked, or awaiting revision
- **THEN** no ADR or detailed design is written to the repository

#### Scenario: Design is approved
- **WHEN** the user explicitly approves the reviewed version
- **THEN** the workflow creates an ADR that records the decision and a detailed design that preserves the approved technical content and traceability

### Requirement: Development handoff is self-contained
`ARCH-RD-HANDOFF` MUST identify the approved design and ADR, target project and repository, implementation boundaries, cross-project dependencies, non-functional acceptance criteria, rollout and rollback obligations, unresolved decisions, and the authorization state.

#### Scenario: Handoff is authorized
- **WHEN** the user records `approved_for_spec` and a target project exists
- **THEN** the handoff contains enough information for the target R&D Team to begin its own requirement analysis and OpenSpec proposal without reinterpreting architecture intent
