---
name: check-changes-completed
description: Scan all active OpenSpec changes, run a four-dimensional completion check (tasks, artifacts, code delivery, dependencies), auto-backfill task markers when code is delivered but tasks are unmarked, and output a summary report. Diagnostic + backfill tool — use opsx:archive to act on results. No arguments needed.
argument-hint: (no arguments)
disable-model-invocation: true
allowed-tools: Bash(openspec *) Bash(git *) Bash(ls *) Bash(test *) Bash(cat *) Bash(grep *) Bash(find *) Bash(wc *) Bash(sed *) Bash(mv *) Read Glob Grep Edit AskUserQuestion
---

Check all active OpenSpec changes for completion using a four-dimensional model, auto-backfill task markers when contradictions are detected, then output a diagnostic report.

**Input**: No arguments required. Example: `/check-changes-completed`.

**Steps**

1. **Validate prerequisites**

   Run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo → error: "Must be inside a git repository."
   - No openspec CLI → error: "OpenSpec CLI is required. Install it first."

2. **Scan active changes**

   List all subdirectories under `openspec/changes/`, excluding `archive/`:
   ```bash
   ls -d openspec/changes/*/ 2>/dev/null | sed 's|openspec/changes/||;s|/||' | grep -v '^archive$'
   ```

   If the output is empty:
   > "No active changes found. Nothing to check."
   Then stop.

   Store the list as `ACTIVE_CHANGES`.

3. **For each change, run four-dimensional checks**

   For each `<name>` in `ACTIVE_CHANGES`, perform the following checks sequentially. Collect results into a structured record.

   ### Dimension 1 — Tasks Completion

   Read the file `openspec/changes/<name>/tasks.md`:
   ```bash
   test -f openspec/changes/<name>/tasks.md && echo "EXISTS" || echo "MISSING"
   ```

   If **MISSING**: mark D1 = `"缺失 (no tasks.md)"`, skip counting.

   If **EXISTS**:
   ```bash
   TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
   DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
   ```
   - If `DONE == TOTAL` → D1 = `✓ N/N`
   - Otherwise → D1 = `✗ X/N`, list uncompleted items:
     ```bash
     grep -nE '^\s*- \[ \]' openspec/changes/<name>/tasks.md
     ```

   ### Dimension 2 — Artifacts Completeness

   Run:
   ```bash
   openspec status --change "<name>" --json
   ```

   Parse the JSON `artifacts` array. For each artifact, check `status`.

   - If all artifacts have `status: "done"` → D2 = `✓`
   - Otherwise → D2 = `✗`, list incomplete artifact names:
     ```
     Incomplete: design, specs
     ```

   ### Dimension 3 — Code Delivery Verification

   **Step 3a: Identify expected output files**

   Read `openspec/changes/<name>/design.md`. Look for file path patterns such as:
   - References like `SKILL.md`, `*.py`, `*.ts` etc. in the document
   - Sections like "新增文件", "产出", "output", "new file", "deliverable"

   Also check `openspec/changes/<name>/proposal.md` for the `## Impact` section which may list expected files.

   Store identified paths as `EXPECTED_FILES`. If no specific files found, use the change name as a heuristic: check if `<name>/SKILL.md` exists.

   **Step 3b: Check file existence**

   For each path in `EXPECTED_FILES`:
   ```bash
   test -f <path> && echo "EXISTS" || echo "MISSING"
   ```

   **Step 3c: Check git commits**

   ```bash
   git log --oneline main..HEAD -- <expected-file-paths>
   ```

   **Result logic:**
   - Files exist AND commits found → D3 = `✓`
   - Files missing → D3 = `✗ 缺失: <list>`
   - Files exist BUT no commits → D3 = `⚠ 有文件但未提交`

   ### Dimension 4 — Dependency Integrity

   Read `openspec/changes/<name>/proposal.md`. Extract the `## Dependencies` section.

   ```bash
   sed -n '/^## Dependencies/,/^## /p' openspec/changes/<name>/proposal.md | grep -v '^##' | grep -oE '\b[a-z][a-z0-9-]*\b'
   ```

   - If no `## Dependencies` section or section is empty → D4 = `✓ (无依赖)`
   - Otherwise, for each dependency name:
     1. Verify the dependency change exists in `openspec/changes/` or `openspec/changes/archive/`
     2. If not found → mark as `无效引用: <dep-name>`
     3. If found, recursively check its four-dimensional status (use a VISITED set to detect circular dependencies)
     4. If all dependencies pass → D4 = `✓`
     5. If any dependency fails → D4 = `✗ 阻塞: <dep-name> (<reason>)`

   **Circular dependency detection**: Maintain a `VISITED` set across recursive calls. If a change is already in `VISITED`, stop and mark as `循环依赖`.

4. **Smart task backfill (when contradictions detected)**

   After collecting all four-dimensional results, detect contradictions:

   A contradiction exists when a change has **D3 = ✓** (code delivered) but **D1 = ✗** (tasks incomplete). This means code is on disk but task markers were not updated.

   Build a list `CONTRADICTORY_CHANGES` of all changes matching this pattern.

   **If `CONTRADICTORY_CHANGES` is empty**: Skip to Step 5 (no backfill needed).

   **If `CONTRADICTORY_CHANGES` is not empty**: For each change in the list, perform two-level backfill:

   ### Level-1: Automatic backfill via 4-rule parser

   For each change in `CONTRADICTORY_CHANGES`, read its `tasks.md` and process each `- [ ]` line:

   **Rule 1 — Backtick-enclosed file paths**:
   Extract text inside backticks (e.g., `` `SKILL.md` ``, `` `src/auth.py` ``). For each extracted path:
   ```bash
   test -f <path> && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → auto-mark this task: `- [ ]` → `- [x]`.

   **Rule 2 — Directory creation patterns**:
   If task description matches "创建 `xxx/` 目录" or "Create `xxx/` directory":
   ```bash
   test -d <directory-path> && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → auto-mark this task: `- [ ]` → `- [x]`.

   **Rule 3 — Frontmatter patterns**:
   If task description matches "编写 frontmatter" or "write frontmatter", extract any backtick-enclosed file reference. Check if that file contains frontmatter:
   ```bash
   test -f <path> && head -1 <path> | grep -q '^---' && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → auto-mark this task: `- [ ]` → `- [x]`.

   **Rule 4 — Implementation keyword patterns**:
   If task description matches "实现 xxx" or "implement xxx", extract the keyword phrase and search for related code files:
   ```bash
   grep -rl "<keyword>" --include="*.md" --include="*.py" --include="*.ts" --include="*.js" --include="*.go" . 2>/dev/null | head -3
   ```
   If results found → auto-mark this task: `- [ ]` → `- [x]`.

   Track results for each change:
   - `L1_MARKED`: count of tasks auto-marked by Level-1
   - `L1_UNMARKED`: list of tasks that Level-1 could not resolve (no matching file/directory found)

   ### Level-2: Fallback backfill with user confirmation

   For each change in `CONTRADICTORY_CHANGES` that has remaining `L1_UNMARKED` tasks:

   Check if D3 fully passes (files exist AND git commits found). If D3 does not fully pass, skip Level-2 for this change — only the verified-delivery case warrants override marking.

   If D3 fully passes and `L1_UNMARKED` is non-empty, collect all residual `- [ ]` tasks across all such changes. Present them to the user via **AskUserQuestion**:

   > "The following tasks could not be auto-matched to files, but code delivery (D3) is verified. Mark them all as complete?"
   >
   > (lists the residual tasks grouped by change)
   >
   > Options: "Mark all as complete" / "Skip (keep as incomplete)"

   - If user chooses **"Mark all as complete"**: change all listed `- [ ]` → `- [x]`.
   - If user chooses **"Skip"**: leave them as `- [ ]`.

   Track: `L2_MARKED` = count of tasks confirmed via Level-2.

   ### Commit backfilled tasks

   After both levels complete, check if any `tasks.md` files were actually modified:

   ```bash
   CHANGED=0
   for name in CONTRADICTORY_CHANGES; do
     if git diff --quiet openspec/changes/$name/tasks.md 2>/dev/null; then
       : # no change
     else
       CHANGED=$((CHANGED + 1))
     fi
   done
   ```

   If `CHANGED > 0`:
   ```bash
   for name in CONTRADICTORY_CHANGES; do
     git add -f openspec/changes/$name/tasks.md
   done
   git commit -m "fix: auto-backfill task markers ($CHANGED changes)"
   ```

   If `CHANGED == 0`: skip git operations.

   ### Recount D1 after backfill

   For each change in `CONTRADICTORY_CHANGES`, recount task completion:
   ```bash
   TOTAL=$(grep -cE '^\s*- \[[ x]\]' openspec/changes/<name>/tasks.md)
   DONE=$(grep -cE '^\s*- \[x\]' openspec/changes/<name>/tasks.md)
   ```

   Update the D1 result for that change. If now `DONE == TOTAL` → D1 = `✓ N/N`. Otherwise → D1 = `✗ X/N` (updated count).

5. **Output summary table**

   After backfill (or if skipped), output a markdown table using the latest D1 values:

   ```markdown
   ## Changes Completion Report

   | Change | Tasks | Artifacts | Code 落地 | 依赖 | 可存档? |
   |--------|-------|-----------|----------|------|---------|
   | name-1 | ✓ N/N | ✓ | ✓ | ✓ (无依赖) | ✓ |
   | name-2 | ✗ X/N | ✗ | ✗ 缺失 | ✗ 阻塞 | ✗ |
   ```

   **Archivable logic**: A change is archivable only when ALL four dimensions pass.

   If backfill was performed, output a backfill report immediately after the table:
   ```markdown
   ### Task Backfill Report

   **change-a**: L1 auto-marked: 3, L2 confirmed: 2, Remaining: 0 → D1 updated ✓
   **change-b**: L1 auto-marked: 1, L2 confirmed: 0, Remaining: 2 → D1 still ✗
   ```

6. **Show blocking reasons**

   For any non-archivable changes (using post-backfill D1 values), list the blocking reasons:

   ```markdown
   ### Blocking Reasons

   **name-2:**
   - Tasks: X/N incomplete
   - Artifacts: missing design, specs
   - Code: 缺失 SKILL.md
   - Dependencies: 阻塞 by name-1 (tasks incomplete)
   ```

7. **Archive hint**

   If there are archivable changes, output:
   > "Archivable changes: `<name-1>`, `<name-2>`. Use `/opsx:archive <name>` to archive."

   If no archivable changes:
   > "No archivable changes found. See blocking reasons above."

**Output On Success**

```
## Changes Completion Report

| Change | Tasks | Artifacts | Code 落地 | 依赖 | 可存档? |
|--------|-------|-----------|----------|------|---------|
| ...    | ...   | ...       | ...      | ...  | ...     |

### Task Backfill Report
(if backfill was performed)

### Blocking Reasons
(detailed list if any)

Archivable changes: <list>. Use `/opsx:archive <name>` to archive.
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
- May modify `tasks.md` files ONLY for changes where D3 passes and D1 fails (contradiction detected). All other change artifacts remain strictly read-only.
- Stop on git or openspec CLI failures
- Circular dependency: mark as anomaly, do not recurse infinitely
- If `openspec status` fails for a change, mark D2 as error and continue with others
- Level-1 backfill is automatic (no user confirmation); Level-2 requires explicit user confirmation
- After backfill, always use `git add -f` for tasks.md to bypass .gitignore
- Only commit if tasks.md was actually modified
