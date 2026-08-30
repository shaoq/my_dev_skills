## ADDED Requirements

### Requirement: Blocking human clarification requests are reviewable
When architecture work cannot progress until a recognizable human supplies one or more decisions, the skill SHALL make the clarification request independently reviewable in the Work Item. For every decision item it MUST state the decision required, a concrete candidate recommendation or explicit `no_recommendation`, the factual or principled basis, material risks or consequences, missing evidence with Owner and closure condition, and an editable accept/modify/reject response form. The request MUST distinguish facts, inferences, recommendations and unresolved evidence, and MUST NOT merely state that confirmation is required.

#### Scenario: Critical evidence gaps need human input
- **WHEN** an `ARCH-DESIGN` remains at `researching` or `designing` with `BLOCKED_REASON=critical_evidence_gaps` and asks a human to choose governance, SLO, deployment, ownership or product-contract inputs
- **THEN** the corresponding `ARCH-CONTROL` update or linked clarification comment contains the complete reviewable clarification structure for each requested decision

#### Scenario: No defensible candidate value exists
- **WHEN** available evidence cannot support a safe candidate value for a requested decision
- **THEN** the item records `no_recommendation`, explains which missing evidence changes the choice, and provides bounded options or a deterministic evidence-gathering path with Owner and closure condition
