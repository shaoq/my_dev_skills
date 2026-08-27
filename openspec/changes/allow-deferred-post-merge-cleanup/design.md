## Context

The return workflow currently equates proposal completion with cleanup eligibility by requiring `DONE == TOTAL` after merge. Users intentionally leave some tests unchecked with the exact `[post-merge-verification]` tag because those tests must be run manually later in the target worktree. Preserving the source worktree adds no recovery value once delivery is merged and all Git safety gates pass.

## Goals / Non-Goals

**Goals:**

- Let `merge-worktree-return` distinguish ordinary incomplete work from explicitly deferred user-run verification.
- Permit ordinary cleanup only when every unchecked task is explicitly deferred and all existing structural gates pass.
- Keep deferred tasks visible and keep the OpenSpec change incomplete/non-archivable.

**Non-Goals:**

- Running, marking, staging, or committing deferred tests.
- Relaxing Git identity, containment, cleanliness, frozen-hash, merge, or cleanup gates.
- Changing `parall-new-worktree-apply`.

## Decisions

### Use an exact task-line tag

Only unchecked checkbox lines containing the exact literal `[post-merge-verification]` are deferred. Every other unchecked task is ordinary unfinished work and blocks cleanup. Missing/unreadable tasks, zero recognized tasks, or an unclassifiable result remain fail-closed.

Alternative: infer deferred tests from wording. Rejected because natural-language inference would make cleanup nondeterministic.

### Separate delivery cleanup from OpenSpec completion

The return workflow records `TASK_CLEANUP_POLICY_PASSED=true` when there are no ordinary unchecked tasks. Deferred tasks remain unchecked, are listed in the final report, and keep the change non-archivable. The Skill does not execute them.

Alternative: mark deferred tasks complete after merge. Rejected because the user explicitly owns their execution and marking them without evidence would be false reporting.

### Preserve every existing structural gate

`TASK_CLEANUP_POLICY_PASSED` is an additional explicit input to `CLEANUP_READY`; it does not replace target/source identity, frozen commit, containment, cleanliness, delivery, or post-merge integrity checks.

## Risks / Trade-offs

- [A tag is added accidentally] → Require the exact literal on the unchecked task line and display every deferred item in the confirmation and final report.
- [Cleanup is mistaken for completion] → State that the proposal remains incomplete/non-archivable and provide the target worktree/commit for later user verification.
- [Parallel behavior changes indirectly] → Scope instructions, tests, and the delta scenario specifically to `merge-worktree-return`.
