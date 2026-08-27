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

### Requirement: Parallel apply uses one confirmed target
`parall-new-worktree-apply` SHALL use one confirmed target worktree and maintain an `EXPECTED_TARGET_HEAD` advanced only by this controller's verified serial merges. Each Batch SHALL verify target worktree identity and equality with that expected snapshot, freeze `BATCH_TARGET_HEAD`, validate every scheduled proposal's artifact manifest against that commit, and create canonical child worktrees from the exact hash. Each successful child SHALL pass the same post-rebase frozen-source merge protocol and `CLEANUP_READY` gate as the single return workflow. Each child SHALL independently classify ordinary unchecked tasks and exact `[post-merge-verification]` tasks; the Worker and controller MUST NOT execute or modify deferred tasks. A child with only deferred tasks MAY be cleaned and advance `EXPECTED_TARGET_HEAD` and dependent Waves after all structural delivery gates pass, while remaining incomplete and non-archivable. The controller MUST NOT checkout/switch or auto-commit an existing target worktree.

#### Scenario: Multiple changes run against one target
- **WHEN** multiple changes are discovered and the user confirms `develop`
- **THEN** every child in one Batch starts from the same exact `BATCH_TARGET_HEAD` and every successful child is serially integrated as a frozen post-rebase commit

#### Scenario: Target contains pending changes
- **WHEN** the confirmed target worktree is dirty
- **THEN** parallel execution stops without auto-committing the target or spawning a Worker

#### Scenario: Later Batch follows a verified controller merge
- **WHEN** the controller successfully merges and verifies an earlier child
- **THEN** it updates `EXPECTED_TARGET_HEAD` to the verified target HEAD and may freeze that exact value for the next Batch

#### Scenario: Target advances outside the controller
- **WHEN** target ref or target worktree HEAD differs from `EXPECTED_TARGET_HEAD` for a reason not recorded as this controller's verified merge
- **THEN** the next Batch and serial merge stop without rebasing against, accepting, or retrying on the new target

#### Scenario: Later Wave depends on an earlier Wave
- **WHEN** Wave 2 depends on a change successfully merged and verified in Wave 1
- **THEN** Wave 2 artifact validation and child creation use the post-Wave-1 `EXPECTED_TARGET_HEAD`

#### Scenario: User cancels the batch plan
- **WHEN** the user declines after reviewing manifests, canonical identities, waves, batches, target snapshot, planned merges, verification, and cleanup
- **THEN** the workflow creates no worktree, spawns no implementation agent, invokes no apply, and makes no commit

#### Scenario: Only one change is discovered
- **WHEN** discovery produces exactly one executable change
- **THEN** the workflow still creates a canonical isolated worktree from a frozen hash and uses the full serial merge and cleanup state machine

#### Scenario: Worker source drifts after rebase
- **WHEN** a Worker changes its worktree HEAD, branch ref, mapping, or clean state after `POST_REBASE_SOURCE_HEAD` is frozen
- **THEN** the controller does not merge the moving ref and does not clean up that child

#### Scenario: Parallel child has ordinary incomplete work
- **WHEN** a child has any unchecked task without the exact `[post-merge-verification]` tag
- **THEN** its `TASK_CLEANUP_POLICY_PASSED=false`, cleanup is blocked, and dependent Waves do not treat it as delivered

#### Scenario: Parallel child has only deferred verification
- **WHEN** every unchecked child task has the exact `[post-merge-verification]` tag and its merge and structural verification gates pass
- **THEN** the controller leaves those tasks unchecked for the user, reports the child incomplete and non-archivable, may clean its source, advances `EXPECTED_TARGET_HEAD`, and may schedule dependent Waves

#### Scenario: One child fails cleanup
- **WHEN** a child merge succeeds but any post-merge or cleanup gate fails
- **THEN** that child worktree and branch are preserved, the failure is reported with exact hashes, and no forced deletion or automatic merge retry occurs
