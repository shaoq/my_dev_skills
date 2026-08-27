## ADDED Requirements

### Requirement: Skills inherit the caller-selected model
Repository skills SHALL continue using the model selected by the caller or host unless a separate requirement explicitly requests a model override. Invocation policy fields MUST NOT be used to simulate model pinning, and the affected OpenSpec orchestration skills MUST omit `model:` frontmatter.

#### Scenario: Team invokes a workflow
- **WHEN** a Team or subagent routes an OpenSpec workflow while the session uses its current model
- **THEN** the workflow runs with that current model and does not select or persist a different model

#### Scenario: Explicit command invokes a workflow
- **WHEN** a user invokes the same workflow through its command syntax
- **THEN** model selection remains identical to natural-language or Team routing

### Requirement: Action workflows support intent-based routing
`new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, `merge-worktree-return`, and `check-changes-completed` SHALL be available to explicit commands, model selection from an action-oriented natural-language request, Team/subagent orchestration, and nested skill workflows. They MUST NOT require user-only invocation metadata. Their descriptions MUST distinguish requests to perform the action from discussion, exploration, proposal review, or status questions.

#### Scenario: Natural-language implementation request
- **WHEN** the user asks the agent to implement a named OpenSpec change in an isolated worktree and provides or permits resolution of the required inputs
- **THEN** the model may select `new-worktree-apply` without requiring the user to repeat the request as a skill command

#### Scenario: Team routes a child workflow
- **WHEN** an authorized Team workflow delegates proposal creation, apply, completion checking, or return work to the matching skill
- **THEN** the child skill may run under the same documented scope and safety gates

#### Scenario: User is only discussing behavior
- **WHEN** the user asks how a workflow works or requests review without asking to perform it
- **THEN** the action skill is not selected merely because its name or artifacts are mentioned

### Requirement: Authorization is placed at the material side-effect boundary
Each affected skill SHALL separate read-only routing/preflight from authorization to mutate state. `new-worktree-apply` SHALL treat a concrete user implementation request as authorization for its limited isolated-source operation and MUST NOT ask again after stable preflight. `parall-new-proposal`, `parall-new-worktree-apply`, and `merge-worktree-return` MUST retain one affirmative confirmation immediately before their documented material writes. Completion backfill MUST require explicit backfill intent.

#### Scenario: Single apply reaches stable write boundary
- **WHEN** a concrete implementation request has been routed to `new-worktree-apply` and all preflight/revalidation gates pass
- **THEN** the skill begins its limited source-worktree writes without a repeated confirmation

#### Scenario: Parallel proposal reaches artifact creation
- **WHEN** a routed parallel proposal workflow has displayed its split and dependency plan
- **THEN** it creates proposal artifacts only after one affirmative confirmation

#### Scenario: Parallel apply or return reaches Git writes
- **WHEN** the routed workflow has displayed its complete target, hash, verification, merge, and cleanup plan
- **THEN** it begins the planned writes only after one affirmative confirmation

#### Scenario: Safety gate fails
- **WHEN** a deterministic repository, target, snapshot, path, manifest, or scope gate fails
- **THEN** the workflow stops and MUST NOT ask the user to authorize bypassing the failed safety condition

### Requirement: Tool preapproval is independent from invocation policy
Environment validation SHALL treat `allowed-tools` as permission preapproval and invocation metadata as routing policy. A model-invocable skill that intentionally omits both `allowed-tools` and `disable-model-invocation` SHALL be valid and MUST NOT produce a warning merely because automatic invocation is possible.

#### Scenario: Model-invocable skill has no preapproved tools
- **WHEN** a valid skill omits both fields and relies on normal Runtime permission handling
- **THEN** the consistency checker emits no missing-guardrail warning

#### Scenario: Skill declares Bash preapprovals
- **WHEN** a skill declares Bash command prefixes through `allowed-tools`
- **THEN** the consistency checker still compares those prefixes with the repository's standard permission list

#### Scenario: GitNexus is needed by an affected workflow
- **WHEN** applicable repository instructions require GitNexus impact or change detection
- **THEN** omission from `allowed-tools` does not classify GitNexus as unavailable, and the normal Runtime permission flow governs the call
