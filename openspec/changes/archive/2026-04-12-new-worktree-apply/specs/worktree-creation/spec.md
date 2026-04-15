## ADDED Requirements

### Requirement: Git status check and auto-commit
The skill SHALL check the current git working directory status using `git status --porcelain`. If any uncommitted files exist (staged, unstaged, or untracked), the skill SHALL automatically stage all files with `git add -A` and commit them with the message `chore: auto-commit before worktree for <proposal-name>`.

#### Scenario: Working directory has uncommitted changes
- **WHEN** user runs `/new-worktree-apply add-user-auth` and there are modified files
- **THEN** the skill stages all changes with `git add -A` and commits with message `chore: auto-commit before worktree for add-user-auth`

#### Scenario: Working directory is clean
- **WHEN** user runs `/new-worktree-apply add-user-auth` and `git status --porcelain` returns empty
- **THEN** the skill skips the commit step and proceeds to worktree creation

### Requirement: Main branch detection
The skill SHALL detect the main branch name automatically by checking in order: `main`, `master`, `trunk`. If none of these branches exist locally, the skill SHALL attempt `git remote show origin` to determine the default branch. The user MAY override the detected branch by specifying it as a second argument.

#### Scenario: Automatic detection of main branch
- **WHEN** user runs `/new-worktree-apply add-user-auth` without specifying a branch
- **THEN** the skill detects the main branch by checking `main`, `master`, `trunk` in order, using the first one that exists

#### Scenario: User-specified branch override
- **WHEN** user runs `/new-worktree-apply add-user-auth --branch develop`
- **THEN** the skill uses `develop` as the main branch instead of auto-detecting

### Requirement: Worktree creation via EnterWorktree tool
The skill SHALL use Claude Code's built-in `EnterWorktree` tool to create a new worktree with the proposal name as the branch name. The skill MUST verify that the branch name does not already exist before creating the worktree.

#### Scenario: Successful worktree creation
- **WHEN** user runs `/new-worktree-apply add-user-auth` and branch `add-user-auth` does not exist
- **THEN** the skill creates a worktree using `EnterWorktree` with name `add-user-auth`, which creates a new branch and switches the session CWD

#### Scenario: Branch name already exists
- **WHEN** user runs `/new-worktree-apply add-user-auth` and branch `add-user-auth` already exists
- **THEN** the skill reports an error indicating the branch already exists and suggests using a different name or deleting the existing branch

#### Scenario: Invalid branch name characters
- **WHEN** user runs `/new-worktree-apply add user auth` (contains spaces or invalid characters)
- **THEN** the skill validates the proposal name conforms to worktree naming rules (letters, digits, dots, underscores, hyphens, max 64 chars) and reports an error if invalid

### Requirement: HEAD consistency verification
After worktree creation, the skill SHALL compare the worktree HEAD commit with the main branch HEAD commit. If they differ, the skill SHALL merge the main branch into the worktree branch to ensure the worktree has the latest code.

#### Scenario: Worktree HEAD matches main branch
- **WHEN** worktree is created and its HEAD matches the main branch HEAD
- **THEN** the skill proceeds to the apply step without any additional merge

#### Scenario: Worktree HEAD is behind main branch
- **WHEN** worktree is created but its HEAD is behind the main branch HEAD
- **THEN** the skill executes `git merge <main-branch>` in the worktree to bring it up to date
