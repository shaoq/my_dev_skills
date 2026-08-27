# worktree-targeting Specification

## Purpose
TBD - created by archiving change standardize-worktree-targeting. Update Purpose after archive.
## Requirements
### Requirement: Uniform target option
The three worktree skills SHALL use `--target <target-branch>` as their only explicit target branch option. `new-worktree-apply` MUST reject the legacy `--branch` option before any Git write and display the equivalent `--target` invocation.

#### Scenario: Create worktree with explicit target
- **WHEN** the user invokes `/new-worktree-apply add-user-auth --target develop`
- **THEN** the skill records `add-user-auth` as the proposal and `develop` as the explicit target

#### Scenario: Return worktree with explicit target
- **WHEN** the user invokes `/merge-worktree-return add-user-auth --target develop`
- **THEN** the skill records `add-user-auth` as the optional proposal and `develop` as the explicit target

#### Scenario: Parallel apply with explicit target
- **WHEN** the user invokes `/parall-new-worktree-apply --target develop`
- **THEN** the skill records `develop` as the target used for every discovered change

#### Scenario: Legacy branch option is used
- **WHEN** the user invokes `new-worktree-apply` with `--branch develop`
- **THEN** the skill performs no Git write and displays a migration command using `--target develop`

#### Scenario: Target arguments are invalid
- **WHEN** an invocation has a missing target value, duplicate target options, an unknown option, or invalid positional arguments for that skill
- **THEN** the skill reports an argument error and performs no Git write operation

### Requirement: Shared deterministic target selection
Each worktree skill SHALL select `TARGET_BRANCH` in this order: explicit `--target`, the local branch currently checked out in the primary worktree, the existing local branch named by `origin/HEAD`, then the first existing local branch among `main`, `master`, and `trunk`. Each skill SHALL record and display the winning source. An invalid explicit target MUST fail without falling back. As the only exception to automatic selection, Issue-authorized autonomous `new-worktree-apply` MUST require an explicit `--target` and MUST NOT consult fallback candidates.

#### Scenario: Explicit target wins
- **WHEN** the user supplies an existing local branch through `--target`
- **THEN** the skill selects it regardless of other automatic candidates

#### Scenario: Primary worktree branch is the default
- **WHEN** no explicit target is supplied and the primary worktree has a valid local branch checked out
- **THEN** the skill selects that branch before consulting `origin/HEAD` or conventional names

#### Scenario: Origin default is the next fallback
- **WHEN** the primary worktree branch is unusable and `origin/HEAD` names an existing local branch
- **THEN** the skill selects the local branch named by `origin/HEAD`

#### Scenario: Conventional fallback is required
- **WHEN** neither the primary worktree nor `origin/HEAD` yields a usable local target
- **THEN** the skill selects the first existing local branch in the order `main`, `master`, `trunk`

#### Scenario: Explicit target does not exist locally
- **WHEN** `--target` names a branch absent from `refs/heads/`
- **THEN** the skill stops without fetching, creating a branch, or selecting a fallback

#### Scenario: Autonomous apply omits target
- **WHEN** `new-worktree-apply` is invoked with `--authorized-by-issue` but without `--target`
- **THEN** it stops before target fallback selection and performs no Git write

#### Scenario: No target can be selected
- **WHEN** every automatic candidate is unusable
- **THEN** the skill asks the user to provide `--target` and performs no Git write

### Requirement: Shared worktree topology preflight
Each worktree skill SHALL derive repository root, primary worktree, invocation worktree, branch-to-worktree registration, and applicable target/source worktrees from `git worktree list --porcelain` plus exact Git ref checks. The selected `TARGET_BRANCH` MUST already be held by one registered `TARGET_WORKTREE_DIR`; the skills MUST NOT checkout or switch the primary worktree or any other existing worktree to make a target available. Target status and identity checks MUST address the same confirmed `TARGET_WORKTREE_DIR`, and target auto-commit is prohibited.

#### Scenario: Target is checked out in another worktree
- **WHEN** the selected target is already checked out outside the invocation worktree
- **THEN** the skill records that exact path as `TARGET_WORKTREE_DIR`, performs only preflight reads there, and does not checkout, switch, stage, or auto-commit that worktree

#### Scenario: Target is not checked out
- **WHEN** the selected target local ref exists but no registered worktree holds it
- **THEN** the skill stops before confirmation and asks the user to prepare a target worktree manually

#### Scenario: Target worktree is dirty
- **WHEN** the registered target worktree has staged, unstaged, untracked, conflict, or unreadable status
- **THEN** the workflow stops without auto-committing, stashing, resetting, or switching it

#### Scenario: Target registration changes
- **WHEN** the confirmed target path, registered branch, HEAD, or ref changes before a write or merge
- **THEN** the previous confirmation or operation snapshot is invalidated and the workflow fails closed

#### Scenario: Required branch is detached
- **WHEN** a workflow requires a named source or target but the relevant worktree is detached
- **THEN** the skill reports detached HEAD as unsupported and performs no Git write

#### Scenario: Persistent target context cannot be established
- **WHEN** a merge or cleanup requires the controller to be in `TARGET_WORKTREE_DIR` but real CWD, top-level path, current branch, HEAD, and target ref cannot all be verified
- **THEN** the workflow stops and does not treat a one-off `git -C` command as a persistent context switch

### Requirement: Mandatory preflight confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `merge-worktree-return`, `parall-new-worktree-apply`, and default-mode `new-worktree-apply` MUST obtain an explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. Only `new-worktree-apply` invoked with a fully verified Issue authorization envelope MAY replace the interactive response with an immutable autonomous authorization snapshot.

#### Scenario: User confirms
- **WHEN** the complete preflight summary is displayed and the user explicitly continues
- **THEN** the skill proceeds to snapshot revalidation

#### Scenario: User rejects or cancels
- **WHEN** the user declines or cancels the displayed plan
- **THEN** the skill stops with no Git state changes and without invoking apply

#### Scenario: Response is missing or ambiguous
- **WHEN** the environment cannot collect a clear affirmative response
- **THEN** the skill pauses for explicit user input and performs no Git write

#### Scenario: No interaction tool is available
- **WHEN** no platform interaction tool is available
- **THEN** the skill asks in its response, ends the current execution, and waits for the next user message

#### Scenario: Proposal or change risks exist
- **WHEN** preflight finds incomplete OpenSpec tasks, pending target worktree changes, or a required checkout
- **THEN** the confirmation summary lists those risks before asking whether to continue

### Requirement: Confirmation snapshot revalidation
After interactive confirmation or autonomous Issue authorization and before the first write, each skill SHALL revalidate the parsed arguments, authorization mode and evidence, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, artifact manifest, and displayed warnings. Any material change MUST invalidate the prior execution snapshot.

#### Scenario: Snapshot remains stable
- **WHEN** revalidation matches every material fact in the confirmed summary
- **THEN** the skill may begin the planned write operations

#### Scenario: Snapshot changed while waiting
- **WHEN** revalidation finds a changed target, HEAD, worktree path, status, checkout requirement, or warning
- **THEN** the skill displays an updated summary and requests a new confirmation before writing

#### Scenario: Autonomous snapshot changes before writing
- **WHEN** autonomous-mode revalidation differs from the authorized snapshot in any material field
- **THEN** the skill performs no write, reports the drift, and requires a newly initiated authorization rather than automatically accepting the new state or switching modes

### Requirement: New worktree starts from the confirmed target
`new-worktree-apply` SHALL freeze `TARGET_HEAD` before interactive confirmation or autonomous authorization, bind a complete verified artifact manifest to that snapshot, and create the canonical source branch/worktree with `TARGET_HEAD` as an explicit commit-hash start point. It MUST NOT refresh the baseline by auto-committing target changes or pass `TARGET_BRANCH` as the actual creation start point. Before OpenSpec apply it MUST verify the registered path, current branch, source branch ref, and worktree HEAD exactly match the expected canonical identity and authorized frozen hash.

#### Scenario: Worktree is created from an explicit commit hash
- **WHEN** preflight and snapshot revalidation succeed for proposal `add-user-auth`
- **THEN** the workflow runs the equivalent of `git worktree add <repo>/.claude/worktrees/add-user-auth -b worktree-add-user-auth <TARGET_HEAD>`

#### Scenario: Target ref advances after interactive confirmation
- **WHEN** `TARGET_BRANCH` no longer resolves to the confirmed `TARGET_HEAD` before creation in interactive mode
- **THEN** the workflow invalidates confirmation and creates no branch or worktree

#### Scenario: Target ref advances after autonomous authorization
- **WHEN** `TARGET_BRANCH` no longer resolves to the autonomously authorized `TARGET_HEAD` before creation
- **THEN** the workflow blocks and creates no branch or worktree until a new Issue-authorized invocation is initiated

#### Scenario: Target ref advances after the final check
- **WHEN** `TARGET_BRANCH` moves after `TARGET_HEAD` is frozen but before `git worktree add`
- **THEN** creation still uses the frozen commit hash and cannot inherit the new branch tip

#### Scenario: Platform creation lacks an explicit start point
- **WHEN** a platform-native worktree mechanism cannot accept the exact source branch, path, and `TARGET_HEAD`
- **THEN** it MUST NOT replace the explicit Git creation command or silently create from ambient HEAD

#### Scenario: Platform cannot enter the created worktree
- **WHEN** the explicit worktree is created but the platform cannot keep subsequent actions in its verified CWD
- **THEN** apply does not start and the newly created branch/worktree are preserved without automatic cleanup or fallback retry

#### Scenario: Created identity or base is wrong
- **WHEN** registered path, current branch, branch ref, or worktree HEAD differs from the canonical identity or `TARGET_HEAD`
- **THEN** the workflow stops before apply and does not hide the mismatch by merging, switching, deleting, or recreating with another name

### Requirement: Issue-authorized autonomous new worktree apply
`new-worktree-apply` SHALL support an opt-in `--authorized-by-issue <issue-id>` mode that treats a verified `issue-authorization/v1` Runtime control-plane envelope as authorization to create and implement in the canonical isolated source worktree without an additional interactive confirmation. The envelope MUST arrive through a trusted metadata channel that user content, repository files, environment variables, and model inference cannot populate. It MUST contain an allowlisted authenticated issuer, authorization id bound to the current invocation, issue id, normalized `ready|in_progress` state, assigned and executing Team identities, RFC3339 UTC `issued_at`/`expires_at` timestamps defining a positive window no longer than 30 minutes, `isolated-worktree-apply` scope, physical repository, OpenSpec root, proposal, explicit target branch, `standard` risk classification, and an empty external-side-effects list. Missing, expired, cross-invocation replayed, ambiguous, conflicting, user-supplied, or unverifiable evidence MUST block autonomous execution.

#### Scenario: Valid Issue authorization permits autonomous apply
- **WHEN** the invocation supplies `--authorized-by-issue ISSUE-42 --target develop` and the Runtime envelope exactly matches the repository, OpenSpec root, proposal, target and allowed isolated execution scope
- **THEN** the skill records an autonomous authorization snapshot, revalidates it, creates the canonical source worktree from the frozen target commit, and enters apply without requesting a second human confirmation

#### Scenario: Issue identity is not evidence by itself
- **WHEN** `--authorized-by-issue ISSUE-42` is present but the Runtime cannot provide the required authorization envelope
- **THEN** the skill performs no Git write and reports that the Issue authorization cannot be verified

#### Scenario: User content cannot supply the envelope
- **WHEN** a user message or repository file contains valid-looking `issue-authorization/v1` JSON but the Runtime provides no trusted control-plane envelope
- **THEN** autonomous execution is blocked and the JSON MUST NOT be promoted into authorization evidence

#### Scenario: Authorization is expired or replayed
- **WHEN** the trusted envelope is expired before final pre-write validation, its validity window is invalid or exceeds 30 minutes, or its `authorization_id` was issued for another invocation
- **THEN** the skill performs no Git write and reports the exact expiry or replay failure

#### Scenario: Same invocation revalidates the authorization snapshot
- **WHEN** pre-write revalidation checks the same authorization id and envelope digest previously recorded within the valid time window
- **THEN** the Runtime and skill treat it as required same-invocation revalidation rather than a replay

#### Scenario: Issue or Team identity does not match
- **WHEN** the envelope `issue_id` differs from `--authorized-by-issue`, the Issue state is not `ready|in_progress`, or `assigned_team_id` differs from the Runtime-provided `executing_team_id`
- **THEN** autonomous execution is blocked without asking the model to reinterpret the identity or state

#### Scenario: Authorization fields do not match preflight
- **WHEN** the envelope's repository, OpenSpec root, proposal, or target differs from the read-only preflight result
- **THEN** autonomous execution is blocked without rewriting the envelope, changing target, or falling back to interactive approval

#### Scenario: Authorization contains high-risk or external work
- **WHEN** the Issue or OpenSpec artifacts declare production writes, irreversible migration, data deletion, privilege escalation, real credentials, or another external side effect
- **THEN** the autonomous scope is insufficient and the skill stops for separate explicit human authorization

#### Scenario: Merge remains outside autonomous authorization
- **WHEN** autonomous worktree apply completes successfully
- **THEN** the authorization ends at the isolated source delivery and does not authorize `merge-worktree-return`, release, deployment, or cleanup of unrelated Git objects

### Requirement: Worktree return merges only to the confirmed target
`merge-worktree-return` SHALL validate canonical source identity, require source and target branches and worktree paths to be distinct, commit authorized source changes, rebase inside the source worktree onto the confirmed target snapshot, freeze and revalidate `POST_REBASE_SOURCE_HEAD`, enter and verify the confirmed clean target worktree, and merge exactly the frozen commit. It SHALL preserve the source until the complete `CLEANUP_READY` gate passes. An optional proposal argument MUST equal the proposal derived from exactly one `worktree-` prefix removal.

#### Scenario: Source and target resolve to the same identity
- **WHEN** the selected target branch equals the canonical source branch or `TARGET_WORKTREE_DIR` equals `SOURCE_WORKTREE_DIR`
- **THEN** return stops before confirmation and performs no Git write, merge, or cleanup

#### Scenario: Return succeeds to a non-main target
- **WHEN** the user confirms `develop`, rebase and exact-hash merge succeed, post-merge verification passes, and every cleanup condition remains true
- **THEN** the canonical source is safely removed only after `develop` contains the exact `POST_REBASE_SOURCE_HEAD`

#### Scenario: Target worktree is dirty
- **WHEN** the return workflow finds uncommitted or unreadable state in the target worktree
- **THEN** it stops without merging into, staging, committing, stashing, resetting, or switching that worktree

#### Scenario: Proposal tasks are incomplete
- **WHEN** the proposal check finds incomplete tasks
- **THEN** the preflight lists them and return MUST NOT declare post-merge verification passed until the applicable completion policy is explicitly satisfied

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
`parall-new-worktree-apply` SHALL use one confirmed target worktree and maintain an `EXPECTED_TARGET_HEAD` advanced only by this controller's verified serial merges. Each Batch SHALL verify target worktree identity and equality with that expected snapshot, freeze `BATCH_TARGET_HEAD`, validate every scheduled proposal's artifact manifest against that commit, and create canonical child worktrees from the exact hash. Each successful child SHALL pass the same post-rebase frozen-source merge protocol and `CLEANUP_READY` gate as the single return workflow. The controller MUST NOT checkout/switch or auto-commit an existing target worktree.

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

#### Scenario: One child fails cleanup
- **WHEN** a child merge succeeds but any post-merge or cleanup gate fails
- **THEN** that child worktree and branch are preserved, the failure is reported with exact hashes, and no forced deletion or automatic merge retry occurs

### Requirement: Target-aware reporting and cleanup
All three skills SHALL report confirmed target branch/worktree, immutable target and source snapshots, canonical proposal/branch/path mapping, artifact manifest result, merge result, every cleanup gate, and preserved recovery objects. Cleanup MUST use ordinary explicit Git commands from verified target CWD only after the applicable complete gate succeeds; platform convenience tools MUST NOT weaken or obscure these conditions.

#### Scenario: Successful creation report
- **WHEN** a canonical source worktree is created and verified from a frozen hash
- **THEN** the report identifies proposal, source branch, source path, target branch/worktree, `TARGET_HEAD`, and artifact manifest result

#### Scenario: Successful return report
- **WHEN** merge, post-merge verification, ordinary worktree removal, and safe branch deletion all succeed
- **THEN** the report includes `POST_REBASE_SOURCE_HEAD`, `POST_MERGE_TARGET_HEAD`, and a true result for every cleanup gate

#### Scenario: Verification blocks cleanup
- **WHEN** any target containment, CWD, mapping, clean-state, ref/HEAD, source-only commit, delivery commit, or post-merge check fails
- **THEN** the report names the failed or unknown gate and confirms which exact source worktree and branch were preserved

#### Scenario: Cross-platform ordinary cleanup
- **WHEN** cleanup is ready on any supported platform
- **THEN** the workflow attempts only ordinary `git worktree remove <exact-source-path>` and safe `git branch -d -- <exact-source-branch>` without force or opaque destructive fallback

### Requirement: Canonical proposal worktree identity
The worktree lifecycle SHALL define an exact reversible identity for every proposal `P`: proposal name `P`, local source branch `worktree-P`, and source path `<REPO_ROOT>/.claude/worktrees/P`. Creation MUST reject any existing branch, filesystem path, or registered worktree collision and MUST NOT reuse an existing object, infer a proposal approximately, or append a conflict suffix. Return flows MUST derive a proposal only by removing exactly one leading `worktree-` prefix from the current source branch and MUST revalidate the complete identity before rebase, merge, or cleanup.

#### Scenario: Canonical identity is created
- **WHEN** proposal `add-search-index` has no existing source branch, source path, or registered worktree collision
- **THEN** creation uses branch `worktree-add-search-index` and path `.claude/worktrees/add-search-index`

#### Scenario: Existing source branch blocks creation
- **WHEN** `refs/heads/worktree-add-search-index` already exists
- **THEN** creation stops without reusing, deleting, renaming, or appending a suffix to that branch

#### Scenario: Existing source path blocks creation
- **WHEN** `.claude/worktrees/add-search-index` already exists or is already registered to any worktree
- **THEN** creation stops without taking ownership of, deleting, or selecting a different path

#### Scenario: Return derives proposal from one exact prefix
- **WHEN** the current source branch is `worktree-add-search-index`
- **THEN** return derives `add-search-index` by removing exactly one leading `worktree-` prefix and verifies the expected proposal directory and exact source path

#### Scenario: Return receives an explicit mismatched proposal
- **WHEN** the current branch derives `add-search-index` but the command argument names another proposal
- **THEN** return stops before any Git write and preserves the source worktree and branch

#### Scenario: Legacy unprefixed branch is encountered
- **WHEN** return runs from branch `add-search-index` or another branch without one exact leading `worktree-` prefix
- **THEN** it reports a manual migration requirement and MUST NOT infer, merge, rename, or clean up that branch automatically

### Requirement: OpenSpec artifact manifest is committed and immutable
Before creating any source worktree, the workflow SHALL build an `ARTIFACT_MANIFEST` for each proposal containing `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`, and the recursively enumerated complete delta spec file set. A parallel workflow SHALL also include every `dependencies.yaml` it reads; absence is valid only when both the confirmed workspace and frozen target commit omit the file and the execution plan records no dependencies. The workflow MUST prove that the path set exists in the frozen target commit and is byte-for-byte identical to the user-confirmed content. Missing, added, deleted, ignored, untracked, renamed, unreadable, or content-different artifacts MUST block creation.

#### Scenario: All artifacts match the frozen target
- **WHEN** both the confirmed workspace and `TARGET_HEAD` contain the same required artifact paths with identical bytes and at least one recursive delta `spec.md`
- **THEN** the workflow records the manifest and its stable digest in the confirmation snapshot

#### Scenario: Artifact exists only in the workspace
- **WHEN** a required artifact is untracked, ignored, newly added, or otherwise absent from `TARGET_HEAD`
- **THEN** creation stops before `git worktree add` and reports the exact path

#### Scenario: Artifact was deleted from the workspace
- **WHEN** `TARGET_HEAD` contains a required artifact that is absent from the confirmed workspace path set
- **THEN** creation stops before `git worktree add`

#### Scenario: Artifact content differs
- **WHEN** the workspace and `TARGET_HEAD` contain the same artifact path but their bytes differ
- **THEN** creation stops and identifies the mismatched path without auto-committing either version

#### Scenario: Nested delta specs are present
- **WHEN** a proposal stores specs under `specs/<capability>/spec.md` or deeper directories
- **THEN** recursive manifest enumeration includes every file instead of using a one-level `specs/*.md` glob

#### Scenario: Parallel dependency file differs
- **WHEN** the parallel execution plan reads `dependencies.yaml` but that file is missing from `TARGET_HEAD` or differs from the confirmed content
- **THEN** the proposal is not scheduled and no child worktree is created for it

#### Scenario: Artifact snapshot changes after confirmation
- **WHEN** any manifest path, content, digest, or `TARGET_HEAD` changes while awaiting confirmation
- **THEN** the prior confirmation is invalidated and no Git write occurs until a new summary is confirmed

### Requirement: Post-rebase source snapshot is frozen before merge
After a successful source rebase, the workflow SHALL record `POST_REBASE_SOURCE_HEAD` in the source worktree. Immediately before merge it MUST revalidate the exact source worktree registration, canonical branch, real CWD, source worktree HEAD, source branch ref, clean status, non-empty delivery commit set, target branch ref, target worktree HEAD, and target clean status. Merge MUST name the frozen `POST_REBASE_SOURCE_HEAD` commit rather than the mutable source branch ref.

#### Scenario: Source remains stable after rebase
- **WHEN** source HEAD and source branch ref both equal `POST_REBASE_SOURCE_HEAD`, source is clean, canonical mapping is intact, and target matches its expected snapshot
- **THEN** the target worktree may merge the exact `POST_REBASE_SOURCE_HEAD`

#### Scenario: Worker commits after rebase
- **WHEN** the source branch ref or source worktree HEAD advances after `POST_REBASE_SOURCE_HEAD` is recorded
- **THEN** the workflow stops before merge or, if the frozen commit was already merged, marks cleanup not ready and preserves the source

#### Scenario: Source worktree registration changes
- **WHEN** the source path is no longer registered or is registered with a different branch or HEAD
- **THEN** merge and cleanup stop without trying to reconstruct or reuse the source

#### Scenario: Source is dirty after rebase
- **WHEN** the source worktree has staged, unstaged, untracked, or conflict state after rebase
- **THEN** merge is blocked and the source worktree is preserved

#### Scenario: No explicit delivery commits exist
- **WHEN** the source contains no non-empty source-only delivery commit set relative to the confirmed target baseline
- **THEN** merge and cleanup are blocked instead of treating an empty worktree branch as delivered

#### Scenario: Target drifts before merge
- **WHEN** target branch ref or target worktree HEAD differs from the expected pre-merge target snapshot
- **THEN** merge stops and MUST NOT silently rebase again, switch branches, or retry against the new target

### Requirement: Cleanup requires complete delivery evidence
The workflow SHALL compute `CLEANUP_READY` as the conjunction of: real controller CWD is the confirmed target worktree; source identity mapping is exact; source is clean; source has explicit delivery commits; source worktree HEAD and source branch ref equal `POST_REBASE_SOURCE_HEAD`; merge succeeded exactly once; target branch ref equals target worktree HEAD; target contains the exact `POST_REBASE_SOURCE_HEAD`; no commits remain reachable from the live source ref but not the target; and all declared post-merge verification passes. Every condition MUST be produced by an explicit successful check. A false, unknown, unparsable, or failed condition MUST preserve the source worktree and branch.

#### Scenario: All cleanup conditions pass
- **WHEN** every `CLEANUP_READY` condition is explicitly true immediately before deletion
- **THEN** the workflow may run ordinary `git worktree remove <exact-source-path>` followed by safe `git branch -d -- <exact-source-branch>` after repeating containment

#### Scenario: Controller has only left the source directory
- **WHEN** the controller is outside the source worktree but its real CWD is not the confirmed target worktree
- **THEN** cleanup is not ready and neither source worktree nor branch is removed

#### Scenario: Frozen source commit is contained but live source advanced
- **WHEN** target contains `POST_REBASE_SOURCE_HEAD` but the live source ref contains additional target-external commits
- **THEN** cleanup is not ready and the advanced source worktree and branch are preserved

#### Scenario: Target ref and target worktree HEAD disagree
- **WHEN** `refs/heads/TARGET_BRANCH` differs from the target worktree HEAD
- **THEN** cleanup is not ready even if a previous containment check succeeded

#### Scenario: Post-merge verification fails
- **WHEN** OpenSpec checks, artifact checks, `git diff --check`, or any declared project validation command fails or cannot run
- **THEN** the completed merge is not automatically reset or reverted, while the source worktree and branch are preserved for recovery

#### Scenario: Ordinary worktree removal fails
- **WHEN** `git worktree remove <exact-source-path>` fails because of a Windows path lock, active process, dirty state, platform lock, or any other reason
- **THEN** the workflow reports the failure, leaves the source branch intact, and MUST NOT retry with force

#### Scenario: Safe branch deletion fails
- **WHEN** ordinary worktree removal succeeds but `git branch -d -- <exact-source-branch>` refuses deletion
- **THEN** the workflow preserves the branch and MUST NOT escalate to forced ref deletion

### Requirement: Destructive recovery and merge retry are prohibited
Worktree lifecycle instructions, commands, guardrails, error messages, and recovery guidance MUST NOT use or recommend `git worktree remove --force`, `git branch -D`, `git update-ref -d`, automatic reset/revert of a completed merge, or automatic retry of a failed or unverified merge. An unfinished rebase or uncommitted merge conflict MAY be safely aborted before merge success is recorded.

#### Scenario: Cleanup validation fails
- **WHEN** any cleanup prerequisite fails
- **THEN** the workflow reports the failed gate and exact recovery context without issuing or recommending a forced cleanup command

#### Scenario: Completed merge fails later verification
- **WHEN** merge succeeds but a post-merge verification later fails
- **THEN** the workflow preserves the completed target state and source recovery state without automatic reset, revert, or second merge attempt

#### Scenario: Rebase is unresolved before merge
- **WHEN** a rebase cannot be resolved and no successful merge has occurred
- **THEN** the workflow may abort that unfinished rebase and preserves the source worktree for manual recovery

### Requirement: New worktree apply selects an explicit OpenSpec project root
`new-worktree-apply` SHALL accept at most one optional
`--openspec-root <repo-relative-directory>` in addition to its proposal and optional
`--target`. The value SHALL identify the Git-worktree-relative directory that directly
contains `openspec/`; omission SHALL be equivalent to `--openspec-root .`. The workflow
MUST validate the lexical and physical path, bind the normalized root and complete
repository-relative change prefix to confirmation, build the immutable artifact manifest
with that prefix, and run OpenSpec status/apply from the corresponding project directory in
the invocation and source worktrees. It MUST NOT discover, guess, or fall back to another
OpenSpec project.

#### Scenario: Existing root-level invocation remains compatible
- **WHEN** the user invokes `new-worktree-apply add-user-auth` and the proposal exists at `openspec/changes/add-user-auth`
- **THEN** the workflow records `OPENSPEC_ROOT=.`, uses `openspec/changes/add-user-auth` without a `./` prefix, and preserves the existing root-project behavior

#### Scenario: Explicit dot matches the default
- **WHEN** the same repository and proposal are invoked with `--openspec-root .`
- **THEN** the normalized project directory, change prefix, artifact manifest paths, digest inputs, and OpenSpec working directory are identical to the omitted-option invocation

#### Scenario: Nested OpenSpec project is selected
- **WHEN** the user invokes `new-worktree-apply add-user-auth --openspec-root twin-rag` and `twin-rag/openspec/changes/add-user-auth` exists
- **THEN** the workflow uses `twin-rag` as the OpenSpec CLI working directory and prefixes every manifest path with `twin-rag/openspec/changes/add-user-auth`

#### Scenario: OpenSpec root arguments are invalid
- **WHEN** `--openspec-root` is repeated, lacks a value, or is combined with otherwise invalid positional or unknown options
- **THEN** the workflow reports an argument error and performs no Git write or OpenSpec apply action

#### Scenario: OpenSpec root path is unsafe
- **WHEN** the value is absolute, begins with `~`, contains backslashes, whitespace, control characters, empty path segments, `.` or `..` segments, leading or trailing slash, or consecutive slashes
- **THEN** the workflow rejects it before target selection and performs no Git write

#### Scenario: Physical project path escapes the invocation worktree
- **WHEN** resolving the selected directory, its `openspec` directory, or its proposal directory traverses a symbolic link outside the invocation worktree or selected project boundary
- **THEN** the workflow fails closed without searching for another project or changing any Git state

#### Scenario: Selected project or proposal does not exist
- **WHEN** the normalized project directory, its `openspec` directory, or `openspec/changes/<proposal>` cannot be read
- **THEN** the workflow stops and reports the exact selected path without trying root-level or recursively discovered alternatives

#### Scenario: Confirmation binds the selected project
- **WHEN** read-only preflight succeeds for a selected OpenSpec project
- **THEN** the confirmation summary includes whether the option was explicit, the normalized root, invocation project directory, expected source project directory, repository-relative change prefix, manifest paths, and manifest digest

#### Scenario: Selected project changes while awaiting confirmation
- **WHEN** argument parsing, normalized or physical project paths, containment results, OpenSpec status, change prefix, manifest paths, blobs, digest, or target snapshot differs during pre-write revalidation
- **THEN** the prior confirmation is invalidated and no write occurs until the updated summary is explicitly confirmed

#### Scenario: Source project context is verified before apply
- **WHEN** the canonical source worktree is created from the confirmed target hash
- **THEN** the workflow verifies the source project remains inside that worktree, rechecks OpenSpec status and every repository-relative manifest blob, and invokes apply only from the verified source project directory

#### Scenario: Source project verification fails after creation
- **WHEN** the source project directory is missing, escapes its worktree, has incomplete OpenSpec artifacts, or differs from the confirmed target manifest
- **THEN** apply does not start and the canonical source branch and worktree are preserved without cleanup, root substitution, or creation retry

#### Scenario: Task backfill uses both project and repository contexts
- **WHEN** apply completes and the workflow reconciles `tasks.md`
- **THEN** it reads tasks from the selected source OpenSpec project, stages changes from the source worktree root, and force-adds the repository-relative `<CHANGE_PREFIX>/tasks.md`
