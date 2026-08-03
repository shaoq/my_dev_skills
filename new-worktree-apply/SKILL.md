---
name: new-worktree-apply
description: Create a git worktree branch for an OpenSpec proposal and apply it. Use when starting implementation of an OpenSpec change in an isolated worktree. Requires git and openspec CLI. All Git write actions happen only after an explicit preflight confirmation.
argument-hint: <proposal-name> [--target <target-branch>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(test *) Bash(head *) Bash(sed *) EnterWorktree ExitWorktree Read Write Edit Glob Grep Skill AskUserQuestion
---

Create a git worktree for an OpenSpec proposal and start applying it.

**Input**: A proposal name (required) and an optional `--target <target-branch>` flag. The proposal branch and worktree are created with the selected target as the explicit start point.

Examples:
- `/new-worktree-apply add-user-auth`
- `/new-worktree-apply add-user-auth --target develop`

**BREAKING**: The legacy `--branch` option is replaced by `--target`. If `--branch` is supplied, this skill performs **no Git write** and prints the equivalent `--target` invocation. See Step 1.

**Invariant (read-only before confirmation)**: Steps 1–6 perform no Git write and do not invoke any apply skill. `git add`, `git commit`, `git checkout`/`git switch`, `git worktree add`/remove, `git rebase`, `git merge`, and `openspec apply` only run in Step 7 onward — after confirmation and snapshot revalidation.

**Steps**

1. **Parse arguments and validate prerequisites** (read-only)

   Extract the proposal name and optional `--target <target-branch>` from `$ARGUMENTS`.

   **Argument rules:**
   - Exactly one positional argument is allowed (the proposal name). Zero or more than one positional → argument error, no Git write.
   - `--target <target-branch>` is the only accepted option. `--target` may appear at most once.
   - If `--target` is given without a value, or a value is given without `--target`, or any unknown option appears → argument error, no Git write.

   **Legacy `--branch` handling (zero-write migration):**
   - If `--branch <name>` is detected → stop immediately, perform **no Git write**, and print:
     ```
     ## Error: legacy option --branch

     `--branch` has been replaced by `--target`. Use instead:

         /new-worktree-apply <proposal-name> --target <name>

     No Git state was changed.
     ```
   - `--branch` is not a silent alias and triggers no fallback.

   If no proposal name is provided and no legacy option was used, use the **AskUserQuestion tool** to ask:
   > "What proposal do you want to create a worktree for?"

   Then run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo → error: "Must be inside a git repository."
   - No openspec CLI → error: "OpenSpec CLI is required. Install it first."

   Validate the proposal exists (read-only):
   ```bash
   test -d openspec/changes/<proposal-name>
   ```
   If not found → error with list of available proposals from `openspec list --json`.

   Validate the proposal name conforms to worktree naming rules (only lowercase letters, digits, dots, underscores, hyphens; max 64 characters). If invalid → error with the naming constraints. No Git write occurs.

2. **Select the target branch** (read-only)

   Select `TARGET_BRANCH` using this exact order, recording `TARGET_SOURCE` for the confirmation summary and final report:

   1. **Explicit `--target`** — if supplied, it MUST exist as a local branch in `refs/heads/`. Verify:
      ```bash
      git rev-parse --verify --quiet refs/heads/<target-branch>
      ```
      If it does not exist → error: "Target branch '<name>' does not exist locally." Do **not** fetch, do **not** create it, do **not** fall back. Stop, no Git write.
      Set `TARGET_SOURCE="explicit --target"`.
   2. **Primary worktree's checked-out branch** — if no explicit target, read the primary worktree branch from `git worktree list --porcelain` (Step 3) and confirm it is a valid local ref:
      ```bash
      git rev-parse --verify --quiet refs/heads/<primary-branch>
      ```
      Usable → `TARGET_BRANCH=<primary-branch>`, `TARGET_SOURCE="primary worktree current branch"`.
   3. **`origin/HEAD` local same-name branch** — if the primary branch is unusable (detached or absent), read the default remote name:
      ```bash
      git rev-parse --abbrev-ref origin/HEAD 2>/dev/null | sed 's#^origin/##'
      ```
      If the resulting name exists in `refs/heads/` → `TARGET_BRANCH=<name>`, `TARGET_SOURCE="origin/HEAD local branch"`.
   4. **Conventional fallback** — first existing local branch among `main`, `master`, `trunk`:
      ```bash
      for b in main master trunk; do git rev-parse --verify --quiet refs/heads/$b && break; done
      ```
      Usable → `TARGET_BRANCH=<b>`, `TARGET_SOURCE="conventional fallback"`.

   If no candidate is usable → error: "No target branch could be selected. Provide `--target <branch>`." No Git write.

3. **Resolve worktree topology** (read-only)

   Use `git worktree list --porcelain` to record:
   - `PRIMARY_WORKTREE_DIR` — the worktree marked `bare` or listed first (the main working tree).
   - `INVOCATION_WORKTREE_DIR` — the worktree whose path equals the current `git rev-parse --show-toplevel`.
   - `TARGET_WORKTREE_DIR` — the worktree (if any) where `TARGET_BRANCH` is already checked out.

   ```bash
   git worktree list --porcelain
   git rev-parse --show-toplevel
   ```

   **Topology rules:**
   - If `TARGET_BRANCH` is checked out in a non-invocation worktree → record it as `TARGET_WORKTREE_DIR`; do not plan a duplicate checkout.
   - If `TARGET_BRANCH` is not checked out anywhere → record that a post-confirmation `git checkout` of `TARGET_BRANCH` in the clean primary worktree is required (only when the primary worktree is clean and can switch safely). If the primary worktree cannot switch safely → error with recovery guidance, stop before confirmation.
   - **Detached HEAD is unsupported** for the required target/source: if the primary worktree that must supply the target is detached (and no explicit target was given) → error: "Primary worktree is in detached HEAD state. Use `--target <branch>`." No Git write.

4. **Read state for the preflight summary** (read-only)

   Record the true target HEAD and pending state **without writing**:
   ```bash
   TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
   git -C <PRIMARY_WORKTREE_DIR> status --porcelain
   ```

   Validate the proposal branch does not already exist (read-only):
   ```bash
   git branch --list <proposal-name>
   ```
   If it already exists → error: "Branch '<proposal-name>' already exists. Choose a different name or delete it with `git branch -D <proposal-name>`." Stop, no Git write.

   Read OpenSpec artifact status (read-only):
   ```bash
   openspec status --change "<proposal-name>" --json
   ```
   Record whether every artifact is `done` and whether `isComplete` is `true`.

5. **Preflight summary and confirmation** (read-only; no Git write)

   Display a single read-only summary, then request an **explicit** affirmative response with **no default value and no timed approval**. Use the **AskUserQuestion tool**.

   The summary MUST include:
   - Command scope: `new-worktree-apply <proposal-name>`.
   - Target branch, `TARGET_SOURCE`, and `TARGET_HEAD`.
   - `TARGET_WORKTREE_DIR` (or the planned post-confirmation checkout) and `PRIMARY_WORKTREE_DIR`.
   - Any pending changes in the primary/target worktree that the plan will auto-commit (with file list), or "no pending changes".
   - The planned write operations: auto-commit (if needed), optional `git checkout <TARGET_BRANCH>` in the clean primary worktree, `git worktree add`/`EnterWorktree` from `TARGET_HEAD`, then `openspec apply`, task backfill, and `git commit`.
   - Risk warnings: proposal branch does not exist yet (it will be created); whether a checkout of the primary worktree is required.

   **Confirmation handling:**
   - **User confirms** → proceed to Step 6 (snapshot revalidation).
   - **User declines or cancels** → stop, no Git write, do not invoke apply.
   - **Response is missing or ambiguous** → pause for explicit input, no Git write.
   - **No interaction tool is available** → print the question in the response, end the current execution, and wait for the next user message. No Git write.

6. **Snapshot revalidation** (read-only, immediately before the first write)

   Re-run the read-only checks from Steps 1–4 and compare against the confirmed summary. Revalidate:
   - Parsed arguments (proposal, target).
   - `TARGET_BRANCH` ref still resolves and `TARGET_HEAD` is unchanged.
   - Worktree mapping (`PRIMARY_WORKTREE_DIR`, `TARGET_WORKTREE_DIR`) unchanged.
   - Pending-change state of the target/primary worktree.
   - Required checkout (still needed / still safe).
   - Displayed risk warnings.

   **If any material fact changed** while waiting → invalidate the confirmation, display the updated summary, and request a new confirmation (back to Step 5). No Git write until re-confirmed.

   **If everything matches** → proceed to Step 7.

7. **Execute confirmed writes** (writes begin here)

   7a. **Handle pending target/primary worktree changes** — if the confirmed summary said pending changes will be auto-committed:
   ```bash
   git add -A
   git commit -m "chore: auto-commit before worktree for <proposal-name>"
   ```
   If the commit advanced `TARGET_BRANCH` (e.g. the target worktree had changes on `TARGET_BRANCH`), **refresh** `TARGET_HEAD`:
   ```bash
   TARGET_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
   ```
   All later creation steps use this refreshed snapshot.

   If there were no pending changes → announce "Working directory clean, proceeding."

   7b. **Make the target available** — only if `TARGET_BRANCH` is not checked out anywhere:
   - The clean primary worktree (confirmed clean in Step 4/6) checks out the target:
     ```bash
     git -C <PRIMARY_WORKTREE_DIR> checkout <TARGET_BRANCH>
     ```
   - This is a confirmed, displayed write. If the primary worktree is not clean or cannot switch, do not proceed — report and stop.

   7c. **Create the worktree from `TARGET_HEAD`** — choose by environment:

   **Claude Code (EnterWorktree available):**
   - `EnterWorktree` branches from the **current HEAD**, so the primary worktree MUST be on `TARGET_BRANCH` (ensured by 7b) before creation. This is the "target checkout context".
   - Call `EnterWorktree` with `name: <proposal-name>`.
   - If the platform cannot prove it will branch from `TARGET_HEAD` (primary worktree is not on `TARGET_BRANCH` and cannot be aligned) → **stop safely** instead of silently using another HEAD. Do not fall back.

   **Other environments (Codex CLI, EnterWorktree unavailable):**
   - Create with an **explicit start point**:
     ```bash
     git worktree add .claude/worktrees/<proposal-name> -b <proposal-name> <TARGET_BRANCH>
     cd .claude/worktrees/<proposal-name>
     ```
   - The explicit `<TARGET_BRANCH>` start point guarantees the base is `TARGET_HEAD`.

   If creation fails → report the failure. Do not attempt a manual fallback in Claude Code.

   7d. **CWD verification (mandatory):**
   ```bash
   pwd
   git branch --show-current
   ```
   Expected:
   - `pwd` shows the worktree path containing `<proposal-name>`.
   - `git branch --show-current` shows `<proposal-name>`.

   If verification fails → stop:
   > "CWD 验证失败：当前目录 <pwd> 或分支 <branch> 不符合预期。"
   >
   > **Recovery:** manually `cd .claude/worktrees/<proposal-name>`, or re-run `git worktree add .claude/worktrees/<proposal-name> -b <proposal-name> <TARGET_BRANCH>`.

8. **Verify HEAD consistency** (read)

   ```bash
   WORKTREE_HEAD=$(git rev-parse HEAD)
   ```
   Compare `$WORKTREE_HEAD` with `$TARGET_HEAD` (recorded in Step 4, refreshed in 7a).

   - **Match** → announce: "HEAD verified: worktree starts exactly from <TARGET_BRANCH>."
   - **Differ** → **stop**. Do **not** hide the mismatch with `git merge <TARGET_BRANCH>`. Report:
     > "Base mismatch: worktree HEAD <WORKTREE_HEAD> != target HEAD <TARGET_HEAD>. Aborting apply.
     > Recovery: remove the worktree (`ExitWorktree` action `remove`, or `git worktree remove .claude/worktrees/<proposal-name>` from a non-source dir), verify `TARGET_BRANCH`, and retry."

9. **Pre-apply OpenSpec artifact validation** (read)

   ```bash
   openspec status --change "<proposal-name>" --json
   ```
   Verify:
   - All artifacts in `artifacts` have `status: "done"`.
   - `isComplete` is `true`.

   Also verify key files exist:
   ```bash
   test -f openspec/changes/<proposal-name>/proposal.md
   test -f openspec/changes/<proposal-name>/design.md
   test -f openspec/changes/<proposal-name>/tasks.md
   ls openspec/changes/<proposal-name>/specs/*.md 2>/dev/null
   ```

   **If any check fails:** list missing/incomplete artifacts, error: "Artifacts not ready for apply: <list>.", and stop — do not invoke apply.

10. **Execute OpenSpec apply** (in the proposal worktree)

    Use the **Skill tool** to invoke `openspec-apply-change` with the proposal name:
    ```
    Skill("openspec-apply-change", args="<proposal-name>")
    ```
    Alternatively: `Skill("opsx:apply", args="<proposal-name>")`.

    This runs inside the correct proposal worktree (verified in Step 7d).

11. **Post-apply task verification and backfill**

    ```bash
    TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<proposal-name>/tasks.md)
    DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<proposal-name>/tasks.md)
    ```

    If `DONE < TOTAL`, perform automatic backfill:

    a. Read `openspec/changes/<proposal-name>/tasks.md` and collect all lines with `- [ ]`.
    b. For each unmarked task, parse its description to extract file path patterns:
       - Text inside backticks (e.g. `` `SKILL.md` ``, `` `src/auth.py` ``) → check if file exists
       - "创建 `xxx/` 目录" → check if directory exists
       - "编写 frontmatter" → check if referenced file contains `---` frontmatter
       - "实现 xxx" → check if related code files exist (keyword matching)
    c. If the referenced file/directory exists, change `- [ ]` to `- [x]`.
    d. Output a backfill report.
    e. If tasks remain `[ ]`, list them but do not stop.

12. **Force-add tasks.md and commit**

    Since `openspec/` is in `.gitignore`, force-add `tasks.md`:
    ```bash
    git add -A
    git add -f openspec/changes/<proposal-name>/tasks.md
    ```
    Count final completion:
    ```bash
    DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<proposal-name>/tasks.md)
    TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<proposal-name>/tasks.md)
    ```
    Commit with completion-aware message:
    - `DONE == TOTAL`: `git commit -m "feat: implement <proposal-name> (DONE/TOTAL tasks)"`
    - `DONE < TOTAL`: `git commit -m "feat: implement <proposal-name> (DONE/TOTAL tasks, partial)"`

    If no changes to commit, skip.

**Output On Success**

```
## Worktree Created & Apply Complete

**Proposal:** <proposal-name>
**Branch:** <proposal-name>
**Target branch:** <TARGET_BRANCH> (selected via <TARGET_SOURCE>)
**Base verified:** ✓ (worktree starts from <TARGET_BRANCH> HEAD)
**Artifacts:** ✓ all done
**Tasks:** N/M complete (or "X/M partial")

### Task Backfill Report
Auto-marked: X tasks, Still incomplete: Y tasks

OpenSpec apply has completed in the worktree.
Use `/merge-worktree-return <proposal-name> --target <TARGET_BRANCH>` when ready to merge.
```

**Error Output Format**

```
## Error: <error-type>

**Step:** <which step failed>
**Reason:** <why it failed>

**Recovery:**
- <suggestion 1>
- <suggestion 2>
```

**Guardrails**
- Steps 1–6 are read-only: no Git write and no apply before explicit confirmation.
- Verify each step succeeds before proceeding to the next.
- The worktree MUST start from `TARGET_HEAD` exactly; a mismatch aborts apply and is never hidden by `git merge`.
- Never delete or overwrite existing branches.
- Only use `--force` for `git add -f` on tasks.md (to bypass `.gitignore`).
- Never use `--force` on `git push`, `git merge`, `git rebase`, or `git checkout`.
- Commit messages include the proposal name for traceability.
- If `EnterWorktree` cannot branch from `TARGET_HEAD`, stop — do not silently use another HEAD or fall back to manual creation in Claude Code.
- All git command failures should stop execution immediately.
- **在 Claude Code 环境下，禁止使用 `git worktree add` 替代 `EnterWorktree`** — 必须使用内置工具以确保 CWD 正确切换。
- CWD 验证（Step 7d）不可跳过，验证失败必须停止执行。
- Confirmation has no default and no timed approval; a missing/ambiguous response leaves Git unchanged.
