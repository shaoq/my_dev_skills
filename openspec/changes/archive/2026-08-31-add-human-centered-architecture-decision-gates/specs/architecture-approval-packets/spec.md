## ADDED Requirements

### Requirement: Approval packet explains every legal human outcome
The packet Human review brief SHALL explain in Chinese what `approved_design_only`, `approved_for_spec`, `revision_requested` and `rejected` do, including next canonical state, publication and handoff effects, OpenSpec boundaries, principal irreversible or terminal consequence, and immediate planned writes. It MUST identify the exact current packet binding and MUST NOT preselect a decision from `ARCHITECTURE_RECOMMENDATION`.

#### Scenario: Human compares approval choices
- **WHEN** a current ready packet is presented for decision
- **THEN** the brief allows the human to distinguish documentation-only publication, R&D handoff authorization, new design iteration and terminal rejection before submitting one legal value

### Requirement: Packet brief surfaces complete material access and accepted risks
The packet SHALL list stable refs for the complete frozen Design, Review and Packet materials and summarize every accepted non-blocking risk with risk ID, Owner, acceptance evidence and conditions. Access confirmation and risk acceptance MUST remain separate from the final packet decision.

#### Scenario: Approvable-with-warnings packet is delivered
- **WHEN** Review conclusion is `APPROVABLE_WITH_WARNINGS`
- **THEN** the human brief identifies each accepted risk and its evidence and does not use final approval to fabricate missing risk-owner acceptance

### Requirement: Revision brief is non-authoritative packet context
A packet MAY expose a stable response path for a separate revision brief. Any revision brief MUST bind the packet ref/version/digest and remain non-authoritative context; only valid `revision_requested` decision evidence changes the gate, and the brief MUST NOT be inserted into or rewrite delivered packet bytes.

#### Scenario: Revision details accompany a valid decision
- **WHEN** a human records a separate packet-bound revision brief and a valid `revision_requested` decision
- **THEN** both refs are preserved, the token drives the canonical transition and the brief guides the replacement design without changing frozen packet content
