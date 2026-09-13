## MODIFIED Requirements

### Requirement: Decision content is visible before audit content
Each new human-facing Multica comment SHALL begin with exactly one label: `【需要你确认】`, `【Agent 处理中，无需回复】` or `【Agent 已完成，无需确认】`. Only `【需要你确认】` may contain a current Action. A human-action comment MUST state the decision in ordinary language, Team recommendation and principal consequence, list one `【需要阅读并确认】` material entry, optionally list bounded `【供人参考，无需单独确认】` resources, and show one exact response. Its visible prose SHALL default to no more than 600 Unicode code points excluding stable links, filenames and the Action code block. Full Design bodies, architecture diagrams, complete alternatives, Review, Research, Control, Packet, digests, sidecar refs, reconciliation and machine fields MUST move to labeled attachments or internal evidence rather than being copied into the comment.

#### Scenario: Formal architecture approval is rendered
- **WHEN** the adapter receives a compatible `human_review_surface_v2`
- **THEN** the Owner sees a compact `【需要你确认】` summary, one `【需要阅读并确认】` Design entry and one Action, with no Review/Packet/Control body in the timeline

#### Scenario: Visible comment exceeds its information budget
- **WHEN** detailed background, full option analysis, diagram explanation or audit evidence would make the visible prose exceed the default budget
- **THEN** the adapter moves that content to the labeled decision material and retains only the routing summary and exact Action in the Issue

#### Scenario: Agent work does not require a decision
- **WHEN** research, design generation, diagram validation, Review, readback, continuation or handoff is still Agent-owned
- **THEN** the adapter writes no ordinary comment by default, or emits one compact `【Agent 处理中，无需回复】` status without an Action when a human-visible checkpoint is materially useful

### Requirement: Access confirmation names every required artifact
The adapter SHALL record `material_access_state` independently from `decision_readiness_state` for the exact `human_required` entry. For formal approval this entry is the canonical Design; for a pre-Design input or risk action it MAY be one action-bound decision-detail attachment. Review, Packet, Research and Control SHALL be verified through internal machine refs/digests without requiring their human rendering. Access MUST be recorded per requested client scope as `opened|manual_check_required|unavailable|not_run`; decision readiness MUST be `validated|manual_check_required|unreadable|incomplete|not_run`. Agent download, local path, transient URL, filename-only card, correct digest or partial preview MUST NOT prove either human opening or human decision readiness.

#### Scenario: Design access fails
- **WHEN** the canonical Design entry fails identity, digest, navigation or complete-content verification and no valid Owner-manual profile applies
- **THEN** the adapter fails closed with Owner and observable closing condition

#### Scenario: Internal Review was not opened by the human
- **WHEN** the Design access and all Review/packet machine readbacks pass but the Owner never opens a separate Review file
- **THEN** access confirmation remains sufficient because Review is not required human material

#### Scenario: Material opens but is not decision-ready
- **WHEN** the Owner can render the exact required attachment but its organization, language, explanation, option comparison or architecture view cannot support a decision
- **THEN** the adapter preserves the successful access evidence, records `decision_readiness_state=unreadable|incomplete`, supersedes the Action and does not consume an accept/modify/reject decision

### Requirement: Multica delivers a complete architecture material bundle
For every architecture-content action depending on detailed material, the adapter SHALL use `multica_human_action_material_bundle_v3` and attach or link exactly one `human_required` entry. For formal approval this MUST be canonical `ARCH-DESIGN-vN.md`; before a Design exists it MAY be one readable action-bound decision-detail attachment that clearly declares its limited scope. The record MUST bind material type, version, raw-byte digest, audience, review requirement, bound Action, comment ID, attachment ID, target Member and client scopes. Research, Control, complete Review and Packet MUST be stored as `agent_internal` evidence and MUST NOT be attached as mandatory materials. A derived PDF or interactive Archify HTML MAY be included as `human_reference` and `derived_non_authoritative=true`. When the Design has a required diagram, the same Design surface SHALL show or link its receipt-bound light/1440×900 static preview. Every visual resource MUST bind to the Markdown visual manifest and MUST NOT create a second required human entry. The preview platform ref/digest and client access evidence MUST remain an external projection rather than modifying the canonical Design bytes.

#### Scenario: Approval bundle is delivered
- **WHEN** a current Design requires a human decision
- **THEN** the delivery contains one canonical Design Markdown attachment and an inline Reviewer summary, without Review/Packet/Control attachments

#### Scenario: Pre-Design decision needs detailed explanation
- **WHEN** the current Action asks for an input that must be fixed before the canonical Design can be completed
- **THEN** the delivery contains one `【需要阅读并确认】` action-bound detail attachment, keeps the Issue comment compact and states that the attachment is not the overall architecture Design

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

## ADDED Requirements

### Requirement: Multica material entries declare audience and confirmation responsibility
Every attachment or material link projected to the Issue SHALL bind `audience=human|agent`, `review_requirement=required|reference_only|none` and `bound_action=<action_id|none>`. The adapter MUST render these as `【需要阅读并确认】`, `【供人参考，无需单独确认】` or `【Agent 内部材料，无需阅读】`. Each Action MUST have exactly one required entry. Reference-only Archify HTML, preview or PDF SHALL be confirmed with the primary material and MUST NOT produce another Action. Agent-internal Research, Control, complete Review, Packet, receipts, continuation and handoff evidence MUST NOT appear in the ordinary required-attachment list.

#### Scenario: Formal Design has supporting Archify resources
- **WHEN** one canonical Design and its receipt-bound preview/interactive HTML are delivered
- **THEN** the Design is labeled `【需要阅读并确认】`, the visuals are labeled `【供人参考，无需单独确认】`, and one Action covers the complete Design surface

#### Scenario: Internal evidence is exportable
- **WHEN** an operator exposes an audit bundle for diagnostics
- **THEN** every internal entry is labeled `【Agent 内部材料，无需阅读】` and the bundle cannot become a human decision prerequisite

### Requirement: Multica distinguishes access failure from decision-material failure
The adapter SHALL accept `ACTION <action_id>: 材料打不开` only as an access/delivery failure and `ACTION <action_id>: 材料不可决策; reason=<原因>` only as a readability/completeness failure after successful or Owner-manual access. Both replies SHALL produce `content_decision=none`; the former repairs or republishes the stable entry, while the latter supersedes the current Action, preserves access evidence, returns to `preparing` and produces corrected material under a new Action ID.

#### Scenario: Owner reports readable-access success but decision failure
- **WHEN** the exact current Owner submits `材料不可决策` after opening the material
- **THEN** the adapter does not classify it as `材料打不开`, `reject` or `revision_requested`, and the replacement attempt carries the reason as non-authoritative authoring input
