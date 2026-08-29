## ADDED Requirements

### Requirement: New worktree apply requires Runtime-native explicit invocation gates
Before `new-worktree-apply` performs repository or OpenSpec writes, the Runtime SHALL enforce a native policy that prevents implicit model invocation of this skill. Claude SHALL load `disable-model-invocation: true`; Codex SHALL load `agents/openai.yaml` with `policy.allow_implicit_invocation: false`; another Runtime MUST provide an equivalent control-plane gate. Activation under such a gate is the trusted user-explicit invocation assertion. User message text, repository files, environment variables, model inference, automatic skill selection, and nested skill calls MUST NOT create or replace that assertion. A Runtime that cannot enforce an equivalent gate MUST stop without writes.

#### Scenario: Claude slash command is explicitly dispatched
- **WHEN** a user directly invokes `/new-worktree-apply add-user-auth --target develop` and Claude Code has enforced `disable-model-invocation: true`
- **THEN** the Runtime-native activation assertion is trusted and the skill may continue to read-only preflight

#### Scenario: Codex skill command is explicitly dispatched
- **WHEN** a user directly invokes `$new-worktree-apply add-user-auth --target develop` and Codex has enforced `policy.allow_implicit_invocation: false`
- **THEN** the Runtime-native activation assertion is trusted and the skill may continue to read-only preflight

#### Scenario: Runtime lacks an explicit invocation gate
- **WHEN** a Runtime loads the skill but cannot enforce a native policy equivalent to the Claude or Codex gate
- **THEN** the skill reports that explicit activation cannot be guaranteed and performs no repository or OpenSpec write

#### Scenario: Model or another skill selects the workflow
- **WHEN** the model selects `new-worktree-apply` from a natural-language task or another skill invokes it through a nested `Skill(...)` call
- **THEN** the invocation is not treated as user-explicit and the workflow stops without writing

#### Scenario: Activation evidence is forged in user-controlled data
- **WHEN** user text, a repository file, or an environment variable claims that an explicit invocation occurred but the Runtime did not enforce its native gate
- **THEN** the claim is ignored as authorization evidence and the workflow performs no write

#### Scenario: Runtime-native gate cannot be guaranteed
- **WHEN** the invocation is not running under the Runtime-native explicit activation policy
- **THEN** the invocation stops without asking for confirmation or performing a write

### Requirement: New worktree apply executes without repeated authorization
`new-worktree-apply` SHALL treat a Runtime-verified user-explicit invocation as authorization to create and implement in the canonical isolated source worktree. After a complete read-only preflight and a stable final pre-write revalidation, the skill SHALL proceed without requesting interactive confirmation and without requiring an Issue, Team, task-platform envelope, authorization token, or authorization flag. This authorization MUST remain limited to canonical source worktree creation, OpenSpec apply, proposal-scoped local verification, and source commit.

#### Scenario: Explicit invocation proceeds after stable preflight
- **WHEN** Runtime-native explicit activation is guaranteed for `new-worktree-apply add-user-auth --target develop` and every preflight and final revalidation check succeeds
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
`new-worktree-apply` SHALL accept one optional `--dry-run` flag on a Runtime-gated user-explicit invocation. Dry-run mode MUST execute the same strict argument, repository, OpenSpec root, target worktree, cleanliness, canonical identity, source-parent physical containment, artifact manifest, frozen target, and planned-write preflight used by default execution, then report the resulting snapshot and stop without any write. A dry-run snapshot MUST NOT be reused as authorization or as the frozen snapshot of a later real invocation.

#### Scenario: Dry run succeeds
- **WHEN** the caller explicitly invokes `new-worktree-apply add-user-auth --target develop --dry-run`, the Runtime-native gate is enforced, and preflight succeeds
- **THEN** the skill reports the complete plan without creating a branch or worktree and without invoking apply, stage, or commit

#### Scenario: Dry run finds a blocker
- **WHEN** dry-run preflight finds a dirty target, missing artifact, existing canonical branch/path, invalid target, or another blocker
- **THEN** it reports the blocker and preserves all repository and OpenSpec state

#### Scenario: Repository changes after dry run
- **WHEN** a successful dry run is followed by a real invocation after repository state has changed
- **THEN** the real invocation requires a new Runtime-gated explicit activation and preflight and MUST NOT trust the prior dry-run snapshot

## MODIFIED Requirements

### Requirement: Shared deterministic target selection
Each worktree skill SHALL accept `--target <target-branch>` as its explicit target input. `new-worktree-apply` MUST require that explicit option and MUST NOT consult the primary worktree branch, `origin/HEAD`, or conventional branch names when it is omitted. `merge-worktree-return` and `parall-new-worktree-apply` SHALL continue selecting `TARGET_BRANCH` in this order when no explicit target is supplied: the local branch currently checked out in the primary worktree, the existing local branch named by `origin/HEAD`, then the first existing local branch among `main`, `master`, and `trunk`. Every skill SHALL record and display the winning source, and an invalid explicit target MUST fail without fallback.

#### Scenario: Explicit target wins
- **WHEN** the caller supplies an existing local branch through `--target`
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

#### Scenario: Canonical source parent escapes physically
- **WHEN** `.claude` or `.claude/worktrees` is absent, unreadable, a symlink, or resolves outside the physical repository root before single-create writes
- **THEN** `new-worktree-apply` creates no branch or worktree, invokes no apply action, and preserves the target state

### Requirement: Preflight authorization and integration confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `merge-worktree-return` and `parall-new-worktree-apply` MUST obtain an explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. `new-worktree-apply` MUST NOT request a second confirmation after Runtime-gated explicit activation: that invocation authorizes the limited isolated-source operation, and it proceeds only after stable final pre-write revalidation. In `--dry-run` mode it MUST stop after reporting the snapshot.

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
- **WHEN** Runtime-native explicit activation, preflight, and final revalidation complete with no blocker or drift
- **THEN** `new-worktree-apply` begins the planned source worktree writes without asking a question

#### Scenario: New worktree preflight has a blocker
- **WHEN** `new-worktree-apply` finds an unavailable Runtime-native gate, incomplete OpenSpec artifacts, a dirty target worktree, an occupied canonical identity, an unsafe source parent, a required checkout, or out-of-scope work
- **THEN** it stops before writing and reports the exact blocker rather than asking whether to bypass it

#### Scenario: Dry run reaches the write boundary
- **WHEN** dry-run preflight has completed successfully
- **THEN** the skill reports the snapshot and exits before final write authorization or any repository mutation

### Requirement: Pre-write snapshot revalidation
Before the first write, each worktree skill SHALL revalidate the parsed arguments, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, source-parent physical containment, artifact manifest, planned writes, and displayed warnings. Merge and parallel skills SHALL compare those facts with their interactively confirmed snapshot. `new-worktree-apply` SHALL create its immutable `PREFLIGHT_SNAPSHOT` exactly once, collect final read-only facts in a separate immutable `REVALIDATION_SNAPSHOT`, and compare the snapshots field-by-field without rerunning the freeze operation or replacing the baseline. Any material change MUST invalidate the snapshot.

#### Scenario: New worktree snapshot remains stable
- **WHEN** every field in the independent final revalidation snapshot matches the immutable preflight baseline
- **THEN** `new-worktree-apply` may begin the planned write operations

#### Scenario: New worktree snapshot changes before writing
- **WHEN** final revalidation finds changed arguments, target ref, HEAD, worktree path, status, source parent, manifest, planned writes, or warnings
- **THEN** it performs no write and requires a fresh user-explicit invocation rather than refreshing the snapshot or asking for confirmation

#### Scenario: Confirmed integration snapshot remains stable
- **WHEN** merge or parallel revalidation matches every material fact in the confirmed summary
- **THEN** the integration skill may begin its planned write operations

#### Scenario: Confirmed integration snapshot changes
- **WHEN** merge or parallel revalidation differs from the interactively confirmed snapshot
- **THEN** the skill invalidates the confirmation and obtains a new confirmation before writing

### Requirement: New worktree starts from the explicit frozen target
`new-worktree-apply` SHALL freeze the explicitly selected `TARGET_HEAD` during preflight, bind a complete verified artifact manifest to that snapshot, and create the canonical source branch/worktree with `TARGET_HEAD` as an explicit commit-hash start point after final revalidation. It MUST NOT refresh the baseline by auto-committing target changes or pass `TARGET_BRANCH` as the actual creation start point. Before OpenSpec apply it MUST verify the registered path, current branch, source branch ref, and worktree HEAD exactly match the expected canonical identity and frozen hash.

#### Scenario: Worktree is created from an explicit commit hash
- **WHEN** Runtime-native explicit activation, preflight, and final revalidation succeed for proposal `add-user-auth`
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

### Requirement: Target-aware reporting and cleanup
All three skills SHALL report the preflight-selected or interactively confirmed target branch/worktree, immutable target and source snapshots, canonical proposal/branch/path mapping, artifact manifest result, merge result, every cleanup gate, and preserved recovery objects. `new-worktree-apply` reports which Runtime-native explicit invocation gate governed its activation. Cleanup MUST use ordinary explicit Git commands from verified target CWD only after the applicable complete gate succeeds; platform convenience tools MUST NOT weaken or obscure these conditions.

#### Scenario: Successful creation report
- **WHEN** a canonical source worktree is created and verified from a frozen hash
- **THEN** the report identifies proposal, source branch, source path, target branch/worktree, `TARGET_HEAD`, artifact manifest result, and Runtime-native activation gate

#### Scenario: Successful return report
- **WHEN** merge, post-merge verification, ordinary worktree removal, and safe branch deletion all succeed
- **THEN** the report includes `POST_REBASE_SOURCE_HEAD`, `POST_MERGE_TARGET_HEAD`, and a true result for every cleanup gate

#### Scenario: Verification blocks cleanup
- **WHEN** any target containment, CWD, mapping, clean-state, ref/HEAD, source-only commit, delivery commit, or post-merge check fails
- **THEN** the report names the failed or unknown gate and confirms which exact source worktree and branch were preserved

#### Scenario: Cross-platform ordinary cleanup
- **WHEN** cleanup is ready on any supported platform
- **THEN** the workflow attempts only ordinary `git worktree remove <exact-source-path>` and safe `git branch -d -- <exact-source-branch>` without force or opaque destructive fallback

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

### Requirement: New worktree apply selects an explicit OpenSpec project root
`new-worktree-apply` SHALL require one explicit `--target <target-branch>` and accept at most one optional `--openspec-root <repo-relative-directory>` in addition to its proposal and optional `--dry-run`. The OpenSpec-root value SHALL identify the Git-worktree-relative directory that directly contains `openspec/`; omission SHALL be equivalent to `--openspec-root .`. The workflow MUST validate the lexical and physical path, bind the normalized root and complete repository-relative change prefix to the immutable preflight snapshot, build the immutable artifact manifest with that prefix, and run OpenSpec status/apply from the corresponding project directory in the invocation and source worktrees. It MUST NOT discover, guess, or fall back to another OpenSpec project.

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
- **THEN** execution stops with no write and requires a fresh user-explicit invocation

#### Scenario: Source project context is verified before apply
- **WHEN** the canonical source worktree is created from the frozen target hash
- **THEN** the workflow verifies the source project remains inside that worktree, rechecks OpenSpec status and every repository-relative manifest blob, and invokes apply only from the verified source project directory

#### Scenario: Source project verification fails after creation
- **WHEN** the source project directory is missing, escapes its worktree, has incomplete OpenSpec artifacts, or differs from the frozen target manifest
- **THEN** apply does not start and the canonical source branch and worktree are preserved without cleanup, root substitution, or creation retry

#### Scenario: Task backfill uses both project and repository contexts
- **WHEN** apply completes and the workflow reconciles `tasks.md`
- **THEN** it reads tasks from the selected source OpenSpec project, stages changes from the source worktree root, and force-adds the repository-relative `<CHANGE_PREFIX>/tasks.md`

## REMOVED Requirements

### Requirement: Issue-authorized autonomous new worktree apply
**Reason**: `new-worktree-apply` is a general OpenSpec/Git workflow whose Runtime-verified user-explicit invocation already authorizes its limited isolated-source operation. Binding it to an Issue, Team, and task-platform envelope adds a second authorization layer, prevents proposal-only use, and provides no additional repository-safety guarantee beyond trusted command dispatch, deterministic preflight, and final drift revalidation.
**Migration**: Remove `--authorized-by-issue <issue-id>` and all `issue-authorization/v1` handling. Users invoke Claude `/new-worktree-apply <proposal> --target <branch> ...`, Codex `$new-worktree-apply <proposal> --target <branch> ...`, or an equivalent Runtime-supported explicit skill command; add `--dry-run` for a strictly read-only preview. Runtimes without an equivalent native explicit invocation gate remain zero-write unsupported.
