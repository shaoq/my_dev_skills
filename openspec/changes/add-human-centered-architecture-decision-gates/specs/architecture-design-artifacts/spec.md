## ADDED Requirements

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
