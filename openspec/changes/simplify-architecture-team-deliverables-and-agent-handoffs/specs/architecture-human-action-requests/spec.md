## MODIFIED Requirements

### Requirement: Every human-dependent next action is independently reviewable
Whenever progress requires a recognizable human content decision or unresolved dependency input, the core SHALL emit one or more platform-neutral `Human Action Request` items. Each item MUST contain a stable action ID/type, current stage/reason, exact Design or routing binding, Decision Owner and authority scope, one atomic decision, recommendation or `no_recommendation`, bounded alternatives, rationale, option consequences/risks, unresolved evidence with Owner/closing condition, one canonical Design entry when architecture content is involved, an exact response form, post-response stage/Owner/writes, and a non-authorization boundary. Other Owners' actions MAY appear only as non-actionable summaries. If Owner binding is unknown, the request SHALL be a dependency-input action rather than a content decision. Internal execution steps and access/readback operations MUST NOT generate human requests merely to expose progress.

#### Scenario: Workflow needs a human content action
- **WHEN** `Next action` requires a human to choose a Design input, accept a risk or approve a current Design
- **THEN** the workflow presents one complete Human Action Request with the canonical Design entry and MUST NOT require separate Research, Control, Review or Packet reading

#### Scenario: Evidence cannot support a recommendation
- **WHEN** evidence cannot support one defensible candidate
- **THEN** the request records `no_recommendation`, gives bounded alternatives or a deterministic evidence path, and states what evidence and Owner close the choice

#### Scenario: Several authority scopes remain open
- **WHEN** independently owned decisions remain open but the current reader is bound to one scope
- **THEN** the request asks only that reader's atomic decision and lists other actions as non-actionable dependencies

#### Scenario: Decision Owner is not bound
- **WHEN** a content action resolves to zero or multiple humans
- **THEN** the workflow asks an authorized routing actor to bind the Owner and MUST NOT ask the reader to decide the content on that role's behalf

### Requirement: Human summary precedes audit detail
User-visible output SHALL be an `Architecture Decision Brief` that leads with: one-paragraph solution summary; simplified architecture view; Design maturity; Architecture Team recommendation, rationale and confidence; concise Reviewer conclusion/findings; determined and undetermined matters; important alternatives/consequences; the one authorized decision; response outcomes; and exactly one clickable complete Design entry. It SHALL then provide the exact response and only minimal current/superseded identity. Research, Control, complete Review, Packet, digests, internal status and Agent execution evidence MUST NOT be mandatory human materials or precede the decision content.

The Design entry MUST be labeled human-accessible only in a client scope where a named verifier actually opened it, or `manual_check_required` under an explicit Owner-manual profile with verified identity/digest/stable entry. Agent-only reads, local paths, untested URLs, filename-only cards and non-navigable text MUST NOT satisfy the contract.

#### Scenario: Human reviews through a constrained client
- **WHEN** a Human Action Request depends on a substantial Design
- **THEN** the brief exposes one independently readable canonical Design entry and records per-scope access evidence without requiring other architecture artifacts to render

#### Scenario: Complete design exists outside the brief
- **WHEN** the Design is too substantial to copy into the comment
- **THEN** the brief summarizes it, binds exact ref/version/digest and provides one verified attachment or link to the complete document

#### Scenario: A stable identity is not navigable
- **WHEN** the Design entry is only an internal identity, untested URI, local path, filename-only card or non-opening display text
- **THEN** the request marks access unavailable or manual-check-required according to the selected profile and MUST NOT falsely claim it was opened
