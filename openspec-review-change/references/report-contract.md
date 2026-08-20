# OpenSpec Proposal Review Report Contract

Use this structure for every completed review. Adapt labels to the user's language, but preserve field meanings and gate values.

## Contents

- Gate algorithm
- Stable finding identifiers
- Required report
- Finding rules
- Large reports
- Stage-specific wording

## Gate algorithm

Evaluate after deduplication:

```text
if BLOCKER > 0: BLOCKED
else if MAJOR > 0: NEEDS_REVISION
else if MINOR > 0: READY_WITH_WARNINGS
else: READY
```

`INFO` never changes the gate. Structural validation success never bypasses this algorithm.

## Stable finding identifiers

Use `OSR-<DIM>-NNN`, where `<DIM>` is the primary dimension code:

```text
SCH, GOL, FAC, DSN, SPC, CON, TRC, TSK
```

After deduplication, order candidate findings by:

1. canonical dimension order above;
2. repository-relative evidence path;
3. starting line number, with unknown last;
4. normalized finding title.

Assign the three-digit sequence within each dimension in that order. Keep the id stable when only severity or recommendation wording changes.

Display findings by severity (`BLOCKER`, `MAJOR`, `MINOR`, `INFO`), then canonical dimension, evidence path, line, and id. This preserves triage priority without making ids depend on severity.

## Required report

```markdown
# OpenSpec Proposal Review: <change>

## Gate

<BLOCKED | NEEDS_REVISION | READY_WITH_WARNINGS | READY>

<One paragraph explaining the highest-severity reasons and whether implementation can safely begin.>

## Review context

- Runtime: <Codex | Claude Code | other/unknown>
- Repository: <absolute or repository-identifying path>
- OpenSpec root: <repository-relative path or .>
- Change: <active change name>
- Schema: <schema name>
- Stage: <pre-apply | in-progress | all-tasks-done>
- Working tree: <clean | dirty; attributable/uncertain limitation>
- Instructions applied: <AGENTS.md or CLAUDE.md paths / already-loaded scope>
- Evidence mode: <GitNexus + source | source fallback; limitations>
- Read-only verification: <confirmed | violated/uncertain>

## Artifact status

| Artifact | Status | Resolved files | Instruction/validation note |
|---|---|---|---|
| <id> | <done/blocked/etc.> | <stable path list or none> | <summary> |

Strict validation: <PASS | FAIL with issue count>

## Severity summary

| BLOCKER | MAJOR | MINOR | INFO |
|---:|---:|---:|---:|
| <n> | <n> | <n> | <n> |

## Dimension summary

| Dimension | Result | Summary |
|---|---|---|
| Schema and structure | <PASS/FINDINGS/N/A> | <summary> |
| Goal and scope | <PASS/FINDINGS/N/A> | <summary> |
| Repository grounding | <PASS/FINDINGS/N/A> | <summary> |
| Design completeness | <PASS/FINDINGS/N/A> | <summary> |
| Spec testability | <PASS/FINDINGS/N/A> | <summary> |
| Cross-artifact consistency | <PASS/FINDINGS/N/A> | <summary> |
| Traceability | <PASS/FINDINGS/N/A> | <summary> |
| Task readiness | <PASS/FINDINGS/N/A> | <summary> |

## Findings

### <OSR-DIM-NNN> — <short title>

- Severity: <BLOCKER | MAJOR | MINOR | INFO>
- Primary dimension: <dimension>
- Affected dimensions: <comma-separated dimensions>
- Evidence: `<repo-relative-path>:<line>` — <concise observation>; repeat for all relevant locations
- Issue: <what is wrong or uncertain>
- Implementation impact: <what could fail, drift, or require guessing>
- Recommendation: <concrete artifact and decision/content to change>
- Confidence: <high | medium | low> — <required only when not high or when evidence is incomplete>

## Traceability gaps

| Source node | Missing link | Downstream impact | Finding |
|---|---|---|---|
| <goal/requirement/task> | <design/task/verification/etc.> | <impact> | <OSR-...> |

Write “None found” when complete. Do not repeat full finding text.

## Next actions

1. <highest-priority concrete correction or “Proceed to apply”>
2. <rerun instruction when corrections are needed>

## Evidence limitations

- <dirty tree, stale/unavailable index, missing baseline, uncertain attribution, or “None”>
```

## Finding rules

- Every non-`INFO` finding must contain id, severity, primary dimension, evidence, implementation impact, and recommendation.
- Cite both artifact locations for a contradiction.
- Mark suspected issues as uncertain; say what evidence would confirm them.
- Do not claim repository-wide absence from a partial search.
- Do not inflate counts by repeating one root cause across dimensions.
- If there are no findings, keep the Findings section and write “No material findings.”

## Large reports

When findings are numerous:

1. Keep Gate, context, artifact status, and severity totals at the top.
2. Show all `BLOCKER` and `MAJOR` findings before lower severities.
3. Preserve every finding in the Findings section; do not silently truncate.
4. Keep the traceability table concise by referencing finding ids.

## Stage-specific wording

- `pre-apply`: say the proposal is or is not ready to enter implementation.
- `in-progress`: say the review assesses artifact quality against the current tree, not a pristine baseline.
- `all-tasks-done`: say the review does not establish implementation consistency or archive readiness.

Never say `READY` means the implementation is correct; it only means no material proposal-readiness defect was found in the available evidence.
