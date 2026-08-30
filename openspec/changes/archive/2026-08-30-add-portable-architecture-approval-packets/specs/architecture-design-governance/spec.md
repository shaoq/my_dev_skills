## MODIFIED Requirements

### Requirement: Workflow classifies and controls architecture work
The skill SHALL classify each accepted architecture request as `evolution`, `greenfield`, or `hybrid`, record its stage in `ARCH-CONTROL`, and allow only transitions defined by the architecture workflow. The canonical stages MUST be `intake`, `routed`, `researching`, `designing`, `reviewing`, `waiting_human`, `approved_design_only`, `approved_for_spec`, `publishing`, `handed_off`, `completed_design_only`, and `rejected`. `revision_requested` MUST be recorded as a decision that starts a new `designing` iteration rather than as a persistent stage. Every `waiting_human` record MUST identify `WAIT_REASON` as `design_approval` or `target_project`. `review_packet_unavailable` SHALL be a stable reviewing blocker distinct from Review conclusion; an approvable review MUST remain at `reviewing` until an external current-packet `review_packet_ready` envelope binds the current packet ref/version/digest. `approved_artifact_unavailable` SHALL be a stable publishing blocker that preserves the valid human decision and readiness while exact approved bytes cannot be recovered.

#### Scenario: Existing system architecture upgrade
- **WHEN** a request primarily changes an existing system and its integration contracts
- **THEN** the workflow classifies it as `evolution` and requires current-state, impact, migration, and rollback evidence

#### Scenario: New supporting system
- **WHEN** a request requires a new standalone system with no existing implementation baseline
- **THEN** the workflow classifies it as `greenfield` and requires boundary, capability, build-vs-buy, deployment, and cost evidence

#### Scenario: Mixed architecture change
- **WHEN** a request combines existing-system modification with a new service or platform
- **THEN** the workflow classifies it as `hybrid` and requires both evidence sets plus their interface and migration sequence

#### Scenario: Review requests revision
- **WHEN** the Reviewer concludes `NEEDS_REVISION`
- **THEN** the workflow starts a new `designing` iteration, preserves the prior design and review versions, and does not enter publication

#### Scenario: Reviewer revision does not create an approval packet
- **WHEN** the Reviewer concludes `NEEDS_REVISION` before an approvable packet exists
- **THEN** the workflow starts a new design version without creating an approval packet, and creates a packet only after a later exact design/review pair becomes approvable

#### Scenario: Design is rejected
- **WHEN** a recognizable human explicitly records `rejected` for the current ready packet ref, version and digest
- **THEN** the workflow enters terminal stage `rejected` and does not publish or create a development handoff

#### Scenario: Approvable review lacks a ready packet
- **WHEN** the Reviewer concludes `APPROVABLE_WITH_WARNINGS` or `APPROVABLE` but current-packet readiness is absent or failed
- **THEN** the workflow preserves that conclusion, remains `reviewing`, and records `BLOCKED_REASON=review_packet_unavailable` with failure evidence and closing condition

#### Scenario: Approvable review has a ready packet
- **WHEN** the Reviewer conclusion is approvable and a valid external `review_packet_ready` envelope binds the current design, review and packet refs, versions and digests
- **THEN** the workflow enters `waiting_human` with `WAIT_REASON=design_approval` and `BLOCKED_REASON=none`

#### Scenario: Historical waiting-human record is not automatically migrated
- **WHEN** workflow rules are upgraded while a historical record is already persisted at `waiting_human` without packet readiness evidence and no new design or review version is produced
- **THEN** the workflow preserves the historical stage and evidence without fabricating readiness or automatically downgrading it, and applies the new packet gate when that record is explicitly refreshed or versioned

### Requirement: Human approval uses two explicit gates
The workflow MUST distinguish `approved_design_only` from `approved_for_spec` and MUST NOT infer either approval from an Agent recommendation, urgency, assignment, Reviewer conclusion, readiness evidence, or ambiguous human comment. A legal human decision MUST bind the current `ARCH-APPROVAL-PACKET` ref, version and digest; a decision for a superseded packet MUST be an auditable no-op for the current gate.

#### Scenario: Design-only approval
- **WHEN** a recognizable human explicitly records `approved_design_only` for the current ready packet
- **THEN** the workflow may publish ADR and detailed design but must not create a development handoff that authorizes OpenSpec work

#### Scenario: Approval for Spec
- **WHEN** a recognizable human explicitly records `approved_for_spec` for the current ready packet
- **THEN** the workflow may publish the approved design and create `ARCH-RD-HANDOFF` for the selected target project

#### Scenario: Revision requested
- **WHEN** a recognizable human records `revision_requested` for the current ready packet ref, version and digest
- **THEN** the workflow returns to designing with a new `ARCH-DESIGN`, records the prior packet as superseded only in external control state without modifying its payload, retains the prior review trail, and does not create a new packet until the replacement design/review pair becomes approvable

#### Scenario: Recommendation is not approval
- **WHEN** the packet contains any `ARCHITECTURE_RECOMMENDATION` but no valid current-packet human decision
- **THEN** the workflow remains `waiting_human` and does not publish or hand off

#### Scenario: Superseded packet is approved late
- **WHEN** a human decision binds an older packet after a new current packet exists
- **THEN** the workflow preserves the old decision as evidence but does not change the current gate
