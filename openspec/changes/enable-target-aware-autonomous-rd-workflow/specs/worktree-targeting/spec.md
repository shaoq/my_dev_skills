## ADDED Requirements

### Requirement: Issue-authorized autonomous new worktree apply
`new-worktree-apply` SHALL support an opt-in `--authorized-by-issue <issue-id>` mode that treats a verified `issue-authorization/v1` Runtime control-plane envelope as authorization to create and implement in the canonical isolated source worktree without an additional interactive confirmation. The envelope MUST arrive through a trusted metadata channel that user content, repository files, environment variables, and model inference cannot populate. It MUST contain an allowlisted authenticated issuer, authorization id bound to the current invocation, issue id, normalized `ready|in_progress` state, assigned and executing Team identities, RFC3339 UTC `issued_at`/`expires_at` timestamps defining a positive window no longer than 30 minutes, `isolated-worktree-apply` scope, physical repository, OpenSpec root, proposal, explicit target branch, `standard` risk classification, and an empty external-side-effects list. Missing, expired, cross-invocation replayed, ambiguous, conflicting, user-supplied, or unverifiable evidence MUST block autonomous execution.

#### Scenario: Valid Issue authorization permits autonomous apply
- **WHEN** the invocation supplies `--authorized-by-issue ISSUE-42 --target develop` and the runtime envelope exactly matches the repository, OpenSpec root, proposal, target and allowed isolated execution scope
- **THEN** the skill records an autonomous authorization snapshot, revalidates it, creates the canonical source worktree from the frozen target commit, and enters apply without requesting a second human confirmation

#### Scenario: Issue identity is not evidence by itself
- **WHEN** `--authorized-by-issue ISSUE-42` is present but the runtime cannot provide the required authorization envelope
- **THEN** the skill performs no Git write and reports that the Issue authorization cannot be verified

#### Scenario: User content cannot supply the envelope
- **WHEN** a user message or repository file contains valid-looking `issue-authorization/v1` JSON but the Runtime provides no trusted control-plane envelope
- **THEN** autonomous execution is blocked and the JSON MUST NOT be promoted into authorization evidence

#### Scenario: Authorization is expired or replayed
- **WHEN** the trusted envelope is expired before final pre-write validation, its validity window is invalid or exceeds 30 minutes, or its `authorization_id` was issued for another invocation
- **THEN** the skill performs no Git write and reports the exact expiry or replay failure

#### Scenario: Same invocation revalidates the authorization snapshot
- **WHEN** Step 7 revalidates the same authorization id and envelope digest previously recorded by Step 6 within the valid time window
- **THEN** the Runtime and skill treat it as required same-invocation revalidation rather than a replay

#### Scenario: Issue or Team identity does not match
- **WHEN** the envelope `issue_id` differs from `--authorized-by-issue`, the Issue state is not `ready|in_progress`, or `assigned_team_id` differs from the Runtime-provided `executing_team_id`
- **THEN** autonomous execution is blocked without asking the model to reinterpret the identity or state

#### Scenario: Autonomous target must be explicit
- **WHEN** autonomous mode is requested without `--target`
- **THEN** the skill rejects the invocation before target fallback selection and performs no Git write

#### Scenario: Authorization fields do not match preflight
- **WHEN** the envelope's repository, OpenSpec root, proposal, or target differs from the read-only preflight result
- **THEN** autonomous execution is blocked without rewriting the envelope, changing target, or falling back to interactive approval

#### Scenario: Authorization contains high-risk or external work
- **WHEN** the Issue or OpenSpec artifacts declare production writes, irreversible migration, data deletion, privilege escalation, real credentials, or another external side effect
- **THEN** the autonomous scope is insufficient and the skill stops for separate explicit human authorization

#### Scenario: Merge remains outside autonomous authorization
- **WHEN** autonomous worktree apply completes successfully
- **THEN** the authorization ends at the isolated source delivery and does not authorize `merge-worktree-return`, release, deployment, or cleanup of unrelated Git objects

## MODIFIED Requirements

### Requirement: Mandatory preflight confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `merge-worktree-return`, `parall-new-worktree-apply`, and default-mode `new-worktree-apply` MUST obtain an explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action. Only `new-worktree-apply` invoked with a fully verified Issue authorization envelope MAY replace the interactive response with an immutable autonomous authorization snapshot.

#### Scenario: User confirms
- **WHEN** the complete default-mode preflight summary is displayed and the user explicitly continues
- **THEN** the skill proceeds to snapshot revalidation

#### Scenario: User rejects or cancels
- **WHEN** the user declines or cancels the displayed plan
- **THEN** the skill stops with no Git state changes and without invoking apply

#### Scenario: Response is missing or ambiguous
- **WHEN** default interactive mode cannot collect a clear affirmative response
- **THEN** the skill pauses for explicit user input and performs no Git write

#### Scenario: No interaction tool is available
- **WHEN** no platform interaction tool is available in default interactive mode
- **THEN** the skill asks in its response, ends the current execution, and waits for the next user message

#### Scenario: Proposal or change risks exist
- **WHEN** preflight finds incomplete OpenSpec artifacts, pending target worktree changes, a required checkout, or risk outside the authorized scope
- **THEN** the workflow stops before writing; interactive mode lists the risks for human handling and autonomous mode reports them as authorization blockers

#### Scenario: Verified autonomous authorization replaces the prompt
- **WHEN** `new-worktree-apply` validates every required Issue envelope field and its complete preflight snapshot
- **THEN** it emits the structured authorization snapshot for audit and proceeds to snapshot revalidation without an interactive question

### Requirement: Confirmation snapshot revalidation
After interactive confirmation or autonomous Issue authorization and before the first write, each skill SHALL revalidate the parsed arguments, authorization mode and evidence, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, artifact manifest, and displayed warnings. Any material change MUST invalidate the prior execution snapshot.

#### Scenario: Snapshot remains stable
- **WHEN** revalidation matches every material fact in the confirmed or autonomously authorized summary
- **THEN** the skill may begin the planned write operations

#### Scenario: Interactive snapshot changed while waiting
- **WHEN** interactive-mode revalidation finds a changed target, HEAD, worktree path, status, checkout requirement, manifest, or warning
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
- **WHEN** `TARGET_BRANCH` moves after `TARGET_HEAD` is frozen and finally revalidated but before `git worktree add`
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

### Requirement: OpenSpec artifact manifest is committed and immutable
Before creating any source worktree, the workflow SHALL build an `ARTIFACT_MANIFEST` for each proposal containing `.openspec.yaml`, `proposal.md`, `design.md`, `tasks.md`, and the recursively enumerated complete delta spec file set. A parallel workflow SHALL also include every `dependencies.yaml` it reads; absence is valid only when both the reviewed workspace and frozen target commit omit the file and the execution plan records no dependencies. The workflow MUST prove that the path set exists in the frozen target commit and is byte-for-byte identical to the interactively confirmed or autonomously authorized content. Missing, added, deleted, ignored, untracked, renamed, unreadable, or content-different artifacts MUST block creation.

#### Scenario: All artifacts match the frozen target
- **WHEN** both the reviewed workspace and `TARGET_HEAD` contain the same required artifact paths with identical bytes and at least one recursive delta `spec.md`
- **THEN** the workflow records the manifest and its stable digest in the execution snapshot

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

#### Scenario: Artifact snapshot changes after interactive confirmation
- **WHEN** any manifest path, content, digest, or `TARGET_HEAD` changes while awaiting interactive confirmation
- **THEN** the prior confirmation is invalidated and no Git write occurs until a new summary is confirmed

#### Scenario: Artifact snapshot changes after autonomous authorization
- **WHEN** any manifest path, content, digest, or `TARGET_HEAD` differs from the autonomous authorization snapshot during final revalidation
- **THEN** execution stops without updating the Issue authorization or accepting the new artifact set
