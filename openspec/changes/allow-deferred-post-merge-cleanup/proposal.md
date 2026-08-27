## Why

`merge-worktree-return` currently blocks cleanup whenever any proposal task remains unchecked. This incorrectly treats explicitly deferred `[post-merge-verification]` tasks as source-delivery failures even though the user, not the Skill, is responsible for running them later in the target worktree.

## What Changes

- Classify unchecked tasks by an exact `[post-merge-verification]` tag.
- Allow merge and ordinary source cleanup when every unchecked task carries that tag and every structural merge/cleanup gate passes.
- Keep ordinary unchecked tasks as cleanup blockers.
- Do not execute, mark, stage, or commit deferred post-merge tasks; report them for the user to perform later in the target worktree.
- Keep the OpenSpec change incomplete and non-archivable until the user completes and marks the deferred tasks.
- Limit the behavior change to `merge-worktree-return`; do not alter the parallel apply workflow.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `worktree-targeting`: Refine single-worktree return cleanup eligibility for explicitly deferred user-run post-merge verification tasks.

## Impact

Affected surfaces are `merge-worktree-return/SKILL.md`, its worktree lifecycle regression tests, README guidance, and the canonical `worktree-targeting` specification. No application runtime, API, dependency, remote operation, or parallel workflow changes.
