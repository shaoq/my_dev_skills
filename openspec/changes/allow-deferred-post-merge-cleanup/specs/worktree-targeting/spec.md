## MODIFIED Requirements

### Requirement: Preflight authorization and integration confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `parall-new-worktree-apply` MUST retain one explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. `merge-worktree-return` SHALL proceed after stable independent revalidation without a second confirmation when a clear return request supplies an explicit target and the canonical source is strictly clean; an inferred target or pending source changes MUST instead receive one explicit affirmative response for the complete interactive plan. Discussion, review, status, or feasibility requests MUST NOT authorize return writes. `new-worktree-apply` MUST NOT request a second confirmation after a concrete user implementation request; it proceeds only after stable final pre-write revalidation. In `--dry-run` mode it MUST stop after reporting the snapshot.

#### Scenario: Deterministic return preflight is stable
- **WHEN** a clear return request uses an explicit target, the canonical source is strictly clean, and independent final revalidation matches every material preflight fact
- **THEN** `merge-worktree-return` begins the bounded return writes without asking a second confirmation

#### Scenario: Interactive return user confirms
- **WHEN** the complete return plan shows an inferred target or exact pending-source commit plan and the user explicitly continues
- **THEN** `merge-worktree-return` proceeds to independent snapshot revalidation

#### Scenario: Parallel integration user confirms
- **WHEN** the complete parallel preflight summary is displayed and the user explicitly continues
- **THEN** `parall-new-worktree-apply` proceeds to snapshot revalidation

#### Scenario: Interactive integration user rejects or cancels
- **WHEN** the user declines or cancels a displayed interactive return or parallel plan
- **THEN** the integration skill stops with no Git state changes and without invoking apply

#### Scenario: Interactive integration response is missing or ambiguous
- **WHEN** an interactive return or parallel integration cannot collect a clear affirmative response
- **THEN** it pauses for explicit user input and performs no Git write

#### Scenario: No interaction tool is available for interactive integration
- **WHEN** no platform interaction tool is available for an interactive return or parallel apply
- **THEN** the integration skill asks in its response, ends the current execution, and waits for the next user message

#### Scenario: New worktree preflight is stable
- **WHEN** a concrete implementation request, preflight, and final revalidation complete with no blocker or drift
- **THEN** `new-worktree-apply` begins the planned source worktree writes without asking a question

#### Scenario: New worktree preflight has a blocker
- **WHEN** `new-worktree-apply` finds incomplete OpenSpec artifacts, a dirty target worktree, an occupied canonical identity, an unsafe source parent, a required checkout, or out-of-scope work
- **THEN** it stops before writing and reports the exact blocker rather than asking whether to bypass it

#### Scenario: Dry run reaches the write boundary
- **WHEN** dry-run preflight has completed successfully
- **THEN** the skill reports the snapshot and exits before final write authorization or any repository mutation

### Requirement: Pre-write snapshot revalidation
Before the first write, each worktree skill SHALL revalidate the parsed arguments, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, source-parent physical containment, artifact manifest, planned writes, and displayed warnings. Parallel apply and the interactive return path SHALL compare those facts with their interactively confirmed snapshot. The deterministic return path and `new-worktree-apply` SHALL create their immutable `PREFLIGHT_SNAPSHOT` exactly once, collect final read-only facts in a separate immutable `REVALIDATION_SNAPSHOT`, and compare the snapshots field-by-field without rerunning the freeze operation or replacing the baseline. Any material change MUST invalidate the applicable authorization.

#### Scenario: New worktree snapshot remains stable
- **WHEN** every field in the independent final revalidation snapshot matches the immutable preflight baseline
- **THEN** `new-worktree-apply` may begin the planned write operations

#### Scenario: New worktree snapshot changes before writing
- **WHEN** final revalidation finds changed arguments, target ref, HEAD, worktree path, status, source parent, manifest, planned writes, or warnings
- **THEN** it performs no write and requires a fresh preflight invocation rather than refreshing the snapshot or asking for confirmation

#### Scenario: Deterministic return snapshot remains stable
- **WHEN** every return argument, identity, ref, HEAD, clean state, task classification, verification command, and planned write matches the immutable deterministic preflight baseline
- **THEN** `merge-worktree-return` may begin the bounded return writes without another confirmation

#### Scenario: Deterministic return snapshot changes before writing
- **WHEN** final revalidation differs from any material deterministic return preflight fact
- **THEN** the workflow performs no write, requires a fresh invocation, and does not replace the baseline or enter the interactive path

#### Scenario: Confirmed integration snapshot remains stable
- **WHEN** an interactive return or parallel revalidation matches every material fact in the confirmed summary
- **THEN** the integration skill may begin its planned write operations

#### Scenario: Confirmed integration snapshot changes
- **WHEN** an interactive return or parallel revalidation differs from the interactively confirmed snapshot
- **THEN** the skill invalidates the confirmation and obtains a new confirmation before writing

### Requirement: Worktree return merges only to the confirmed target
`merge-worktree-return` SHALL validate canonical source identity, require source and target branches and worktree paths to be distinct, rebase inside the source worktree onto the authorized target snapshot, freeze and revalidate `POST_REBASE_SOURCE_HEAD`, enter and verify the authorized clean target worktree, and merge exactly the frozen commit. An optional proposal argument MUST equal the proposal derived from exactly one `worktree-` prefix removal. An optional target MAY retain the documented fallback order, but an inferred target MUST be confirmed before writes.

The workflow SHALL choose its single-return authorization path from observable facts rather than caller runtime. A clear return request with an explicit target, a strictly clean canonical source, and a complete stable preflight SHALL proceed after an independent final read-only revalidation without a second confirmation. A clear return request with an inferred target or pending source changes MUST display one complete interactive plan and receive affirmative confirmation before it commits, rebases, merges, or cleans. Discussion, review, or status requests MUST NOT authorize either path. The workflow MUST NOT require runtime/task-platform identities or generic approval flags.

The interactive path MAY commit the exact pending source plan presented to and confirmed by the user. The deterministic path MUST NOT auto-commit pending changes; source dirtiness selects the interactive path. Any pre-write drift invalidates the applicable authorization. A rebase or merge conflict in the deterministic path MUST stop without an unconfirmed resolution and preserve the canonical source for a fresh decision.

The workflow SHALL preserve the source until the complete `CLEANUP_READY` gate passes. Ordinary unchecked tasks MUST block cleanup, while unchecked task lines containing the exact `[post-merge-verification]` tag SHALL be reported as user-owned deferred work and MUST NOT block cleanup when every other gate passes. The Skill MUST NOT execute, mark, stage, or commit those deferred tasks.

#### Scenario: Explicit clean return uses the deterministic path
- **WHEN** a direct user or Team/Skill handoff clearly requests return, the target is explicitly `develop`, the canonical source is clean, and every frozen preflight and final revalidation result is stable
- **THEN** the workflow reports the complete audit plan and performs its bounded rebase, exact-hash merge, verification, and conditional cleanup without asking a second confirmation

#### Scenario: Proposal is deterministically derived
- **WHEN** the proposal argument is omitted, the current canonical branch is exactly `worktree-add-user-auth`, `--target develop` is explicit, and every deterministic-path predicate passes
- **THEN** the workflow derives `add-user-auth`, validates its exact canonical mapping, and does not require confirmation solely because the redundant proposal argument was omitted

#### Scenario: Target is inferred for a manual return
- **WHEN** a user clearly invokes the return workflow without `--target` and the workflow resolves a target through the documented fallback order
- **THEN** it reports the inferred target, `TARGET_SOURCE`, immutable target snapshot, and complete write plan and requires one affirmative confirmation before any write

#### Scenario: Manual return includes pending source changes
- **WHEN** the source contains pending changes and the user clearly requests return
- **THEN** the deterministic path is unavailable and the workflow lists every pending file and proposed source commit in one interactive plan before any stage, commit, rebase, merge, or cleanup

#### Scenario: Confirmed pending plan remains stable
- **WHEN** the user affirms an interactive pending-source plan and final revalidation proves the target, source, pending-file set, task policy, and planned writes are unchanged
- **THEN** the workflow may commit the confirmed pending source changes and continue the bounded return

#### Scenario: Request does not authorize return
- **WHEN** the request asks only for discussion, review, status, or feasibility and does not clearly ask to execute the return
- **THEN** the workflow performs no commit, rebase, merge, or cleanup even if target and worktree state could otherwise be resolved

#### Scenario: Deterministic path drifts before writes
- **WHEN** any argument, source/target identity, ref, HEAD, cleanliness, task classification, verification command, or planned write differs between the deterministic preflight and final revalidation
- **THEN** the workflow performs zero writes, reports that a fresh invocation is required, and does not refresh its baseline or request a confirmation to bypass the drift

#### Scenario: Deterministic path encounters a conflict
- **WHEN** a no-second-confirmation return encounters a rebase or merge conflict
- **THEN** the workflow does not invent or commit a conflict resolution, safely aborts the incomplete operation when possible, preserves the canonical source, and stops for a fresh decision

#### Scenario: Source and target resolve to the same identity
- **WHEN** the selected target branch equals the canonical source branch or `TARGET_WORKTREE_DIR` equals `SOURCE_WORKTREE_DIR`
- **THEN** return stops before confirmation and performs no Git write, merge, or cleanup

#### Scenario: Return succeeds to a non-main target
- **WHEN** `develop` is explicitly authorized by the deterministic path or affirmatively confirmed by the interactive path, rebase and exact-hash merge succeed, post-merge verification passes, and every cleanup condition remains true
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
