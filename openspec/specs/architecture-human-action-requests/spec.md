# architecture-human-action-requests Specification

## Purpose
Define a platform-neutral, human-first contract for every architecture workflow action that requires a recognizable human decision, while preserving existing authority and audit gates.
## Requirements
### Requirement: Every human-dependent next action is independently reviewable
Whenever architecture workflow progress requires a recognizable human action, the core skill SHALL emit one or more platform-neutral `Human Action Request` items. Each item MUST contain a stable action ID and type, current stage/reason, exact artifact or routing version binding, Decision Owner and authority scope, one atomic decision required, a candidate recommendation or explicit `no_recommendation`, bounded alternatives, factual/principled basis, option-specific consequences and material risks, unresolved evidence with Owner and closure condition, stable human-accessible evidence refs, an exact response form, the resulting next stage/Owner/planned writes for every response, and an explicit non-authorization boundary. A request rendered for one current reader MUST ask for exactly one action that reader is uniquely authorized to decide; other Owners' open actions MAY appear only as dependency summaries without actionable response forms. If the Owner is unknown or cannot be bound uniquely, the current request SHALL be routing/owner-binding rather than a content decision.

#### Scenario: Workflow needs a human action
- **WHEN** `Next action` requires a human to choose a design input, accept a risk, approve a current packet, confirm routing or confirm artifact access
- **THEN** the workflow presents the complete Human Action Request for that exact Decision Owner before asking for a response and MUST NOT merely report that confirmation is required

#### Scenario: Evidence cannot support a recommendation
- **WHEN** available evidence cannot support one defensible candidate
- **THEN** the request records `no_recommendation`, gives bounded alternatives or a deterministic evidence-gathering path, and states what evidence and Owner will close the choice

#### Scenario: Several authority scopes remain open
- **WHEN** Privacy, Security, SRE, Product or other independently owned decisions remain open but the current reader is bound to only one scope
- **THEN** the request asks only the reader's one atomic decision and lists all other actions as non-actionable dependencies with their Owners and closure conditions

#### Scenario: Decision Owner is not bound
- **WHEN** a content action names only an unbound role or resolves to zero or multiple humans
- **THEN** the workflow asks an authorized routing actor to bind the Owner and MUST NOT ask the current reader to decide the content on that role's behalf

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
User-visible output SHALL be an `Architecture Decision Brief` that leads, in order, with: a one-paragraph solution summary; a simplified architecture view; the Architecture Team recommendation, rationale and confidence; determined and undetermined matters; the most important alternatives and consequences; the one decision within the current reader's authority; what happens after each response; and clickable complete Design, Research and Control material entries. It SHALL then provide the exact response and only the audit binding needed to establish current/superseded identity. Complete technical materials MUST be delivered as separately readable versioned artifacts rather than copied into the brief. Digests, internal status projections and other audit fields MUST NOT replace or precede the decision content.

A material entry MUST be labeled human-accessible only for the client scope in which a named verifier has opened it and resolved the exact bound material; stable object identity, Agent-only read, local path, untested URL, filename-only attachment card or rendered text without a navigable target MUST NOT satisfy this contract. Every material SHALL record requested client scopes, per-scope access status, verifier, verification time or `not_run`, and an Owner plus observable closing condition when unavailable.

#### Scenario: Human reviews through a constrained client
- **WHEN** a Human Action Request references complete Design, Research, Control, Review, Packet or evidence materials
- **THEN** the brief exposes independently readable entries the target human can open without an Agent-only path and records access evidence separately for each requested client scope

#### Scenario: Complete design exists outside the brief
- **WHEN** a decision depends on a substantial `ARCH-DESIGN vN`
- **THEN** the brief summarizes rather than copies the design, binds the exact canonical design artifact/version/digest, and provides a verified human-readable attachment or link to the complete document

#### Scenario: A stable identity is not a navigable material entry
- **WHEN** a renderer has only an internal object identity, an untested custom URI, a local path, a filename-only card or display text that does not open the exact complete material
- **THEN** the request marks that client scope unavailable or not run, names the Owner and closing condition, and MUST NOT describe the entry as human-accessible or request the content decision

### Requirement: Superseded requests are explicit no-ops
Every version-bound Human Action Request SHALL identify whether it is current. A response bound to a superseded action or packet MUST be retained for audit, MUST NOT change the current gate, and MUST direct the human to the exact current request that still requires action.

#### Scenario: Human responds to an older request
- **WHEN** a newer bound artifact or routing decision has superseded the request
- **THEN** the old response is recorded as no-op and the workflow presents the current action ref/version and consequences
