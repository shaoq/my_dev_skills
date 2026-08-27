## Why

`merge-worktree-return` currently blocks cleanup whenever any proposal task remains unchecked. This incorrectly treats explicitly deferred `[post-merge-verification]` tasks as source-delivery failures even though the user, not the Skill, is responsible for running them later in the target worktree.

The return workflow also requires an interactive confirmation for every invocation, even when the caller already made an explicit return request, supplied the target branch, and presents a clean canonical source worktree. That confirmation is useful when the Skill inferred the target or proposes committing pending source changes, but it is redundant in a deterministic Team or direct-user return. Removing it globally would break the convenient manual workflow that derives the proposal, infers a target, and commits reviewed pending changes after confirmation.

## What Changes

- Classify unchecked tasks by an exact `[post-merge-verification]` tag.
- Allow merge and ordinary source cleanup when every unchecked task carries that tag and every structural merge/cleanup gate passes.
- Keep ordinary unchecked tasks as cleanup blockers.
- Do not execute, mark, stage, or commit deferred post-merge tasks; report them for the user to perform later in the target worktree.
- Keep the OpenSpec change incomplete and non-archivable until the user completes and marks the deferred tasks.
- Apply the same per-child classification, cleanup, reporting, and dependency-wave semantics in `parall-new-worktree-apply`.
- Add a deterministic no-second-confirmation path when a direct user, Team/subagent, or another Skill clearly requests the return, the target is explicit, the canonical source is clean, and every preflight gate passes.
- Preserve the interactive compatibility path when the target is inferred or the source has pending changes: display the resolved target and exact pending-file/commit plan, require one confirmation, then independently revalidate before writes.
- Preserve optional proposal derivation, optional target fallback, and confirmation-authorized source auto-commit for manual use; do not add runtime-specific modes, Issue authorization envelopes, or generic `--yes`/`--authorized` flags.
- Prevent the deterministic path from silently widening the reviewed delivery: it does not auto-commit pending files, and a rebase/merge conflict stops that path and preserves the source for a fresh decision.

## Capabilities

### New Capabilities

None.

### Modified Capabilities

- `worktree-targeting`: Refine single-return and parallel-child cleanup eligibility for explicitly deferred user-run post-merge verification tasks, and add a fact-based deterministic authorization path for clean explicit-target single returns without removing the interactive manual path.

## Impact

Affected surfaces are `merge-worktree-return/SKILL.md`, `parall-new-worktree-apply/SKILL.md`, their worktree lifecycle regression tests, README guidance, and the canonical `worktree-targeting` specification. The new authorization routing applies only to `merge-worktree-return`; the parallel workflow keeps its existing confirmation boundary. No application runtime, API, dependency, or remote operation changes.
