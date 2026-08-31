## ADDED Requirements

### Requirement: Multica delivers a complete architecture material bundle
For every design-input, risk-acceptance or design-approval brief that depends on a substantial design, the adapter SHALL use `multica_human_action_material_bundle_v1` and attach the exact canonical `ARCH-DESIGN-vN.md` to the same authorized delivery comment. The attachment record MUST bind artifact type, version, raw-byte digest, comment ID, attachment ID, target member and requested client scopes. Research and Control SHALL each have a verified complete Web comment permalink or be included as exact Markdown attachments when their permalinks are unavailable. A derived `ARCH-DESIGN-vN.pdf` SHALL be included only when required to make the complete design comfortably readable in a requested client; it MUST bind the Markdown source digest and remain `derived_non_authoritative=true`.

#### Scenario: Design input is requested
- **WHEN** a current Human Action Request asks an authorized human to decide a design input
- **THEN** the delivery comment includes the Decision Brief and an exact complete `ARCH-DESIGN-vN.md` attachment rather than requiring the human to reconstruct the scheme from historical comments

#### Scenario: Markdown is not readable in one requested client
- **WHEN** the canonical Markdown attachment can be downloaded but cannot be comfortably opened and read in web or mobile acceptance
- **THEN** a separately authorized delivery includes a PDF reading copy bound to the Markdown digest, while Markdown remains the only canonical design artifact

### Requirement: Multica human-facing comment links use a verified client route
For comment-backed Research or Control materials, the adapter SHALL use `multica_web_comment_permalink_v1` with the normalized form `<app_base_url>/<workspace_slug>/issues/<issue_identifier>#comment-<comment_id>`. The app base URL MUST come from an explicitly confirmed current human-facing deployment entry; workspace slug, Issue identifier and comment ID MUST be read back from Multica. The adapter MUST NOT present `multica://issues/...`, another custom URI, an inferred browser path or a local absolute path as a human-accessible material entry unless that exact scheme has independently passed current-client render and navigation verification.

#### Scenario: Existing comment is exposed as supporting material
- **WHEN** the adapter renders a Decision Brief for an exact Research or Control comment
- **THEN** it constructs the Web permalink from read-back identities and exposes it as a clickable entry labeled with artifact type and version

#### Scenario: Custom URI is not supported by the client
- **WHEN** a candidate material ref uses `multica://issues/...` or another scheme whose rendered navigation behavior has not passed current-client verification
- **THEN** the adapter excludes it from human-accessible entries and supplies an attached Markdown fallback or an unavailable closing condition

### Requirement: Material entries are verified after publication
After publishing a Decision Brief and its attachments, the adapter SHALL verify for every Design, Research and Control entry that the rendered attachment card or anchor is clickable, opening resolves to the exact artifact/comment/attachment identity, and the complete content is readable. It SHALL re-download canonical Markdown and match its raw-byte digest. Web and mobile results MUST be recorded independently as `opened|unavailable|not_run`; Agent download or web success MUST NOT be used as evidence for mobile success.

When an exact newly published material entry has no prior requested-client evidence, the delivery SHALL request only `access_confirmation`; the intended content decision SHALL remain non-actionable. After access succeeds, a content decision MUST use a new current Human Action Request version and a separately authorized delivery attempt. The adapter MUST NOT edit the access-confirmation comment to activate a content decision or treat access confirmation as content authority.

#### Scenario: Bundle is readable on web
- **WHEN** the target member opens the Design attachment and Research/Control entries in the web client
- **THEN** each entry records the exact target, complete-content result, verifier and verification time independently

#### Scenario: Mobile has not been exercised
- **WHEN** web access passes but the canonical target member has not opened the same materials from the requested mobile client
- **THEN** web is recorded as opened, mobile remains `not_run|unconfirmed`, and the adapter MUST NOT claim mobile accessibility or content-decision readiness

#### Scenario: New attachment requires post-publication verification
- **WHEN** an exact Design attachment card does not exist until the material bundle is published
- **THEN** that bundle requests only access confirmation, and a later content action requires a new core action version plus a new exact operational authorization

## MODIFIED Requirements

### Requirement: Multica renders portable human actions without changing authority
The adapter SHALL render each compatible core Human Action Request into a Chinese `Architecture Decision Brief` that preserves action type, version binding, Decision Owner, recommendation or `no_recommendation`, alternatives, consequences, evidence refs, exact response and post-response outcome. The brief MUST ask exactly one atomic action for the uniquely bound current member and authority scope. Other Owners' current actions SHALL appear only as non-actionable dependency summaries; if the intended Owner is unbound or ambiguous, the adapter SHALL render an owner-routing request instead of a content-decision form. Platform fields MAY supplement delivery identity and access refs but MUST NOT change core decision semantics, stage, Review conclusion, recommendation or legal human decision values.

#### Scenario: Core action request is delivered to Multica
- **WHEN** an explicitly authorized adapter route receives one current compatible Human Action Request whose Decision Owner binds uniquely to the current member
- **THEN** the resulting brief presents that one decision and its consequences, links the complete material bundle, and records platform identity only as external evidence

#### Scenario: Current member does not own another dependency
- **WHEN** the same architecture design has unresolved actions owned by other authority scopes
- **THEN** their IDs, Owners and closure conditions may be summarized, but their response forms are omitted and the current member cannot close them through this brief

### Requirement: Decision content is visible before audit content
Each human-facing Multica action comment SHALL use this order: one-paragraph solution summary; simplified architecture view; Architecture Team recommendation, rationale and confidence; determined and undetermined matters; most important alternatives and consequences; the one authorized decision; post-response behavior; clickable complete Design/Research/Control entries; exact response; and minimal current/superseded audit binding. Full design bodies, multi-Owner questionnaires, full digests, markers, sidecar refs and reconciliation fields MUST remain in attachments or durable audit records and MUST NOT be copied before or in place of the brief.

#### Scenario: Target member reads from a constrained client
- **WHEN** the target member opens the action comment in the Multica client
- **THEN** the first screen explains the proposed architecture and team recommendation, identifies the member's one decision and consequence, and provides the route to the complete design without requiring interpretation of raw control fields

### Requirement: Access confirmation names every required artifact
The adapter SHALL expose the exact Design Markdown attachment and verified complete Research and Control entries, plus Review and Packet materials when the gate requires them, and SHALL record target-member access confirmation separately for each required artifact and requested client scope. If an exact material cannot be opened, resolved and read completely, the adapter SHALL fail closed with the unavailable Owner and observable closing condition. A generic acknowledgement, Agent download, local path, transient signed URL, unsupported custom URI, filename-only attachment card or partial preview MUST NOT satisfy access confirmation.

#### Scenario: Mobile access is confirmed
- **WHEN** the canonical target member opens and reads every exact required material from the mobile client
- **THEN** the access action records each artifact as opened while raw-byte digest verification and final approval remain separate gates

#### Scenario: No verified complete material route exists
- **WHEN** the Design attachment or a required Research/Control entry fails client opening, exact identity or complete-content verification
- **THEN** the adapter records the affected artifact/client scope as unavailable, provides the Owner and closing condition, and MUST NOT request the content decision
