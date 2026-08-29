## ADDED Requirements

### Requirement: Completion checking is read-only by default
`check-changes-completed` SHALL perform only diagnostics and reporting unless the caller supplies exactly one `--backfill` flag. Without that flag it MUST NOT edit, stage, or commit any task marker, including a deterministic Level-1 match.

#### Scenario: Default completion check finds stale markers
- **WHEN** the selected changes contain incomplete task markers whose implementation evidence is otherwise verified and `--backfill` is absent
- **THEN** the report identifies the proposed marker updates but leaves the working tree and Git history unchanged

#### Scenario: Backfill option is invalid
- **WHEN** `--backfill` is duplicated, given a value, or combined with an unknown option
- **THEN** strict parsing fails before artifact reads, edits, staging, or commits

### Requirement: Explicit backfill intent authorizes only selected task-marker writes
When exactly one `--backfill` flag is present, `check-changes-completed` SHALL treat it as authorization to apply deterministic Level-1 task-marker edits only for the explicitly selected changes after the frozen endpoint and task-input stability checks pass. It MUST NOT modify other artifacts or unselected changes.

#### Scenario: Deterministic backfill is stable
- **WHEN** the caller supplies `--backfill`, Level-1 directly matches task outputs, and every frozen endpoint and selected task input remains stable
- **THEN** the skill may update, stage, and commit only the planned selected `tasks.md` markers

#### Scenario: Backfill evidence drifts
- **WHEN** the target, current HEAD, selection set, or selected task input differs at final revalidation
- **THEN** the skill discards the plan and performs no edit, stage, or commit

#### Scenario: Residual task is semantically ambiguous
- **WHEN** `--backfill` is present but a Level-2 task cannot be directly matched to verified output
- **THEN** the skill asks once whether to add those listed residual markers to the plan and leaves them unchanged if the response is missing, ambiguous, or negative

### Requirement: Completion checking supports model and Team routing
After default mode is made read-only, `check-changes-completed` SHALL support explicit command, natural-language, Team/subagent, and nested-skill invocation. The model MUST include `--backfill` only when the user's request explicitly includes fixing or updating task markers; a request to check, review, report, or assess completion MUST use read-only default mode.

#### Scenario: User asks only for a completion report
- **WHEN** the user asks whether selected changes are complete without requesting marker updates
- **THEN** the model may route to `check-changes-completed` without `--backfill` and the invocation remains read-only

#### Scenario: User asks to check and repair task markers
- **WHEN** the user explicitly asks to update verified stale task markers
- **THEN** the model or Team may route the same selected changes with exactly one `--backfill`
