## ADDED Requirements

### Requirement: Clarification recommendations do not satisfy evidence or approval gates
A candidate recommendation and a human response to a pre-approval clarification request SHALL affect only the explicitly identified design input. They MUST NOT be treated as measured evidence, another responsibility Owner's decision, an approvable Review conclusion, packet readiness, `ARCHITECTURE_RECOMMENDATION`, or a legal human approval decision. A general acceptance MUST leave independently required measurements, named-Owner decisions and exact packet ref/version/digest approval gates open.

#### Scenario: Human accepts provisional clarification defaults
- **WHEN** a recognizable human accepts one or more provisional candidate values while capacity measurements or named-Owner decisions remain missing
- **THEN** the workflow records the accepted design inputs, preserves the unresolved evidence and Owners, and does not enter formal Review or human approval solely from that acceptance

#### Scenario: Clarification comment is explicitly non-authoritative
- **WHEN** a clarification request presents candidate recommendations before an approvable current packet exists
- **THEN** it explicitly states that the recommendations are not human decisions or approvals and cannot produce `approved_design_only` or `approved_for_spec`
