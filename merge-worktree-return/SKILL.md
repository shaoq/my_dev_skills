---
name: merge-worktree-return
description: Commit worktree changes, rebase onto main, merge back to main branch, and exit the worktree. Use when finishing implementation in a worktree. Optional proposal name argument verifies OpenSpec completion. Requires git.
argument-hint: [proposal-name]
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) Bash(awk *) Bash(sed *) Bash(cat *) Bash(head *) Bash(test *) EnterWorktree ExitWorktree Read Write Edit Glob Grep Skill AskUserQuestion
---

Commit worktree changes, merge back to main branch, and exit the worktree safely.

**Input**: An optional proposal name. Example: `/merge-worktree-return add-user-auth` or `/merge-worktree-return`.

**Steps**

1. **Parse arguments and validate prerequisites**

   Extract the optional proposal name from `$ARGUMENTS`.

   Run prerequisite checks:
   ```bash
   git rev-parse --is-inside-work-tree
   ```

   Verify we are inside a worktree (not the main working tree):
   ```bash
   cat .git | head -1
   ```
   If the output starts with `gitdir:` → we are in a worktree. If `.git` is a directory → error: "Not in a worktree. This skill must be run from inside a worktree branch."

   Record key information:
   ```bash
   CURRENT_BRANCH=$(git branch --show-current)
   ```
   Parse the main working tree path from:
   ```bash
   git worktree list
   ```
   Find the line marked with the main branch — that path is `MAIN_DIR`.

2. **Verify OpenSpec proposal completion (only if proposal name provided)**

   If the user passed a proposal name:

   ```bash
   openspec status --change "<proposal-name>" --json
   ```

   Parse the JSON output. Check:
   - `artifacts`: all must have `status: "done"`
   - `isComplete`: must be `true`

   Also read the tasks file at `openspec/changes/<proposal-name>/tasks.md` and count:
   - `- [x]` (complete) vs `- [ ]` (incomplete)

   **If any tasks are incomplete:**
   - Display warning with count: "X/Y tasks incomplete"
   - List the incomplete tasks
   - Use **AskUserQuestion tool** to confirm:
     > "The proposal '<name>' has incomplete tasks. Continue merging anyway?"
   - If user declines → stop execution

   If no proposal name was provided → skip this step entirely.

3. **Detect the main branch**

   Auto-detect by running:
   ```bash
   git rev-parse --verify main 2>/dev/null && echo "main"
   git rev-parse --verify master 2>/dev/null && echo "master"
   git rev-parse --verify trunk 2>/dev/null && echo "trunk"
   ```

   Use the first one that succeeds. If all fail, try:
   ```bash
   git remote show origin 2>/dev/null | grep 'HEAD branch' | awk '{print $NF}'
   ```

   Record as `MAIN_BRANCH`.

4. **Commit all current worktree files**

   ```bash
   git status --porcelain
   ```

   If there are uncommitted files:
   ```bash
   git add -A
   git commit -m "chore: auto-commit before merge from worktree"
   ```

   If no changes → skip, announce: "No uncommitted changes."

   Record the worktree HEAD:
   ```bash
   WORKTREE_HEAD=$(git rev-parse HEAD)
   ```

5. **Rebase onto main branch**

   ```bash
   git rebase <MAIN_BRANCH>
   ```

   **If rebase succeeds** (exit code 0):
   Announce: "Rebase onto <MAIN_BRANCH> completed."

   **If rebase has conflicts** (exit code non-zero):
   - List conflicting files:
     ```bash
     git diff --name-only --diff-filter=U
     ```
   - Read each conflicting file
   - Resolve conflicts: analyze the conflict markers (`<<<<<<<`, `=======`, `>>>>>>>`), understand both sides, and produce the correct merged result. Prefer worktree changes unless the main branch version is clearly more appropriate.
   - Stage resolved files:
     ```bash
     git add <resolved-files>
     ```
   - Continue rebase:
     ```bash
     GIT_EDITOR=true git rebase --continue
     ```
   - If conflicts persist and cannot be resolved:
     ```bash
     git rebase --abort
     ```
     Report all conflicting files to the user and stop execution.

6. **Switch to main directory and merge**

   Change to the main working tree directory:
   ```bash
   cd <MAIN_DIR>
   ```

   Ensure we are on the main branch:
   ```bash
   git checkout <MAIN_BRANCH>
   ```

   Merge the worktree branch:
   ```bash
   git merge <CURRENT_BRANCH>
   ```

   **If merge has conflicts:**
   - Resolve conflicts the same way as in Step 5
   - Stage and commit

   **Verify the merge** — all worktree commits must now be in main:
   ```bash
   git log <MAIN_BRANCH>..<CURRENT_BRANCH>
   ```
   This should return empty (no commits ahead). If it returns commits → merge verification failed. Report the issue and do NOT proceed to exit.

7. **Safely exit the worktree**

   Before exiting, confirm ALL of the following:
   - [x] Step 4: All worktree files committed
   - [x] Step 5: Rebase completed
   - [x] Step 6: Merge to main verified successful
   - [x] Step 2: If proposal name given, proposal is complete (or user confirmed)

   Only if ALL conditions are met, 根据当前环境选择退出方式：

   **Claude Code 环境（ExitWorktree 工具可用）**:
   使用 **ExitWorktree** 工具，参数 `action`: "remove"。

   **其他环境（Codex CLI 等，ExitWorktree 工具不可用）**:
   Step 6 已通过 `cd <MAIN_DIR>` 切回主目录，只需清理 worktree：
   ```bash
   git worktree remove <worktree-path>
   ```
   其中 `<worktree-path>` 为 Step 1 中记录的 worktree 目录路径。

   判断依据：检查 **ExitWorktree** 工具是否在当前环境中可用。

   退出完成后，验证：
   ```bash
   pwd
   git branch --show-current
   ```

   确认已回到主项目目录且在主分支上。

**Output On Success**

```
## Worktree Merged & Closed

**Proposal:** <proposal-name> (or "N/A")
**Branch merged:** <CURRENT_BRANCH> → <MAIN_BRANCH>
**Worktree:** removed
**Current branch:** <MAIN_BRANCH>

All worktree changes have been successfully merged to <MAIN_BRANCH>.

下一步: 运行 `/check-changes-completed` 检查整体完成度，或 `/opsx:archive <proposal-name>` 归档此 change。
```

**Error Output Format**

```
## Error: <error-type>

**Step:** <which step failed>
**Branch:** <CURRENT_BRANCH>

**Details:**
<specific error information>

**Recovery:**
- <suggestion 1>
- <suggestion 2>
```

**Guardrails**
- Verify each step succeeds before proceeding to the next
- Never exit the worktree unless all merge conditions are verified
- Never use --force flags on git commands
- If rebase fails, always use `git rebase --abort` to return to safe state
- If merge verification fails, do NOT call ExitWorktree or remove the worktree
- All git command failures should stop execution immediately
- 非 Claude Code 环境下使用 `git worktree remove` 替代 `ExitWorktree`，Step 6 已确保 CWD 在主目录，无需额外 `cd`
- Always confirm with user before merging if proposal tasks are incomplete
