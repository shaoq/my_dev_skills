## ADDED Requirements

### Requirement: Multica renders portable human actions without changing authority
The adapter SHALL render each compatible core Human Action Request into a Chinese Multica comment that preserves action type, version binding, Decision Owner, recommendation or `no_recommendation`, alternatives, consequences, evidence refs, exact response and post-response outcome. Platform fields MAY supplement delivery identity and access refs but MUST NOT change core decision semantics, stage, Review conclusion, recommendation or legal human decision values.

#### Scenario: Core action request is delivered to Multica
- **WHEN** an explicitly authorized adapter route receives one current compatible Human Action Request
- **THEN** the resulting comment presents the same decision and consequences and records platform identity only as external evidence

### Requirement: Decision content is visible before audit content
Each human-facing Multica action comment SHALL lead with why the action is required now, the recommended choice, principal consequence, authorized actor and exact response. Full digests, markers, sidecar refs and reconciliation fields MUST remain available for audit but MUST NOT precede or replace the decision summary.

#### Scenario: Target member reads from mobile
- **WHEN** the target member opens the action comment in the Multica mobile client
- **THEN** the first screen identifies the requested action and response without requiring interpretation of raw control fields or local paths

### Requirement: Operational authorizations are explicit and separate
Before any adapter operation that requires new human authority, the adapter SHALL present an `operational_authorization` request naming the existing workspace/Issue/Agent/scope, exact planned writes, authorized paths, excluded operations, retained objects, risks, failure behavior and exact authorize/deny response. Such a response MUST NOT count as architecture approval or authorize unlisted writes.

#### Scenario: Packet delivery needs authority
- **WHEN** a verified packet exists but the current task has not explicitly authorized delivery to the named Issue and input paths
- **THEN** the adapter emits the reviewable authorization request and performs no delivery write

#### Scenario: Retry follows partial failure
- **WHEN** prior comment, attachment or projection objects remain after an unavailable attempt
- **THEN** a new authorization request lists those objects and the exact incremental write before any later attempt proceeds

### Requirement: Access confirmation names every required artifact
The adapter SHALL expose stable access refs for exact Design, Review and Packet attachments and SHALL record target-member access confirmation separately for each required artifact and requested client scope. A generic acknowledgement, Agent download or attachment card without retrievable complete material MUST NOT satisfy access confirmation.

#### Scenario: Mobile access is confirmed
- **WHEN** the canonical target member opens all three exact materials from stable refs on mobile
- **THEN** the access action records each artifact as opened while digest verification and final approval remain separate gates
