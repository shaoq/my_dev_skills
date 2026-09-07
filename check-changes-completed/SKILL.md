---
name: check-changes-completed
description: Diagnose completion for explicitly selected active OpenSpec changes against one local target; add --backfill only to authorize deterministic selected task-marker updates.
argument-hint: "--target <target-branch> --change <active-change> [--change <active-change> ...] [--backfill]"
allowed-tools: Bash(openspec *) Bash(git *) Bash(ls *) Bash(test *) Bash(cat *) Bash(grep *) Bash(find *) Bash(wc *) Bash(sed *) Bash(mv *) Bash(head *) Read Glob Grep Edit AskUserQuestion
---

Check an explicitly selected target group of active OpenSpec changes for completion using a five-dimensional model. Default mode is strictly read-only; exactly one bare `--backfill` authorizes deterministic selected task-marker updates only after the frozen range remains stable.

**Input**: Exactly one `--target <target-branch>`, one or more unique
`--change <active-change>` selectors, and optionally exactly one bare `--backfill`. Options may be interleaved.

```text
/check-changes-completed --target develop --change change-a
/check-changes-completed --change change-a --target develop --change change-b
/check-changes-completed --target develop --change change-a --backfill
```

**Steps**

1. **Validate prerequisites and parse arguments without writes**

   Run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo → error: "Must be inside a git repository."
   - No openspec CLI → error: "OpenSpec CLI is required. Install it first."

   Initialize `ZERO_WRITE_GATE=closed`, `READ_ONLY_DEFAULT=true`, and `BACKFILL_AUTHORIZED=false`. Parse the complete original argument vector. Accept only one
   `--target` with a non-empty value, one or more `--change` options with non-empty values, and at most exactly one bare `--backfill`. A valid `--backfill` sets `BACKFILL_AUTHORIZED=true` and `READ_ONLY_DEFAULT=false`. Reject a
   missing target/change, a missing option value, a duplicate or 重复的 `--target`, a duplicate or
   重复的 `--change`, duplicate, valued, or malformed `--backfill`, an unknown flag, any positional argument, and any option-shaped value. Forms such as `--backfill=true`, `--backfill yes`, and a second `--backfill` are invalid. Report the exact
   offending argument and stop before baseline queries or change-level artifact reads. Never infer a target or
   change from Git, `openspec list`, directory order, `main`, `origin/HEAD`, or current branch.

2. **Build the selected set and freeze the baseline without writes**

   For each requested change, require an exact directory match under `openspec/changes/<name>/`. Reject
   absent, ambiguous, path-like, similarly named, or archive-only values. The literal `archive` is invalid.
   Validate only the requested names; do not enumerate unrelated change contents. Sort the unique names:

   ```bash
   SELECTED_CHANGES=$(printf '%s\n' <validated-change-values> | LC_ALL=C sort)
   ```

   未选择的 change 不得读取其 change-level artifacts，不参与五维扫描、依赖递归、blocking
   reasons、可存档结论或 task backfill。selected change 声明的 active dependency 若未被显式选择，
   只标为 `阻塞: <dep-name> (not selected)`，不得读取该 dependency 的 artifacts 或自动扩大集合。
   不同目标分支必须分组调用。

   Require the explicit local target and freeze both endpoints exactly once:

   ```bash
   git rev-parse --verify --quiet refs/heads/<TARGET_BRANCH>
   BASE_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
   CURRENT_HEAD=$(git rev-parse HEAD)
   git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>
   ```

   Do not fetch, substitute a merge base, or re-resolve either endpoint for D3/D5. A missing local ref,
   command error, or failed ancestry check blocks every selected change, keeps `ZERO_WRITE_GATE=closed`, sets
   `archivable = unknown/blocked`, and skips all change artifact reads, backfill, stage, and commit. If
   `BASE_HEAD == CURRENT_HEAD`, record an empty comparison range; do not invent delivered files or commits.

3. **For each change, run five-dimensional checks**

   For each `<name>` in sorted `SELECTED_CHANGES`, perform the following checks sequentially. Collect results into a structured record.

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
   git log <BASE_HEAD>..<CURRENT_HEAD> -- <expected-file-paths>
   ```

   **Result logic:**
   - Files exist AND commits found → D3 = `✓`
   - Files missing → D3 = `✗ 缺失: <list>`
   - Files exist BUT no commits → D3 = `⚠ 有文件但未提交`

   ### Dimension 4 — Dependency Integrity

   Check if `openspec/changes/<name>/dependencies.yaml` exists:

   ```bash
   test -f openspec/changes/<name>/dependencies.yaml && echo "EXISTS" || echo "MISSING"
   ```

   - If file does not exist → D4 = `✓ (无依赖)`
   - If exists, read the file and parse the YAML `dependencies` list. If the list is empty → D4 = `✓ (无依赖)`
   - Otherwise, for each dependency name:
     1. Verify the dependency change exists in `openspec/changes/` or `openspec/changes/archive/`
     2. If not found → mark as `无效引用: <dep-name>`
     3. If found only under `openspec/changes/archive/`, treat that dependency as completed without reading its artifacts
     4. If found as an active change but absent from `SELECTED_CHANGES`, mark
        `✗ 阻塞: <dep-name> (not selected)` and do not read its artifacts
     5. If it is also selected, reuse that selected record's four-dimensional status; recursively resolve only
        within `SELECTED_CHANGES` using a VISITED set
     6. If all dependencies pass → D4 = `✓`
     7. If any dependency fails → D4 = `✗ 阻塞: <dep-name> (<reason>)`

   **Circular dependency detection**: Maintain a `VISITED` set across recursive calls. If a change is already in `VISITED`, stop and mark as `循环依赖`.

   ### Dimension 5 — Project Compliance

   Check whether the change satisfies project-level compliance requirements defined in CLAUDE.md.

   **Step 5a: Locate CLAUDE.md files**

   Check for project-level CLAUDE.md:
   ```bash
   test -f CLAUDE.md && echo "EXISTS" || echo "MISSING"
   ```

   If the change's `EXPECTED_FILES` (from D3 Step 3a) include files in subdirectories, also check those subdirectories for CLAUDE.md:
   ```bash
   test -f <subdir>/CLAUDE.md && echo "EXISTS" || echo "MISSING"
   ```

   Store all found CLAUDE.md paths as `CLAUDE_MD_FILES`.

   **Step 5b: Skip conditions**

   - If `CLAUDE_MD_FILES` is empty → D5 = `✓ (无项目规范)`, skip remaining D5 steps.
   - Read each CLAUDE.md file. If a file cannot be read (encoding issues, binary content) → skip that file. If ALL files are unreadable → D5 = `✓ (无法解析)`, skip remaining D5 steps.

   **Step 5c: Extract companion requirements**

   For each CLAUDE.md file in `CLAUDE_MD_FILES`, scan line-by-line and match against the following keyword patterns (case-insensitive). For each match, extract the requirement type and the full line as description.

   **Pattern table:**

   | Pattern (regex, case-insensitive) | Requirement Type |
   |---|---|
   | `must\s+update.*(test\|spec\|测试\|用例)` | `test-sync` |
   | `必须更新.*(test\|测试\|用例\|spec)` | `test-sync` |
   | `每次变更后.*(test\|测试\|spec)` | `test-sync` |
   | `always\s+(run\|write\|update).*(test\|spec)` | `test-sync` |
   | `must\s+update.*(doc\|文档\|readme)` | `doc-sync` |
   | `必须更新.*(doc\|文档)` | `doc-sync` |
   | `always\s+include.*(doc\|文档)` | `doc-sync` |
   | `must\s+update.*(api\|schema\|接口\|openapi)` | `api-schema-sync` |
   | `必须更新.*(api\|schema\|接口)` | `api-schema-sync` |
   | `must\s+update.*(changelog\|变更日志)` | `changelog-sync` |

   Collect all extracted requirements into `COMPANION_REQS` as a list of:
   `{ type: string, description: string, source_file: string }`

   Deduplicate by `type`: if multiple CLAUDE.md files produce the same type, keep the entry with the most specific description.

   If `COMPANION_REQS` is empty after scanning all files → D5 = `✓ (无合规要求)`, skip remaining D5 steps.

   **Step 5d: Determine if the change triggers companion requirements**

   Determine the change's modification scope from two sources:
   1. The `EXPECTED_FILES` list from D3 Step 3a.
   2. If `design.md` exists, read it and check for mentions of API, endpoint, route, or schema changes.

   A companion requirement is "triggered" when the change's scope overlaps with the requirement's domain:

   | Requirement Type | Triggered When |
   |---|---|
   | `test-sync` | `EXPECTED_FILES` contains source code files (files NOT matching `test`, `spec`, `_test.` patterns) |
   | `doc-sync` | `EXPECTED_FILES` contains source code files or `SKILL.md` |
   | `api-schema-sync` | `design.md` mentions API, endpoint, route, schema, or protocol changes |
   | `changelog-sync` | `EXPECTED_FILES` is non-empty |

   Collect triggered requirements into `TRIGGERED_REQS`. If empty → D5 = `✓ (不适用)`.

   **Step 5e: Check compliance for each triggered requirement**

   For each triggered requirement in `TRIGGERED_REQS`, verify that the companion artifact was updated alongside the change:

   ```bash
   CHANGED_FILES=$(git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only)
   ```

   D3 and D5 MUST reuse the same literal frozen values. Do not pass `TARGET_BRANCH`, `HEAD`, or a freshly
   resolved ref to either query.

   Match `CHANGED_FILES` against requirement-specific patterns:

   | Requirement Type | File Pattern (grep) |
   |---|---|
   | `test-sync` | `grep -iE '(test\|spec\|_test\.)'` |
   | `doc-sync` | `grep -iE '(doc\|\.md\|README)'` |
   | `api-schema-sync` | `grep -iE '(schema\|openapi\|swagger\|\.proto)'` |
   | `changelog-sync` | `grep -iE '(CHANGELOG\|HISTORY)'` |

   If the pattern match produces output → the requirement is satisfied.
   If the pattern match produces no output → the requirement is violated; add to `D5_GAPS` list.

   **Result logic:**
   - All triggered requirements pass → D5 = `✓`
   - Any triggered requirement fails → D5 = `✗ 缺失: <type-list>`, where `<type-list>` is the comma-separated list of failed requirement types (e.g., `test-sync, doc-sync`)

   Each entry in `D5_GAPS` contains: `{ type, description, source_file }` for use in blocking reasons.

4. **Plan contradiction backfill, then conditionally open the final zero-write gate**

   After collecting all five-dimensional results, detect contradictions:

   A contradiction exists when a change has **D3 = ✓** (code delivered) but **D1 = ✗** (tasks incomplete). This means code is on disk but task markers were not updated.

   **Note**: D5 (Project Compliance) does not participate in backfill. D5 gaps are diagnostic-only and reported as prompts to the user.

   Build a list `CONTRADICTORY_CHANGES` of all changes matching this pattern.

   **If `CONTRADICTORY_CHANGES` is empty**: no backfill plan is needed.

   **If `CONTRADICTORY_CHANGES` is not empty**: build the deterministic plan for reporting. If `BACKFILL_AUTHORIZED=false`, do not ask Level-2 questions and do not edit, stage, or commit; report the candidate Level-1 edits and residual Level-2 tasks. If `BACKFILL_AUTHORIZED=true`, perform the following two-level backfill:

   ### Level-1: Build an automatic backfill plan via the 4-rule parser

   For each change in `CONTRADICTORY_CHANGES`, read its `tasks.md` and process each `- [ ]` line:

   **Rule 1 — Backtick-enclosed file paths**:
   Extract text inside backticks (e.g., `` `SKILL.md` ``, `` `src/auth.py` ``). For each extracted path:
   ```bash
   test -f <path> && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → add this exact task-line edit to `BACKFILL_PLAN`; do not edit yet.

   **Rule 2 — Directory creation patterns**:
   If task description matches "创建 `xxx/` 目录" or "Create `xxx/` directory":
   ```bash
   test -d <directory-path> && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → add this exact task-line edit to `BACKFILL_PLAN`; do not edit yet.

   **Rule 3 — Frontmatter patterns**:
   If task description matches "编写 frontmatter" or "write frontmatter", extract any backtick-enclosed file reference. Check if that file contains frontmatter:
   ```bash
   test -f <path> && head -1 <path> | grep -q '^---' && echo "EXISTS" || echo "MISSING"
   ```
   If EXISTS → add this exact task-line edit to `BACKFILL_PLAN`; do not edit yet.

   **Rule 4 — Implementation keyword patterns**:
   If task description matches "实现 xxx" or "implement xxx", extract the keyword phrase and search for related code files:
   ```bash
   grep -rl "<keyword>" --include="*.md" --include="*.py" --include="*.ts" --include="*.js" --include="*.go" . 2>/dev/null | head -3
   ```
   If results found → add this exact task-line edit to `BACKFILL_PLAN`; do not edit yet.

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

   - If user chooses **"Mark all as complete"**: add all listed `- [ ]` → `- [x]` edits to
     `BACKFILL_PLAN`; do not edit yet.
   - If user chooses **"Skip"**: leave them as `- [ ]`.
   - A missing, negative, or ambiguous response is not affirmative authorization and leaves every residual task unchanged.

   Track: `L2_MARKED` = count of tasks confirmed via Level-2.

   ### Final endpoint stability check

   After every diagnostic and any Level-2 wait, but before applying `BACKFILL_PLAN`, staging, or committing,
   resolve only for equality checking:

   ```bash
   OBSERVED_BASE_HEAD=$(git rev-parse refs/heads/<TARGET_BRANCH>)
   OBSERVED_CURRENT_HEAD=$(git rev-parse HEAD)
   ```

   Require `OBSERVED_BASE_HEAD == BASE_HEAD` and `OBSERVED_CURRENT_HEAD == CURRENT_HEAD`. Also require the
   parsed arguments, sorted `SELECTED_CHANGES`, and every selected `tasks.md` input used to build
   `BACKFILL_PLAN` to remain byte-identical. Any target/current drift, unreadable state, selection drift, or
   task-input drift keeps `ZERO_WRITE_GATE=closed`: discard the plan, perform zero backfill, zero stage, zero
   commit, mark frozen diagnostics as stale, and report `archivable = unknown/blocked`. Never rerun against
   new commits inside the same invocation.

   Only after all checks pass and `BACKFILL_AUTHORIZED=true` set `ZERO_WRITE_GATE=open`, then apply the planned edits strictly to
   `openspec/changes/<name>/tasks.md` where `<name>` is in `SELECTED_CHANGES`. In default mode the stable diagnostic completes with `ZERO_WRITE_GATE=closed` and zero writes.

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

5. **Output baseline evidence and summary table**

   Before the table report:

   ```text
   Selected changes: <sorted SELECTED_CHANGES> (explicit --change values)
   Target branch: <TARGET_BRANCH> (explicit --target)
   BASE_HEAD: <frozen commit>
   CURRENT_HEAD: <frozen commit>
   Comparison range: <BASE_HEAD>..<CURRENT_HEAD> | empty
   Target stability: <stable|drifted|unknown> (observed: <hash|unavailable>)
   Current stability: <stable|drifted|unknown> (observed: <hash|unavailable>)
   Writes: <diagnostic-only|allowed and performed|allowed but unnecessary|blocked>
   ```

   On a prerequisite/ancestry/final-stability failure, list every selected change as blocked, explain that
   writes and archivable conclusions were blocked, and use `archivable = unknown/blocked`; do not present a
   positive or negative archive verdict derived from incomplete/drifted evidence.

   After backfill (or if skipped), output a markdown table using the latest D1 values:

   ```markdown
   ## Changes Completion Report

   | Change | Tasks | Artifacts | Code 落地 | 依赖 | 合规 | 可存档? |
   |--------|-------|-----------|----------|------|------|---------|
   | name-1 | ✓ N/N | ✓ | ✓ | ✓ (无依赖) | ✓ | ✓ |
   | name-2 | ✗ X/N | ✗ | ✗ 缺失 | ✗ 阻塞 | ✗ 缺失: test-sync | ✗ |
   | name-3 | ✓ N/N | ✓ | ✓ | ✓ | ✓ (无项目规范) | ✓ |
   ```

   **Archivable logic**: A selected change is archivable only when ALL five dimensions pass and final baseline
   stability is confirmed. The read-only default can report an already-complete selected change as archivable without opening the write gate. Unselected changes never appear in this table.

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
   - Compliance: 缺失 test-sync — CLAUDE.md 要求 "must update tests when changing source code"
     → 建议: 运行 `/opsx:explore` 分析需要更新的测试范围
   ```

7. **Archive hint**

   If there are archivable changes, output:
   > "可归档: <name-1>, <name-2>
   >   → 运行 `/opsx:archive <name>` 逐个归档"

   If there are non-archivable changes, additionally output:
   > "未完成: <name-3>
   >   → 运行 `/opsx:apply <name>` 补实施
   >   → 或 `/new-worktree-apply <name> --target <TARGET_BRANCH>` 在同一冻结目标的 worktree 中实施
   >   → 如有合规缺失，运行 `/opsx:explore` 分析需要补充的 companion 产出"

   If no archivable changes:
   > "No archivable changes found. See blocking reasons above."

**Output On Success**

```
## Changes Completion Report

| Change | Tasks | Artifacts | Code 落地 | 依赖 | 合规 | 可存档? |
|--------|-------|-----------|----------|------|------|---------|
| ...    | ...   | ...       | ...      | ...  | ...  | ...     |

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
- May modify `tasks.md` files ONLY for explicitly selected changes where D3 passes, D1 fails, and
  `ZERO_WRITE_GATE=open`. All other change artifacts remain strictly read-only.
- Parameter, selection, target-ref, ancestry, or final stability failure means zero task edits, zero stage, and
  zero commit; frozen drifted evidence may be shown only as stale diagnostics
- Never scan or backfill an unselected active change; different target branches require separate grouped calls
- D3 and D5 use only `<BASE_HEAD>..<CURRENT_HEAD>`, never a moving branch name, literal `HEAD`, guessed default,
  or substituted merge base
- Stop on git or openspec CLI failures
- Circular dependency: mark as anomaly, do not recurse infinitely
- If `openspec status` fails for a change, mark D2 as error and continue with others
- Level-1 backfill is automatic only when one valid `--backfill` authorized it; default mode is zero-write. Level-2 always requires explicit user confirmation
- After backfill, always use `git add -f` for tasks.md to bypass .gitignore
- Only commit if tasks.md was actually modified
- D5 (Project Compliance) is strictly read-only and diagnostic: it NEVER auto-creates or auto-modifies companion artifacts. It only reports gaps with suggestions.
- If CLAUDE.md cannot be parsed (encoding issues, binary content), treat as D5 = `✓ (无法解析)` and do not block archiving.
- If no CLAUDE.md exists in the project, D5 does not block archiving (D5 = `✓ (无项目规范)`).
