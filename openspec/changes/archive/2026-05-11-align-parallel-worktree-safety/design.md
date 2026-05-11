## Context

`parall-new-worktree-apply` has two execution layers:

1. Spawned agents apply individual OpenSpec changes in isolated worktrees.
2. The main controller waits for each batch, then serially rebases and merges successful branches back into the main working tree.

The recent `cross-platform-worktree-cwd-fix` change updated `new-worktree-apply`, `merge-worktree-return`, and the parallel agent prompt so worktree creation/exit behaves correctly in Claude Code and Codex-like environments. However, the parallel main-controller merge flow still assumes the branch is named `main`, performs weaker merge verification, and does not explicitly verify that merge commands run from the expected CWD and branch.

## Goals / Non-Goals

**Goals:**
- Align the parallel main-controller merge flow with the single-worktree skills' main-branch detection strategy.
- Remove hardcoded `main` references from parallel rebase, checkout, merge, and conflict-resolution instructions.
- Add CWD and branch verification around serial merge operations.
- Strengthen merge verification so the controller confirms the worktree branch has no commits ahead of the detected main branch after merge.
- Update README to accurately describe cross-platform worktree behavior.

**Non-Goals:**
- Do not change proposal decomposition behavior.
- Do not change `MAX_PARALLEL = 3` or batch scheduling.
- Do not change `dependencies.yaml` format.
- Do not introduce retry orchestration or new conflict-resolution algorithms.
- Do not modify the single-worktree skills beyond using them as the behavioral reference.

## Decisions

### D1: Reuse the single-worktree main-branch detection strategy

`parall-new-worktree-apply` should detect `MAIN_BRANCH` with the same priority used by `new-worktree-apply` and `merge-worktree-return`: `main`, then `master`, then `trunk`, then `origin` HEAD fallback.

This avoids a split-brain workflow where single-change skills work on non-`main` repositories but parallel apply fails.

Alternative considered: keep requiring `main` for the parallel skill. This is simpler but inconsistent with the rest of the worktree workflow and unnecessarily excludes supported repositories.

### D2: Treat CWD/branch verification as part of the controller contract

The spawned agent prompt already verifies CWD before applying and committing. The controller should also verify:
- before starting each batch merge, it is in the main working tree;
- before merging each branch, the current branch is `<MAIN_BRANCH>`;
- after merge and cleanup/backfill, the current branch remains `<MAIN_BRANCH>`.

This catches wrong-directory execution before it can merge into the wrong branch or inspect the wrong `tasks.md`.

Alternative considered: rely on `git checkout <MAIN_BRANCH>` alone. That switches branches but does not prove the command is running from the intended working tree path, which is the exact class of issue the recent CWD fix addressed.

### D3: Use branch-ahead verification instead of HEAD-only verification

The current parallel skill says `git log --oneline -1` confirms HEAD advanced. That is not enough: it does not prove all commits from the worktree branch are now included in `<MAIN_BRANCH>`.

The parallel flow should use the single-worktree pattern:

```bash
git log <MAIN_BRANCH>..<branch>
```

The result must be empty. If it is not empty, the merge is incomplete and the controller must not treat that branch as merged.

Alternative considered: compare HEAD before/after merge. That detects movement but still cannot prove the specific branch was fully integrated.

### D4: Keep agent-level platform adaptation, add controller-level safety

The existing agent prompt platform adaptation remains valid. This change should not duplicate worktree creation logic in the controller. It should instead make the controller's serial merge phase robust after agents return.

## Risks / Trade-offs

- **[False failure if branch detection finds the wrong default]** -> Mitigation: use the established single-worktree detection order and origin HEAD fallback.
- **[Extra checks make the skill text longer]** -> Mitigation: keep checks localized to Step 0 and Step 5, and avoid changing unrelated sections.
- **[README and SKILL.md drift again]** -> Mitigation: include README updates in the task list and spec requirements.
- **[Merge verification failure leaves branches unmerged]** -> Mitigation: report the exact branch and command result, skip cleanup, and continue with other safe branches where possible.
