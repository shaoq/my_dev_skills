## ADDED Requirements

### Requirement: Optional proposal completion verification
When the user provides a proposal name argument, the skill SHALL verify that the corresponding OpenSpec proposal has been fully applied before proceeding with the merge. The skill MUST check `openspec status --change <name> --json` and confirm all tasks are complete.

#### Scenario: Proposal fully applied
- **WHEN** user runs `/merge-worktree-return add-user-auth` and all tasks in the `add-user-auth` proposal are complete
- **THEN** the skill proceeds with the merge workflow

#### Scenario: Proposal partially applied
- **WHEN** user runs `/merge-worktree-return add-user-auth` and some tasks in the `add-user-auth` proposal are incomplete
- **THEN** the skill reports which tasks are incomplete and uses AskUserQuestion to confirm whether to proceed with the merge

#### Scenario: Proposal not found
- **WHEN** user runs `/merge-worktree-return non-existent-proposal` and the proposal does not exist
- **THEN** the skill reports an error listing available proposals

#### Scenario: No proposal argument provided
- **WHEN** user runs `/merge-worktree-return` without a proposal name
- **THEN** the skill skips the OpenSpec verification step and proceeds directly with the merge workflow

### Requirement: Skill frontmatter configuration
The SKILL.md file SHALL include proper frontmatter with `name: merge-worktree-return`, `disable-model-invocation: true`, and `argument-hint: [proposal-name]` (square brackets indicating optional argument).

#### Scenario: Skill is user-invocable only
- **WHEN** the skill is loaded into Claude Code
- **THEN** Claude does not automatically trigger this skill; it can only be invoked by the user via `/merge-worktree-return`

#### Scenario: Argument hint indicates optional parameter
- **WHEN** user types `/merge-worktree-return` and triggers auto-complete
- **THEN** the hint `[proposal-name]` is displayed, with square brackets indicating the argument is optional
