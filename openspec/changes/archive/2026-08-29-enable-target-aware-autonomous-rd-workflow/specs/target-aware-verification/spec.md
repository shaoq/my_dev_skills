## ADDED Requirements

### Requirement: Verification skills require an explicit target baseline
Repository skills that attribute implementation, tests, commits, or companion artifacts to an OpenSpec change SHALL accept the target branch explicitly and MUST NOT hard-code or silently substitute `main`. `verify-impl-consistency` SHALL require `<change-name> --base <target-branch>` for active-change incremental verification. `check-changes-completed` SHALL require `--target <target-branch>` plus one or more `--change <active-change>` selectors for its five-dimensional completion check.

#### Scenario: Implementation consistency targets develop
- **WHEN** the caller runs `verify-impl-consistency add-search --base develop`
- **THEN** the skill records `develop` as the only target baseline for OpenSpec incremental verification

#### Scenario: Completion check targets a release branch
- **WHEN** the caller runs `check-changes-completed --target release-next --change release-candidate`
- **THEN** D3 code delivery and D5 compliance use `release-next` as their shared target baseline

#### Scenario: Required baseline is missing
- **WHEN** an active-change verification or completion check is invoked without its required change selector, `--base`, or `--target`
- **THEN** the affected change-scoped verification stops or is explicitly reported as not executed and MUST NOT fall back to `main`, the current branch, `origin/HEAD`, or another guessed ref

#### Scenario: Baseline arguments are invalid
- **WHEN** a call contains a duplicate option, a missing value, an unknown flag, an unsupported positional argument, or a target absent from local `refs/heads/`
- **THEN** the skill reports the exact argument error and performs no change-scoped verification or backfill write

### Requirement: Change-scoped verification uses an explicit selection set
Change-scoped verification SHALL operate only on active changes explicitly selected by the caller. `verify-impl-consistency` MUST accept exactly one positional active change for incremental verification and MUST run project-level diagnostics only when no change is supplied. `check-changes-completed` MUST accept one or more unique `--change <name>` values and MUST exclude every unselected active change from scanning, conclusions, and task backfill.

#### Scenario: Verify runs project-level mode without a change
- **WHEN** `verify-impl-consistency` is invoked without a change name and without `--base`
- **THEN** it runs project-level D1/D2/D3 only and MUST NOT auto-select an active change

#### Scenario: Completion check selects one target group
- **WHEN** active changes `change-a` and `change-b` target `develop` while `change-c` targets `release`, and the caller runs `check-changes-completed --target develop --change change-a --change change-b`
- **THEN** only `change-a` and `change-b` are scanned or eligible for backfill and `change-c` remains unread and unmodified by change-level processing

#### Scenario: Selected change is invalid or duplicated
- **WHEN** a `--change` value is not an exact active change name or the same name is supplied twice
- **THEN** the invocation fails before baseline queries or task backfill

### Requirement: Target branches resolve to immutable comparison snapshots
Each target-aware verification skill SHALL resolve the explicit local target branch to `BASE_HEAD`, freeze current `CURRENT_HEAD`, prove `BASE_HEAD` is an ancestor of `CURRENT_HEAD`, and use the immutable range `<BASE_HEAD>..<CURRENT_HEAD>` for every Git query in that invocation. It MUST NOT re-resolve a moving branch independently for separate dimensions or silently substitute a merge base when ancestry fails.

#### Scenario: Non-main baseline is frozen
- **WHEN** local branch `develop` resolves to commit `abc123` at preflight
- **THEN** every change-scoped `git diff` or `git log` in the invocation compares from `abc123` rather than the literal branch name or `main`

#### Scenario: Target moves during verification
- **WHEN** the target branch ref no longer equals `BASE_HEAD` at final revalidation
- **THEN** the report identifies both the frozen commit and the observed drift and does not combine evidence from the new target tip; `check-changes-completed` MUST NOT backfill, stage, or commit task markers

#### Scenario: Current HEAD moves during verification
- **WHEN** current `HEAD` no longer equals `CURRENT_HEAD` at final revalidation
- **THEN** the report marks the frozen evidence stale and `check-changes-completed` MUST NOT backfill, stage, or commit task markers

#### Scenario: Target snapshot is not an ancestor
- **WHEN** `git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>` fails
- **THEN** `verify-impl-consistency` reports the OpenSpec incremental dimension as not executed, while `check-changes-completed` reports the selected changes blocked and performs no task write

#### Scenario: Current HEAD equals target snapshot
- **WHEN** `CURRENT_HEAD` equals `BASE_HEAD`
- **THEN** the skill reports an empty comparison range without inventing delivered files or commits

### Requirement: Verification reports disclose baseline evidence
Every report containing change-scoped findings SHALL include the explicit change selection set, parameter source, target branch, frozen target commit, frozen current commit, comparison range, and final target-ref/current-HEAD stability results. A skipped, failed, non-ancestor, or drifted baseline check MUST be visible as an evidence limitation; completion reports MUST additionally disclose that writes and archivable conclusions were blocked.

#### Scenario: Stable baseline is reported
- **WHEN** verification completes, the target ref still resolves to `BASE_HEAD`, and current HEAD still resolves to `CURRENT_HEAD`
- **THEN** the report records the selected changes, branch, both commits, exact range, and `stable` status for both sides

#### Scenario: Incremental dimension is skipped
- **WHEN** `verify-impl-consistency` performs only project-level analysis because the caller selected no change
- **THEN** the report states that no change-scoped baseline was required and does not imply OpenSpec incremental coverage

### Requirement: Fixed-main regression audit covers all source skills
The project verification suite SHALL scan every non-archived source `SKILL.md` for Git comparison logic that fixes the base to `main`. Fixed-main comparison commands MUST fail the regression check; documented prohibited examples and conventional target-selection fallback text MAY be allowlisted only when they do not execute a comparison against `main`.

#### Scenario: Fixed diff is introduced
- **WHEN** a source skill contains executable guidance equivalent to `git diff main..HEAD`
- **THEN** the regression audit fails and identifies the skill and line

#### Scenario: Frozen target comparison is used
- **WHEN** a source skill compares `<BASE_HEAD>..<CURRENT_HEAD>` or explicit pre/post snapshot hashes
- **THEN** the regression audit accepts the comparison

#### Scenario: Conventional fallback is descriptive
- **WHEN** a worktree skill lists `main/master/trunk` only as the final target-selection candidates and all later operations use `TARGET_BRANCH` or `TARGET_HEAD`
- **THEN** the regression audit does not classify that text as a fixed comparison baseline
