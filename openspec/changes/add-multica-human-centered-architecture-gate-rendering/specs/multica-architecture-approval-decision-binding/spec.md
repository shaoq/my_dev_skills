## ADDED Requirements

### Requirement: Legal token remains separate from human-readable context
The adapter SHALL continue to treat only one exact legal token under an accepted binding profile as authoritative decision content. Human-readable explanations, option consequences, reactions and revision prose MUST remain non-authoritative context and MUST NOT be concatenated with or parsed as the token.

#### Scenario: Member copies token with explanation
- **WHEN** the target member writes `revision_requested` plus prose in one candidate decision comment
- **THEN** the adapter retains it as non-binding audit/context text and asks for a fresh token-only decision comment

### Requirement: Revision brief can guide but not authorize replacement design
A separate revision brief MAY be associated with a valid `revision_requested` decision through a current packet/comment-bound `decision_context_ref`. The adapter MUST reread and digest that context, record `revision_scope=provided|missing|changed`, and MUST NOT let the brief create, replace or invalidate legal decision authority except that changed/missing context is reported for core follow-up.

#### Scenario: Valid revision decision has separate context
- **WHEN** the canonical member publishes a packet-bound revision brief and independently submits a valid token-only `revision_requested`
- **THEN** decision evidence keeps the token authoritative, records the brief as non-authoritative context and lets core use it as replacement-design input

#### Scenario: Revision token has no context
- **WHEN** `revision_requested` is otherwise valid and no current revision brief can be reread
- **THEN** the decision remains valid, `revision_scope=missing` is reported and core must request actionable scope separately

### Requirement: Decision evidence records the explained outcome version
Decision evidence SHALL identify the Human Action Request ref/version whose option consequences were displayed with the current packet. Missing or superseded display evidence MUST NOT fabricate approval; the adapter SHALL retain the decision candidate for audit and require the current readable request and binding preconditions before consumption.

#### Scenario: Token replies to a superseded approval rendering
- **WHEN** a decision token descends from an older packet comment after a new action request is current
- **THEN** evidence remains no-op and identifies the current approval request still requiring a response
