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

### Requirement: New worktree apply requires trusted explicit invocation provenance
Before `new-worktree-apply` performs repository or OpenSpec writes, the Runtime SHALL prove through an immutable `explicit-skill-invocation/v1` control-plane record that the current invocation came directly from a user-explicit skill command. The record MUST bind a Runtime identity, invocation-unique dispatch id, `user-explicit-skill-command` kind, exact `new-worktree-apply` skill identity, and exact Runtime-dispatched raw arguments. User message text, repository files, environment variables, model inference, automatic skill selection, and nested skill calls MUST NOT create or replace this provenance. Missing, ambiguous, mismatched, replayed, or unverifiable provenance MUST stop execution without writes.

#### Scenario: Claude slash command is explicitly dispatched
- **WHEN** a user directly invokes `/new-worktree-apply add-user-auth --target develop` and Claude Code supplies matching trusted slash-command dispatch provenance
- **THEN** the skill records the invocation snapshot and may continue to read-only preflight

#### Scenario: Codex skill command is explicitly dispatched
- **WHEN** a user directly invokes `$new-worktree-apply add-user-auth --target develop` and Codex supplies matching trusted skill-dispatch provenance
- **THEN** the skill records the invocation snapshot and may continue to read-only preflight

#### Scenario: Runtime cannot prove explicit dispatch
- **WHEN** a Runtime loads the skill but cannot provide trusted `user-explicit-skill-command` provenance bound to this invocation
- **THEN** the skill reports that explicit invocation cannot be verified and performs no repository or OpenSpec write

#### Scenario: Model or another skill selects the workflow
- **WHEN** the model selects `new-worktree-apply` from a natural-language task or another skill invokes it through a nested `Skill(...)` call
- **THEN** the invocation is not treated as user-explicit and the workflow stops without writing

#### Scenario: Provenance is forged in user-controlled data
- **WHEN** user text, a repository file, or an environment variable contains valid-looking `explicit-skill-invocation/v1` metadata but the Runtime dispatcher supplies no matching trusted record
- **THEN** the metadata is ignored as authorization evidence and the workflow performs no write

#### Scenario: Provenance changes before writing
- **WHEN** final revalidation observes a different dispatch id, skill identity, raw argument vector, or provenance digest from the preflight snapshot
- **THEN** the invocation stops without refreshing provenance, asking for confirmation, or performing a write

### Requirement: New worktree apply executes without repeated authorization
`new-worktree-apply` SHALL treat a Runtime-verified user-explicit invocation as authorization to create and implement in the canonical isolated source worktree. After a complete read-only preflight and a stable final pre-write revalidation, the skill SHALL proceed without requesting interactive confirmation and without requiring an Issue, Team, task-platform envelope, authorization token, or authorization flag. This authorization MUST remain limited to canonical source worktree creation, OpenSpec apply, proposal-scoped local verification, and source commit.

#### Scenario: Explicit invocation proceeds after stable preflight
- **WHEN** trusted explicit dispatch is verified for `new-worktree-apply add-user-auth --target develop` and every preflight and final revalidation check succeeds
- **THEN** the skill creates the canonical source worktree from the frozen target commit and enters apply without asking for confirmation

#### Scenario: Proposal has no Issue
- **WHEN** a local OpenSpec proposal is invoked directly without any Issue or Team context
- **THEN** the skill applies the same invocation, repository, target, artifact, and worktree safety checks and does not require task-platform metadata

#### Scenario: Legacy Issue authorization option is supplied
- **WHEN** an invocation contains `--authorized-by-issue`
- **THEN** the skill performs no write, reports the option as removed, and displays an equivalent explicit invocation without it

#### Scenario: Generic authorization option is supplied
- **WHEN** an invocation contains `--authorized`, `--yes`, or another unsupported approval flag
- **THEN** strict argument parsing rejects it before any Git or OpenSpec write because no additional authorization flag is required

#### Scenario: Merge remains outside apply scope
- **WHEN** default worktree apply completes successfully
- **THEN** the invocation does not authorize `merge-worktree-return`, release, deployment, production writes, or cleanup of unrelated Git objects

#### Scenario: Proposal requires an external side effect
- **WHEN** proposal artifacts require deployment, production mutation, irreversible migration, data deletion, privilege escalation, real credentials, or another action outside isolated source delivery
- **THEN** the skill stops before that action and reports that it requires a separate authorized workflow

### Requirement: New worktree apply supports a read-only dry run
`new-worktree-apply` SHALL accept one optional `--dry-run` flag on a Runtime-verified user-explicit invocation. Dry-run mode MUST execute the same strict argument, repository, OpenSpec root, target worktree, cleanliness, canonical identity, artifact manifest, frozen target, and planned-write preflight used by default execution, then report the resulting snapshot and stop without any write. A dry-run snapshot MUST NOT be reused as authorization or as the frozen snapshot of a later real invocation.

#### Scenario: Dry run succeeds
- **WHEN** the caller explicitly invokes `new-worktree-apply add-user-auth --target develop --dry-run`, trusted dispatch is verified, and preflight succeeds
- **THEN** the skill reports the complete plan without creating a branch or worktree and without invoking apply, stage, or commit

#### Scenario: Dry run finds a blocker
- **WHEN** dry-run preflight finds a dirty target, missing artifact, existing canonical branch/path, invalid target, or another blocker
- **THEN** it reports the blocker and preserves all repository and OpenSpec state

#### Scenario: Repository changes after dry run
- **WHEN** a successful dry run is followed by a real invocation after repository state has changed
- **THEN** the real invocation performs a new explicit-dispatch check and preflight and MUST NOT trust the prior dry-run snapshot

### Requirement: Shared deterministic target selection
Each worktree skill SHALL accept `--target <target-branch>` as its explicit target input. `new-worktree-apply` MUST require that explicit option and MUST NOT consult the primary worktree branch, `origin/HEAD`, or conventional branch names when it is omitted. `merge-worktree-return` and `parall-new-worktree-apply` SHALL continue selecting `TARGET_BRANCH` in this order when no explicit target is supplied: the local branch currently checked out in the primary worktree, the existing local branch named by `origin/HEAD`, then the first existing local branch among `main`, `master`, and `trunk`. Every skill SHALL record and display the winning source, and an invalid explicit target MUST fail without fallback.

#### Scenario: Explicit target wins
- **WHEN** the user supplies an existing local branch through `--target`
- **THEN** the skill selects it regardless of other automatic candidates

#### Scenario: New worktree apply omits target
- **WHEN** `new-worktree-apply` is invoked without `--target`
- **THEN** it stops before target fallback selection and performs no Git or OpenSpec write

#### Scenario: Integration primary worktree branch is the default
- **WHEN** merge or parallel apply has no explicit target and the primary worktree has a valid local branch checked out
- **THEN** it selects that branch before consulting `origin/HEAD` or conventional names

#### Scenario: Origin default is the next integration fallback
- **WHEN** the primary worktree branch is unusable for merge or parallel apply and `origin/HEAD` names an existing local branch
- **THEN** the integration skill selects the local branch named by `origin/HEAD`

#### Scenario: Conventional integration fallback is required
- **WHEN** neither the primary worktree nor `origin/HEAD` yields a usable target for merge or parallel apply
- **THEN** the integration skill selects the first existing local branch in the order `main`, `master`, `trunk`

#### Scenario: Explicit target does not exist locally
- **WHEN** `--target` names a branch absent from `refs/heads/`
- **THEN** the skill stops without fetching, creating a branch, or selecting a fallback

#### Scenario: No target can be selected by a skill that permits fallback
- **WHEN** every automatic candidate is unusable for merge or parallel apply
- **THEN** the skill asks the user to provide `--target` and performs no Git write

### Requirement: Shared worktree topology preflight
Each worktree skill SHALL derive repository root, primary worktree, invocation worktree, branch-to-worktree registration, and applicable target/source worktrees from `git worktree list --porcelain` plus exact Git ref checks. The selected `TARGET_BRANCH` MUST already be held by one registered `TARGET_WORKTREE_DIR`; the skills MUST NOT checkout or switch the primary worktree or any other existing worktree to make a target available. Target status and identity checks MUST address the same preflight-selected or interactively confirmed `TARGET_WORKTREE_DIR`, and target auto-commit is prohibited.

#### Scenario: Target is checked out in another worktree
- **WHEN** the selected target is already checked out outside the invocation worktree
- **THEN** the skill records that exact path as `TARGET_WORKTREE_DIR`, performs only preflight reads there, and does not checkout, switch, stage, or auto-commit that worktree

#### Scenario: Target is not checked out
- **WHEN** the selected target local ref exists but no registered worktree holds it
- **THEN** the skill stops before any write or applicable confirmation and asks the user to prepare a target worktree manually

#### Scenario: Target worktree is dirty
- **WHEN** the registered target worktree has staged, unstaged, untracked, conflict, or unreadable status
- **THEN** the workflow stops without auto-committing, stashing, resetting, or switching it

#### Scenario: Target registration changes
- **WHEN** the preflight or confirmed target path, registered branch, HEAD, or ref changes before a write or merge
- **THEN** the operation snapshot is invalidated and the workflow fails closed

#### Scenario: Required branch is detached
- **WHEN** a workflow requires a named source or target but the relevant worktree is detached
- **THEN** the skill reports detached HEAD as unsupported and performs no Git write

#### Scenario: Persistent target context cannot be established
- **WHEN** a merge or cleanup requires the controller to be in `TARGET_WORKTREE_DIR` but real CWD, top-level path, current branch, HEAD, and target ref cannot all be verified
- **THEN** the workflow stops and does not treat a one-off `git -C` command as a persistent context switch

### Requirement: Mandatory preflight confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `merge-worktree-return` and `parall-new-worktree-apply` MUST obtain an explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. `new-worktree-apply` MUST NOT request a second confirmation after trusted explicit dispatch: that invocation authorizes the limited isolated-source operation, and it proceeds only after stable final pre-write revalidation. In `--dry-run` mode it MUST stop after reporting the snapshot.

#### Scenario: Integration user confirms
- **WHEN** the complete merge or parallel preflight summary is displayed and the user explicitly continues
- **THEN** the integration skill proceeds to snapshot revalidation

#### Scenario: Integration user rejects or cancels
- **WHEN** the user declines or cancels the displayed merge or parallel plan
- **THEN** the integration skill stops with no Git state changes and without invoking apply

#### Scenario: Integration response is missing or ambiguous
- **WHEN** merge or parallel integration cannot collect a clear affirmative response
- **THEN** it pauses for explicit user input and performs no Git write

#### Scenario: No interaction tool is available for integration
- **WHEN** no platform interaction tool is available to merge or parallel apply
- **THEN** the integration skill asks in its response, ends the current execution, and waits for the next user message

#### Scenario: New worktree preflight is stable
- **WHEN** trusted explicit dispatch, preflight, and final revalidation complete with no blocker or drift
- **THEN** `new-worktree-apply` begins the planned source worktree writes without asking a question

#### Scenario: New worktree preflight has a blocker
- **WHEN** `new-worktree-apply` finds unverified dispatch provenance, incomplete OpenSpec artifacts, a dirty target worktree, an occupied canonical identity, a required checkout, or out-of-scope work
- **THEN** it stops before writing and reports the exact blocker rather than asking whether to bypass it

#### Scenario: Dry run reaches the write boundary
- **WHEN** dry-run preflight has completed successfully
- **THEN** the skill reports the snapshot and exits before final write authorization or any repository mutation

### Requirement: Confirmation snapshot revalidation
Before the first write, each worktree skill SHALL revalidate the parsed arguments, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, artifact manifest, planned writes, and displayed warnings. Merge and parallel skills SHALL compare those facts with their interactively confirmed snapshot. `new-worktree-apply` SHALL additionally revalidate the same trusted explicit dispatch id, skill identity, raw arguments, and provenance digest, then compare all material facts with the immutable preflight snapshot created in the same invocation. Any material change MUST invalidate the snapshot.

#### Scenario: New worktree snapshot remains stable
- **WHEN** explicit dispatch provenance and every preflight fact match during final revalidation
- **THEN** `new-worktree-apply` may begin the planned write operations

#### Scenario: New worktree snapshot changes before writing
- **WHEN** final revalidation finds changed provenance, arguments, target ref, HEAD, worktree path, status, manifest, planned writes, or warnings
- **THEN** it performs no write and requires a fresh user-explicit invocation rather than refreshing the snapshot or asking for confirmation

#### Scenario: Confirmed integration snapshot remains stable
- **WHEN** merge or parallel revalidation matches every material fact in the confirmed summary
- **THEN** the integration skill may begin its planned write operations

#### Scenario: Confirmed integration snapshot changes
- **WHEN** merge or parallel revalidation differs from the interactively confirmed snapshot
- **THEN** the skill invalidates the confirmation and obtains a new confirmation before writing

### Requirement: New worktree starts from the confirmed target
`new-worktree-apply` SHALL freeze the explicitly selected `TARGET_HEAD` during preflight, bind a complete verified artifact manifest to that snapshot, and create the canonical source branch/worktree with `TARGET_HEAD` as an explicit commit-hash start point after final revalidation. It MUST NOT refresh the baseline by auto-committing target changes or pass `TARGET_BRANCH` as the actual creation start point. Before OpenSpec apply it MUST verify the registered path, current branch, source branch ref, and worktree HEAD exactly match the expected canonical identity and frozen hash.

#### Scenario: Worktree is created from an explicit commit hash
- **WHEN** trusted explicit dispatch, preflight, and final revalidation succeed for proposal `add-user-auth`
- **THEN** the workflow runs the equivalent of `git worktree add <repo>/.claude/worktrees/add-user-auth -b worktree-add-user-auth <TARGET_HEAD>`

#### Scenario: Target ref advances before final revalidation
- **WHEN** `TARGET_BRANCH` no longer resolves to the frozen `TARGET_HEAD` at final revalidation
- **THEN** the workflow stops and creates no branch or worktree

#### Scenario: Target ref advances after final revalidation
- **WHEN** `TARGET_BRANCH` moves after `TARGET_HEAD` is finally revalidated but before `git worktree add`
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
All three skills SHALL report the preflight-selected or interactively confirmed target branch/worktree, immutable target and source snapshots, canonical proposal/branch/path mapping, artifact manifest result, merge result, every cleanup gate, and preserved recovery objects. `new-worktree-apply` reports the Runtime id and non-sensitive dispatch audit id without echoing private Runtime metadata. Cleanup MUST use ordinary explicit Git commands from verified target CWD only after the applicable complete gate succeeds; platform convenience tools MUST NOT weaken or obscure these conditions.

#### Scenario: Successful creation report
- **WHEN** a canonical source worktree is created and verified from a frozen hash
- **THEN** the report identifies proposal, source branch, source path, target branch/worktree, `TARGET_HEAD`, artifact manifest result, and explicit-dispatch audit source

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
Before creating any source worktree, the workflow SHALL build an `ARTIFACT_MANIFEST` for each proposal containing `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`, and the recursively enumerated complete delta spec file set. A parallel workflow SHALL also include every `dependencies.yaml` it reads; absence is valid only when both the reviewed workspace and frozen target commit omit the file and the execution plan records no dependencies. The workflow MUST prove that the path set exists in the frozen target commit and is byte-for-byte identical to the preflight or interactively confirmed content. Missing, added, deleted, ignored, untracked, renamed, unreadable, or content-different artifacts MUST block creation.

#### Scenario: All artifacts match the frozen target
- **WHEN** both the reviewed workspace and `TARGET_HEAD` contain the same required artifact paths with identical bytes and at least one recursive delta `spec.md`
- **THEN** the workflow records the manifest and its stable digest in the operation snapshot

#### Scenario: Artifact exists only in the workspace
- **WHEN** a required artifact is untracked, ignored, newly added, or otherwise absent from `TARGET_HEAD`
- **THEN** creation stops before `git worktree add` and reports the exact path

#### Scenario: Artifact was deleted from the workspace
- **WHEN** `TARGET_HEAD` contains a required artifact that is absent from the reviewed workspace path set
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

#### Scenario: Artifact snapshot changes before default execution
- **WHEN** any manifest path, content, digest, or `TARGET_HEAD` differs during final revalidation
- **THEN** execution stops with no Git write and requires a fresh user-explicit invocation

#### Scenario: Dry-run artifact snapshot is not reusable
- **WHEN** artifacts matched during dry-run but differ during a later real invocation
- **THEN** the real invocation reports its own mismatch and does not rely on the earlier snapshot

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
`new-worktree-apply` SHALL require one explicit `--target <target-branch>` and accept at most one optional `--openspec-root <repo-relative-directory>` in addition to its proposal and optional `--dry-run`. The OpenSpec-root value SHALL identify the Git-worktree-relative directory that directly contains `openspec/`; omission SHALL be equivalent to `--openspec-root .`. The workflow MUST validate the lexical and physical path, bind the normalized root and complete repository-relative change prefix to the trusted dispatch and preflight snapshots, build the immutable artifact manifest with that prefix, and run OpenSpec status/apply from the corresponding project directory in the invocation and source worktrees. It MUST NOT discover, guess, or fall back to another OpenSpec project.

#### Scenario: Existing root-level invocation remains compatible
- **WHEN** the user explicitly invokes `new-worktree-apply add-user-auth --target develop` and the proposal exists at `openspec/changes/add-user-auth`
- **THEN** the workflow records `OPENSPEC_ROOT=.`, uses `openspec/changes/add-user-auth` without a `./` prefix, and preserves the existing root-project behavior

#### Scenario: Explicit dot matches the default
- **WHEN** the same repository and proposal are invoked with `--target develop --openspec-root .`
- **THEN** the normalized project directory, change prefix, artifact manifest paths, digest inputs, and OpenSpec working directory are identical to the omitted-option invocation

#### Scenario: Nested OpenSpec project is selected
- **WHEN** the user explicitly invokes `new-worktree-apply add-user-auth --target develop --openspec-root twin-rag` and `twin-rag/openspec/changes/add-user-auth` exists
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

#### Scenario: Preflight binds the selected project
- **WHEN** read-only preflight succeeds for a selected OpenSpec project
- **THEN** the preflight snapshot includes whether the option was explicit, the normalized root, invocation project directory, expected source project directory, repository-relative change prefix, manifest paths, and manifest digest

#### Scenario: Selected project changes before writing
- **WHEN** argument parsing, normalized or physical project paths, containment results, OpenSpec status, change prefix, manifest paths, blobs, digest, or target snapshot differs during pre-write revalidation
- **THEN** the invocation performs no write and requires a fresh user-explicit invocation rather than refreshing the snapshot or asking for confirmation

#### Scenario: Source project context is verified before apply
- **WHEN** the canonical source worktree is created from the preflight target hash
- **THEN** the workflow verifies the source project remains inside that worktree, rechecks OpenSpec status and every repository-relative manifest blob, and invokes apply only from the verified source project directory

#### Scenario: Source project verification fails after creation
- **WHEN** the source project directory is missing, escapes its worktree, has incomplete OpenSpec artifacts, or differs from the preflight target manifest
- **THEN** apply does not start and the canonical source branch and worktree are preserved without cleanup, root substitution, or creation retry

#### Scenario: Task backfill uses both project and repository contexts
- **WHEN** apply completes and the workflow reconciles `tasks.md`
- **THEN** it reads tasks from the selected source OpenSpec project, stages changes from the source worktree root, and force-adds the repository-relative `<CHANGE_PREFIX>/tasks.md`
