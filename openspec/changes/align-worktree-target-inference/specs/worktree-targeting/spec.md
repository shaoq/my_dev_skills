## MODIFIED Requirements

### Requirement: New worktree apply executes without repeated authorization
`new-worktree-apply` SHALL treat a concrete user request to implement or apply the selected OpenSpec proposal as authorization for its limited canonical isolated-source operation, whether routed from an explicit command, natural language, Team/subagent orchestration, or a nested skill workflow. When that request supplies an explicit target and complete read-only preflight plus stable final revalidation succeed, the workflow SHALL proceed without a second confirmation. When the target is inferred, the workflow MUST display and receive one affirmative confirmation for the complete inferred-target plan before any write. It MUST NOT require task-platform authorization metadata. Authorization remains limited to source worktree creation, OpenSpec apply, proposal-scoped local verification, and source commit.

#### Scenario: Explicit-target implementation proceeds after stable preflight
- **WHEN** a concrete implementation request for `add-user-auth --target develop` is routed and every deterministic preflight and final revalidation check succeeds
- **THEN** the skill creates the canonical source worktree from the frozen target commit and enters apply without asking for a second confirmation

#### Scenario: Inferred-target implementation is confirmed
- **WHEN** a concrete implementation request omits `--target`, target inference succeeds, and the user affirms the displayed complete plan
- **THEN** the skill independently revalidates that confirmed snapshot before beginning the limited source-worktree writes

#### Scenario: Proposal has no Issue
- **WHEN** a local OpenSpec proposal is requested without any Issue or Team context
- **THEN** the skill applies the same argument, repository, target, artifact, worktree, and applicable confirmation checks without requiring task-platform metadata

#### Scenario: Legacy Issue authorization option is supplied
- **WHEN** an invocation contains `--authorized-by-issue`
- **THEN** the skill performs no write, reports the option as removed, and displays an equivalent supported invocation without it

#### Scenario: Generic authorization option is supplied
- **WHEN** an invocation contains `--authorized`, `--yes`, or another unsupported approval flag
- **THEN** strict argument parsing rejects it before any Git or OpenSpec write because authorization follows the explicit or interactive path instead of a generic flag

#### Scenario: Merge remains outside apply scope
- **WHEN** worktree apply completes successfully
- **THEN** the invocation does not authorize `merge-worktree-return`, release, deployment, production writes, or cleanup of unrelated Git objects

#### Scenario: Proposal requires an external side effect
- **WHEN** proposal artifacts require deployment, production mutation, irreversible migration, data deletion, privilege escalation, real credentials, or another action outside isolated source delivery
- **THEN** the skill stops before that action and reports that it requires a separate authorized workflow

### Requirement: New worktree apply supports a read-only dry run
`new-worktree-apply` SHALL accept one optional `--dry-run` flag through every supported routing path. Dry-run mode MUST execute the same strict argument, repository, OpenSpec root, target selection, target worktree, cleanliness, canonical identity, source-parent physical containment, artifact manifest, frozen target, and planned-write preflight used by default execution, then report the resulting snapshot and stop without confirmation or any write. A dry-run snapshot MUST NOT be reused as authorization or as the frozen snapshot of a later real invocation.

#### Scenario: Explicit-target dry run succeeds
- **WHEN** the caller requests `new-worktree-apply add-user-auth --target develop --dry-run` and preflight succeeds
- **THEN** the skill reports the complete plan without creating a branch or worktree and without invoking apply, stage, or commit

#### Scenario: Inferred-target dry run succeeds
- **WHEN** the caller requests `new-worktree-apply add-user-auth --dry-run` and target inference plus preflight succeed
- **THEN** the skill reports the inferred target source and complete plan, requests no write confirmation, and performs no write

#### Scenario: Dry run finds a blocker
- **WHEN** dry-run preflight finds a dirty target, missing artifact, existing canonical branch/path, invalid target, or another blocker
- **THEN** it reports the blocker and preserves all repository and OpenSpec state

#### Scenario: Repository changes after dry run
- **WHEN** a successful dry run is followed by a real invocation after repository state has changed
- **THEN** the real invocation performs a new complete preflight and MUST NOT trust the prior dry-run snapshot

### Requirement: Shared deterministic target selection
Each worktree skill SHALL accept `--target <target-branch>` as its explicit target input. When the option is omitted, `new-worktree-apply`, `merge-worktree-return`, and `parall-new-worktree-apply` SHALL select `TARGET_BRANCH` in this order: the named branch recorded for the primary worktree when its local ref exists, the existing local branch named by `origin/HEAD`, then the first existing local branch among `main`, `master`, and `trunk`. Every skill SHALL record and display the winning source. Candidate eligibility SHALL depend only on branch-source resolution and local ref existence. Worktree ownership, topology, identity, HEAD/ref equality, cleanliness, and path safety SHALL be post-selection validation; a failure there MUST stop rather than select a lower-priority candidate. An invalid explicit target MUST fail without fallback.

#### Scenario: Explicit target wins
- **WHEN** the user supplies an existing local branch through `--target`
- **THEN** the skill records `TARGET_SOURCE=explicit` and selects it regardless of automatic candidates

#### Scenario: Primary worktree branch is the default
- **WHEN** a worktree skill has no explicit target, the primary worktree registration records a named branch, and that local ref exists
- **THEN** it selects that branch with `TARGET_SOURCE=inferred:primary-worktree` before consulting `origin/HEAD` or conventional names

#### Scenario: Origin default is the next fallback
- **WHEN** the primary worktree yields no eligible named local ref and `origin/HEAD` names an existing local branch
- **THEN** the skill selects the local branch named by `origin/HEAD` with `TARGET_SOURCE=inferred:origin-head`

#### Scenario: Conventional fallback is required
- **WHEN** neither the primary worktree nor `origin/HEAD` yields an existing local ref
- **THEN** the skill selects the first existing local branch in the order `main`, `master`, `trunk` with `TARGET_SOURCE=inferred:fallback-name`

#### Scenario: Explicit target does not exist locally
- **WHEN** `--target` names a branch absent from `refs/heads/`
- **THEN** the skill stops without fetching, creating a branch, or selecting a fallback

#### Scenario: Selected candidate fails later validation
- **WHEN** the highest-priority selected candidate is not uniquely held by a registered clean matching worktree
- **THEN** the skill reports that blocker and MUST NOT try a lower-priority target candidate

#### Scenario: No target can be inferred
- **WHEN** none of the automatic branch sources yields an existing local ref
- **THEN** the skill asks the user to provide `--target` and performs no Git or OpenSpec write

### Requirement: Preflight authorization and integration confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `parall-new-worktree-apply` MUST retain one explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. `merge-worktree-return` SHALL proceed after stable independent revalidation without a second confirmation when a clear return request supplies an explicit target and the canonical source is strictly clean; an inferred target or pending source changes MUST instead receive one explicit affirmative response for the complete interactive plan. `new-worktree-apply` SHALL proceed without a second confirmation for an explicit target after a concrete implementation request and stable revalidation; an inferred target MUST instead receive one explicit affirmative response for the complete plan. Discussion, review, status, or feasibility requests MUST NOT authorize writes. In `--dry-run` mode single apply MUST stop after reporting the snapshot.

#### Scenario: Deterministic single apply preflight is stable
- **WHEN** a concrete implementation request supplies an explicit target and independent final revalidation matches every material preflight fact
- **THEN** `new-worktree-apply` begins its limited source-worktree writes without asking a second confirmation

#### Scenario: Interactive single apply user confirms
- **WHEN** the complete single-apply plan shows an inferred target and the user explicitly continues
- **THEN** `new-worktree-apply` freezes the confirmed snapshot and proceeds to independent revalidation

#### Scenario: Deterministic return preflight is stable
- **WHEN** a clear return request uses an explicit target, the canonical source is strictly clean, and independent final revalidation matches every material preflight fact
- **THEN** `merge-worktree-return` begins the bounded return writes without asking a second confirmation

#### Scenario: Interactive return user confirms
- **WHEN** the complete return plan shows an inferred target or exact pending-source commit plan and the user explicitly continues
- **THEN** `merge-worktree-return` proceeds to independent snapshot revalidation

#### Scenario: Parallel integration user confirms
- **WHEN** the complete parallel preflight summary is displayed and the user explicitly continues
- **THEN** `parall-new-worktree-apply` proceeds to snapshot revalidation

#### Scenario: Interactive user rejects or cancels
- **WHEN** the user declines or cancels a displayed inferred single-apply, interactive return, or parallel plan
- **THEN** the workflow stops with no Git state changes and without invoking apply

#### Scenario: Interactive response is missing or ambiguous
- **WHEN** an interactive workflow cannot collect a clear affirmative response
- **THEN** it pauses for explicit user input and performs no Git write

#### Scenario: No interaction tool is available
- **WHEN** no platform interaction tool is available for an inferred single apply, interactive return, or parallel apply
- **THEN** the skill asks in its response, ends the current execution, and waits for the next user message

#### Scenario: Single apply preflight has a blocker
- **WHEN** `new-worktree-apply` finds incomplete OpenSpec artifacts, a dirty target worktree, an occupied canonical identity, an unsafe source parent, a required checkout, or out-of-scope work
- **THEN** it stops before writing and reports the exact blocker rather than asking whether to bypass it

#### Scenario: Dry run reaches the write boundary
- **WHEN** dry-run preflight has completed successfully with an explicit or inferred target
- **THEN** the skill reports the snapshot and exits before confirmation, final write authorization, or any repository mutation

### Requirement: Pre-write snapshot revalidation
Before the first write, each worktree skill SHALL revalidate the parsed arguments, selected target source, target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, source-parent physical containment, artifact manifest, planned writes, and displayed warnings. Explicit-target single apply and the deterministic return path SHALL create their immutable `PREFLIGHT_SNAPSHOT` exactly once. Each interactive confirmation round SHALL create a new immutable `PREFLIGHT_SNAPSHOT[n]`; prior rounds SHALL remain unchanged, and `ACTIVE_CONFIRMED_SNAPSHOT` SHALL identify the latest affirmed round used by revalidation. Every path SHALL collect final read-only facts in a separate immutable `REVALIDATION_SNAPSHOT` and compare field-by-field without replacing its applicable baseline. Any material change MUST invalidate the applicable authorization.

#### Scenario: Deterministic single apply snapshot remains stable
- **WHEN** every explicit-target single-apply field in the independent final revalidation snapshot matches the immutable preflight baseline
- **THEN** `new-worktree-apply` may begin the planned write operations

#### Scenario: Deterministic single apply snapshot changes
- **WHEN** final revalidation finds changed arguments, target source, target ref, HEAD, worktree path, status, source parent, manifest, planned writes, or warnings
- **THEN** it performs no write and requires a fresh invocation rather than refreshing the snapshot or entering the interactive path

#### Scenario: Confirmed inferred single apply remains stable
- **WHEN** every inferred-target single-apply field matches the interactively confirmed snapshot
- **THEN** `new-worktree-apply` may begin the confirmed planned writes

#### Scenario: Confirmed inferred single apply changes
- **WHEN** revalidation changes the inferred target, target source, target state, artifacts, paths, or planned writes
- **THEN** the skill invalidates `ACTIVE_CONFIRMED_SNAPSHOT` and reruns the complete read-only validation. If the latest facts contain any blocker, it stops without asking for confirmation; only a complete blocker-free plan may create the next immutable confirmation round before writing

#### Scenario: Deterministic return snapshot remains stable
- **WHEN** every return argument, identity, ref, HEAD, clean state, task classification, verification command, and planned write matches the immutable deterministic preflight baseline
- **THEN** `merge-worktree-return` may begin the bounded return writes without another confirmation

#### Scenario: Deterministic return snapshot changes before writes
- **WHEN** final revalidation differs from any material deterministic return preflight fact
- **THEN** the workflow performs no write, requires a fresh invocation, and does not replace the baseline or enter the interactive path

#### Scenario: Confirmed integration snapshot remains stable
- **WHEN** an interactive return or parallel revalidation matches every material fact in the confirmed summary
- **THEN** the integration skill may begin its planned write operations

#### Scenario: Confirmed integration snapshot changes
- **WHEN** an interactive return or parallel revalidation differs from the interactively confirmed snapshot
- **THEN** the skill invalidates the confirmation and obtains a new confirmation before writing

### Requirement: New worktree starts from the explicit frozen target
`new-worktree-apply` SHALL freeze the selected `TARGET_HEAD` during preflight, bind the recorded `TARGET_SOURCE` and complete verified artifact manifest to that snapshot, and create the canonical source branch/worktree with `TARGET_HEAD` as an explicit commit-hash start point after the applicable final revalidation. It MUST NOT refresh the baseline by auto-committing target changes or pass `TARGET_BRANCH` as the actual creation start point. Before OpenSpec apply it MUST verify the registered path, current branch, source branch ref, and worktree HEAD exactly match the expected canonical identity and frozen hash.

#### Scenario: Worktree is created from an explicit commit hash
- **WHEN** the applicable explicit or inferred target path, preflight, and final revalidation succeed for proposal `add-user-auth`
- **THEN** the workflow runs the equivalent of `git worktree add <repo>/.claude/worktrees/add-user-auth -b worktree-add-user-auth <TARGET_HEAD>`

#### Scenario: Target ref advances before final revalidation
- **WHEN** `TARGET_BRANCH` no longer resolves to the frozen `TARGET_HEAD` at final revalidation
- **THEN** the workflow stops and creates no branch or worktree under an unconfirmed snapshot

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

### Requirement: New worktree apply selects an explicit OpenSpec project root
`new-worktree-apply` SHALL accept at most one optional `--target <target-branch>`, at most one optional `--openspec-root <repo-relative-directory>`, and at most one optional `--dry-run` in addition to its required proposal. The OpenSpec-root value SHALL identify the Git-worktree-relative directory that directly contains `openspec/`; omission SHALL be equivalent to `--openspec-root .`. The workflow MUST validate the lexical and physical path, bind the normalized root and complete repository-relative change prefix to the applicable immutable preflight snapshot, build the immutable artifact manifest with that prefix, and run OpenSpec status/apply from the corresponding project directory in the invocation and source worktrees. It MUST NOT discover, guess, or fall back to another OpenSpec project.

#### Scenario: Existing root-level invocation remains compatible
- **WHEN** the user invokes `new-worktree-apply add-user-auth` and the proposal exists at `openspec/changes/add-user-auth`
- **THEN** the workflow records `OPENSPEC_ROOT=.`, uses `openspec/changes/add-user-auth` without a `./` prefix, and resolves the target through the explicit-or-inferred target contract

#### Scenario: Explicit dot matches the default
- **WHEN** the same repository and proposal are invoked with `--openspec-root .`
- **THEN** the normalized project directory, change prefix, artifact manifest paths, digest inputs, and OpenSpec working directory are identical to the omitted-option invocation

#### Scenario: Nested OpenSpec project is selected
- **WHEN** the user invokes `new-worktree-apply add-user-auth --openspec-root twin-rag` and `twin-rag/openspec/changes/add-user-auth` exists
- **THEN** the workflow uses `twin-rag` as the OpenSpec CLI working directory, prefixes every manifest path with `twin-rag/openspec/changes/add-user-auth`, and resolves target independently

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
- **THEN** the preflight snapshot includes whether the root option was explicit, the normalized root, invocation project directory, expected source project directory, repository-relative change prefix, manifest paths, and manifest digest

#### Scenario: Selected project changes before writing
- **WHEN** argument parsing, normalized or physical project paths, containment results, OpenSpec status, change prefix, manifest paths, blobs, digest, or target snapshot differs during pre-write revalidation
- **THEN** the invocation follows its authorization path's drift rule instead of refreshing the snapshot or silently changing projects

#### Scenario: Source project context is verified before apply
- **WHEN** the canonical source worktree is created from the preflight target hash
- **THEN** the workflow verifies the source project remains inside that worktree, rechecks OpenSpec status and every repository-relative manifest blob, and invokes apply only from the verified source project directory

#### Scenario: Source project verification fails after creation
- **WHEN** the source project directory is missing, escapes its worktree, has incomplete OpenSpec artifacts, or differs from the preflight target manifest
- **THEN** apply does not start and the canonical source branch and worktree are preserved without cleanup, root substitution, or creation retry

#### Scenario: Task backfill uses both project and repository contexts
- **WHEN** apply completes and the workflow reconciles `tasks.md`
- **THEN** it reads tasks from the selected source OpenSpec project, stages changes from the source worktree root, and force-adds the repository-relative `<CHANGE_PREFIX>/tasks.md`
