## ADDED Requirements

### Requirement: OpenSpec apply invocation
After worktree creation and HEAD verification, the skill SHALL invoke the `/opsx:apply` skill with the proposal name as argument. The skill MUST use the Skill tool to invoke `openspec-apply-change` or the `/opsx:apply` command.

#### Scenario: Successful apply invocation
- **WHEN** worktree creation and HEAD verification complete successfully
- **THEN** the skill invokes `/opsx:apply <proposal-name>` using the Skill tool, passing the proposal name as the argument

#### Scenario: OpenSpec CLI not available
- **WHEN** `openspec` command is not found in the system
- **THEN** the skill reports an error indicating OpenSpec CLI is required and suggests installing it

#### Scenario: Proposal does not exist
- **WHEN** the specified proposal name does not exist in `openspec/changes/`
- **THEN** the skill reports an error listing available proposals and suggests using `/opsx:propose` to create one first

### Requirement: Prerequisites validation
Before starting the workflow, the skill SHALL validate that all prerequisites are met: the current directory is a git repository, OpenSpec CLI is available, and the proposal name argument is provided.

#### Scenario: All prerequisites met
- **WHEN** user runs `/new-worktree-apply add-user-auth` in a git repo with OpenSpec CLI installed
- **THEN** the skill proceeds with the full workflow

#### Scenario: Missing proposal name argument
- **WHEN** user runs `/new-worktree-apply` without any argument
- **THEN** the skill prompts the user to provide a proposal name using AskUserQuestion

#### Scenario: Not in a git repository
- **WHEN** user runs `/new-worktree-apply add-user-auth` in a non-git directory
- **THEN** the skill reports an error indicating a git repository is required

### Requirement: Skill frontmatter configuration
The SKILL.md file SHALL include proper frontmatter with `name: new-worktree-apply`, `disable-model-invocation: true` to prevent auto-triggering, and `argument-hint: <proposal-name>` to guide argument input.

#### Scenario: Skill is user-invocable only
- **WHEN** the skill is loaded into Claude Code
- **THEN** Claude does not automatically trigger this skill; it can only be invoked by the user via `/new-worktree-apply`

#### Scenario: Argument hint is displayed
- **WHEN** user types `/new-worktree-apply` and triggers auto-complete
- **THEN** the hint `<proposal-name>` is displayed to guide the user
