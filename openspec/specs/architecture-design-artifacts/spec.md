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
`ARCH-DESIGN vN` SHALL be understandable without an OpenSpec change, Issue history or other comment context and MUST exist as a canonical UTF-8 Markdown artifact suitable for immutable attachment delivery. It MUST contain identity and evidence inputs; executive summary; architecture recommendation, rationale and confidence; problem/current state and architecture drivers; goals and non-goals; system context, responsibility boundaries and a simplified architecture view; components, data/control flows, interfaces and consistency semantics; normal and critical failure flows; security, privacy, reliability, performance, capacity, cost, observability and evaluation design; alternatives, trade-offs and rejected reasons; migration, rollout, rollback, roll-forward and exit; operations/RACI; risks, assumptions, determined and undetermined matters; validation/acceptance plan; and R&D decomposition. Missing evidence MAY prevent `decision_ready` or a final product/platform choice, but the design MUST still distinguish the frozen architecture, current default or PoC recommendation, decisions that remain human-owned, and evidence that would change the recommendation.

#### Scenario: Solution Architect completes a candidate design
- **WHEN** sufficient research evidence exists to recommend a solution or a platform-neutral architecture while bounded decisions remain open
- **THEN** the Solution Architect publishes a versioned standalone `ARCH-DESIGN-vN.md` linked to its `ARCH-RESEARCH` inputs, records its raw-byte digest, labels its readiness and unresolved decisions accurately, and does not create OpenSpec artifacts

#### Scenario: A design is only a collection of prompts or comment fragments
- **WHEN** the candidate output lacks the complete architecture narrative, recommendation, architecture views, consequences, operational design or validation path and instead relies on questions or historical comments to reconstruct the solution
- **THEN** the workflow marks the design incomplete, does not request a content decision, and returns it to the Solution Architect with the missing sections

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

### Requirement: Human-facing architecture artifacts use the shared action contract
`ARCH-CONTROL`, `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET` and `ARCH-RD-HANDOFF` SHALL use the platform-neutral Human Action Request contract whenever their next action depends on a recognizable human. Artifacts MAY retain complete control and audit fields, but their human-facing entry point MUST present the action summary before those fields and link the exact complete materials needed for the decision.

#### Scenario: Control record waits for routing
- **WHEN** Subject Project or approved-for-spec Target Project routing is missing
- **THEN** `ARCH-CONTROL` presents bounded routing candidates or `no_recommendation`, Owner, consequences, exact reply and post-response state instead of only `WAIT_REASON=target_project`

### Requirement: Non-blocking risk acceptance is explicit and attributable
Every risk represented as accepted in `ARCH-REVIEW` MUST identify a stable risk ID, the exact accepting human Owner and authority scope, acceptance conditions or expiry, evidence ref and recorded time. Reviewer conclusion `APPROVABLE_WITH_WARNINGS` MUST NOT rely on an unowned or generally acknowledged warning.

#### Scenario: Reviewer finds a non-blocking operational risk
- **WHEN** the risk can remain in an approvable design only if an accountable Owner accepts it
- **THEN** the workflow emits a `risk_acceptance` Human Action Request and Reviewer uses only its version-bound acceptance evidence

#### Scenario: One human accepts another Owner's risk
- **WHEN** a human without the declared authority scope writes an acceptance-looking response
- **THEN** the risk remains unaccepted and the Review cannot treat that response as closure evidence

### Requirement: Handoff routing is decision-ready
Before `ARCH-RD-HANDOFF` becomes authoritative, target Project, repository, default branch and R&D Owner SHALL be either already confirmed or presented through routing Human Action Requests that explain candidate fit, cross-project consequences and exact post-selection writes. The workflow MUST NOT create a missing target resource.

#### Scenario: Approved design has multiple possible implementation projects
- **WHEN** `approved_for_spec` is valid but target routing is not unique
- **THEN** the workflow preserves approval, remains `waiting_human`, presents bounded routing choices and creates no handoff until one authorized choice is recorded
