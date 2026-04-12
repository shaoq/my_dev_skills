---
name: archived-all-completed-changes
description: Batch archive all completed OpenSpec changes. Scans active changes, checks three dimensions (tasks + code delivery + dependencies), and archives eligible ones in one shot.
argument-hint: (no arguments)
disable-model-invocation: true
allowed-tools: Bash(openspec *) Bash(git *) Bash(ls *) Bash(test *) Bash(cat *) Bash(grep *) Bash(find *) Bash(wc *) Bash(sed *) Bash(mkdir *) Read Glob Grep Skill AskUserQuestion
---

Batch archive all completed OpenSpec changes using a three-dimensional completion check.

**Input**: No arguments required. Example: `/archived-all-completed-changes`.

**Steps**

1. **Validate prerequisites**

   Run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo -> error: "Must be inside a git repository."
   - No openspec CLI -> error: "OpenSpec CLI is required. Install it first."

2. **Record current branch**

   ```bash
   git branch --show-current
   ```

   Store as `CURRENT_BRANCH`. Used later for git log checks.

3. **Scan active changes**

   List all subdirectories under `openspec/changes/`, excluding `archive/`:
   ```bash
   ls -d openspec/changes/*/ 2>/dev/null | sed 's|openspec/changes/||;s|/||' | grep -v '^archive$'
   ```

   If the output is empty:
   > "No active changes found. Nothing to archive."
   Then stop.

   Store the list as `ACTIVE_CHANGES`.

4. **For each change, run three-dimensional checks**

   For each `<name>` in `ACTIVE_CHANGES`, perform the following checks. Collect results into a structured record.

   ### Dimension 1 -- Tasks Completion

   Read the file `openspec/changes/<name>/tasks.md`:
   ```bash
   test -f openspec/changes/<name>/tasks.md && echo "EXISTS" || echo "MISSING"
   ```

   If **MISSING**: mark D1 = `"missing tasks.md"`, skip counting.

   If **EXISTS**:
   ```bash
   TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
   DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
   ```
   - If `DONE == TOTAL` -> D1 passed, record `"X/X"`
   - Otherwise -> D1 failed, record `"X/N (N-X incomplete)"`, list uncompleted items:
     ```bash
     grep -nE '^\s*- \[ \]' openspec/changes/<name>/tasks.md
     ```

   ### Dimension 3 -- Code Delivery Verification

   **Step A: Identify expected output files**

   Read `openspec/changes/<name>/design.md` and `openspec/changes/<name>/proposal.md`. Look for file path patterns:
   - In `proposal.md`, check the `## Impact` section for paths like `SKILL.md`, `*.py`, `*.ts`
   - In `design.md`, look for sections mentioning "new file", "新增文件", "output", "deliverable"

   Extract paths and store as `EXPECTED_FILES`.

   If no specific paths found, use heuristic fallback:
   ```bash
   test -f <name>/SKILL.md && echo "EXISTS" || echo "MISSING"
   ```

   **Step B: Check file existence**

   For each path in `EXPECTED_FILES`:
   ```bash
   test -f <path> && echo "EXISTS" || echo "MISSING"
   ```

   **Step C: Check git commits**

   ```bash
   git log --oneline <CURRENT_BRANCH> -- <expected-file-paths>
   ```

   **Result logic:**
   - Files exist AND commits found -> D3 passed
   - Files missing -> D3 failed, record `"missing: <list>"`
   - Files exist BUT no commits -> D3 failed, record `"files exist but not committed"`

   ### Dimension 4 -- Dependency Integrity

   Read `openspec/changes/<name>/proposal.md`. Extract the `## Dependencies` section:

   ```bash
   sed -n '/^## Dependencies/,/^## /p' openspec/changes/<name>/proposal.md | grep -v '^##' | grep -oE '\b[a-z][a-z0-9-]*\b'
   ```

   - If no `## Dependencies` section or section is empty -> D4 passed, record `"(no deps)"`
   - Otherwise, for each dependency name:
     1. Check if the dependency exists in `openspec/changes/archive/` -> if yes, it's archived, considered satisfied
     2. Check if the dependency is also in `ACTIVE_CHANGES` AND passes the same three-dimensional check -> if yes, it's archivable, considered satisfied
     3. If neither -> D4 failed, record `"blocked by: <dep-name> (<reason>)"`
   - If all dependencies satisfied -> D4 passed

5. **Output completion report**

   Output a markdown table:

   ```markdown
   ## Batch Archive Report

   | Change | Tasks | Code | Dependencies | Archivable |
   |--------|-------|------|-------------|------------|
   | name-1 | X/X   | committed | (no deps)  | Yes        |
   | name-2 | X/N   | missing   | blocked    | No         |
   ```

   **Archivable logic**: A change is archivable only when ALL three dimensions pass.

6. **Show blocking reasons**

   For any non-archivable changes, list the blocking reasons:

   ```markdown
   ### Blocking Reasons

   **name-2:**
   - Tasks: X/N incomplete
   - Code: missing SKILL.md
   - Dependencies: blocked by name-1 (tasks incomplete)
   ```

   If no archivable changes exist, output:
   > "No archivable changes found. See blocking reasons above."
   Then stop without offering archive options.

7. **Archive confirmation and execution**

   If there are archivable changes, use **AskUserQuestion tool** to ask:

   > "以下 changes 已通过三维检查，可以归档：<list>
   > 请选择归档策略："

   Options:
   - **全部归档**: Sequentially call for each archivable change (in alphabetical order):
     ```
     Skill("opsx:archive", args="<name>")
     ```
     After each archive, record result. If one fails, log the error and continue to the next.
   - **逐个确认**: For each archivable change, use AskUserQuestion to confirm:
     > "是否归档 `<name>`？"
     If confirmed, call `Skill("opsx:archive", args="<name>")`. If declined, skip.
   - **仅查看**: End the flow without any archive operations.

8. **Output final archive summary**

   After all archive operations complete (or if "仅查看" was selected), output a summary:

   ```markdown
   ### Archive Results

   | Change | Status | Details |
   |--------|--------|---------|
   | name-1 | Success | archived to openspec/changes/archive/name-1 |
   | name-2 | Failed | error message |
   | name-3 | Skipped | user declined |
   ```

   List successful archive locations and error details for failures.

**Output On Success**

```
## Batch Archive Report

| Change | Tasks | Code | Dependencies | Archivable |
|--------|-------|------|-------------|------------|
| ...    | ...   | ...  | ...         | ...        |

### Blocking Reasons
(detailed list if any)

### Archive Results
| Change | Status | Details |
|--------|--------|---------|
| ...    | ...    | ...     |
```

**Error Output Format**

```
## Error: <error-type>

**Step:** <which step failed>
**Reason:** <why it failed>

**Recovery:**
- <suggestion 1>
```

**Guardrails**
- Never modify any change files during the scanning phase -- read-only
- Never archive without explicit user confirmation
- Stop on git or openspec CLI failures
- Archive failures do not block subsequent changes -- log error and continue
- If `openspec status` fails for a change, skip it and report the error
- Do not recurse infinitely on dependency checks -- use a VISITED set
