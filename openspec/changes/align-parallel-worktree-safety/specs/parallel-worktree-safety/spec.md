## ADDED Requirements

### Requirement: Detect canonical main branch for parallel apply
`parall-new-worktree-apply` SHALL detect a canonical `MAIN_BRANCH` before executing pending changes. Detection SHALL use the priority `main` -> `master` -> `trunk`, then fall back to the remote default branch reported by `origin`.

#### Scenario: Main branch is named master
- **WHEN** the repository has `master` but not `main`
- **THEN** `parall-new-worktree-apply` records `MAIN_BRANCH=master`
- **THEN** all later rebase, checkout, merge, and verification instructions use `master`

#### Scenario: Remote default branch fallback
- **WHEN** local `main`, `master`, and `trunk` cannot be verified
- **THEN** `parall-new-worktree-apply` queries `origin` for the HEAD branch
- **THEN** it uses that value as `MAIN_BRANCH`

#### Scenario: Main branch cannot be detected
- **WHEN** no supported local branch exists and remote default branch detection fails
- **THEN** `parall-new-worktree-apply` reports that the main branch cannot be detected
- **THEN** it stops before spawning agents or merging branches

### Requirement: Verify controller CWD and branch during serial merge
`parall-new-worktree-apply` SHALL verify the main-controller working directory and current branch before and after serial merge operations. The controller MUST be in the main working tree and on `<MAIN_BRANCH>` before merging a branch.

#### Scenario: Controller is on expected main branch before merge
- **WHEN** a batch has completed and a branch is ready to merge
- **THEN** the controller verifies `pwd` is the main working tree path
- **THEN** the controller verifies `git branch --show-current` equals `<MAIN_BRANCH>`
- **THEN** it proceeds with rebase and merge

#### Scenario: Controller branch verification fails
- **WHEN** the controller is not on `<MAIN_BRANCH>` before merging
- **THEN** `parall-new-worktree-apply` attempts to switch to `<MAIN_BRANCH>` from the main working tree
- **THEN** it re-runs verification before continuing

#### Scenario: Controller CWD verification fails
- **WHEN** `pwd` does not match the expected main working tree path before merge
- **THEN** `parall-new-worktree-apply` reports a CWD verification error
- **THEN** it does not merge the branch until the controller is back in the expected main working tree

### Requirement: Use detected main branch in conflict and merge commands
`parall-new-worktree-apply` SHALL use `<MAIN_BRANCH>` instead of a hardcoded `main` in serial merge, rebase, checkout, and conflict-resolution instructions.

#### Scenario: Rebase command uses detected branch
- **WHEN** `MAIN_BRANCH=trunk` and branch `change-a` is ready to merge
- **THEN** the rebase instruction is `git rebase trunk change-a`
- **THEN** no hardcoded `git rebase main change-a` instruction is used

#### Scenario: Conflict handler references detected branch
- **WHEN** a rebase conflict occurs while `MAIN_BRANCH=master`
- **THEN** conflict-resolution instructions describe the conflict as originating from `git rebase master <branch>`
- **THEN** subsequent continue or abort guidance remains tied to that rebase operation

### Requirement: Verify merged branch has no ahead commits
After merging a successful branch into `<MAIN_BRANCH>`, `parall-new-worktree-apply` SHALL verify that the branch has no remaining commits ahead of `<MAIN_BRANCH>` by checking `git log <MAIN_BRANCH>..<branch>`. The branch SHALL be considered merged only when this output is empty.

#### Scenario: Branch fully merged
- **WHEN** branch `change-a` has been merged into `<MAIN_BRANCH>`
- **THEN** `git log <MAIN_BRANCH>..change-a` returns no commits
- **THEN** `parall-new-worktree-apply` records the branch merge as successful

#### Scenario: Branch still has unmerged commits
- **WHEN** `git log <MAIN_BRANCH>..change-a` returns one or more commits after merge
- **THEN** `parall-new-worktree-apply` reports merge verification failure for `change-a`
- **THEN** it does not mark that branch as merged

### Requirement: Document cross-platform parallel worktree safety
`README.md` SHALL describe that the parallel worktree workflow inherits the cross-platform worktree/CWD safety behavior used by the single-worktree skills.

#### Scenario: README documents platform-adaptive behavior
- **WHEN** a user reads the README entries for `new-worktree-apply`, `merge-worktree-return`, or `parall-new-worktree-apply`
- **THEN** the documentation states that Claude Code uses built-in worktree tools where available
- **THEN** the documentation states that non-Claude Code environments use git worktree fallback with explicit CWD handling
