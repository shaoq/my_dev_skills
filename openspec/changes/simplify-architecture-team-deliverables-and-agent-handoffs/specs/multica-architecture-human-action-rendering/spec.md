## MODIFIED Requirements

### Requirement: Decision content is visible before audit content
Each human-facing Multica action comment SHALL lead with one-paragraph solution summary, simplified view, Design maturity, Team recommendation/rationale/confidence, concise Reviewer conclusion/findings, determined/undetermined matters, alternatives/consequences, one authorized decision, post-response behavior and exactly one complete Design entry. It SHALL then show the exact response and minimal current/superseded identity. Full Design bodies, complete Review, Research, Control, Packet, digests, sidecar refs, reconciliation and machine fields MUST NOT precede or replace the brief; non-Design artifacts MUST remain internal or optional audit detail.

#### Scenario: Formal architecture approval is rendered
- **WHEN** the adapter receives a compatible `human_review_surface_v1`
- **THEN** the Owner sees one Design entry and one Action before any audit details, with no mandatory Review/Packet/Control entry

### Requirement: Access confirmation names every required artifact
The adapter SHALL require human access confirmation only for the exact canonical Design. It SHALL verify Review, Packet, Research and Control through internal machine refs/digests without requiring their human rendering. Design access MUST be recorded per requested client scope as `opened|manual_check_required|unavailable|not_run`; Agent download, local path, transient URL, filename-only card or partial preview MUST NOT count as `opened`.

#### Scenario: Design access fails
- **WHEN** the canonical Design entry fails identity, digest, navigation or complete-content verification and no valid Owner-manual profile applies
- **THEN** the adapter fails closed with Owner and observable closing condition

#### Scenario: Internal Review was not opened by the human
- **WHEN** the Design access and all Review/packet machine readbacks pass but the Owner never opens a separate Review file
- **THEN** access confirmation remains sufficient because Review is not required human material

### Requirement: Multica delivers a complete architecture material bundle
For every architecture-content action depending on a substantial Design, the adapter SHALL use `multica_human_action_material_bundle_v2` and attach exactly one canonical `ARCH-DESIGN-vN.md` to the authorized delivery comment. The record MUST bind Design type, version, maturity, raw-byte digest, comment ID, attachment ID, target Member and client scopes. Research, Control, complete Review and Packet MUST be stored as internal evidence and MUST NOT be attached as mandatory materials. A derived PDF or interactive Archify HTML MAY be included as `derived_non_authoritative=true` supporting resources. When the Design has a required diagram, the same Design surface SHALL show or link its receipt-bound light/1440×900 static preview. Every visual resource MUST bind to the Markdown visual manifest and MUST NOT create a second required human entry. The preview platform ref/digest and client access evidence MUST remain an external projection rather than modifying the canonical Design bytes.

#### Scenario: Approval bundle is delivered
- **WHEN** a current Design requires a human decision
- **THEN** the delivery contains one canonical Design Markdown attachment and an inline Reviewer summary, without Review/Packet/Control attachments

#### Scenario: Markdown is not comfortably readable
- **WHEN** canonical Markdown bytes verify but a requested client cannot comfortably render them
- **THEN** the adapter may add a derived PDF representation, keeps Markdown authoritative and records client-specific access separately

#### Scenario: Design contains a required Archify visual
- **WHEN** the current visual manifest and all required receipts verify
- **THEN** the same Design surface shows or links the receipt-bound light/1440×900 static preview and MAY offer an interactive link while the Owner is still required to open only the canonical Design

### Requirement: Material entries are verified after publication
After publishing a Human Action Request and its Design attachment, the adapter SHALL verify that the Design card/anchor is clickable, resolves to the exact attachment identity and presents complete content; it SHALL re-download Markdown and match its digest. Web/mobile states MUST be independent. Newly published material with no requested-client evidence SHALL first request only access confirmation unless explicit Owner-manual policy applies; a later content action MUST use a new current Action version. The adapter MUST NOT edit an access-confirmation comment into a content decision.

#### Scenario: Design is readable on web
- **WHEN** the target Member opens the Design in the web client
- **THEN** the Design entry records target, complete-content result, verifier and time

#### Scenario: Mobile has not been exercised
- **WHEN** web access passes but mobile was requested and not opened
- **THEN** mobile remains `not_run|manual_check_required` according to profile and the adapter does not claim it opened

#### Scenario: New attachment requires verification
- **WHEN** the Design card did not exist before publication and automatic mode is selected
- **THEN** the bundle requests only access confirmation, and a content decision requires a new Action after access succeeds
