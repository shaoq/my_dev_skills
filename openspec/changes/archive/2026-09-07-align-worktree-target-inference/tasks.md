## 1. Regression Contract

- [x] 1.1 Repair the stale archived-delta fixture path so the existing lifecycle suite has a clean baseline.
- [x] 1.2 Add failing contract checks for optional single-apply target syntax, shared inference priority, explicit/inferred authorization paths, invalid-explicit no-fallback behavior, and target-preserving handoff.

## 2. Skill Behavior

- [x] 2.1 Update `new-worktree-apply/SKILL.md` with explicit deterministic and inferred interactive target paths, including dry-run and drift semantics.
- [x] 2.2 Update `check-changes-completed/SKILL.md` to pass its frozen target through the implementation hint.
- [x] 2.3 Align `merge-worktree-return` and `parall-new-worktree-apply` with standardized target-source labels and post-selection no-fallback behavior.

## 3. Normative and User Documentation

- [x] 3.1 Update the canonical worktree-targeting and skill-invocation-governance specifications to remove conflicting requirements.
- [x] 3.2 Update README syntax, workflow examples, inference behavior, confirmation rules, and backfill wording.

## 4. Verification

- [x] 4.1 Run strict OpenSpec validation, skill validation, focused lifecycle and target-aware verification suites, and repository consistency checks.
- [x] 4.2 Run GitNexus change detection and review the final diff without modifying unrelated working-tree changes.
