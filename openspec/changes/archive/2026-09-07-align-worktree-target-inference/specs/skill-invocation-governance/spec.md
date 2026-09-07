## MODIFIED Requirements

### Requirement: Authorization is placed at the material side-effect boundary
`new-worktree-apply` SHALL treat a concrete implementation request with an explicit target as authorization for its limited isolated-source operation and MUST NOT ask again after stable preflight. An inferred target MUST receive one affirmative confirmation for the complete plan before writes. `parall-new-proposal` and `parall-new-worktree-apply` MUST retain one affirmative confirmation immediately before documented material writes. `merge-worktree-return` MUST require confirmation for an inferred target or pending source changes, while an explicit-target clean-source return MAY proceed after stable independent revalidation without a second confirmation. Completion backfill MUST require explicit backfill intent. Safety failures MUST NOT become confirmation prompts.

#### Scenario: Explicit single apply reaches a stable boundary
- **WHEN** a concrete implementation request supplies an explicit target and passes every preflight and revalidation gate
- **THEN** the skill begins limited source-worktree writes without repeated confirmation

#### Scenario: Inferred single apply reaches a stable boundary
- **WHEN** a concrete implementation request omits the target and the workflow displays a complete inferred-target plan
- **THEN** it begins material writes only after one affirmative confirmation and stable revalidation

#### Scenario: Parallel workflow reaches writes
- **WHEN** a parallel proposal or parallel apply workflow displays its complete plan
- **THEN** it begins material writes only after one affirmative confirmation

#### Scenario: Deterministic return reaches writes
- **WHEN** a clear return request supplies an explicit target, the canonical source is clean, and every preflight fact remains stable
- **THEN** the return workflow begins bounded writes without a second confirmation

#### Scenario: Interactive return reaches writes
- **WHEN** a clear return request uses an inferred target or has pending source changes
- **THEN** the return workflow begins material writes only after one affirmative confirmation for the complete plan
