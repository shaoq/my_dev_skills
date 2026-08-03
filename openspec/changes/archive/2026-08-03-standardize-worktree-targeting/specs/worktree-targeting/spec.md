## ADDED Requirements

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
Each worktree skill SHALL select `TARGET_BRANCH` in this order: explicit `--target`, the local branch currently checked out in the primary worktree, the existing local branch named by `origin/HEAD`, then the first existing local branch among `main`, `master`, and `trunk`. Each skill SHALL record and display the winning source. An invalid explicit target MUST fail without falling back.

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

#### Scenario: No target can be selected
- **WHEN** every automatic candidate is unusable
- **THEN** the skill asks the user to provide `--target` and performs no Git write

### Requirement: Shared worktree topology preflight
Each worktree skill SHALL derive the primary worktree, invocation worktree, checked-out branch mapping, and applicable target/source worktrees from `git worktree list --porcelain`. The skill MUST identify a safe execution directory and validate all required local refs before requesting confirmation. Target status snapshots, revalidation, staging, and commits MUST all address the same confirmed `TARGET_WORKTREE_DIR`.

#### Scenario: Target is checked out in another worktree
- **WHEN** the selected target is already checked out outside the invocation worktree
- **THEN** the skill records that worktree as `TARGET_WORKTREE_DIR` and does not attempt a duplicate checkout

#### Scenario: Target worktree contains pending changes
- **WHEN** the target is checked out outside the invocation worktree and has pending changes
- **THEN** preflight displays those target changes and any authorized Auto-commit stages and commits in `TARGET_WORKTREE_DIR`, not the invocation or primary worktree

#### Scenario: Target is not checked out
- **WHEN** the selected target is not checked out and the clean primary worktree can safely switch
- **THEN** the skill records the required post-confirmation checkout in the plan

#### Scenario: Target cannot be made available safely
- **WHEN** the target is not checked out and the primary worktree cannot safely switch
- **THEN** the skill stops before confirmation with recovery guidance

#### Scenario: Required branch is detached
- **WHEN** a workflow requires a named source or target but the relevant worktree is detached
- **THEN** the skill reports detached HEAD as unsupported and performs no Git write

#### Scenario: Persistent target context cannot be established
- **WHEN** an implicit worktree or Agent creation mechanism would inherit the invocation checkout and the controller cannot persistently enter `TARGET_WORKTREE_DIR`
- **THEN** the skill stops before creation and does not treat `git -C` as a controller context switch

### Requirement: Mandatory preflight confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. The skill MUST obtain an explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action.

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
After confirmation and before the first write, each skill SHALL revalidate the parsed arguments, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, and displayed warnings. Any material change MUST invalidate the prior confirmation.

#### Scenario: Snapshot remains stable
- **WHEN** revalidation matches every material fact in the confirmed summary
- **THEN** the skill may begin the planned write operations

#### Scenario: Snapshot changed while waiting
- **WHEN** revalidation finds a changed target, HEAD, worktree path, status, checkout requirement, or warning
- **THEN** the skill displays an updated summary and requests a new confirmation before writing

### Requirement: New worktree starts from the confirmed target
`new-worktree-apply` SHALL record `TARGET_HEAD` from `TARGET_BRANCH`, perform any confirmed target-worktree commit before refreshing that value, and create the proposal branch and worktree with the confirmed target as the explicit start point. The skill MUST verify `WORKTREE_HEAD` equals `TARGET_HEAD` before invoking OpenSpec apply.

#### Scenario: Codex creates from an explicit start point
- **WHEN** Codex CLI creates a proposal worktree after confirmation
- **THEN** it runs the equivalent of `git worktree add <path> -b <proposal> <TARGET_BRANCH>` and verifies the resulting HEAD

#### Scenario: Claude worktree creation can use target context
- **WHEN** `EnterWorktree` is available and the confirmed target checkout context is available
- **THEN** the skill first verifies the controller CWD, current branch, and current HEAD in `TARGET_WORKTREE_DIR`, then creates from that context and verifies the resulting HEAD equals `TARGET_HEAD`

#### Scenario: Claude invocation is outside the target worktree
- **WHEN** `EnterWorktree` is available but the selected target is checked out in a different worktree from the invocation
- **THEN** the skill stops during read-only preflight and asks the user to rerun from the target worktree

#### Scenario: Platform cannot guarantee the target start point
- **WHEN** the worktree creation mechanism cannot prove it will branch from `TARGET_HEAD`
- **THEN** the skill stops or safely aligns a clean primary worktree after confirmation instead of silently using another HEAD

#### Scenario: Created worktree has the wrong base
- **WHEN** `WORKTREE_HEAD` differs from the recorded `TARGET_HEAD` immediately after creation
- **THEN** the skill stops before apply and does not hide the mismatch by merging the target branch

### Requirement: Worktree return merges only to the confirmed target
`merge-worktree-return` SHALL commit the source when authorized, rebase `SOURCE_BRANCH` onto `TARGET_BRANCH`, merge it in `TARGET_WORKTREE_DIR`, and verify the target contains every source commit before removing the source worktree.

#### Scenario: Return succeeds to a non-main target
- **WHEN** the user confirms `develop` as the target and all operations succeed
- **THEN** the source is rebased and merged into `develop`, verified, and then removed

#### Scenario: Target worktree is dirty
- **WHEN** the return workflow finds uncommitted changes in the target worktree
- **THEN** it stops before confirmation and does not merge into or alter that worktree

#### Scenario: Proposal tasks are incomplete
- **WHEN** the optional proposal check finds incomplete tasks
- **THEN** the single preflight confirmation lists them and explicitly asks whether to merge despite the risk

#### Scenario: Merge verification fails
- **WHEN** any source commit remains outside `TARGET_BRANCH`
- **THEN** the skill reports the failure and MUST NOT remove the source worktree

### Requirement: Parallel apply uses one confirmed target
`parall-new-worktree-apply` SHALL use the confirmed `TARGET_BRANCH` as the destination for every serial rebase and merge. Before spawning, the controller MUST persistently enter `TARGET_WORKTREE_DIR`. Each Batch SHALL read the latest target commit as `BATCH_TARGET_HEAD`, create every child in that Batch from the same snapshot, and refresh the target baseline after merges so later Waves include dependency code during implementation. Auto-commit and apply execution MUST occur only after confirmation and revalidation.

#### Scenario: Multiple changes run against one target
- **WHEN** multiple changes are discovered and the user confirms `develop`
- **THEN** every child worktree in one Batch starts from that Batch's latest target snapshot and every successful branch is serially integrated into `develop`

#### Scenario: Auto-commit is needed
- **WHEN** the target worktree has changes that the confirmed plan says will be auto-committed
- **THEN** the skill commits them only after confirmation and refreshes the target HEAD before creating child worktrees

#### Scenario: Controller was invoked from another worktree
- **WHEN** `INVOCATION_WORKTREE_DIR` differs from `TARGET_WORKTREE_DIR`
- **THEN** the controller persistently enters and verifies `TARGET_WORKTREE_DIR` before spawning any Agent or performing serial merges

#### Scenario: Later Wave depends on an earlier Wave
- **WHEN** Wave 2 contains a change that depends on a change merged by Wave 1
- **THEN** Wave 2's Batch baseline is refreshed from the post-Wave-1 target HEAD and includes the Wave 1 implementation during apply

#### Scenario: User cancels the batch plan
- **WHEN** the user declines after reviewing waves, batches, target, and planned writes
- **THEN** the skill creates no worktree, spawns no implementation agent, invokes no apply, and makes no commit

#### Scenario: Only one change is discovered
- **WHEN** discovery produces exactly one executable change
- **THEN** the skill still implements it in an isolated worktree based on `TARGET_BRANCH` and merges it through the same verified target workflow

#### Scenario: Batch merge verification fails
- **WHEN** a branch still has commits outside `TARGET_BRANCH` after its merge
- **THEN** the skill marks that branch unmerged, preserves its worktree or recovery state, and continues only according to the documented failure policy

### Requirement: Target-aware reporting and cleanup
All three skills SHALL use `TARGET_BRANCH` terminology in frontmatter, instructions, success output, errors, verification, and guardrails. Cleanup MUST occur only after the applicable target-based verification succeeds and MUST use the available platform-safe mechanism.

#### Scenario: Successful report
- **WHEN** a create, return, or parallel workflow finishes successfully
- **THEN** its report identifies the confirmed target, selection source, affected branches, and verification result

#### Scenario: Cross-platform source cleanup
- **WHEN** a return or parallel child merge is verified and `ExitWorktree` is unavailable
- **THEN** cleanup runs `git worktree remove <source-path>` from a non-source directory without force

#### Scenario: Verification blocks cleanup
- **WHEN** target containment, CWD, branch, or other required verification fails
- **THEN** the skill does not remove the affected source worktree
