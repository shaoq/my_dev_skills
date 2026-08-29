## REMOVED Requirements

### Requirement: New worktree apply requires Runtime-native explicit invocation gates
**Reason**: The requirement incorrectly uses invocation routing as authorization and model-selection control. It blocks natural-language, Team/subagent, and nested-skill orchestration even though deterministic preflight and scope gates remain available.

**Migration**: Remove Claude user-only invocation metadata, remove the Codex implicit-invocation prohibition, and route concrete implementation requests through the same preflight and safety state machine regardless of command syntax.

## MODIFIED Requirements

### Requirement: New worktree apply executes without repeated authorization
`new-worktree-apply` SHALL treat a concrete user request to implement or apply the selected OpenSpec proposal as authorization to create and implement in the canonical isolated source worktree, whether the Runtime routes that intent from an explicit command, natural language, Team/subagent orchestration, or a nested skill workflow. After a complete read-only preflight and stable final pre-write revalidation, the skill SHALL proceed without requesting interactive confirmation and without requiring an Issue, Team, task-platform envelope, authorization token, or authorization flag. This authorization MUST remain limited to canonical source worktree creation, OpenSpec apply, proposal-scoped local verification, and source commit.

#### Scenario: Routed implementation request proceeds after stable preflight
- **WHEN** a concrete request to implement `add-user-auth` on `develop` is routed to `new-worktree-apply` and every preflight and final revalidation check succeeds
- **THEN** the skill creates the canonical source worktree from the frozen target commit and enters apply without asking for confirmation

#### Scenario: Proposal has no Issue
- **WHEN** a local OpenSpec proposal is requested without any Issue or Team context
- **THEN** the skill applies the same argument, repository, target, artifact, and worktree safety checks and does not require task-platform metadata

#### Scenario: Legacy Issue authorization option is supplied
- **WHEN** an invocation contains `--authorized-by-issue`
- **THEN** the skill performs no write, reports the option as removed, and displays an equivalent invocation without it

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
`new-worktree-apply` SHALL accept one optional `--dry-run` flag through every supported routing path. Dry-run mode MUST execute the same strict argument, repository, OpenSpec root, target worktree, cleanliness, canonical identity, source-parent physical containment, artifact manifest, frozen target, and planned-write preflight used by default execution, then report the resulting snapshot and stop without any write. A dry-run snapshot MUST NOT be reused as authorization or as the frozen snapshot of a later real invocation.

#### Scenario: Dry run succeeds
- **WHEN** the caller requests `new-worktree-apply add-user-auth --target develop --dry-run` and preflight succeeds
- **THEN** the skill reports the complete plan without creating a branch or worktree and without invoking apply, stage, or commit

#### Scenario: Dry run finds a blocker
- **WHEN** dry-run preflight finds a dirty target, missing artifact, existing canonical branch/path, invalid target, or another blocker
- **THEN** it reports the blocker and preserves all repository and OpenSpec state

#### Scenario: Repository changes after dry run
- **WHEN** a successful dry run is followed by a real invocation after repository state has changed
- **THEN** the real invocation performs a new complete preflight and MUST NOT trust the prior dry-run snapshot

### Requirement: Preflight authorization and integration confirmation
Each worktree skill SHALL finish its read-only preflight and display the command scope, target branch and source, relevant worktree paths, pending file changes, planned writes, and risk warnings. `merge-worktree-return` and `parall-new-worktree-apply` MUST obtain one explicit affirmative response with no default or timed approval before any Git write or OpenSpec apply action, regardless of whether routing was explicit, model-selected, Team/subagent-driven, or nested. `new-worktree-apply` MUST NOT request a second confirmation after a concrete user implementation request: that request authorizes the limited isolated-source operation, and it proceeds only after stable final pre-write revalidation. In `--dry-run` mode it MUST stop after reporting the snapshot.

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
- **WHEN** a concrete implementation request, preflight, and final revalidation complete with no blocker or drift
- **THEN** `new-worktree-apply` begins the planned source worktree writes without asking a question

#### Scenario: New worktree preflight has a blocker
- **WHEN** `new-worktree-apply` finds incomplete OpenSpec artifacts, a dirty target worktree, an occupied canonical identity, an unsafe source parent, a required checkout, or out-of-scope work
- **THEN** it stops before writing and reports the exact blocker rather than asking whether to bypass it

#### Scenario: Dry run reaches the write boundary
- **WHEN** dry-run preflight has completed successfully
- **THEN** the skill reports the snapshot and exits before any repository mutation

### Requirement: Pre-write snapshot revalidation
Before the first write, each worktree skill SHALL revalidate the parsed arguments, selected target ref and HEAD, worktree mapping, cleanliness or pending-change state, required checkout, source-parent physical containment, artifact manifest, planned writes, and displayed warnings. Merge and parallel skills SHALL compare those facts with their interactively confirmed snapshot. `new-worktree-apply` SHALL create its immutable `PREFLIGHT_SNAPSHOT` exactly once, collect final read-only facts in a separate immutable `REVALIDATION_SNAPSHOT`, and compare the snapshots field-by-field without rerunning the freeze operation or replacing the baseline. Any material change MUST invalidate the snapshot.

#### Scenario: New worktree snapshot remains stable
- **WHEN** every field in the independent final revalidation snapshot matches the immutable preflight baseline
- **THEN** `new-worktree-apply` may begin the planned write operations

#### Scenario: New worktree snapshot changes before writing
- **WHEN** final revalidation finds changed arguments, target ref, HEAD, worktree path, status, source parent, manifest, planned writes, or warnings
- **THEN** it performs no write and requires a fresh preflight invocation rather than refreshing the snapshot or asking for confirmation

#### Scenario: Confirmed integration snapshot remains stable
- **WHEN** merge or parallel revalidation matches every material fact in the confirmed summary
- **THEN** the integration skill may begin the planned write operations

#### Scenario: Confirmed integration snapshot changes
- **WHEN** merge or parallel revalidation differs from the interactively confirmed snapshot
- **THEN** the skill invalidates the confirmation and obtains a new confirmation before writing

### Requirement: Target-aware reporting and cleanup
All three skills SHALL report the preflight-selected or interactively confirmed target branch/worktree, immutable target and source snapshots, canonical proposal/branch/path mapping, artifact manifest result, merge result, every cleanup gate, and preserved recovery objects. Invocation syntax or Runtime activation policy MUST NOT be reported as authorization evidence. Cleanup MUST use ordinary explicit Git commands from verified target CWD only after the applicable complete gate succeeds; platform convenience tools MUST NOT weaken or obscure these conditions.

#### Scenario: Successful creation report
- **WHEN** a canonical source worktree is created and verified from a frozen hash
- **THEN** the report identifies proposal, source branch, source path, target branch/worktree, `TARGET_HEAD`, artifact manifest result, and limited operation scope

#### Scenario: Successful return report
- **WHEN** merge, post-merge verification, ordinary worktree removal, and safe branch deletion all succeed
- **THEN** the report includes `POST_REBASE_SOURCE_HEAD`, `POST_MERGE_TARGET_HEAD`, and a true result for every cleanup gate

#### Scenario: Verification blocks cleanup
- **WHEN** any target containment, CWD, mapping, clean-state, ref/HEAD, source-only commit, delivery commit, or post-merge check fails
- **THEN** the report names the failed or unknown gate and confirms which exact source worktree and branch were preserved

#### Scenario: Cross-platform ordinary cleanup
- **WHEN** cleanup is ready on any supported platform
- **THEN** the workflow attempts only ordinary `git worktree remove <exact-source-path>` and safe `git branch -d -- <exact-source-branch>` without force or opaque destructive fallback
