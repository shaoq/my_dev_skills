---
name: openspec-review-change
description: "Use when asked to review, audit, assess, or check the quality or implementation readiness of one active OpenSpec proposal before apply. Do not use for pull-request or source-diff code review, post-implementation consistency verification, archive readiness, or editing proposal artifacts."
allowed-tools: Bash(openspec --version) Bash(openspec list *) Bash(openspec status *) Bash(openspec instructions *) Bash(openspec validate *) Bash(git rev-parse *) Bash(git status *) Bash(git diff *) Bash(git log *) Bash(git show *) Bash(git ls-files *) Bash(git check-ignore *) Bash(git worktree list *) Read Glob Grep AskUserQuestion mcp__gitnexus__query mcp__gitnexus__context mcp__gitnexus__impact
---

# Review an OpenSpec Change

Review one active OpenSpec change as a read-only gate between proposal creation and implementation. Accept:

```text
[change-name] [--openspec-root <repo-relative-path>]
```

Use the user's language in the report. Read [references/review-rubric.md](references/review-rubric.md) before semantic review and [references/report-contract.md](references/report-contract.md) before writing the report.

## Workflow

### 1. Enforce the read-only boundary

- Perform only inspection and diagnostic commands.
- Do not edit artifacts, application code, configuration, task markers, or runtime settings.
- Do not install dependencies, initialize OpenSpec, update indexes, or repair links.
- If the request combines review and repair, complete the review first and require a separate explicit revision workflow.
- Capture `git status --short` before review and compare it after review. Any review-caused change is a `BLOCKER` and must be disclosed.

### 2. Resolve the repository and OpenSpec root

1. Verify `git rev-parse --is-inside-work-tree` and `openspec --version` succeed. Otherwise return `BLOCKED` with the missing prerequisite.
2. Resolve the enclosing repository with `git rev-parse --show-toplevel`.
3. Parse the input strictly:
   - Allow zero or one positional change name.
   - Allow zero or one `--openspec-root` value in either order.
   - Treat omission as `--openspec-root .`.
   - Reject unknown flags, duplicates, missing values, absolute paths, and any lexical `..` component.
4. Resolve the candidate path, including symlinks, and require it to remain inside the repository root.
5. Require `<resolved-root>/openspec/` and an initialized OpenSpec project. Do not search recursively, guess another root, or fall back silently.
6. Run every OpenSpec command with the resolved root as its working directory. Resolve every artifact relative to that root or the returned change directory as documented by the CLI.

An invalid or escaping root produces a `BLOCKER` and ends artifact review.

### 3. Select exactly one active change

Run `openspec list --json` in the resolved OpenSpec root and use only active changes.

- If a name is supplied, require an exact active-name match. A missing or archive-only name is a recoverable selection error; list active candidates and stop.
- If no name is supplied and exactly one active change exists, select it and say so.
- If several active changes exist, use a change already named unambiguously in the conversation; otherwise ask the user to select one.
- If no active change exists, report that there is no review target. Never substitute an archived change.

Do not continue until selection is deterministic.

### 4. Discover the Schema and artifacts from OpenSpec

1. Run `openspec status --change <name> --json`.
2. Record `schemaName`, `applyRequires`, and every artifact's id, status, and declared completion.
3. Support full semantic review only for `schemaName: spec-driven`. For another Schema, emit one `BLOCKER` identifying the Schema and return `BLOCKED`; do not pretend to apply the spec-driven rubric.
4. For every declared artifact id, run:

   ```text
   openspec instructions <artifact-id> --change <name> --json
   ```

5. Treat returned `instruction`, `rules`, dependencies, and `outputPath` as the current normative artifact contract.
6. Resolve each `outputPath` safely against the returned change directory:
   - Reject absolute paths or matches outside the change directory.
   - Expand globs without following an escape outside the change directory.
   - Sort matches by repository-relative POSIX path.
   - Read all matches; do not stop at the first delta Spec.
   - If a required or completed artifact matches no file, create a `BLOCKER` and continue with readable artifacts.

Never assume the four default filenames when CLI output declares something else.

### 5. Run structural preflight

Run:

```text
openspec validate <name> --type change --strict --json
```

- Convert every strict-validation issue into evidence for a `BLOCKER` root cause.
- If an apply-required artifact is missing, blocked, or incomplete, record a `BLOCKER` for the missing prerequisite.
- Continue reviewing readable artifacts so the user receives a useful consolidated report.
- Never turn a successful strict validation into `READY` without semantic, consistency, traceability, and task-readiness review.
- Compare each artifact with its generated instruction even when strict validation passes; report missing required sections or mappings.

### 6. Classify review stage and evidence limits

Inspect the declared tasks artifact and attributable repository evidence:

- `pre-apply`: no checked implementation task and no clearly attributable implementation evidence.
- `in-progress`: some tasks are checked, or implementation has clearly begun.
- `all-tasks-done`: every implementation task is checked while the change remains active.

Record `git status --short` and whether changes can be attributed to this change. Unrelated or uncertain dirty files are an evidence limitation, not proof for or against the proposal. For `in-progress` or `all-tasks-done`, state that the current tree is not a clean pre-implementation baseline. Do not replace implementation-consistency or archive-completion tools.

### 7. Load runtime-specific project instructions

Follow the instruction chain for the active runtime:

- In Codex, follow applicable `AGENTS.md` instructions already loaded or discovered from repository root to the reviewed paths.
- In Claude Code, follow applicable `CLAUDE.md` instructions already loaded or discovered for the same scope.
- Do not merge runtime-specific instruction files blindly when they conflict.
- Record the material project constraints used in the report.

If project instructions require a code-intelligence workflow, follow it before making repository claims.

### 8. Ground material claims in the repository

Verify claims about existing files, symbols, interfaces, behavior, dependencies, and affected workflows.

- Prefer the project's required tools. When GitNexus is required and available, use `query` to locate relevant flows, `context` for named symbols, and upstream `impact` only for existing public or key symbols the proposal plans to modify.
- Do not run symbol impact for wholly new files or names that do not yet exist.
- If GitNexus is unavailable or stale, use `rg`, file inspection, Git history, and other read-only evidence. State the reduced scope and confidence.
- Treat “not found” as absence of evidence unless the search scope proves absence.
- Cite repository-relative file paths and line numbers whenever practical.

### 9. Perform the eight-dimensional review

Read [references/review-rubric.md](references/review-rubric.md) completely. Apply all applicable dimensions:

1. Schema and structural compliance
2. Goal and scope clarity
3. Repository grounding and impact
4. Design completeness
5. Spec testability
6. Cross-artifact consistency
7. End-to-end traceability
8. Task implementation readiness

Mark conditional concerns `N/A` when genuinely absent. Do not create checklist findings merely because a change has no API, migration, security boundary, performance-sensitive path, deployment effect, or rollback action.

Build the many-to-many chain:

```text
problem/goal → What Changes → capability → requirement/scenario
             → design decision → task → verification
```

Report orphan scope, uncovered scenarios, ungrounded tasks, unresolved decisions, and missing verification. Accept clear many-to-many mappings.

### 10. Consolidate and gate findings

Read [references/report-contract.md](references/report-contract.md) completely and apply it exactly.

- Deduplicate symptoms caused by one omission into a primary finding with all relevant evidence and affected dimensions.
- Assign stable ids after deduplication using canonical dimension and evidence order.
- Sort findings by severity, dimension order, evidence path, line, then id.
- Distinguish proven findings from uncertainties; state what confirmation is missing.
- Derive exactly one gate:
  - any `BLOCKER` → `BLOCKED`
  - otherwise any `MAJOR` → `NEEDS_REVISION`
  - otherwise any `MINOR` → `READY_WITH_WARNINGS`
  - otherwise → `READY`

### 11. Emit the report and verify read-only behavior

Produce the report using the contract. Include the selected runtime, resolved OpenSpec root, Schema, change, stage, dirty-tree limitation, artifact inventory, dimension summary, findings, traceability gaps, and next actions.

Finally rerun `git status --short` and compare it with the initial snapshot. State that review was read-only only when no review-caused difference exists. Never mark tasks or artifacts complete during this review.

## Stop conditions

Stop safely and report `BLOCKED` when:

- Git, OpenSpec, or an initialized project root is unavailable.
- The requested root escapes the repository or is invalid.
- No deterministic active change can be selected.
- The Schema is unsupported.
- Artifact paths escape the returned change directory.

For selection ambiguity, ask the user rather than inventing a finding about an arbitrary change.
