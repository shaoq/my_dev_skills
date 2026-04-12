---
name: check-changes-completed
description: Scan all active OpenSpec changes, run a four-dimensional completion check (tasks, artifacts, code delivery, dependencies), and output a summary report. Pure diagnostic tool — use opsx:archive to act on results. No arguments needed.
argument-hint: (no arguments)
disable-model-invocation: true
allowed-tools: Bash(openspec *) Bash(git *) Bash(ls *) Bash(test *) Bash(cat *) Bash(grep *) Bash(find *) Bash(wc *) Read Glob Grep
---

Check all active OpenSpec changes for completion using a four-dimensional model, then output a diagnostic report.

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

4. **Output summary table**

   After checking all changes, output a markdown table:

   ```markdown
   ## Changes Completion Report

   | Change | Tasks | Artifacts | Code 落地 | 依赖 | 可存档? |
   |--------|-------|-----------|----------|------|---------|
   | name-1 | ✓ N/N | ✓ | ✓ | ✓ (无依赖) | ✓ |
   | name-2 | ✗ X/N | ✗ | ✗ 缺失 | ✗ 阻塞 | ✗ |
   ```

   **Archivable logic**: A change is archivable only when ALL four dimensions pass.

5. **Show blocking reasons**

   For any non-archivable changes, list the blocking reasons:

   ```markdown
   ### Blocking Reasons

   **name-2:**
   - Tasks: X/N incomplete
   - Artifacts: missing design, specs
   - Code: 缺失 SKILL.md
   - Dependencies: 阻塞 by name-1 (tasks incomplete)
   ```

6. **Archive hint**

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
- Never modify any change files — this is a read-only check
- Stop on git or openspec CLI failures
- Circular dependency: mark as anomaly, do not recurse infinitely
- If `openspec status` fails for a change, mark D2 as error and continue with others
