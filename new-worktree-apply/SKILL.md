---
name: new-worktree-apply
description: Create a git worktree branch for an OpenSpec proposal and apply it. Use when starting implementation of an OpenSpec change in an isolated worktree. Requires git and openspec CLI.
argument-hint: <proposal-name> [--branch <main-branch>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(test *) Bash(head *) Bash(sed *) Read Write Edit Glob Grep Skill AskUserQuestion
---

Create a git worktree for an OpenSpec proposal and start applying it.

**Input**: A proposal name (required) and an optional `--branch <main-branch>` flag. Example: `/new-worktree-apply add-user-auth` or `/new-worktree-apply add-user-auth --branch develop`.

**Steps**

1. **Parse arguments and validate prerequisites**

   Extract the proposal name and optional `--branch` flag from `$ARGUMENTS`.

   If no proposal name is provided, use the **AskUserQuestion tool** to ask:
   > "What proposal do you want to create a worktree for?"

   Then run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo → error: "Must be inside a git repository."
   - No openspec CLI → error: "OpenSpec CLI is required. Install it first."

   Validate the proposal exists:
   ```bash
   test -d openspec/changes/<proposal-name>
   ```
   If not found → error with list of available proposals from `openspec list --json`.

   Validate the proposal name conforms to worktree naming rules (only lowercase letters, digits, dots, underscores, hyphens; max 64 characters). If invalid → error with the naming constraints.

2. **Check git status and commit unsaved files**

   ```bash
   git status --porcelain
   ```

   If there are uncommitted files (any output):
   ```bash
   git add -A
   git commit -m "chore: auto-commit before worktree for <proposal-name>"
   ```

   If no changes, skip this step and announce: "Working directory clean, proceeding."

3. **Detect the main branch**

   If the user provided `--branch <name>`, use that value as `MAIN_BRANCH`.

   Otherwise, auto-detect by running:
   ```bash
   git rev-parse --verify main 2>/dev/null && echo "main"
   git rev-parse --verify master 2>/dev/null && echo "master"
   git rev-parse --verify trunk 2>/dev/null && echo "trunk"
   ```

   Use the first one that succeeds. If all fail, try:
   ```bash
   git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'
   ```

   If still undetectable → error: "Cannot detect main branch. Use --branch to specify."

   Record the main branch HEAD for later verification:
   ```bash
   MAIN_HEAD=$(git rev-parse HEAD)
   ```

4. **Check if branch already exists**

   ```bash
   git branch --list <proposal-name>
   ```

   If the branch already exists → error:
   > "Branch '<proposal-name>' already exists. Choose a different name or delete the existing branch with `git branch -D <proposal-name>`."

   Do NOT proceed. Let the user decide.

5. **Create the worktree**

   Use the **EnterWorktree** tool with:
   - `name`: the proposal name

   This creates a new branch named after the proposal, creates a worktree directory, and switches the session CWD.

   If EnterWorktree fails → error with the failure message. Suggest the user check git status and try manually.

6. **Verify HEAD consistency**

   ```bash
   WORKTREE_HEAD=$(git rev-parse HEAD)
   ```

   Compare `$WORKTREE_HEAD` with `$MAIN_HEAD` (recorded in Step 3).

   If they match → announce: "HEAD verified: worktree is up to date with <MAIN_BRANCH>."

   If they differ:
   ```bash
   git merge <MAIN_BRANCH>
   ```
   Announce: "Merged latest <MAIN_BRANCH> into worktree branch."

   If the merge has conflicts → resolve them (prefer worktree changes), then commit.

7. **Pre-apply OpenSpec artifact validation**

   Run the following checks to ensure all artifacts are ready for implementation:

   ```bash
   openspec status --change "<proposal-name>" --json
   ```

   Parse the JSON output. Verify:
   - All artifacts in the `artifacts` array have `status: "done"`
   - `isComplete` is `true`

   Also verify key files exist:
   ```bash
   test -f openspec/changes/<proposal-name>/proposal.md
   test -f openspec/changes/<proposal-name>/design.md
   test -f openspec/changes/<proposal-name>/tasks.md
   ls openspec/changes/<proposal-name>/specs/*.md 2>/dev/null
   ```

   **If any check fails:**
   - List the missing or incomplete artifacts
   - Error: "Artifacts not ready for apply: <list>. Complete them first (e.g., `/opsx:explore <proposal-name>`)."
   - Stop execution — do not proceed to apply.

8. **Execute OpenSpec apply**

   Use the **Skill tool** to invoke `openspec-apply-change` with the proposal name as the argument:
   ```
   Skill("openspec-apply-change", args="<proposal-name>")
   ```

   Alternatively, if using the command version:
   ```
   Skill("opsx:apply", args="<proposal-name>")
   ```

   This starts the implementation of the proposal within the worktree.

9. **Post-apply task verification and backfill**

   After `opsx:apply` completes, verify task completion status:

   ```bash
   TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<proposal-name>/tasks.md)
   DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<proposal-name>/tasks.md)
   ```

   If `DONE < TOTAL`, perform automatic backfill:

   a. Read `openspec/changes/<proposal-name>/tasks.md` and collect all lines with `- [ ]`.

   b. For each unmarked task, parse its description to extract file path patterns:
      - Text inside backticks (e.g., `` `SKILL.md` ``, `` `src/auth.py` ``) → check if file exists
      - "创建 `xxx/` 目录" → check if directory exists
      - "编写 frontmatter" → check if referenced file contains `---` frontmatter
      - "实现 xxx" → check if related code files exist (use keyword matching)

   c. If the referenced file/directory exists, automatically change `- [ ]` to `- [x]` in `tasks.md`.

   d. Output a backfill report:
      ```
      ### Task Backfill Report
      - Auto-marked: X tasks
      - Still incomplete: Y tasks (listed below)
      - Total progress: N/M
      ```

   e. If tasks remain `[ ]` after backfill, list them but do NOT stop — the user can address them later.

10. **Force-add tasks.md and commit**

    Since `openspec/` is in `.gitignore`, `git add -A` skips `tasks.md`. Force-add it:

    ```bash
    git add -A
    git add -f openspec/changes/<proposal-name>/tasks.md
    ```

    Count the final task completion:
    ```bash
    DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<proposal-name>/tasks.md)
    TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<proposal-name>/tasks.md)
    ```

    Commit with completion-aware message:
    - If `DONE == TOTAL`: `git commit -m "feat: implement <proposal-name> (DONE/TOTAL tasks)"`
    - If `DONE < TOTAL`: `git commit -m "feat: implement <proposal-name> (DONE/TOTAL tasks, partial)"`

    If no changes to commit (both `git add -A` and `git add -f` produced nothing), skip commit.

**Output On Success**

```
## Worktree Created & Apply Complete

**Proposal:** <proposal-name>
**Branch:** <proposal-name>
**Main branch:** <MAIN_BRANCH>
**HEAD verified:** ✓ (or "merged from <MAIN_BRANCH>")
**Artifacts:** ✓ all done
**Tasks:** N/M complete (or "X/M partial")

### Task Backfill Report
Auto-marked: X tasks, Still incomplete: Y tasks

OpenSpec apply has completed in the worktree.
Use `/merge-worktree-return <proposal-name>` when ready to merge.
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
- Verify each step succeeds before proceeding to the next
- Never delete or overwrite existing branches
- Only use `--force` flag for `git add -f` on tasks.md (required to bypass .gitignore)
- Never use `--force` on `git push`, `git merge`, `git rebase`, or `git checkout`
- Commit messages include proposal name for traceability
- If EnterWorktree fails, do not attempt manual worktree creation — report to user
- All git command failures should stop execution immediately
