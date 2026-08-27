## MODIFIED Requirements

### Requirement: Worktree return merges only to the confirmed target
`merge-worktree-return` SHALL validate canonical source identity, require source and target branches and worktree paths to be distinct, commit authorized source changes, rebase inside the source worktree onto the confirmed target snapshot, freeze and revalidate `POST_REBASE_SOURCE_HEAD`, enter and verify the confirmed clean target worktree, and merge exactly the frozen commit. It SHALL preserve the source until the complete `CLEANUP_READY` gate passes. For this single-return workflow, ordinary unchecked tasks MUST block cleanup, while unchecked task lines containing the exact `[post-merge-verification]` tag SHALL be reported as user-owned deferred work and MUST NOT block cleanup when every other gate passes. The Skill MUST NOT execute, mark, stage, or commit those deferred tasks. An optional proposal argument MUST equal the proposal derived from exactly one `worktree-` prefix removal.

#### Scenario: Source and target resolve to the same identity
- **WHEN** the selected target branch equals the canonical source branch or `TARGET_WORKTREE_DIR` equals `SOURCE_WORKTREE_DIR`
- **THEN** return stops before confirmation and performs no Git write, merge, or cleanup

#### Scenario: Return succeeds to a non-main target
- **WHEN** the user confirms `develop`, rebase and exact-hash merge succeed, post-merge verification passes, and every cleanup condition remains true
- **THEN** the canonical source is safely removed only after `develop` contains the exact `POST_REBASE_SOURCE_HEAD`

#### Scenario: Target worktree is dirty
- **WHEN** the return workflow finds uncommitted or unreadable state in the target worktree
- **THEN** it stops without merging into, staging, committing, stashing, resetting, or switching that worktree

#### Scenario: Ordinary proposal tasks are incomplete
- **WHEN** at least one unchecked task line lacks the exact `[post-merge-verification]` tag
- **THEN** the preflight lists it, `TASK_CLEANUP_POLICY_PASSED=false`, and the source worktree and branch are preserved after any completed merge

#### Scenario: Only deferred post-merge tasks remain
- **WHEN** every unchecked task line contains the exact `[post-merge-verification]` tag and every structural merge and cleanup gate passes
- **THEN** `merge-worktree-return` lists those tasks, leaves them unchecked for the user, reports the change as incomplete and non-archivable, and may ordinarily remove the source worktree and safely delete its branch

#### Scenario: Deferred task state is unknown
- **WHEN** `tasks.md` is missing, unreadable, has zero recognized checkbox tasks, or any unchecked task cannot be classified deterministically
- **THEN** task cleanup policy is unknown and cleanup is blocked

#### Scenario: Merge verification fails
- **WHEN** target does not contain `POST_REBASE_SOURCE_HEAD`, target ref/HEAD disagree, source has additional target-external commits, or another required check fails
- **THEN** the completed target state is reported without automatic rollback and the source worktree and branch are preserved

#### Scenario: Source worktree removal succeeds
- **WHEN** every cleanup condition passes and ordinary removal of the exact canonical source path succeeds
- **THEN** the workflow repeats exact containment and may delete only the canonical local source branch with `git branch -d --`

#### Scenario: Source branch is already absent unexpectedly
- **WHEN** the canonical source branch ref is absent before the workflow performs its authorized safe deletion
- **THEN** cleanup is treated as an identity drift failure rather than an idempotent success, and no broader deletion is attempted

#### Scenario: Cleanup verification command fails
- **WHEN** CWD, worktree mapping, status, ref, HEAD, containment, source-only commit, or post-merge verification cannot be executed reliably
- **THEN** the command error is a hard failure and the workflow preserves every source object still present
