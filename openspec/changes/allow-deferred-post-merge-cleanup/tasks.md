## 1. Regression tests

- [x] 1.1 Add return-workflow assertions for exact deferred-task classification, ordinary-task blocking, user-owned execution, and incomplete/non-archivable reporting.
- [x] 1.2 Run the focused worktree lifecycle suite and record the expected RED failures against the old `DONE == TOTAL` rule.

## 2. Return workflow

- [x] 2.1 Update `merge-worktree-return/SKILL.md` to compute and report `TASK_CLEANUP_POLICY_PASSED` without executing or marking deferred tasks.
- [x] 2.2 Preserve every existing identity, containment, frozen-hash, merge, verification, and ordinary cleanup gate.

## 3. Documentation and specification

- [x] 3.1 Update README guidance for user-owned `[post-merge-verification]` tasks and non-archivable status after cleanup.
- [x] 3.2 Apply the approved `worktree-targeting` delta to the canonical specification without changing the parallel workflow.

## 4. Verification

- [x] 4.1 Run the worktree lifecycle, target-aware verification, and setup environment test suites.
- [x] 4.2 Run strict validation for the new and directly related OpenSpec changes plus `git diff --check`.
- [x] 4.3 Run GitNexus `detect_changes` before committing and confirm the change remains scoped to return workflow documentation/tests/specification.
