## ADDED Requirements

### Requirement: Auto-commit worktree changes
The skill SHALL check the current worktree branch for uncommitted files using `git status --porcelain`. If any uncommitted files exist, the skill SHALL automatically stage and commit all changes with a descriptive commit message.

#### Scenario: Worktree has uncommitted changes
- **WHEN** user runs `/merge-worktree-return` and there are uncommitted files in the worktree
- **THEN** the skill stages all changes with `git add -A` and commits with message `chore: auto-commit before merge from worktree`

#### Scenario: Worktree is clean
- **WHEN** user runs `/merge-worktree-return` and `git status --porcelain` returns empty
- **THEN** the skill skips the commit step and proceeds to rebase

### Requirement: Rebase from main branch
The skill SHALL detect the main branch name (same strategy as `new-worktree-apply`: check `main`, `master`, `trunk` in order) and execute `git rebase <main-branch>` in the worktree. If conflicts occur, the skill SHALL attempt to resolve them automatically.

#### Scenario: Rebase without conflicts
- **WHEN** the worktree branch is rebased onto the main branch and no conflicts occur
- **THEN** the skill completes the rebase and proceeds to merge step

#### Scenario: Rebase with auto-resolvable conflicts
- **WHEN** the worktree branch is rebased onto the main branch and conflicts occur
- **THEN** the skill reads the conflict markers, analyzes the conflicting files, resolves conflicts by keeping the worktree changes, and continues the rebase with `git rebase --continue`

#### Scenario: Rebase with unresolvable conflicts
- **WHEN** the worktree branch is rebased onto the main branch and conflicts cannot be automatically resolved
- **THEN** the skill aborts the rebase with `git rebase --abort`, reports the conflicting files to the user, and pauses for manual intervention

### Requirement: Merge to main branch
After successful rebase, the skill SHALL switch to the main branch directory and execute `git merge <worktree-branch-name>` to integrate the worktree changes into the main branch.

#### Scenario: Fast-forward merge
- **WHEN** the worktree branch has been rebased and is ahead of the main branch
- **THEN** the skill switches to the main branch and merges using fast-forward

#### Scenario: Merge with conflicts
- **WHEN** merging the worktree branch into main produces conflicts
- **THEN** the skill resolves conflicts favoring the worktree changes and completes the merge

### Requirement: Merge verification
After merging, the skill SHALL verify that the merge was successful by checking that the main branch HEAD now includes all commits from the worktree branch.

#### Scenario: Successful merge verification
- **WHEN** merge completes and `git log <main-branch>..<worktree-branch>` returns no commits
- **THEN** the skill confirms all worktree changes are in the main branch and proceeds to exit

#### Scenario: Merge verification failure
- **WHEN** merge completes but some worktree commits are missing from main
- **THEN** the skill reports the issue and does NOT proceed to exit the worktree
