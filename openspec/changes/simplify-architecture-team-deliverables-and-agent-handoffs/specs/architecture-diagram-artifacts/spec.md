## ADDED Requirements

### Requirement: Architecture diagrams remain subordinate to the canonical Design
The workflow SHALL treat every Archify diagram as a version-bound supporting visual of one `ARCH-DESIGN`, never as a second canonical architecture document. The Design MUST remain understandable without opening an interactive diagram and MUST contain an `architecture_visual_manifest_v1` that records each diagram's ID, type, purpose, covered Design sections, Typed JSON source ref/digest, delivered HTML ref/digest, the latest successful artifact-bound `visual-check` receipt, its light-theme 1440×900 PNG capture ref/raw-byte digest, repository revision, validation result, `browser_evidence=passed|failed|skipped`, `visual_review=passed|failed|skipped`, Reviewer findings and supersession state. A required diagram MUST NOT use `none` for the static preview. Typed JSON SHALL be the editable diagram source; HTML, image previews, contact sheets and exports MUST be marked `derived_non_authoritative`. Only an accepted `diagram_not_applicable` decision MAY omit the visual manifest and preview.

#### Scenario: Design includes an architecture overview
- **WHEN** a Solution Architect delivers a Design with a required Archify overview
- **THEN** the Design explains the architectural conclusion in prose, references the exact diagram ID, and binds source, rendered artifact and evidence digests without making the HTML a second mandatory human entry

#### Scenario: Interactive diagram is unavailable
- **WHEN** the canonical Design can be opened but its optional interactive HTML cannot be rendered on one client
- **THEN** the Design remains reviewable through its prose and the digest-bound light/1440×900 static preview on the same Design surface, records the client limitation, and does not silently claim interactive access

#### Scenario: Required static preview is absent
- **WHEN** a required diagram has a delivered HTML but no light/1440×900 PNG capture bound to the same successful `visual-check` receipt and artifact digest
- **THEN** the visual chain is incomplete, the Design MUST NOT enter formal Architecture Review, and an older or manually exported image MUST NOT be substituted

### Requirement: Diagram selection is proportional to decision value
Every architecture Design SHALL record `diagram_requirement=required|not_applicable` with a reason. A formally reviewable complex Architecture Team Design SHALL default to one Architecture overview with 6–12 primary nodes; `not_applicable` is allowed only when a diagram would not materially improve structural understanding and the independent Reviewer accepts the recorded reason. The workflow MUST add at most two further primary diagrams by default and SHALL select their types by semantics: components/services/storage/boundaries use `architecture`; responsibility, approval, release, rollback or runbook paths use `workflow`; ordered API/authentication/cache/async interactions use `sequence`; lineage, classification, transformation, custody or consumers use `dataflow`; states, events, retries, cancellation and terminal behavior use `lifecycle`. It MUST NOT generate all supported types merely for completeness.

#### Scenario: Critical asynchronous path affects the recommendation
- **WHEN** the Design depends on an ordered cross-service request with asynchronous completion or retry
- **THEN** the visual manifest includes a Sequence diagram for that critical path in addition to the Architecture overview, unless the same semantics are already unambiguously represented

#### Scenario: Additional diagrams add no decision information
- **WHEN** candidate Workflow, Data Flow or Lifecycle diagrams would only repeat the Design prose and overview
- **THEN** the workflow omits them and records no quality failure for their absence

### Requirement: Diagram delivery separates deterministic, browser and perceptual claims
For each required diagram the author SHALL use a pinned Archify dependency, author fresh Typed JSON in the request language, set `meta.locale=zh-CN` for Simplified Chinese content, default to `quality_profile=showcase` and static presentation, validate after each edit, and perform no more than two focused correction rounds. A final artifact MUST be produced by successful `deliver`, and `visual-check` MUST run only against that exact successful artifact. The handoff SHALL record `specification_sha256`, `artifact_sha256`, `validation`, `browser_evidence`, `visual_review`, `correction_rounds` and the selected light/1440×900 PNG ref/digest separately. A required diagram SHALL enter formal Architecture Review only when `deliver` and `browser_evidence` passed, the selected preview belongs to the same receipt/artifact, `visual_review=passed`, and current independent semantic findings are closed. `deliver=failed`, `browser_evidence=failed|skipped` or `visual_review=failed|skipped` MUST fail closed; a manual browser record or another evidence claim MUST NOT upgrade those statuses. Deterministic delivery MUST NOT imply browser evidence or perceptual review, and browser evidence MUST NOT imply semantic or perceptual approval.

#### Scenario: Deliver fails while an older HTML exists
- **WHEN** the current candidate fails `deliver` and the output path still contains a previous trusted artifact
- **THEN** the workflow does not run or reuse `visual-check` as evidence for the rejected candidate and returns the delivery diagnostics for focused repair

#### Scenario: Automated browser evidence passes
- **WHEN** `visual-check` succeeds for the exact delivered artifact digest
- **THEN** the manifest records `browser_evidence=passed`, binds the receipt's light/1440×900 PNG raw-byte digest as the default static preview, and leaves independent semantic and perceptual review as a separate required judgment

#### Scenario: Automated browser evidence is failed or skipped
- **WHEN** `visual-check` returns `failed` for a defect/runtime error or `skipped` because Chrome/Chromium is unavailable
- **THEN** the required diagram remains non-reviewable until the current artifact, or a corrected and newly rebound artifact, obtains a successful browser receipt; supplementary manual inspection MUST remain separate and MUST NOT convert the status to passed

#### Scenario: Perceptual review cannot pass
- **WHEN** the frozen artifact has `visual_review=failed|skipped` or an unresolved material semantic finding
- **THEN** the required diagram remains non-reviewable and the author MUST publish a corrected candidate for a new independent review instead of advancing packet readiness

### Requirement: Diagram review is independent and version-bound
The `diagram_reviewer` SHALL remain distinct from the diagram author, treat the Design and Typed JSON as read-only, verify the frozen refs/digests and Archify receipts, inspect the rendered composition, and compare every material node, edge, boundary, message, state and label with the Design and cited evidence. Findings MUST identify a stable diagram ID and, where applicable, node/edge/message/state ID, evidence, impact, Owner and closure condition. A Reviewer MUST NOT edit the source, rerender a corrected candidate, or turn a tooling pass into an architecture approval.

#### Scenario: Diagram omits a critical trust boundary
- **WHEN** the Design and repository evidence require a trust boundary that the frozen diagram does not show
- **THEN** the Reviewer records a version-bound finding and the Design remains non-approvable until the author publishes a corrected Design/diagram version

#### Scenario: Diagram is visually polished but semantically wrong
- **WHEN** validation and browser evidence pass but a component relationship conflicts with the Design or verified code evidence
- **THEN** the Reviewer rejects the semantic claim and MUST NOT accept the tooling receipts as proof of correctness

### Requirement: R&D reuses approved architecture visuals without creating drift
The downstream R&D flow SHALL preserve approved Design diagram IDs, refs and digests in `ARCH-RD-HANDOFF`. Product & Spec Engineer MUST reuse those visuals before creating any new diagram and MAY create one scope-local implementation visual only when OpenSpec needs workflow, sequence, data-flow or lifecycle detail absent from the approved Design. Solution Review Architect SHALL review that visual read-only against the approved Design and proposal artifacts. Development, Code Review, QA, Integration and Watchdog responsibilities MUST NOT author replacement architecture diagrams. Any visual change affecting recommendation, system/responsibility/trust boundaries, external interfaces, data ownership, NFR, accepted risk, migration or Design maturity MUST be classified `architecture_impact` and returned to Architecture Team.

#### Scenario: OpenSpec needs an implementation state machine
- **WHEN** the approved Design fixes system boundaries but the proposal needs explicit retry, waiting, cancellation and terminal states for implementation
- **THEN** Product & Spec Engineer may add one Lifecycle diagram bound to the proposal while retaining the approved Architecture diagram by reference

#### Scenario: Developer discovers an architecture boundary change
- **WHEN** implementation evidence shows that the approved component or trust boundary must change
- **THEN** R&D stops local diagram revision, reports `architecture_impact`, and requests a superseding Architecture Design instead of silently updating the proposal visual
