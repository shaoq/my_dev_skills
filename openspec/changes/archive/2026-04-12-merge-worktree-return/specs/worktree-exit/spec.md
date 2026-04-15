## ADDED Requirements

### Requirement: Safe worktree exit via ExitWorktree
The skill SHALL use Claude Code's built-in `ExitWorktree` tool to exit the worktree and return to the main directory. The skill MUST only call `ExitWorktree` after confirming that all merge operations have succeeded.

#### Scenario: Successful exit
- **WHEN** all merges are verified successful and no uncommitted changes remain
- **THEN** the skill calls `ExitWorktree` with `action: "remove"` to exit and clean up the worktree

#### Scenario: Exit blocked by uncommitted changes
- **WHEN** there are still uncommitted changes in the worktree after merge attempts
- **THEN** the skill does NOT call `ExitWorktree` and instead reports the issue to the user

#### Scenario: Exit with keep option
- **WHEN** the user wants to keep the worktree for later reference
- **THEN** the skill calls `ExitWorktree` with `action: "keep"` to exit but preserve the worktree

### Requirement: Session CWD restoration
After exiting the worktree, the skill SHALL verify that the session's working directory has been restored to the original main project directory.

#### Scenario: CWD restored successfully
- **WHEN** `ExitWorktree` completes
- **THEN** the session working directory is the original main project directory (not the worktree directory)

#### Scenario: Post-exit verification
- **WHEN** the skill has exited the worktree
- **THEN** the skill runs `git status` and `git branch --show-current` to confirm the user is back on the main branch with a clean state
