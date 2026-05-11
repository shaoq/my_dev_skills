## Why

`new-worktree-apply` and `merge-worktree-return` recently gained cross-platform worktree CWD safeguards, but `parall-new-worktree-apply` only absorbed those safeguards inside the spawned agent prompt. Its main-controller merge flow still hardcodes `main`, uses weaker merge verification, and does not consistently verify CWD/branch state before serial merges.

This creates a higher-risk gap in the parallel workflow: multiple worktree branches can be applied correctly by agents, then merged from the wrong branch, wrong directory, or wrong main-branch assumption.

## What Changes

- Update `parall-new-worktree-apply` to detect the main branch using the same strategy as the single-worktree skills: `main` -> `master` -> `trunk` -> remote default branch.
- Replace hardcoded `main` references in the serial merge and conflict-resolution flow with the detected `<MAIN_BRANCH>`.
- Add main-controller CWD and branch verification before and after each serial merge step.
- Strengthen merge verification to ensure the merged branch has no commits ahead of `<MAIN_BRANCH>` after merge.
- Keep the existing agent-level platform adaptation, and make the main-controller flow explicitly compatible with the same cross-platform CWD assumptions.
- Update README documentation so the parallel workflow reflects the current cross-platform worktree behavior.

## Capabilities

### New Capabilities
- `parallel-worktree-safety`: Safety requirements for the main-controller phase of parallel worktree apply, including main-branch detection, CWD/branch verification, and robust merge verification.

### Modified Capabilities
- `batch-concurrency-control`: Clarify that batch execution still merges serially after each batch, but now uses detected main-branch and stronger merge safety checks.

## Impact

- Affected files:
  - `parall-new-worktree-apply/SKILL.md`
  - `README.md`
- No new runtime dependencies.
- No change to `dependencies.yaml` format.
- No change to the max parallelism policy (`MAX_PARALLEL = 3`).
- Behavior becomes safer for repositories whose main branch is not named `main`, and for non-Claude Code environments where CWD must be handled explicitly.
