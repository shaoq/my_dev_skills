## ADDED Requirements

### Requirement: Workflow classifies and controls architecture work
The skill SHALL classify each accepted architecture request as `evolution`, `greenfield`, or `hybrid`, record its stage in `ARCH-CONTROL`, and allow only transitions defined by the architecture workflow.

#### Scenario: Existing system architecture upgrade
- **WHEN** a request primarily changes an existing system and its integration contracts
- **THEN** the workflow classifies it as `evolution` and requires current-state, impact, migration, and rollback evidence

#### Scenario: New supporting system
- **WHEN** a request requires a new standalone system with no existing implementation baseline
- **THEN** the workflow classifies it as `greenfield` and requires boundary, capability, build-vs-buy, deployment, and cost evidence

#### Scenario: Mixed architecture change
- **WHEN** a request combines existing-system modification with a new service or platform
- **THEN** the workflow classifies it as `hybrid` and requires both evidence sets plus their interface and migration sequence

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

### Requirement: Code facts use GitNexus-first evidence
For code discovery, logic analysis, execution-flow tracing, change impact, and architecture fact validation, the skill MUST prefer the applicable GitNexus skill and MUST rebuild a stale index before relying on it.

#### Scenario: GitNexus index is stale
- **WHEN** an Agent detects that the target repository index is stale
- **THEN** it rebuilds the index before querying and records the repository and indexed commit in `ARCH-RESEARCH`

#### Scenario: GitNexus is unavailable
- **WHEN** the target repository cannot be indexed or GitNexus is unavailable
- **THEN** the Agent uses bounded source inspection, declares the evidence limitation, and does not convert absence of evidence into a factual negative

### Requirement: Human approval uses two explicit gates
The workflow MUST distinguish `approved_design_only` from `approved_for_spec` and MUST NOT infer either approval from an Agent recommendation, urgency, assignment, or ambiguous human comment.

#### Scenario: Design-only approval
- **WHEN** the user explicitly records `approved_design_only`
- **THEN** the workflow may publish ADR and detailed design but must not create a development handoff that authorizes OpenSpec work

#### Scenario: Approval for Spec
- **WHEN** the user explicitly records `approved_for_spec`
- **THEN** the workflow may publish the approved design and create `ARCH-RD-HANDOFF` for the selected target project

#### Scenario: Revision requested
- **WHEN** the user or Reviewer requests revision
- **THEN** the workflow returns to designing with a new `ARCH-DESIGN` version and retains the prior review trail

### Requirement: Project creation and delivery remain outside the skill
The skill MUST NOT create repositories, Multica Projects, Teams, Agents, watchdogs, development Issues, worktrees, branches, or commits as an implied consequence of architecture analysis.

#### Scenario: Greenfield target project does not exist
- **WHEN** an approved greenfield design has no confirmed target repository or Multica Project
- **THEN** the workflow enters `waiting_human`, reports the missing routing decision, and creates nothing automatically
