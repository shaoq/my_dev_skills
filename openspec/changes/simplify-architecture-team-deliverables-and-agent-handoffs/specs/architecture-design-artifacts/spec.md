## MODIFIED Requirements

### Requirement: Every architecture stage has a structured report contract
The skill SHALL provide templates for `ARCH-CONTROL`, `ARCH-RESEARCH`, `ARCH-DESIGN`, `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET`, `ARCH-RD-HANDOFF`, ADR, and detailed design, and each artifact MUST identify the Work Item, version, owner, status, evidence and next action applicable to that artifact. Every artifact MUST declare `audience=human_canonical|human_summary|internal_evidence|downstream`, with `ARCH-DESIGN` as the only `human_canonical` artifact; `ARCH-CONTROL`, `ARCH-RESEARCH`, `ARCH-APPROVAL-PACKET`, readiness, continuation and task readback MUST default to `internal_evidence`. `ARCH-CONTROL` SHALL separately record Review conclusion, current packet ref/version/digest, readiness or unavailable evidence ref, human decision evidence, `WAIT_REASON`, and `BLOCKED_REASON` without requiring those fields to be rendered as an ordinary human timeline comment.

#### Scenario: Architecture work begins
- **WHEN** an architecture request is accepted and routed
- **THEN** the coordination actor creates or updates an internal `ARCH-CONTROL` record with design type, Subject Project, current stage, owners, expected artifacts, human gates and next action, and does not publish a progress-only human comment

#### Scenario: Architecture review becomes approvable
- **WHEN** Reviewer completes an approvable review for an exact design version
- **THEN** the workflow creates an immutable machine-only `ARCH-APPROVAL-PACKET`, records readiness separately, and exposes only the Design plus the concise decision surface to the human

### Requirement: Design output is independently reviewable
`ARCH-DESIGN vN` SHALL be the sole mandatory human-readable canonical architecture artifact and SHALL be understandable without an OpenSpec change, Issue history, Research, Control, Review, Packet or interactive diagram. It MUST exist as canonical UTF-8 Markdown suitable for immutable attachment delivery and MUST contain identity and evidence inputs; executive summary; architecture recommendation, rationale and confidence; problem/current state and architecture drivers; goals and non-goals; system context, responsibility boundaries and a simplified architecture view; components, data/control flows, interfaces and consistency semantics; normal and critical failure flows; security, privacy, reliability, performance, capacity, cost, observability and evaluation design; alternatives, trade-offs and rejected reasons; migration, rollout, rollback, roll-forward and exit; operations/RACI; risks, assumptions, determined and undetermined matters; validation/acceptance plan; and R&D decomposition. When `diagram_requirement=required`, the Design MUST also contain an `architecture_visual_manifest_v1` that binds each supporting visual to its Design sections, source/rendered digests, successful delivery/browser/perceptual evidence, current semantic review and the light/1440×900 PNG preview from the same successful browser receipt while keeping every visual `derived_non_authoritative`.

Every Design MUST declare exactly one `design_maturity=directional|spec_ready|implementation_ready`. A non-`implementation_ready` Design MUST list every remaining decision or evidence gap, its Owner, closing condition and blocked downstream stage. Maturity MUST remain distinct from Review conclusion and human approval.

#### Scenario: Solution Architect completes a candidate design
- **WHEN** sufficient research evidence exists to recommend a solution or a platform-neutral architecture while bounded decisions remain open
- **THEN** the Solution Architect publishes a standalone `ARCH-DESIGN-vN.md`, binds its Research inputs internally, records its raw-byte digest, assigns the truthful maturity, lists unresolved items in the Design itself, and does not require the reader to open another artifact to understand the solution

#### Scenario: Design is only directional
- **WHEN** unresolved decisions can change specification scope, system boundaries or public interfaces
- **THEN** the Design declares `directional`, identifies those decisions and MUST NOT be represented as ready for OpenSpec handoff

#### Scenario: A design is only a collection of prompts or comment fragments
- **WHEN** the candidate output lacks the complete architecture narrative, recommendation, architecture views, consequences, operational design or validation path and relies on questions or historical comments to reconstruct the solution
- **THEN** the workflow marks the Design incomplete, does not request approval, and returns it to the Solution Architect with the missing sections

#### Scenario: Required visual is not bound to the Design
- **WHEN** a Design declares `diagram_requirement=required` but omits the visual manifest, exact source/artifact/preview digests, passed browser/perceptual statuses or current semantic review evidence
- **THEN** the workflow marks the Design incomplete and MUST NOT enter formal architecture Review

### Requirement: Architecture review is independent and deterministic
`ARCH-REVIEW` MUST bind to one `ARCH-DESIGN` version, remain read-only, list only evidence-backed findings with severity, impact, Owner and closure condition, and conclude with `BLOCKED`, `NEEDS_REVISION`, `APPROVABLE_WITH_WARNINGS`, or `APPROVABLE`. It MUST NOT duplicate the Design narrative, component catalogue, full alternatives or implementation guidance. If a finding changes architecture content, the Solution Architect MUST publish a new Design version before an approvable conclusion can apply.

#### Scenario: Critical evidence is missing
- **WHEN** the reviewed Design lacks required current-state, boundary, security, migration, rollback, operational or cost evidence
- **THEN** the Reviewer reports a blocking or major finding, identifies the affected Design section and does not mark the Design approvable

#### Scenario: Review passes
- **WHEN** all mandatory evidence and decisions are complete and only explicitly accepted non-blocking risks remain
- **THEN** the Reviewer emits an approvable conclusion for the exact Design, produces a concise human summary, and retains the complete Review as internal evidence

#### Scenario: Review wording would repair the design
- **WHEN** an approvable result depends on architecture content present only in the Review
- **THEN** the Review remains `NEEDS_REVISION` until a new Design incorporates that content and is independently reviewed

### Requirement: Development handoff is self-contained
`ARCH-RD-HANDOFF` MUST identify the approved Design and ADR, Design maturity, target project and repository, implementation boundaries, cross-project dependencies, non-functional acceptance criteria, rollout and rollback obligations, unresolved decisions, and authorization state. Its complete payload and acceptance/readback SHALL be a downstream internal artifact; the human timeline MAY contain one concise handoff summary but MUST NOT require a dedicated Agent-to-Agent handoff comment.

#### Scenario: Handoff is authorized
- **WHEN** the user records `approved_for_spec`, the approved Design has `design_maturity=spec_ready|implementation_ready`, and a target project exists
- **THEN** the internal handoff contains enough information for the target R&D Team to begin its own requirement analysis and OpenSpec proposal without reinterpreting architecture intent, and the human timeline receives at most one terminal handoff summary

#### Scenario: Directional design is approved
- **WHEN** a Design with `design_maturity=directional` receives `approved_design_only`
- **THEN** the workflow may publish the approved direction but MUST NOT create an R&D handoff that authorizes OpenSpec work

### Requirement: Human-facing architecture artifacts use the shared action contract
Only a Human Action Request and the canonical `ARCH-DESIGN` it binds SHALL be mandatory human-facing architecture material. `ARCH-CONTROL`, `ARCH-RESEARCH`, complete `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET`, continuation and handoff/readback MAY be available as optional audit evidence but MUST NOT be required for a human content decision. The human entry point MUST present one action summary, one exact Design entry, concise Reviewer conclusion/findings, consequences and the exact response before minimal audit identity.

#### Scenario: Control record waits for routing
- **WHEN** Subject Project or approved-for-spec Target Project routing is missing after automatic discovery
- **THEN** the workflow emits one human dependency-input action with bounded candidates or `no_recommendation`, Owner, consequences, exact reply and post-response state while keeping the complete `ARCH-CONTROL` record internal

#### Scenario: Formal approval is requested
- **WHEN** an exact Design and approvable Review are ready for the unique Decision Owner
- **THEN** the human request exposes the complete Design as the sole mandatory material and summarizes Review findings without requiring the Owner to open Control, Research, Review or Packet

## ADDED Requirements

### Requirement: Design revisions are impact-based
Before producing a replacement Design for changed input, the workflow SHALL create an internal `architecture_design_impact_v1` record containing changed inputs, affected Design sections, rationale, verifier and exactly one result: `no_architecture_impact|architecture_impact`. Changes to recommendation, boundaries, external interfaces, consistency, security, privacy, reliability, capacity, performance, cost, migration, rollback, accepted risk, unresolved human decisions, validation criteria, Design maturity, or the material topology/meaning of a Design-bound diagram MUST be `architecture_impact`. Pure rendering, spacing or accessibility-preview changes that preserve source topology and Design meaning MAY be `no_architecture_impact` when exact evidence proves that classification. Unknown or unprovable impact MUST fail closed as `architecture_impact`.

#### Scenario: Evidence metadata changes without architecture impact
- **WHEN** only raw evidence location, execution status, wording or a non-consequential implementation detail changes and all architecture conclusions remain identical
- **THEN** the workflow updates internal evidence and does not create a new Design, Review, approval request or human progress comment

#### Scenario: Architecture conclusion changes
- **WHEN** a changed input affects any enumerated architecture-impact field
- **THEN** the workflow creates a new Design version, obtains a new independent Review and supersedes the old Action/manifest before requesting another decision

#### Scenario: Impact cannot be established
- **WHEN** evidence is insufficient to prove that a change has no architecture impact
- **THEN** the workflow treats it as `architecture_impact` and does not silently reuse prior approval
