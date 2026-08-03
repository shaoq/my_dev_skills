---
name: merge-worktree-return
description: Commit worktree changes, rebase onto the confirmed target, merge back to the target branch, and exit the worktree. Use when finishing implementation in a worktree. Optional proposal name verifies OpenSpec completion. Requires git. All Git write actions happen only after an explicit preflight confirmation.
argument-hint: [proposal-name] [--target <target-branch>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(awk *) Bash(sed *) Bash(cat *) Bash(head *) Bash(test *) EnterWorktree ExitWorktree Read Write Edit Glob Grep Skill AskUserQuestion
---

Commit worktree changes, merge back to the confirmed target branch, and exit the worktree safely.

**Input**: An optional proposal name and an optional `--target <target-branch>` flag.

Examples:
- `/merge-worktree-return`
- `/merge-worktree-return add-user-auth`
- `/merge-worktree-return add-user-auth --target develop`

**Invariant (read-only before confirmation)**: Steps 1–6 perform no Git write and do not invoke apply. `git add`, `git commit`, `git checkout`/`git switch`, `git rebase`, `git merge`, `git worktree remove`, and `ExitWorktree` only run in Step 7 onward — after confirmation and snapshot revalidation.

**Steps**

1. **Parse arguments and validate prerequisites** (read-only)

   Extract the optional proposal name and optional `--target <target-branch>` from `$ARGUMENTS`.

   **Argument rules:**
   - Zero or one positional argument (the proposal name). More than one → argument error, no Git write.
   - `--target <target-branch>` is the only accepted option and may appear at most once.
   - Missing target value, value without `--target`, duplicate `--target`, or unknown option → argument error, no Git write.

   Run prerequisite checks (read-only):
   ```bash
   git rev-parse --is-inside-work-tree
   git rev-parse --is-inside-work-tree && cat .git | head -1
   ```
   If `.git` does not start with `gitdir:` → error: "Not in a worktree. This skill must be run from inside a worktree branch." Stop, no Git write.

2. **Select the target branch** (read-only)

   Select `TARGET_BRANCH` using this exact order, recording `TARGET_SOURCE`:

   1. **Explicit `--target`** — if supplied, it MUST exist locally:
      ```bash
      git rev-parse --verify --quiet refs/heads/<target-branch>
      ```
      If absent → error: "Target branch '<name>' does not exist locally." Do not fetch/create/fallback. Stop, no Git write. `TARGET_SOURCE="explicit --target"`.
   2. **Primary worktree's checked-out branch** — read from `git worktree list --porcelain` (Step 3); if it is a valid local ref → `TARGET_SOURCE="primary worktree current branch"`.
   3. **`origin/HEAD` local same-name branch**:
      ```bash
      git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's#^origin/##'
      ```
      If the resulting name exists in `refs/heads/` → `TARGET_SOURCE="origin/HEAD local branch"`.
   4. **Conventional fallback** — first existing local branch among `main`, `master`, `trunk`.

   If no candidate is usable → error: "No target branch could be selected. Provide `--target <branch>`." No Git write.

3. **Resolve worktree topology and source** (read-only)

   ```bash
   git worktree list --porcelain
   git rev-parse --show-toplevel
   git branch --show-current
   ```

   Record:
   - `SOURCE_WORKTREE_DIR` = the current worktree path (`git rev-parse --show-toplevel`).
   - `SOURCE_BRANCH` = `git branch --show-current`. **If the source is in detached HEAD** → error: "Source worktree is in detached HEAD state. A named source branch is required." No Git write.
   - `PRIMARY_WORKTREE_DIR` = the main working tree.
   - `TARGET_WORKTREE_DIR` = the worktree where `TARGET_BRANCH` is already checked out (may equal `PRIMARY_WORKTREE_DIR`).

   **Validate source ≠ target:** if `SOURCE_BRANCH == TARGET_BRANCH` → error: "Source and target are the same branch ('<branch>'). Nothing to merge." No Git write.

   **If `TARGET_BRANCH` is not checked out in any worktree:**
   - If the primary worktree is clean and is not the source worktree → plan a post-confirmation `git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>`; set `TARGET_WORKTREE_DIR=<PRIMARY_WORKTREE_DIR>`.
   - Otherwise → error: "Target '<TARGET_BRANCH>' is not checked out and the primary worktree cannot switch safely. Check it out first." Stop before confirmation.

4. **Read state for the preflight summary** (read-only)

   ```bash
   git status --porcelain                                   # source pending changes
   git -C <TARGET_WORKTREE_DIR> status --porcelain          # target MUST be clean
   git rev-parse refs/heads/<TARGET_BRANCH>                 # TARGET_HEAD
   git rev-parse refs/heads/<SOURCE_BRANCH>                 # SOURCE_HEAD
   ```

   **Target worktree must be clean:** if the target worktree has uncommitted changes → error: "Target worktree '<TARGET_WORKTREE_DIR>' has uncommitted changes. Commit or stash them first." Stop before confirmation, no merge into that worktree.

   **OpenSpec proposal check (only if proposal name provided):**
   ```bash
   openspec status --change "<proposal-name>" --json
   ```
   Read `openspec/changes/<proposal-name>/tasks.md` and count `- [x]` vs `- [ ]`. Record incomplete task count and list for the confirmation summary (do not confirm separately — fold into Step 5).

   If no proposal name → skip the proposal check.

5. **Preflight summary and confirmation** (read-only; no Git write)

   Display a single read-only summary, then request an **explicit** affirmative response with **no default and no timed approval** via the **AskUserQuestion tool**.

   The summary MUST include:
   - Command scope: `merge-worktree-return` + proposal (or "N/A").
   - `SOURCE_BRANCH` → `TARGET_BRANCH`, with `TARGET_SOURCE` and `TARGET_HEAD`.
   - `SOURCE_WORKTREE_DIR` and `TARGET_WORKTREE_DIR`.
   - Pending source changes that the plan will auto-commit (file list), or "no pending changes".
   - Planned writes: source auto-commit, `git rebase <TARGET_BRANCH>` (with conflict handling), merge `SOURCE_BRANCH` into `TARGET_BRANCH` inside `TARGET_WORKTREE_DIR`, then worktree removal.
   - Risk warnings: incomplete OpenSpec tasks (if any) — explicitly ask whether to merge despite the risk; required target/primary checkout (if any).

   **Confirmation handling:**
   - **Confirm** → proceed to Step 6.
   - **Decline/cancel** → stop, no Git write, no apply.
   - **Missing/ambiguous** → pause for explicit input, no Git write.
   - **No interaction tool** → print the question, end the current execution, wait for the next message. No Git write.

6. **Snapshot revalidation** (read-only, immediately before the first write)

   Revalidate the parsed arguments, `SOURCE_BRANCH`, `TARGET_BRANCH` ref + `TARGET_HEAD`, `SOURCE_HEAD`, worktree mapping, target cleanliness, source pending state, required checkout, and displayed warnings.

   **If any material fact changed** → invalidate the confirmation, display an updated summary, request a new confirmation. No Git write.

   **If everything matches** → proceed to Step 7.

7. **Execute confirmed writes** (writes begin here)

   7a. **Commit source changes** (if pending):
   ```bash
   git add -A
   git commit -m "chore: auto-commit before merge from worktree"
   ```
   If no changes → announce "No uncommitted changes." Record `SOURCE_HEAD=$(git rev-parse refs/heads/<SOURCE_BRANCH>)`.

   7b. **Make the target available** (only if `TARGET_BRANCH` was not checked out and the plan said so):
   ```bash
   git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>
   ```

   7c. **Rebase source onto target:**
   ```bash
   git rebase <TARGET_BRANCH> <SOURCE_BRANCH>
   ```
   - **Success** → announce "Rebase onto <TARGET_BRANCH> completed."
   - **Conflicts** → list `git diff --name-only --diff-filter=U`, read each file, resolve markers (`<<<<<<<`, `=======`, `>>>>>>>`) preferring source changes unless the target version is clearly more appropriate, `git add <resolved>`, `GIT_EDITOR=true git rebase --continue`.
   - **Unresolvable** → `git rebase --abort`, report conflicting files, and stop. Do not remove the worktree.

8. **Merge into the target worktree and verify containment** (writes)

   ```bash
   cd <TARGET_WORKTREE_DIR>
   git merge <SOURCE_BRANCH>
   ```
   - **Conflicts** → resolve the same way as Step 7c, stage and commit.

   **Containment verification** — every source commit must now be in target:
   ```bash
   git log <TARGET_BRANCH>..<SOURCE_BRANCH>
   ```
   This MUST return empty. If it returns commits → merge verification **failed**: report and do **not** proceed to exit/remove. The source worktree is preserved for recovery.

9. **Safely exit the worktree** (only after verification succeeds)

   Confirm ALL of:
   - [x] Step 7a: source files committed
   - [x] Step 7c: rebase completed
   - [x] Step 8: merge verified (`git log <TARGET_BRANCH>..<SOURCE_BRANCH>` empty)
   - [x] Step 4/5: if proposal name given, proposal complete or user confirmed despite incomplete tasks

   Only if ALL pass, choose by environment:

   **Claude Code (ExitWorktree available):**
   - Use `ExitWorktree` with `action: "remove"`.

   **Other environments (ExitWorktree unavailable):**
   - Step 8 already `cd`'d into `TARGET_WORKTREE_DIR` (non-source). Remove the source:
     ```bash
     git worktree remove <SOURCE_WORKTREE_DIR>
     ```

   After exit, verify:
   ```bash
   pwd
   git branch --show-current
   ```
   Confirm CWD is the target worktree and on `TARGET_BRANCH`.

**Output On Success**

```
## Worktree Merged & Closed

**Proposal:** <proposal-name> (or "N/A")
**Branch merged:** <SOURCE_BRANCH> → <TARGET_BRANCH>
**Target source:** <TARGET_SOURCE>
**Worktree:** removed
**Containment:** ✓ (<SOURCE_BRANCH> fully contained in <TARGET_BRANCH>)
**Current branch:** <TARGET_BRANCH>

All worktree changes have been successfully merged to <TARGET_BRANCH>.

下一步: 运行 `/check-changes-completed` 检查整体完成度，或 `/opsx:archive <proposal-name>` 归档此 change。
```

**Error Output Format**

```
## Error: <error-type>

**Step:** <which step failed>
**Source:** <SOURCE_BRANCH>
**Target:** <TARGET_BRANCH>

**Details:**
<specific error information>

**Recovery:**
- <suggestion 1>
- <suggestion 2>
```

**Guardrails**
- Steps 1–6 are read-only: no Git write and no apply before explicit confirmation.
- Source and target MUST differ; detached source HEAD is unsupported.
- The target worktree MUST be clean before merge; never merge into a dirty target.
- Never exit the worktree unless rebase succeeded AND `git log <TARGET_BRANCH>..<SOURCE_BRANCH>` is empty.
- Never use `--force` flags on git commands.
- If rebase fails, use `git rebase --abort` to return to a safe state.
- If merge containment verification fails, do **NOT** call `ExitWorktree` or `git worktree remove` — preserve the source worktree for recovery.
- OpenSpec incomplete-task warnings are part of the single preflight confirmation, never a separate gate.
- All git command failures should stop execution immediately.
- 非 Claude Code 环境下使用 `git worktree remove` 替代 `ExitWorktree`，Step 8 已确保 CWD 在目标工作树（非来源目录），无需额外 `cd`。
- Confirmation has no default and no timed approval; a missing/ambiguous response leaves Git unchanged.
