## MODIFIED Requirements

### Requirement: Claude Code and Codex share one skill source
The implementation SHALL maintain one root `architecture-design-workflow/` source and one sibling `multica-architecture-approval-adapter/` source, expose each to Claude Code and Codex through the managed installation mechanism, and record compatible contract revisions when both are active. Runtime refresh MUST update the selected pair from repository bytes without copying divergent prompt content into runtime homes. Archify SHALL remain an independently sourced external Skill and MUST NOT be copied into either repository Skill or treated as part of their shared source tree.

#### Scenario: Compatible skills are installed
- **WHEN** the installer scans valid core and adapter Skill sources
- **THEN** it creates or preserves runtime links to the repository sources and validation proves both runtimes resolve the same compatible contract pair

#### Scenario: Runtime target conflicts with regular content
- **WHEN** a runtime contains a regular file or directory at either skill target
- **THEN** the installer preserves it, reports the conflict, and MUST NOT claim the new pair active for that runtime

### Requirement: Behavioral tests preserve hard gates
Implementation MUST include versioned fixtures and repeatable contract runners for project routing, OpenSpec prohibition, two-stage human approval, exact Design/Review/visual-manifest binding, one-Design human delivery, internal-only Agent flow, Design maturity, impact-based revision, Archify missing/stale/invalid evidence, light/1440×900 preview receipt/digest and requested-client projection, failed/skipped browser/perceptual gates, author/reviewer role boundaries, Chinese output, dependency preflight, supersession and missing evidence. Each fixture MUST define expected stage, gate, visible entries/attachments, forbidden human-visible artifacts, permitted writes and evidence fields. Claude Code and Codex evidence MUST identify Runtime version, fixture, normalized result, evidence location and limitations.

#### Scenario: Single Design surface is replayed
- **WHEN** an approvable Design enters formal human review
- **THEN** both runtimes expose exactly one canonical Design material, keep Review/Packet/Control internal, and preserve the same current-Action gate

#### Scenario: Agent handoff is replayed
- **WHEN** one architecture responsibility transfers to another without a human decision
- **THEN** both runtimes require accepted/active internal continuation evidence and forbid a dedicated human handoff comment

#### Scenario: Baseline failure is replayed after implementation
- **WHEN** a test asks an Agent to bypass routing and create a cross-project OpenSpec proposal
- **THEN** the Agent refuses, records the project route internally and waits for the correct gate

#### Scenario: Runtime dependency is missing
- **WHEN** a fixture makes a required dependency unavailable
- **THEN** the normalized result records the expected blocker, contains no OpenSpec or implementation write, and gives the next action in Chinese

#### Scenario: Routine engineering task is replayed
- **WHEN** a fixture asks for ordinary bug triage, status follow-up, approved implementation or code review
- **THEN** the normalized result confirms that the architecture workflow does not claim primary ownership

## ADDED Requirements

### Requirement: Contract activation is attempt-scoped and atomic
Activation SHALL verify core/adapter compatibility before any real workspace binding, record the selected revisions, and apply them only to new attempts. A partially refreshed pair MUST fail closed. Existing attempt artifacts and actions MUST remain bound to their frozen revisions until explicitly superseded.

#### Scenario: Only one skill refreshes
- **WHEN** runtime resolution yields new core bytes with an incompatible old adapter or the reverse
- **THEN** activation fails before platform writes and reports both observed revisions

#### Scenario: A new attempt starts after refresh
- **WHEN** compatible core and adapter revisions pass local and sandbox validation
- **THEN** the new attempt records the pair while old attempts retain their prior interpretation

### Requirement: External diagram dependency is pinned and independently activated
Any activation that enables Archify-backed visual companions SHALL record the external Skill name, semantic version, source repository revision, archive SHA-256, available diagram types and CLI contract before binding. Runtime-local installation and Multica workspace import MUST be verified separately. A mutable checkout path, same-name catalog entry or successful local command MUST NOT be accepted as proof that the selected workspace Agents have the pinned Skill enabled. Upgrade, digest mismatch or import conflict MUST stop activation before changing Agent bindings.

#### Scenario: Runtime has Archify but workspace does not
- **WHEN** Claude or Codex resolves the pinned Archify source but `multica skill list` has no matching imported Skill ID
- **THEN** local diagram use may remain available while Multica activation reports `BLOCKED_SKILL_BINDING` and performs no Agent binding

#### Scenario: Pinned archive is verified
- **WHEN** name, version, source revision and archive digest all match the approved activation manifest
- **THEN** the operator may import the archive with conflict-fail semantics and continue to additive role bindings

#### Scenario: Existing Archify name has different bytes
- **WHEN** the workspace contains a same-name Skill whose observed version or digest differs from the activation manifest
- **THEN** activation stops and MUST NOT overwrite, rename or partially bind without a new explicit human decision
