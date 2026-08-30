## ADDED Requirements

### Requirement: Human waiting states publish actionable decision semantics
Whenever core reports `waiting_human` or otherwise names a human as `Next Owner`, it SHALL also publish the applicable Human Action Request items. Each legal response MUST state the resulting canonical stage, remaining blockers, next Owner and immediate planned writes; no response MAY imply authorization outside its declared action type.

#### Scenario: Subject Project is missing
- **WHEN** intake reaches `waiting_human` with `WAIT_REASON=target_project` and `BLOCKED_REASON=missing_subject_project`
- **THEN** a routing request explains the ownership decision, candidates or evidence path, consequences and exact reply while gate remains `none`

#### Scenario: Current packet awaits approval
- **WHEN** a current ready packet enters `waiting_human` with `WAIT_REASON=design_approval`
- **THEN** a design-approval request explains all four legal outcomes and no recommendation, readiness or ambiguous acknowledgement is treated as the decision

### Requirement: Formal revision decision and revision guidance remain separate
`revision_requested` SHALL remain the only authoritative current-packet decision value for returning to `designing`. Detailed requested changes MAY be captured in a separate version-bound revision brief ref, but prose, the brief itself or an edited decision MUST NOT replace legal decision evidence. When no actionable brief exists, the workflow SHALL create a new `design_input` request after entering `designing` rather than claim that revision scope is known.

#### Scenario: Human requests revision with a brief
- **WHEN** a recognizable human records current-packet `revision_requested` and supplies a separate bound revision brief
- **THEN** the workflow starts a replacement design attempt and uses the brief as non-authoritative design input without altering the prior packet

#### Scenario: Human provides only the revision token
- **WHEN** current-packet `revision_requested` is valid but no actionable revision brief exists
- **THEN** the workflow enters `designing`, records the missing scope and presents a reviewable design-input request before claiming a complete revision requirement

### Requirement: Human-readable requests do not weaken canonical gates
Adding a Human Action Request MUST NOT change canonical stages, blockers, Review conclusions, packet readiness, recommendation or legal decision tokens. A readable request, candidate option, reaction or authorization-looking text is non-authoritative until the corresponding existing evidence and actor-binding rules pass.

#### Scenario: Readable approval card has no legal decision
- **WHEN** the card and complete materials are available but no valid current-packet decision evidence exists
- **THEN** the workflow remains `waiting_human` and performs no publication or handoff
