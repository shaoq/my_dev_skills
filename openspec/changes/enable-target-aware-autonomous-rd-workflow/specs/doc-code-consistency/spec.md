## MODIFIED Requirements

### Requirement: OpenSpec change-level doc verification
When the caller explicitly selects one active OpenSpec change and supplies `--base <target-branch>`, the skill SHALL additionally read that change's proposal.md, design.md, and specs/*/spec.md to extract structured claims, prove the frozen base commit is an ancestor of the frozen current commit, and verify each claim against that immutable range. The skill MUST NOT auto-select active changes, use a fixed `main..HEAD` range, or guess a missing target branch or merge base.

#### Scenario: Change proposal claims verified
- **WHEN** active change's proposal.md declares "add refresh token endpoint" and the caller supplies `--base develop`
- **THEN** skill SHALL verify the refresh token endpoint exists in the frozen `develop`-to-current-HEAD diff scope

#### Scenario: Spec WHEN/THEN scenarios verified
- **WHEN** spec.md defines "WHEN user submits valid email THEN system sends verification"
- **THEN** skill SHALL check code within the explicit frozen change scope for email sending logic after validation

#### Scenario: Selected active change has no explicit base
- **WHEN** the caller selects an active OpenSpec change but supplies no `--base`
- **THEN** the skill SHALL report the OpenSpec incremental dimension as not executed and MUST NOT substitute `main` or another inferred branch

#### Scenario: No change is explicitly selected
- **WHEN** active OpenSpec changes exist but the caller invokes `verify-impl-consistency` without a change name and without `--base`
- **THEN** the skill SHALL run project-level verification only and MUST NOT read an active change as the incremental target

#### Scenario: Selected base is not an ancestor
- **WHEN** the selected target commit is not an ancestor of the frozen current commit
- **THEN** the skill SHALL report the OpenSpec incremental dimension as not executed and MUST NOT reinterpret a tree-to-tree diff as the selected change's delivery scope
