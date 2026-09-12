## MODIFIED Requirements

### Requirement: Adapter remains an independently installable sibling skill
The repository SHALL maintain `multica-architecture-approval-adapter/` as a valid sibling skill with independent metadata while keeping core usable standalone. When both are activated for Multica, the adapter MUST refuse delivery unless it proves compatibility with the core revision and the `human_review_surface_v1`/`architecture_internal_evidence_v1` pair frozen by the attempt.

#### Scenario: Both skills are installed locally
- **WHEN** the installer scans the two root skill sources
- **THEN** Claude Code and Codex receive separate links pointing to repository sources and validation records their compatible pair

#### Scenario: Adapter is absent
- **WHEN** only core is installed
- **THEN** standalone profiles continue and no Multica field becomes a core dependency

#### Scenario: Revisions are incompatible
- **WHEN** core and adapter advertise incompatible surface contracts
- **THEN** adapter activation and platform delivery fail before writes

### Requirement: Workspace activation requires explicit human authorization
Delivery SHALL provide a runbook that packages/imports the compatible core and adapter pair, additively binds both to the selected existing Architecture Agent, and verifies final skill IDs/revisions. The runbook MUST NOT use replace-all binding by default, create missing resources or leave a partially activated pair reported as ready.

#### Scenario: Human authorizes activation
- **WHEN** a human names target workspace/existing Agent and authorizes exact pair activation
- **THEN** the operator imports both revisions, applies additive bindings, verifies compatibility and records that only new attempts use them

#### Scenario: Either import conflicts
- **WHEN** either skill has a same-name conflict or incompatible existing revision
- **THEN** activation stops before changing the remaining binding and reports supported recovery choices without overwriting

#### Scenario: Target Agent does not exist
- **WHEN** selected Architecture Agent cannot be resolved
- **THEN** activation stops without creating Agent, Team, Project or fallback binding

### Requirement: Activation verifies a sandbox review flow before production use
After authorized import/binding, the runbook MUST require a new sandbox Issue acceptance covering one canonical Design attachment, Design opening or Owner-manual attestation, internal Review/manifest digest reread, one current Action, supersession, internal Agent handoff/readback, and failure retention. Production readiness MUST NOT be claimed from static installation or an old attempt.

#### Scenario: Sandbox acceptance passes
- **WHEN** target clients can access the one Design entry under selected profile, internal evidence verifies, a valid reply produces current decision evidence, stale replies no-op, and Agent handoff produces no dedicated human comment
- **THEN** the compatible pair may be reported ready for new attempts on the selected Architecture Agent

#### Scenario: Design cannot be accessed
- **WHEN** the target Member cannot retrieve/render the Design and no valid Owner-manual path succeeds
- **THEN** acceptance fails and the pair remains inactive for production use

### Requirement: Sandbox acceptance presents a human checklist
The sandbox SHALL present a concise checklist for opening exactly one canonical Design on requested clients or making the explicit Owner-manual declaration, submitting one current Action, observing supersession and confirming failure retention. Review/Packet/Control opening and Agent handoff comments MUST NOT appear as required human checks. Each human-observed result MUST be recorded individually; generic `OK` MUST NOT pass acceptance.

#### Scenario: Human completes only desktop checks
- **WHEN** desktop Design opens but a required mobile scope or Owner-manual declaration and supersession check are incomplete
- **THEN** sandbox acceptance remains `not_run|failed` and production readiness is not claimed

### Requirement: Archify bindings are role-scoped across Architecture and R&D
When a human explicitly authorizes Archify activation, the adapter runbook SHALL import the pinned archive with conflict-fail behavior and additively bind it only to resolved existing Agents whose deployment responsibilities require diagram authorship or review. The current deployment profile SHALL map Architecture `solution_design` and R&D `product_spec` to author-capable instructions, and Architecture `independent_review` and R&D `solution_review` to review-only instructions. Review-only Agents MUST be limited by their role contract to `inspect`, `validate`, `check`, current-receipt verification and explicitly requested Architecture comparison; they MUST NOT edit Typed JSON, render or deliver a replacement. Coordination, research, development, code-review, QA, integration/archive and watchdog responsibilities SHALL remain unbound by default. Display names are deployment evidence only; every binding MUST use a uniquely resolved current Agent ID and a final read-only skill list.

#### Scenario: Four intended Agents resolve uniquely
- **WHEN** the selected workspace contains one existing Agent for each current author/reviewer deployment responsibility and the pinned Archify Skill ID is verified
- **THEN** activation uses additive bindings for exactly those four Agents, preserves all existing skills, updates their author/review-only instructions, and confirms every final assignment by ID

#### Scenario: Reviewer receives author behavior
- **WHEN** the proposed Architecture Reviewer or Solution Review Architect instructions allow source edits, `render`, `deliver`, `preview` or unrequested corrected output
- **THEN** activation fails before binding because independent review cannot be proven

#### Scenario: A non-target Agent is selected
- **WHEN** activation would bind Archify to a Lead, Analyst, Development, Code Review, QA, Integration/Archive or Watchdog Agent without a separately approved deployment need
- **THEN** the runbook leaves that Agent unchanged and records the rejected expansion

#### Scenario: Only some target bindings succeed
- **WHEN** import succeeds but any required Agent resolution, instruction update or additive binding cannot be verified
- **THEN** activation is not reported ready, completed bindings are recorded for reconciliation, and production attempts remain on the old contract until the authorized set is repaired or rolled back

### Requirement: Archify sandbox acceptance covers author, reviewer and downstream reuse
The sandbox acceptance SHALL exercise a current Architecture Design with one Architecture overview, successful deterministic delivery, `browser_evidence=passed`, `visual_review=passed`, closed independent semantic findings, one canonical Design human entry and the same browser receipt's light/1440×900 PNG preview opened and found readable in the requested mobile scope. `browser_evidence=failed|skipped`, `visual_review=failed|skipped`, preview digest drift or unavailable mobile projection MUST fail acceptance and MUST NOT be replaced by another evidence claim. It SHALL also exercise one R&D proposal that reuses the approved visual by ref and conditionally adds an implementation-only visual without changing the architecture. Acceptance MUST prove that internal Agent handoffs do not generate presentation diagrams and that a simulated architecture-impacting R&D change routes back to Architecture Team.

#### Scenario: End-to-end visual acceptance passes
- **WHEN** the author and review-only Agents use the pinned Skill within their command boundaries, all visual refs/digests bind the current Design, web/mobile presentation is truthful, and R&D reuses the approved visual
- **THEN** Archify may be reported active for new attempts in the selected workspace

#### Scenario: Diagram passes tooling but fails semantic review
- **WHEN** `deliver` and `visual-check` pass while the independent Reviewer identifies a topology, boundary or evidence mismatch
- **THEN** sandbox acceptance fails and no human approval Action is made current

### Requirement: Adapter 必须兼容 portable 历史版本并只投影 current 新操作
adapter SHALL retain readers for historical mandate/continuation/blocker/material-bundle/approval surfaces and SHALL write only the current contract versions for new attempts. Old attempts and their three-attachment actions remain audit-only under frozen revisions; a new one-Design writer MUST NOT reinterpret, edit or delete them. Any migration requiring new side effects SHALL create a superseding attempt after compatible core/adapter activation.

#### Scenario: 旧三附件 attempt 仍在等待
- **WHEN** 新 contract 激活时历史 Action 仍 current-looking
- **THEN** adapter 保留其旧语义或创建显式 superseding attempt，绝不把旧评论原地变为新 `multica_human_action_material_bundle_v2`

#### Scenario: 新 attempt 写入
- **WHEN** compatible current pair 与新 attempt 已冻结
- **THEN** adapter 只写一份 Design 人类材料和内部 execution evidence，不生成 dedicated Agent handoff comment
