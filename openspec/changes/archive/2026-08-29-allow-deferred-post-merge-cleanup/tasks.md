## 1. Regression tests

- [x] 1.1 Add return-workflow assertions for exact deferred-task classification, ordinary-task blocking, user-owned execution, and incomplete/non-archivable reporting.
- [x] 1.2 Run the focused worktree lifecycle suite and record the expected RED failures against the old `DONE == TOTAL` rule.

## 2. Return workflow

- [x] 2.1 Update `merge-worktree-return/SKILL.md` to compute and report `TASK_CLEANUP_POLICY_PASSED` without executing or marking deferred tasks.
- [x] 2.2 Preserve every existing identity, containment, frozen-hash, merge, verification, and ordinary cleanup gate.

## 3. Documentation and specification

- [x] 3.1 Update README guidance for user-owned `[post-merge-verification]` tasks and non-archivable status after cleanup.
- [x] 3.2 Apply the approved `worktree-targeting` delta to the canonical specification for the single-return workflow.

## 4. Verification

- [x] 4.1 Run the worktree lifecycle, target-aware verification, and setup environment test suites.
- [x] 4.2 Run strict validation for the new and directly related OpenSpec changes plus `git diff --check`.
- [x] 4.3 Run GitNexus `detect_changes` before committing and confirm the change remains scoped to return workflow documentation/tests/specification.

## 5. Parallel workflow consistency

- [x] 5.1 Add regression assertions for per-child deferred-task classification, user-owned execution, cleanup eligibility, and dependency-Wave advancement.
- [x] 5.2 Run the focused worktree lifecycle suite and record the expected RED failures against the current `tasks 全部完成` gate.
- [x] 5.3 Update `parall-new-worktree-apply/SKILL.md` to use `TASK_CLEANUP_POLICY_PASSED` per child without executing or modifying deferred tasks.
- [x] 5.4 Update README and the canonical `Parallel apply uses one confirmed target` requirement.
- [x] 5.5 Run all regression suites, strict OpenSpec validation, `git diff --check`, and GitNexus `detect_changes` before committing.

## 6. Conditional return authorization regression tests

- [x] 6.1 Add focused assertions that the current unconditional confirmation blocks an otherwise valid explicit-target, clean-source return; record the expected RED result before changing the Skill.
- [x] 6.2 Add deterministic-path cases for an explicit proposal and for a proposal derived from the exact canonical `worktree-` branch, both with an explicit non-main target and clean source.
- [x] 6.3 Add compatibility cases proving that an inferred target still requires confirmation and keeps the existing target fallback order.
- [x] 6.4 Add dirty-source cases proving that pending files disable the deterministic path, are all displayed in one interactive plan, and are committed only after affirmative confirmation and stable revalidation.
- [x] 6.5 Add negative cases for status/review-only requests, pre-write drift, missing/ambiguous canonical identity, and deterministic-path rebase/merge conflicts; prove zero unconfirmed writes and preserved recovery objects.
- [x] 6.6 Add regression assertions that no caller-runtime mode, Issue/task-platform authorization envelope, or generic `--yes`/`--authorized` flag is introduced.

## 7. Conditional single-return workflow

- [x] 7.1 Update `merge-worktree-return/SKILL.md` to classify clear limited return authorization, explicit versus inferred target source, and strict source cleanliness from observable facts.
- [x] 7.2 Add `DETERMINISTIC_RETURN_READY` so a clear return request with an explicit target, clean canonical source, complete preflight, and stable final revalidation proceeds without a second confirmation.
- [x] 7.3 Preserve optional proposal derivation and optional target fallback; require the existing complete interactive confirmation whenever the target is inferred.
- [x] 7.4 Preserve confirmation-authorized pending-source commit behavior only in the interactive path; ensure the deterministic path never stages or commits pending files.
- [x] 7.5 Make any deterministic-path drift require a fresh invocation, and stop/abort safely on rebase or merge conflicts without inventing an unconfirmed resolution.
- [x] 7.6 Report the selected authorization path, proposal/target source, immutable snapshots, pending-file policy, deferred-task status, and every retained recovery object.

## 8. Conditional authorization documentation and specification

- [x] 8.1 Update README examples for Team/direct-user deterministic returns and manual inferred-target or pending-source interactive returns.
- [x] 8.2 Apply the approved conditional authorization scenarios to the canonical `worktree-targeting` specification without changing the parallel workflow's existing confirmation boundary.
- [x] 8.3 Review the Skill description and argument hint for compatibility with both paths; do not require proposal or target globally and do not describe the deterministic path as the only supported workflow.

## 9. Conditional authorization verification

- [x] 9.1 Run the focused worktree lifecycle suite and record GREEN results for every deterministic and interactive-path scenario.
- [x] 9.2 Run target-aware verification and setup environment regressions, strict validation for this and directly related OpenSpec changes, and `git diff --check`.
- [x] 9.3 Run GitNexus `detect_changes` before committing and confirm the implementation remains scoped to `merge-worktree-return`, its tests, README, and canonical specification.
