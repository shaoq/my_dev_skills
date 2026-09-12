## MODIFIED Requirements

### Requirement: Human approval uses two explicit gates
The workflow MUST distinguish `approved_design_only` from `approved_for_spec` and MUST NOT infer either from an Agent recommendation, urgency, assignment, Reviewer conclusion, readiness or ambiguous comment. A legal decision MUST bind the current Action, whose verified machine manifest freezes current Design/Review/packet refs, versions and digests plus the current required visual manifest or explicit `diagram_not_applicable` decision. The human MUST open the canonical Design but MUST NOT be required to open the machine packet or interactive diagram. A decision for a superseded Action or manifest MUST be an auditable no-op.

#### Scenario: Design-only approval
- **WHEN** a recognizable human explicitly records `approved_design_only` for the current ready Action
- **THEN** the workflow may publish ADR and detailed design but MUST NOT create a development handoff authorizing OpenSpec work

#### Scenario: Approval for Spec
- **WHEN** a recognizable human explicitly records `approved_for_spec` for a current ready Action whose Design maturity is `spec_ready|implementation_ready`
- **THEN** the workflow may publish the approved Design and create `ARCH-RD-HANDOFF` for the selected target project

#### Scenario: Directional design cannot authorize specification
- **WHEN** a current Design declares `design_maturity=directional`
- **THEN** `approved_for_spec` is unavailable and the human surface explains that only design-only approval or revision can be selected

#### Scenario: Revision requested
- **WHEN** a recognizable human records `revision_requested` for the current ready Action
- **THEN** the workflow returns to designing, preserves all old artifacts, and creates a new Design/Review/manifest only after the revision scope or impact is established

#### Scenario: Recommendation is not approval
- **WHEN** any recommendation exists but no valid current-Action human decision exists
- **THEN** the workflow remains `waiting_human` and does not publish or hand off

#### Scenario: Superseded Action is approved late
- **WHEN** a human decision binds an older Action after a new current Action exists
- **THEN** the workflow preserves it as evidence but does not change the current gate

### Requirement: Human-readable requests do not weaken canonical gates
Reducing the human surface to one Design entry MUST NOT change canonical stages, blockers, Review conclusions, packet readiness, recommendation, legal decisions, digest verification or supersession. A readable request, Design attachment, candidate option, reaction or authorization-looking text remains non-authoritative until current Action, actor, manifest and evidence rules pass. Conversely, a human decision MUST NOT be blocked solely because internal Review, Control or Packet was not separately rendered to that human.

#### Scenario: Readable approval card has no legal decision
- **WHEN** the card and Design are available but no valid current-Action decision exists
- **THEN** the workflow remains `waiting_human` and performs no publication or handoff

#### Scenario: Internal artifacts were not human-rendered
- **WHEN** Design access and all machine readbacks pass but Review, Control and Packet were not opened by the Owner
- **THEN** the workflow may accept an otherwise valid current-Action decision because those artifacts are not mandatory human materials

## ADDED Requirements

### Requirement: Workflow attempts are pinned to one surface contract revision
Every attempt SHALL freeze compatible core, human-surface, internal-evidence and adapter contract revisions before its first side effect. A newly activated contract MUST apply only to new attempts. An existing attempt MUST continue under its frozen reader or be replaced by an explicit superseding attempt; it MUST NOT be reinterpreted in place.

#### Scenario: New contract is activated while an old Action waits
- **WHEN** an old three-attachment Action is still current-looking at activation time
- **THEN** the workflow leaves it under the old contract or marks it superseded through a new attempt, and MUST NOT consume it as a new one-Design Action

#### Scenario: Compatible new attempt starts
- **WHEN** core and adapter report a compatible new contract pair
- **THEN** the attempt freezes both revisions and all subsequent surfaces/evidence use that pair
