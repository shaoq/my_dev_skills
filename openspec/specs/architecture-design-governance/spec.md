# architecture-design-governance Specification

## Purpose
TBD - created by archiving change add-architecture-design-workflow. Update Purpose after archive.
## Requirements
### Requirement: Workflow classifies and controls architecture work
The skill SHALL classify each accepted architecture request as `evolution`, `greenfield`, or `hybrid`, record its stage in `ARCH-CONTROL`, and allow only transitions defined by the architecture workflow. The canonical stages MUST be `intake`, `routed`, `researching`, `designing`, `reviewing`, `waiting_human`, `approved_design_only`, `approved_for_spec`, `publishing`, `handed_off`, `completed_design_only`, and `rejected`. `revision_requested` MUST be recorded as a decision that starts a new `designing` iteration rather than as a persistent stage. Every `waiting_human` record MUST identify `WAIT_REASON` as `design_approval` or `target_project`. `review_packet_unavailable` SHALL be a stable reviewing blocker distinct from Review conclusion; an approvable review MUST remain at `reviewing` until an external current-packet `review_packet_ready` envelope binds the current packet ref/version/digest. `approved_artifact_unavailable` SHALL be a stable publishing blocker that preserves the valid human decision and readiness while exact approved bytes cannot be recovered.

#### Scenario: Existing system architecture upgrade
- **WHEN** a request primarily changes an existing system and its integration contracts
- **THEN** the workflow classifies it as `evolution` and requires current-state, impact, migration, and rollback evidence

#### Scenario: New supporting system
- **WHEN** a request requires a new standalone system with no existing implementation baseline
- **THEN** the workflow classifies it as `greenfield` and requires boundary, capability, build-vs-buy, deployment, and cost evidence

#### Scenario: Mixed architecture change
- **WHEN** a request combines existing-system modification with a new service or platform
- **THEN** the workflow classifies it as `hybrid` and requires both evidence sets plus their interface and migration sequence

#### Scenario: Review requests revision
- **WHEN** the Reviewer concludes `NEEDS_REVISION`
- **THEN** the workflow starts a new `designing` iteration, preserves the prior design and review versions, and does not enter publication

#### Scenario: Reviewer revision does not create an approval packet
- **WHEN** the Reviewer concludes `NEEDS_REVISION` before an approvable packet exists
- **THEN** the workflow starts a new design version without creating an approval packet, and creates a packet only after a later exact design/review pair becomes approvable

#### Scenario: Design is rejected
- **WHEN** a recognizable human explicitly records `rejected` for the current ready packet ref, version and digest
- **THEN** the workflow enters terminal stage `rejected` and does not publish or create a development handoff

#### Scenario: Approvable review lacks a ready packet
- **WHEN** the Reviewer concludes `APPROVABLE_WITH_WARNINGS` or `APPROVABLE` but current-packet readiness is absent or failed
- **THEN** the workflow preserves that conclusion, remains `reviewing`, and records `BLOCKED_REASON=review_packet_unavailable` with failure evidence and closing condition

#### Scenario: Approvable review has a ready packet
- **WHEN** the Reviewer conclusion is approvable and a valid external `review_packet_ready` envelope binds the current design, review and packet refs, versions and digests
- **THEN** the workflow enters `waiting_human` with `WAIT_REASON=design_approval` and `BLOCKED_REASON=none`

#### Scenario: Historical waiting-human record is not automatically migrated
- **WHEN** workflow rules are upgraded while a historical record is already persisted at `waiting_human` without packet readiness evidence and no new design or review version is produced
- **THEN** the workflow preserves the historical stage and evidence without fabricating readiness or automatically downgrading it, and applies the new packet gate when that record is explicitly refreshed or versioned

### Requirement: Architecture stage remains separate from OpenSpec delivery
During architecture research, design, review, and design-only publication, the skill MUST NOT create or modify OpenSpec proposal, design, specs, tasks, or implementation artifacts.

#### Scenario: User asks for a design proposal
- **WHEN** the user requests a complex architecture proposal but has not approved entry into the target project's Spec workflow
- **THEN** the skill produces architecture reports only and does not create an OpenSpec change

#### Scenario: Urgent wording requests direct proposal creation
- **WHEN** an architecture Issue contains urgency wording or asks an Agent to proceed directly
- **THEN** the skill preserves the architecture gates and does not treat urgency as OpenSpec authorization

### Requirement: Brainstorming is conditional and bounded
The skill SHALL use `superpowers:brainstorming` only when intent, scope, constraints, or solution space requires clarification, and MUST return to the architecture workflow using a frozen brainstorming conclusion before `openspec-explore` thinking.

#### Scenario: Requirements are already precise
- **WHEN** the accepted architecture request has clear goals, boundaries, constraints, and decision criteria
- **THEN** the workflow may skip brainstorming and proceed to evidence-based exploration

#### Scenario: Brainstorming is required
- **WHEN** key goals, boundaries, constraints, or alternatives are ambiguous
- **THEN** the workflow runs brainstorming, records its confirmed conclusion, and prevents brainstorming's downstream planning or implementation steps from taking control

#### Scenario: Required brainstorming dependency is unavailable
- **WHEN** clarification is required but the Runtime cannot resolve `superpowers:brainstorming`
- **THEN** the workflow keeps its current stage, records `BLOCKED_REASON=missing_brainstorming`, performs no architecture research or OpenSpec write, and asks the user to restore the dependency or provide sufficient clarification

### Requirement: OpenSpec exploration dependency fails closed
The workflow MUST verify that the Runtime can resolve `openspec-explore` before entering architecture research. It MUST NOT install missing skills, modify Runtime configuration, or silently substitute another planning, proposal, or implementation workflow.

#### Scenario: OpenSpec exploration is unavailable
- **WHEN** the Runtime cannot resolve `openspec-explore`
- **THEN** the workflow keeps its current stage, records `BLOCKED_REASON=missing_openspec_explore`, reports the missing dependency in Chinese, and stops before research or repository writes

### Requirement: Code facts use GitNexus-first evidence
For code discovery, logic analysis, execution-flow tracing, change impact, and architecture fact validation, the skill MUST prefer the applicable GitNexus skill and MUST rebuild a stale index before relying on it.

#### Scenario: GitNexus index is stale
- **WHEN** an Agent detects that the target repository index is stale
- **THEN** it rebuilds the index before querying and records the repository and indexed commit in `ARCH-RESEARCH`

#### Scenario: GitNexus is unavailable
- **WHEN** the target repository cannot be indexed or GitNexus is unavailable
- **THEN** the Agent uses bounded source inspection, declares the evidence limitation, and does not convert absence of evidence into a factual negative

### Requirement: Human approval uses two explicit gates
The workflow MUST distinguish `approved_design_only` from `approved_for_spec` and MUST NOT infer either approval from an Agent recommendation, urgency, assignment, Reviewer conclusion, readiness evidence, or ambiguous human comment. A legal human decision MUST bind the current `ARCH-APPROVAL-PACKET` ref, version and digest; a decision for a superseded packet MUST be an auditable no-op for the current gate.

#### Scenario: Design-only approval
- **WHEN** a recognizable human explicitly records `approved_design_only` for the current ready packet
- **THEN** the workflow may publish ADR and detailed design but must not create a development handoff that authorizes OpenSpec work

#### Scenario: Approval for Spec
- **WHEN** a recognizable human explicitly records `approved_for_spec` for the current ready packet
- **THEN** the workflow may publish the approved design and create `ARCH-RD-HANDOFF` for the selected target project

#### Scenario: Revision requested
- **WHEN** a recognizable human records `revision_requested` for the current ready packet ref, version and digest
- **THEN** the workflow returns to designing with a new `ARCH-DESIGN`, records the prior packet as superseded only in external control state without modifying its payload, retains the prior review trail, and does not create a new packet until the replacement design/review pair becomes approvable

#### Scenario: Recommendation is not approval
- **WHEN** the packet contains any `ARCHITECTURE_RECOMMENDATION` but no valid current-packet human decision
- **THEN** the workflow remains `waiting_human` and does not publish or hand off

#### Scenario: Superseded packet is approved late
- **WHEN** a human decision binds an older packet after a new current packet exists
- **THEN** the workflow preserves the old decision as evidence but does not change the current gate

### Requirement: Project creation and delivery remain outside the skill
The skill MUST NOT create repositories, Multica Projects, Teams, Agents, watchdogs, development Issues, worktrees, branches, or commits as an implied consequence of architecture analysis.

#### Scenario: Greenfield target project does not exist
- **WHEN** an approved greenfield design has no confirmed target repository or Multica Project
- **THEN** the workflow preserves `approved_for_spec`, enters or remains in `waiting_human` with `WAIT_REASON=target_project`, reports the missing routing decision, and creates nothing automatically

### Requirement: User-visible workflow output is Chinese
The skill MUST use Chinese for user-visible status updates, clarification questions, research summaries, review findings, human-gate prompts, publication summaries, and development handoff reports. Commands, paths, canonical state values, code identifiers, protocol fields, and quoted authoritative source text MAY remain in their original language when accuracy requires it.

#### Scenario: Workflow reports a blocked dependency
- **WHEN** a required dependency, evidence source, or routing decision is missing
- **THEN** the workflow explains the blocker and next action in Chinese while preserving exact technical identifiers

#### Scenario: Workflow completes an architecture report
- **WHEN** the workflow emits any structured architecture report
- **THEN** its narrative and user guidance are Chinese and its commands, identifiers, and citations remain technically exact

### Requirement: Clarification recommendations do not satisfy evidence or approval gates
A candidate recommendation and a human response to a pre-approval clarification request SHALL affect only the explicitly identified design input. They MUST NOT be treated as measured evidence, another responsibility Owner's decision, an approvable Review conclusion, packet readiness, `ARCHITECTURE_RECOMMENDATION`, or a legal human approval decision. A general acceptance MUST leave independently required measurements, named-Owner decisions and exact packet ref/version/digest approval gates open.

#### Scenario: Human accepts provisional clarification defaults
- **WHEN** a recognizable human accepts one or more provisional candidate values while capacity measurements or named-Owner decisions remain missing
- **THEN** the workflow records the accepted design inputs, preserves the unresolved evidence and Owners, and does not enter formal Review or human approval solely from that acceptance

#### Scenario: Clarification comment is explicitly non-authoritative
- **WHEN** a clarification request presents candidate recommendations before an approvable current packet exists
- **THEN** it explicitly states that the recommendations are not human decisions or approvals and cannot produce `approved_design_only` or `approved_for_spec`

### Requirement: Human waiting states publish actionable decision semantics
Whenever core reports `waiting_human` or otherwise names a human as `Next Owner`, it SHALL also publish the applicable Human Action Request items. Each legal response MUST state the resulting canonical stage, remaining blockers, next Owner and immediate planned writes; no response MAY imply authorization outside its declared action type.

#### Scenario: Subject Project is missing
- **WHEN** intake reaches `waiting_human` with `WAIT_REASON=target_project` and `BLOCKED_REASON=missing_subject_project`
- **THEN** a routing request explains the ownership decision, candidates or evidence path, consequences and exact reply while gate remains `none`

#### Scenario: Current packet awaits approval
- **WHEN** a current ready packet enters `waiting_human` with `WAIT_REASON=design_approval`
- **THEN** a design-approval request explains all four legal outcomes and no recommendation, readiness or ambiguous acknowledgement is treated as the decision

### Requirement: Formal revision decision and revision guidance remain separate
`revision_requested` SHALL remain the only authoritative current-packet decision value for returning to `designing`. Detailed requested changes MAY be captured in a separate version-bound revision brief ref, but prose, the brief itself or an edited decision MUST NOT replace legal decision evidence. When no actionable brief exists, the workflow SHALL create a new `design_input` request after entering `designing` rather than claim that revision scope is known.

#### Scenario: Human requests revision with a brief
- **WHEN** a recognizable human records current-packet `revision_requested` and supplies a separate bound revision brief
- **THEN** the workflow starts a replacement design attempt and uses the brief as non-authoritative design input without altering the prior packet

#### Scenario: Human provides only the revision token
- **WHEN** current-packet `revision_requested` is valid but no actionable revision brief exists
- **THEN** the workflow enters `designing`, records the missing scope and presents a reviewable design-input request before claiming a complete revision requirement

### Requirement: Human-readable requests do not weaken canonical gates
Adding a Human Action Request MUST NOT change canonical stages, blockers, Review conclusions, packet readiness, recommendation or legal decision tokens. A readable request, candidate option, reaction or authorization-looking text is non-authoritative until the corresponding existing evidence and actor-binding rules pass.

#### Scenario: Readable approval card has no legal decision
- **WHEN** the card and complete materials are available but no valid current-packet decision evidence exists
- **THEN** the workflow remains `waiting_human` and performs no publication or handoff
