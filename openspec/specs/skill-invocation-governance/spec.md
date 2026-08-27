# skill-invocation-governance Specification

## Purpose
Define independent controls for model inheritance, intent routing, material-write authorization, tool preapproval, and deterministic safety validation.

## Requirements

### Requirement: Skills inherit the caller-selected model
Repository skills SHALL continue using the model selected by the caller or host unless a separate requirement explicitly requests a model override. Invocation policy fields MUST NOT simulate model pinning, and affected OpenSpec orchestration skills MUST omit `model:` frontmatter.

#### Scenario: Team invokes a workflow
- **WHEN** a Team or subagent routes an OpenSpec workflow
- **THEN** it runs with the current model and does not select or persist a different model

### Requirement: Action workflows support intent-based routing
`new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, `merge-worktree-return`, and `check-changes-completed` SHALL support explicit commands, action-oriented natural language, Team/subagent orchestration, and nested skill workflows without user-only invocation metadata. Descriptions MUST exclude discussion, exploration, proposal review, and status-only intent.

#### Scenario: Team routes a child workflow
- **WHEN** an authorized Team delegates proposal creation, apply, completion checking, or return work
- **THEN** the matching skill runs under the same documented scope and safety gates

#### Scenario: User only discusses behavior
- **WHEN** the user requests explanation or review without asking to perform the action
- **THEN** the action skill is not selected merely because its name is mentioned

### Requirement: Authorization is placed at the material side-effect boundary
`new-worktree-apply` SHALL treat a concrete implementation request as authorization for its limited isolated-source operation and MUST NOT ask again after stable preflight. `parall-new-proposal`, `parall-new-worktree-apply`, and `merge-worktree-return` MUST retain one affirmative confirmation immediately before documented material writes. Completion backfill MUST require explicit backfill intent. Safety failures MUST NOT become confirmation prompts.

#### Scenario: Single apply reaches a stable boundary
- **WHEN** a concrete implementation request passes every preflight and revalidation gate
- **THEN** the skill begins limited source-worktree writes without repeated confirmation

#### Scenario: Higher-impact workflow reaches writes
- **WHEN** a parallel proposal, parallel apply, or return workflow displays its complete plan
- **THEN** it begins material writes only after one affirmative confirmation

### Requirement: Tool preapproval is independent from invocation policy
Environment validation SHALL treat `allowed-tools` as permission preapproval and invocation metadata as routing policy. A model-invocable skill omitting both `allowed-tools` and `disable-model-invocation` SHALL be valid and MUST NOT warn merely because automatic invocation is possible. Declared Bash prefixes SHALL still be checked against standard permissions.

#### Scenario: Model-invocable skill has no preapproved tools
- **WHEN** a valid skill omits both fields and relies on normal Runtime permission handling
- **THEN** the consistency checker emits no missing-guardrail warning

#### Scenario: GitNexus is required
- **WHEN** repository instructions require GitNexus impact or change detection
- **THEN** omission from `allowed-tools` does not classify GitNexus as unavailable and normal Runtime permission flow governs the call
