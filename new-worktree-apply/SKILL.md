---
name: new-worktree-apply
description: Create a git worktree branch for an OpenSpec proposal and apply it. Use when starting implementation of an OpenSpec change in an isolated worktree. Requires git and openspec CLI.
argument-hint: <proposal-name> [--branch <main-branch>]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Read Write Edit Glob Grep Skill AskUserQuestion
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

7. **Execute OpenSpec apply**

   Use the **Skill tool** to invoke `openspec-apply-change` with the proposal name as the argument:
   ```
   Skill("openspec-apply-change", args="<proposal-name>")
   ```

   Alternatively, if using the command version:
   ```
   Skill("opsx:apply", args="<proposal-name>")
   ```

   This starts the implementation of the proposal within the worktree.

**Output On Success**

```
## Worktree Created & Apply Started

**Proposal:** <proposal-name>
**Branch:** <proposal-name>
**Main branch:** <MAIN_BRANCH>
**HEAD verified:** ✓ (or "merged from <MAIN_BRANCH>")

OpenSpec apply is now running in the worktree.
Use `/merge-worktree-return <proposal-name>` when done.
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
- Never use --force flags
- Commit messages include proposal name for traceability
- If EnterWorktree fails, do not attempt manual worktree creation — report to user
- All git command failures should stop execution immediately
