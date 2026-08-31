## ADDED Requirements

### Requirement: Every human-dependent next action is independently reviewable
Whenever architecture workflow progress requires a recognizable human action, the core skill SHALL emit one or more platform-neutral `Human Action Request` items. Each item MUST contain a stable action ID and type, current stage/reason, exact artifact or routing version binding, Decision Owner and authority scope, one atomic decision required, a candidate recommendation or explicit `no_recommendation`, bounded alternatives, factual/principled basis, option-specific consequences and material risks, unresolved evidence with Owner and closure condition, stable human-accessible evidence refs, an exact response form, the resulting next stage/Owner/planned writes for every response, and an explicit non-authorization boundary.

#### Scenario: Workflow needs a human action
- **WHEN** `Next action` requires a human to choose a design input, accept a risk, approve a current packet, confirm routing or confirm artifact access
- **THEN** the workflow presents the complete Human Action Request before asking for a response and MUST NOT merely report that confirmation is required

#### Scenario: Evidence cannot support a recommendation
- **WHEN** available evidence cannot support one defensible candidate
- **THEN** the request records `no_recommendation`, gives bounded alternatives or a deterministic evidence-gathering path, and states what evidence and Owner will close the choice

### Requirement: Human action types preserve distinct authority
The core skill SHALL distinguish `design_input`, `risk_acceptance`, `design_approval`, `routing`, and `access_confirmation`. A response MUST affect only its action type, authority scope and bound version; it MUST NOT satisfy another action type, another Owner's decision, missing measurements, Review conclusion, packet readiness or a current-packet approval unless that response independently satisfies the applicable legal gate.

#### Scenario: Design input is accepted
- **WHEN** an authorized Owner accepts a `design_input` candidate while independent measurements or other Owner decisions remain open
- **THEN** only that bound input changes and every unrelated evidence or approval gate remains open

#### Scenario: Access is confirmed
- **WHEN** a target human confirms opening complete artifacts through the listed stable refs
- **THEN** only the access-confirmation action closes and no design approval is inferred

### Requirement: Independent decisions are split by owner and consequence
One Human Action Request item MUST bind one authority scope and one atomic decision. Fields with different authorized Owners, independently selectable outcomes or different next-state consequences MUST be separate items. A summary MAY group items for reading, but a general response MUST NOT close items across authority scopes.

#### Scenario: Multiple teams own one apparent questionnaire section
- **WHEN** one topic includes Privacy policy, SRE evidence and Product preference decisions
- **THEN** the workflow emits separate action items or sub-items with independent Owners and exact replies instead of one ambiguous `接受全部`

### Requirement: Human summary precedes audit detail
User-visible output SHALL lead with a concise action summary containing why the action is needed now, the recommendation, principal consequence, authorized Owner, exact response and post-response outcome. Complete technical materials MUST be available through stable human-accessible refs, while digests, internal status projections and other audit fields remain available after the decision content and MUST NOT be used as substitutes for a readable summary.

#### Scenario: Human reviews from a mobile client
- **WHEN** a Human Action Request references complete design, review, packet or evidence materials
- **THEN** the summary exposes stable refs that the target human can open without relying on an Agent-only absolute local path

### Requirement: Superseded requests are explicit no-ops
Every version-bound Human Action Request SHALL identify whether it is current. A response bound to a superseded action or packet MUST be retained for audit, MUST NOT change the current gate, and MUST direct the human to the exact current request that still requires action.

#### Scenario: Human responds to an older request
- **WHEN** a newer bound artifact or routing decision has superseded the request
- **THEN** the old response is recorded as no-op and the workflow presents the current action ref/version and consequences
