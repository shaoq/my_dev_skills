## Why

`new-worktree-apply` currently rejects an omitted target even though the related merge and parallel worktree workflows already use a deterministic fallback order. This creates an inconsistent interface, and existing handoff text can either fail outright or discard a target that is already known.

## What Changes

- Allow `new-worktree-apply` to infer a local target with the shared worktree fallback order when `--target` is omitted.
- Keep explicit targets on the no-second-confirmation deterministic path; route inferred targets through one complete interactive preflight confirmation.
- Standardize target-source labels, candidate eligibility, and post-selection no-fallback behavior across all three worktree skills.
- Preserve fail-closed behavior for invalid explicit targets, unusable inferred targets, target drift, and unsafe target worktrees.
- Pass an already selected target through completion-check implementation hints instead of asking the next skill to infer it again.
- Align the invocation-governance specification, README examples, and worktree lifecycle regression tests with the two-path contract.
- Repair the lifecycle test's stale reference to the archived return-contract delta.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `worktree-targeting`: Extend single-change worktree apply with deterministic target inference plus an interactive confirmation path.
- `skill-invocation-governance`: Define confirmation at the side-effect boundary according to whether the target and source plan are explicit and deterministic.

## Impact

Affected files include all three worktree lifecycle skills, the completion-check skill, shared OpenSpec specifications, README workflow documentation, and worktree lifecycle contract tests. Git operations remain local and continue to use a frozen target commit hash; no runtime dependency or external API changes are introduced.
