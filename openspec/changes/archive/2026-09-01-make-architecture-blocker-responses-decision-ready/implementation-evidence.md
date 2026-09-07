# Implementation evidence

## Status

- Automated implementation: complete
- Live UNIDRAG-12 acceptance: passed with real Owner invalid/canonical replies and accepted/active continuation readback
- Baseline: `require-actionable-architecture-blockers` archived on 2026-09-01 in both repositories before this change

## Affected-surface manifest

| Ownership boundary | Changed surface | Runtime responsibility |
|---|---|---|
| Portable core | `architecture-design-workflow/SKILL.md`, blocker reference/template, mandate reference, recommendation fixtures | Produces platform-neutral recommendation intent/reason/confidence/boundary/alternatives; no Multica required fields |
| Optional adapter | `multica-architecture-approval-adapter/SKILL.md`, blocker projection/reply reference, comment template, correction fixtures | Binds current Action ID, renders the first-screen recommendation, emits at-most-once state-neutral correction |
| Repository contract | OpenSpec artifacts and deterministic tests | Specifies and verifies behavior only |
| Explicitly unchanged | Multica core/runtime, Team/Agent/Issue resources, business repositories | No code or resource creation/update performed by automated implementation |

The same-name `uni-architecture` change maps the portable semantics into architecture Team instruction sources and audit evidence. It contains no Skill runtime, CLI, renderer, schema validator, or platform adapter implementation.

## RED / GREEN evidence

- RED: `python3 -m unittest tests.test_actionable_architecture_blocker_contract` failed because recommendation fields, first-screen recommendation layout, correction identity/idempotency and no-state-change rules were absent.
- GREEN: the same targeted suite passed `10/10` after implementation.
- Regression: combined Python contract suite passed `31/31`.
- Static workflow safety: `architecture workflow safety: PASS (static, 27 fixtures)`.
- Package validation: both Skill directories returned `Skill is valid!` using the validator with an ephemeral `PyYAML` dependency.
- OpenSpec: strict validation passed.
- `git diff --check`: passed.
- GitNexus `detect-changes --scope all`: 10 files / 95 symbols, 0 affected processes, risk `low`, `partial=false`, `truncated=false`.

## Safety invariants

- Only exact canonical replies are consumed.
- A correction candidate remains invalid input and keeps `awaiting_input + blocked`.
- `reply_correction_v1` is keyed by `action_id + request_revision`, binds invalid comment ref/revision/raw digest, and is emitted at most once.
- Correction never mentions an Architecture Agent, creates a task, restores Issue state, or changes Review/approval/implementation authority.
- A canonical reply still requires accepted/active handoff task readback before `in_progress`.

## Live acceptance

- Installed core identity: `b93d9e63-027c-4227-a760-4591444e3334`, readback `updated_at=2026-09-01T10:04:20Z`, aggregate digest `sha256:7ca7d378e26b101397c2f031ef2241a5206bc9542c011ab5fca9d165665a4712`, Lead binding enabled and exact.
- Installed adapter identity: `bbe335c1-e83a-4e27-8922-4fd511b461d7`, readback `updated_at=2026-09-01T10:04:28Z`, aggregate digest `sha256:6679d1f8f301c4cc02d8a371d2c5103897be742f52c3bc5b7cf16b00b9d02918`, Lead binding enabled and exact.
- Live trigger: `comment:01a05c72-c5b8-7771-af0d-e069dbc74af2@revision:1`; Lead task `01a05c72-c5dc-7ad0-b405-3e0a3154ff39` completed at `2026-09-01T10:23:51Z` with `error=null`; result comment `01a05c7e-9dbc-7db7-8d71-336582c2f116@revision:1`.
- Superseding blocker: attempt `unidrag12-g1-product-evidence-owner-01a05c72-a14`, Action `UNIDRAG-12-G1-PRODUCT-EVIDENCE-OWNER-01A05C72-A14`, `comment:01a05c7b-862b-7691-858f-e950567d056d@revision:1`, superseding A13 while preserving the old invalid reply/correction as read-only context.
- First-screen check: mention ends at cp0 `63`; recommended Action occupies cp0 `286..356`, distance `223` after mention and before evidence at cp0 `1458`. Issue readback is revision `287`, `blocked`, Action `awaiting_input`, `recommendation_intent=request_discovery`, `next_task_id=none`.
- Invalid Owner reply: `comment:01a05c83-0540-7d9c-8671-7315415feea4@revision:1@sha256:3c44bf5002ff9b7fae642598031a9cd8fc247a64c5601e7ec07b235a8e0073c4`, content intent `provide_self`, not consumed.
- Exactly one state-neutral correction: `comment:01a05c86-104b-7905-88fa-a52ad5651ff4@revision:1@sha256:9ded052a0808211852f65af6757b94687b4e1ecdf4de2f7c9471f1d92693020d`; no Agent mention; canonical action `ACTION UNIDRAG-12-G1-PRODUCT-EVIDENCE-OWNER-01A05C72-A14: 由我负责`.
- Correction task `01a05c83-0576-7929-be4e-84b66e501e30` completed at `2026-09-01T10:32:43Z`, `error=null`. Issue revision `296` remains `blocked`, blocker `awaiting_input`, `next_task_id=none`, human gate `none`, metadata `7565/8192 bytes`, idempotency result `first_and_only_correction`.
- Canonical Owner reply: `comment:01a05c8a-f724-726f-9b36-1dc9c51eafdf@revision:1@created:2026-09-01T10:36:46Z@sha256:f73513a12af4c7c07816c1126c0a3acdb94a44472cedbe1474f9748abfe09c4d`. Removing one leading current Architecture Lead mention and normalizing whitespace yields the exact current Action `ACTION UNIDRAG-12-G1-PRODUCT-EVIDENCE-OWNER-01A05C72-A14: 由我负责`.
- Consumption task `01a05c8a-f731-7db8-b50e-756a7f125cb5` completed at `2026-09-01T10:42:17Z` and produced exactly one dedicated self-handoff, `comment:01a05c8e-ec13-73d3-aaff-d09ee9c28453@revision:1@sha256:cb8f403c5ccff77c59c5ead88e9c156885757a16eb78d544b54eb362b2711519`.
- Exactly one response continuation task was created: `01a05c8e-ec2a-7d3e-8f89-19dbc698ac65`, assigned to the existing Architecture Lead with precise delegated attribution. It was read back as `queued`, became `running` at `2026-09-01T10:42:17Z`, and completed at `2026-09-01T10:51:24Z` with `error=null`. The Issue changed from revision `304@blocked` to `305@in_progress` only after accepted/active readback; revision `309` records `next_task_id`, `queued_accepted`, and `status=valid`.
- Repeated read-only reconciliation of the same canonical response event found one consumption task, one response self-handoff, and one Owner-binding verification task only. The later Product decision-prep handoff `01a05c96-2c9e-769a-be14-94563e8204a6` and task `01a05c96-2cbc-74ae-8fba-6e89abbb8604` have a new continuation identity, distinct completion condition, and precise delegation from the completed verification task, so they are normal business progression rather than duplicate delivery. G1 `$.request_id=deny`, the real-content outlet remains `OFF`, and Product decision, design, Review, approval, packet, ADR, OpenSpec, implementation, deployment, resource creation, and history rewrite remain forbidden.
- Fresh post-acceptance verification passed: targeted tests `10/10`, architecture contract discovery `21/21`, standalone safety `27 fixtures`, both Skill package validators, both repositories' strict OpenSpec validation, the repository Team contract, and both repositories' `git diff --check`.
