## MODIFIED Requirements

### Requirement: Every human-dependent next action is independently reviewable
Whenever progress requires a recognizable human content decision or unresolved dependency input, the core SHALL emit one or more platform-neutral `Human Action Request` items. Each item MUST contain a stable action ID/type, current stage/reason, exact Design or routing binding, Decision Owner and authority scope, one atomic decision, recommendation or `no_recommendation`, bounded alternatives, rationale, option consequences/risks, unresolved evidence with Owner/closing condition, exactly one action-bound `human_required` material entry when detailed architecture content is needed, an exact response form, post-response stage/Owner/writes, and a non-authorization boundary. For formal architecture approval that material MUST be the canonical `ARCH-DESIGN-vN.md`; a pre-Design input or risk action MAY use one readable non-canonical decision-detail attachment, but it MUST NOT claim to be a second overall Design. Other Owners' actions MAY appear only as non-actionable summaries. If Owner binding is unknown, the request SHALL be a dependency-input action rather than a content decision. Internal execution steps and access/readback operations MUST NOT generate human requests merely to expose progress.

#### Scenario: Workflow needs a human content action
- **WHEN** `Next action` requires a human to choose a Design input, accept a risk or approve a current Design
- **THEN** the workflow presents one complete Human Action Request with exactly one action-appropriate `human_required` entry and MUST NOT require separate Research, Control, Review or Packet reading

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
New writers SHALL emit `human_review_surface_v2`. Its directly visible Issue summary MUST identify whether human action is required, state the decision in ordinary language, show the Team recommendation and principal consequence, provide one labeled `human_required` material entry, and end with one exact Action response. The summary SHALL default to no more than 600 Unicode code points excluding stable links, attachment filenames and the Action code block. Detailed problem context, architecture boundaries, complete alternatives, Archify visuals, evidence and Review content SHALL live in the linked decision material rather than being copied into the Issue comment. Research, Control, complete Review, Packet, digests, internal status and Agent execution evidence MUST remain internal and MUST NOT consume the visible comment budget.

Every visible entry MUST declare `audience=human|agent`, `review_requirement=required|reference_only|none` and `bound_action=<id|none>`, rendered to the human as `【需要阅读并确认】`, `【供人参考，无需单独确认】` or `【Agent 内部材料，无需阅读】`. Only a `required` entry may gate the Action. A reference-only Archify artifact SHALL be confirmed with its bound Design and MUST NOT create a second human decision.

The Design entry MUST be labeled human-accessible only in a client scope where a named verifier actually opened it, or `manual_check_required` under an explicit Owner-manual profile with verified identity/digest/stable entry. Agent-only reads, local paths, untested URLs, filename-only cards and non-navigable text MUST NOT satisfy the contract.

#### Scenario: Human reviews through a constrained client
- **WHEN** a Human Action Request depends on substantial architecture content
- **THEN** the brief exposes one independently readable `human_required` entry, keeps its Issue summary compact, and records per-scope access evidence without requiring internal artifacts to render

#### Scenario: Complete design exists outside the brief
- **WHEN** the Design is too substantial to copy into the comment
- **THEN** the brief summarizes it, binds exact ref/version/digest and provides one verified attachment or link to the complete document

#### Scenario: Detailed pre-Design input is required
- **WHEN** one content decision must be made before a canonical Design can be completed
- **THEN** the brief links one action-bound `human_required` decision-detail attachment, clearly states that it is not the overall Design, and keeps all Agent evidence internal

#### Scenario: Agent progress is reported
- **WHEN** an Agent must expose a useful non-terminal status update
- **THEN** the entry is labeled `【Agent 处理中，无需回复】`, contains no Action, and states only the current stage, current work and next human checkpoint

#### Scenario: A stable identity is not navigable
- **WHEN** the Design entry is only an internal identity, untested URI, local path, filename-only card or non-opening display text
- **THEN** the request marks access unavailable or manual-check-required according to the selected profile and MUST NOT falsely claim it was opened

## ADDED Requirements

### Requirement: Material access and decision readiness are independent
Each current Human Action SHALL record `material_access_state=opened|manual_check_required|unavailable|not_run` separately from `decision_readiness_state=validated|manual_check_required|unreadable|incomplete|not_run`. A machine-readable identity, successful download or correct digest MUST NOT prove decision readiness. Automatic mode MAY activate a content response only after the required structure and human rendering checks pass. Owner-manual mode MAY expose the response after machine structure/identity checks while preserving both states as `manual_check_required`; the Owner may then submit either one legal content decision, `材料打不开`, or `材料不可决策`.

`ACTION <action_id>: 材料不可决策; reason=<原因>` SHALL mean `content_decision=none`. It MUST supersede the current Action, return the Human Action to `preparing`, preserve the access-success evidence, and trigger a new attempt with corrected human material and a new Action ID. It MUST NOT be interpreted as rejection, revision approval, risk acceptance or access failure.

#### Scenario: Attachment opens but cannot support a decision
- **WHEN** the unique Owner can open the exact material but reports `材料不可决策` with a reason
- **THEN** the workflow preserves `material_access_state=opened`, records `decision_readiness_state=unreadable|incomplete`, supersedes the Action and prepares a corrected attempt without consuming a content decision

#### Scenario: Attachment cannot be opened
- **WHEN** the unique Owner reports `材料打不开`
- **THEN** the workflow records an access failure and repairs or republishes the stable material entry without treating it as a readability judgment or content decision

#### Scenario: Digest passes but the brief is machine-oriented
- **WHEN** the bytes and digest verify but the material omits a plain-language decision, adequate explanation, option consequences or a comprehensible architecture view
- **THEN** `decision_readiness_state` is `incomplete|unreadable` and the workflow MUST NOT claim that the Action is human-decision-ready
