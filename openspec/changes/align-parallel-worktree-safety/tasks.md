## 1. Parallel Main-Branch Detection

- [ ] 1.1 Update `parall-new-worktree-apply/SKILL.md` Step 0.3 to detect `MAIN_BRANCH` using `main` -> `master` -> `trunk` -> `origin` HEAD fallback.
- [ ] 1.2 Update Step 0.3 error handling to stop before discovery/spawn when `MAIN_BRANCH` cannot be detected.
- [ ] 1.3 Replace the current branch check so it compares `git branch --show-current` against the detected `MAIN_BRANCH`.

## 2. Serial Merge Safety

- [ ] 2.1 Replace hardcoded `main` references in `parall-new-worktree-apply/SKILL.md` Step 5 with `<MAIN_BRANCH>`.
- [ ] 2.2 Replace hardcoded `main` references in Step 6 conflict-resolution text with `<MAIN_BRANCH>`.
- [ ] 2.3 Add controller CWD and branch verification before merging each successful branch.
- [ ] 2.4 Add post-merge verification that the controller remains on `<MAIN_BRANCH>`.
- [ ] 2.5 Strengthen merge verification from `git log --oneline -1` to `git log <MAIN_BRANCH>..<branch>` and require empty output.

## 3. Reporting And Recovery Guidance

- [ ] 3.1 Update failure reporting for CWD verification failures to include current `pwd`, current branch, expected main directory, and expected `MAIN_BRANCH`.
- [ ] 3.2 Update merge verification failure reporting to list the branch and remaining ahead commits.
- [ ] 3.3 Update final report language so skipped or unverified merges are distinguishable from Agent apply failures.

## 4. Documentation

- [ ] 4.1 Update `README.md` `parall-new-worktree-apply` notes to mention detected main branch instead of hardcoded main.
- [ ] 4.2 Update `README.md` `new-worktree-apply` and `merge-worktree-return` descriptions to mention Claude Code built-in tools plus non-Claude Code git worktree fallback.
- [ ] 4.3 Update `README.md` `parall-new-worktree-apply` description to mention controller-level CWD/branch and merge verification safeguards.

## 5. Verification

- [ ] 5.1 Run `openspec status --change align-parallel-worktree-safety --json` and confirm all apply-required artifacts are done.
- [ ] 5.2 Review `parall-new-worktree-apply/SKILL.md` to confirm no hardcoded `git rebase main`, `git checkout main`, or `git log main..` instructions remain in the merge path.
- [ ] 5.3 Review `README.md` to confirm documented behavior matches the updated skill instructions.
