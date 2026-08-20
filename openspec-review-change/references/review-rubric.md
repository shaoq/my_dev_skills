# OpenSpec Proposal Review Rubric

Use this rubric only after structural preflight. Review evidence, not writing style in isolation.

## Contents

- Severity
- Schema and structural compliance
- Goal and scope clarity
- Repository grounding and impact
- Design completeness
- Spec testability
- Cross-artifact consistency
- End-to-end traceability
- Task implementation readiness
- Deduplication

## Severity

| Severity | Use when | Typical examples |
|---|---|---|
| `BLOCKER` | Safe implementation cannot begin or the review cannot establish its contract | invalid Schema/artifacts, missing apply prerequisite, undefined critical scope, unsupported Schema |
| `MAJOR` | Implementation could begin only by guessing or is likely to deliver incorrect behavior | uncovered requirement, contradictory decision, omitted compatibility/security path, unresolved architecture choice |
| `MINOR` | Implementation remains safe but clarity, maintainability, or verification quality is reduced | weak naming, missing low-risk edge example, imprecise but inferable task evidence |
| `INFO` | Non-problem observation or optional improvement | strong traceability, explicit non-goal, optional future extension |

Do not lower a severity because another artifact happens to contain the missing fact if the artifacts conflict about which statement is authoritative. Do not raise severity based only on document length or personal preference.

## 1. Schema and structural compliance (`SCH`)

Check:

- The active Schema is `spec-driven`.
- `openspec status` and every artifact instruction were loaded.
- Strict validation succeeds, or each failure is captured.
- Proposal capabilities map exactly to delta Spec directories.
- Required artifact sections, normative headers, scenario form, and task checkbox syntax match current instructions.
- Declared artifact status agrees with safely expanded files.

Positive evidence: every capability has one delta Spec, all Requirements have observable Scenarios, and tasks use tracked checkboxes.

Negative evidence:

- `BLOCKER`: missing apply artifact, unsupported Schema, strict validation failure, completed artifact with no matching file.
- `MAJOR`: an instruction-required mapping is absent but implementation scope remains otherwise recoverable.
- `MINOR`: non-normative organizational deviation with no delivery ambiguity.

## 2. Goal and scope clarity (`GOL`)

Check:

- Why states the concrete problem and reason to act now.
- Intended outcome is observable.
- What Changes distinguishes behavior from implementation detail.
- In-scope and relevant non-goals bound the work.
- Terms, actors, target runtime, and lifecycle stage are unambiguous.
- Breaking behavior is labeled and migration impact is visible.

Positive evidence: an implementer can explain what success changes for users and what remains unchanged.

Negative evidence:

- `BLOCKER`: core outcome or target population cannot be determined.
- `MAJOR`: a material boundary has multiple plausible interpretations.
- `MINOR`: a term is undefined but consistently inferable from project context.

## 3. Repository grounding and impact (`FAC`)

Check material claims against current repository evidence:

- Existing files and symbols exist at cited locations.
- Current behavior and installer/runtime assumptions match source.
- Reused APIs and workflows have compatible contracts.
- Planned edits include adjacent callers, configuration, tests, docs, migrations, and cleanup where applicable.
- Required project instruction and impact-analysis workflows were followed.
- Index staleness or dirty-tree limitations are disclosed.

Positive evidence: the proposal identifies the actual source of truth and all direct callers affected by a planned symbol change.

Negative evidence:

- `BLOCKER`: the plan depends on a nonexistent critical system with no replacement decision.
- `MAJOR`: repository behavior contradicts a material design assumption, or a direct affected workflow is omitted.
- `MINOR`: evidence citation is imprecise but the claim is verified.

Never treat unavailable GitNexus or an empty search result as proof of absence.

## 4. Design completeness (`DSN`)

Check applicable concerns:

- Context, constraints, stakeholders, goals, and non-goals.
- Decisions with rationale and meaningful alternatives.
- Interfaces, data/control flow, failure behavior, and compatibility.
- Security boundaries, permission model, and sensitive-data handling.
- Migration, rollout, rollback, observability, performance, and operations.
- Risks, mitigations, and explicit unresolved questions.

Conditional applicability:

- Mark migration `N/A` when no persisted state or incompatible contract changes.
- Mark API compatibility `N/A` when no public or cross-component interface changes.
- Mark security `N/A` only when no trust, permission, secret, or input boundary changes.
- Mark performance/operations `N/A` when execution frequency and resource use are immaterial.
- Do not require rollback machinery for a purely additive, removable documentation/skill change; a deletion/revert path may suffice.

Negative evidence:

- `BLOCKER`: a critical architecture or trust decision is unresolved.
- `MAJOR`: an applicable compatibility, security, migration, rollback, or operational path is omitted.
- `MINOR`: rationale or alternative is thin but the selected behavior is unambiguous.

## 5. Spec testability (`SPC`)

For every Requirement and Scenario, check:

- Normative behavior uses SHALL/MUST.
- WHEN identifies a reproducible state or action.
- THEN states observable behavior, not an internal intention.
- Success, failure, boundary, idempotency, conflict, and recovery paths appear where applicable.
- Scenarios avoid vague terms such as “properly”, “reasonable”, or “works” without a measurable definition.
- Requirements do not prescribe implementation unless that implementation is part of the public contract.

Negative evidence:

- `BLOCKER`: a critical behavior has no determinable expected outcome.
- `MAJOR`: an important error, permission, compatibility, or destructive edge has no scenario.
- `MINOR`: a low-risk boundary is inferable but not explicit.

## 6. Cross-artifact consistency (`CON`)

Compare proposal, design, Specs, tasks, generated instructions, and repository evidence for:

- Names, paths, commands, defaults, states, and supported runtimes.
- Scope and non-goal boundaries.
- Error and conflict behavior.
- Compatibility, permission, migration, and cleanup decisions.
- Read-only versus write behavior.

Negative evidence:

- `BLOCKER`: artifacts conflict on a critical contract and no authority resolves it.
- `MAJOR`: two artifacts prescribe materially different behavior or scope.
- `MINOR`: terminology drifts without changing behavior.

Cite both sides of a contradiction in one finding.

## 7. End-to-end traceability (`TRC`)

Build a many-to-many trace from:

```text
problem/goal → change item → capability → requirement/scenario
             → design decision → implementation task → verification
```

Check:

- Every in-scope change item has a capability and behavioral contract.
- Every Scenario has a delivery and verification path where implementation is required.
- Every material design decision supports a Requirement or stated constraint.
- Every implementation task has a proposal/Spec source.
- Every applicable behavior has documentation, test, validation, migration, or operational verification.

Accept one task covering several Scenarios when the relationship is explicit and testable. Do not demand artificial one-to-one ids.

Negative evidence:

- `BLOCKER`: a critical capability has no implementable delivery path.
- `MAJOR`: a Requirement lacks implementation or verification, or a task introduces unapproved behavior.
- `MINOR`: the mapping is credible but not recorded clearly.

## 8. Task implementation readiness (`TSK`)

Check each task for:

- Dependency order and prerequisites.
- A concrete action and target file/module/artifact.
- Scope small enough for one focused implementation session.
- An observable completion condition.
- Tests or another appropriate verification path.
- Documentation, permission, migration, cleanup, and regression work where applicable.
- No hidden choice between materially different architectures or contracts.

Positive task: “Add a temporary-HOME test covering wrong-link replacement and assert both runtime summaries.”

Weak task: “Improve installation handling.”

Negative evidence:

- `BLOCKER`: implementation cannot start until a critical design choice is made.
- `MAJOR`: a task is unbounded, unverifiable, misordered, or missing for material behavior.
- `MINOR`: target or evidence wording is weak but the action remains safe and clear.

## Deduplication

Before assigning ids:

1. Identify the earliest root cause.
2. Merge downstream symptoms into that primary finding.
3. List every affected dimension and evidence location.
4. Use the highest justified severity.
5. Keep separate findings only when they require different corrective decisions.

Example: one missing runtime decision causing proposal ambiguity, Spec gaps, and vague tasks is one `DSN` primary finding with `GOL`, `SPC`, and `TSK` cross-references—not four findings.
