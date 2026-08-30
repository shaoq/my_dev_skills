## MODIFIED Requirements

### Requirement: Every architecture stage has a structured report contract
The skill SHALL provide readable templates for `ARCH-CONTROL`, `ARCH-RESEARCH`, `ARCH-DESIGN`, `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET`, `ARCH-RD-HANDOFF`, ADR, and detailed design, and each report MUST identify the Work Item or Issue, version, owner, status, evidence, and next action applicable to that artifact. `ARCH-CONTROL` SHALL separately record Review conclusion, current packet ref/version/digest, external readiness or unavailable evidence ref, human decision evidence, `WAIT_REASON`, and `BLOCKED_REASON`.

#### Scenario: Architecture work begins
- **WHEN** an architecture request is accepted and routed
- **THEN** the Lead creates or updates `ARCH-CONTROL` with design type, Subject Project, current stage, owners, expected artifacts, human gates, and next action

#### Scenario: Architecture review becomes approvable
- **WHEN** Reviewer completes an approvable review for an exact design version
- **THEN** the workflow creates or references an immutable versioned `ARCH-APPROVAL-PACKET`, computes its raw-byte digest, and records external readiness evidence separately from both packet payload and Review conclusion before computing the next stage

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
