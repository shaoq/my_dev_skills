# Implementation evidence

## Platform-managed authorization-request regression

- Observed date: `2026-08-31` (`Asia/Shanghai`).
- Issue: `UNIDRAG-12` remained `in_progress`.
- Preparation trigger comment: `01a05616-35b9-7d6d-84fc-6503837a3425`.
- Preparation task: `01a05616-35d2-7932-8839-5f8a436505da`.
- Multica platform-managed task-result comment: `01a0561d-5730-7e51-952c-2f52f07c3f50`, direct parent `01a05616-35b9-7d6d-84fc-6503837a3425`, authored by Architecture Lead Agent `f6135960-aea8-4aaa-a970-0c1e60544a90`, revision `1`.
- The prepared scope digest `sha256:14913ac3e9e9ecb2a9300e9041a9067588f130358b725d042d5cf0acaa305117` was not consumed: it had been frozen before the platform-managed request-comment UUID existed and therefore could not satisfy the adapter's exact request-comment binding contract.
- Root cause: the existing response selector handled the future human authorization-response UUID, but the automatically materialized authorization-request comment was a second future UUID without a canonical selector.

## RED / GREEN evidence

The focused RED run added valid and invalid request-binding fixtures. Before production-document updates, `test_human_action_rendering_contract_is_present` failed because the protocol surfaces lacked `multica_task_result_authorization_request_v1`, `source_task_id`, platform-managed materialization wording and the request selector in the material bundle. The fixture-shape test passed, confirming the failure was in the production contract rather than the fixture parser.

The implementation adds a two-stage binding chain:

1. Resolve `multica_task_result_authorization_request_v1` to exactly one unedited revision-1 platform comment by preparation `source_task_id`, trigger parent, Agent, authorization content, Issue/workspace and uniqueness.
2. Require the human response to be a direct child of that resolved request, then resolve `multica_authorization_response_parent_v1` only to the current task's verified `trigger_comment_id`.

Missing, duplicate, edited or mismatched request/response candidates fail closed without an Agent-invoked Issue diagnostic write. Platform materialization is reported truthfully as a platform-managed comment rather than as “no platform comment”.

## Verification

| Check | Result |
|---|---|
| Focused request/response binding tests | PASS, 2 tests |
| `python3 -m unittest tests.test_multica_architecture_approval_adapter_contract -v` | PASS, 6 tests |
| `python3 -m unittest discover -s tests -v` | PASS, 31 tests |
| `bash tests/architecture-design-workflow-safety.sh` | PASS, static contract with 27 fixtures |
| Skill quick validation: `multica-architecture-approval-adapter` | PASS |
| Skill quick validation: `architecture-design-workflow` | PASS |
| `openspec validate add-verified-human-access-evidence-links --strict` | PASS |
| `git diff --check` | PASS |

GitNexus was rebuilt before the implementation investigation, but the final MCP `detect_changes` call could not read the index because the index database storage version was `43` while the active MCP runtime supported version `42`. Final impact evidence therefore uses a bounded source diff plus the full contract, runner, installer and Skill validation suites. The changed production surfaces are limited to `multica-architecture-approval-adapter`; `architecture-design-workflow`, Multica core, `uni-architecture` and the target business repository are unchanged by this implementation.

## Operational boundary

- `activation=not_run`
- `sandbox_acceptance=not_run`
- `UNIDRAG-12 retry=not_run`
- No Skill activation, Issue delivery, attachment upload, status change or retry is authorized by this local implementation. Each later platform mutation requires a new exact current operational authorization.
