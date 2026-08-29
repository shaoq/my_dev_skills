## 1. Invocation and model-governance regression tests

- [x] 1.1 Extend skill safety tests to assert that affected skills declare no `model:` override, remain model/Team/nested-invocable, and do not carry user-only Claude or Codex invocation policy.
- [x] 1.2 Add behavioral assertions that `new-worktree-apply` still performs deterministic preflight and revalidation without a second confirmation.
- [x] 1.3 Add assertions that parallel proposal creation, parallel worktree apply, and worktree return retain exactly one material-write confirmation boundary after their read-only plans.
- [x] 1.4 Run the targeted tests before implementation and record the expected RED failures for the current overly restrictive policy.

## 2. Worktree and proposal workflow routing

- [x] 2.1 Remove user-only invocation frontmatter and narrow the descriptions of `new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, and `merge-worktree-return` to action-oriented user intent.
- [x] 2.2 Remove `new-worktree-apply/agents/openai.yaml` when it contains only the implicit-invocation prohibition, and remove Runtime activation/provenance checks and reporting from the single-worktree workflow.
- [x] 2.3 Preserve the `new-worktree-apply` no-second-confirmation behavior and all target, manifest, physical containment, immutable snapshot, frozen-hash, scope, and failure-preservation gates.
- [x] 2.4 Preserve one affirmative write-boundary confirmation in `parall-new-proposal`, `parall-new-worktree-apply`, and `merge-worktree-return`, including snapshot revalidation after any wait.

## 3. Completion-check authorization boundary

- [x] 3.1 Add tests proving `check-changes-completed` is zero-write by default and rejects duplicate, valued, or malformed `--backfill` arguments.
- [x] 3.2 Add tests proving exactly one `--backfill` authorizes only deterministic selected `tasks.md` marker edits after stable final revalidation.
- [x] 3.3 Preserve the interactive decision for semantically ambiguous Level-2 residual tasks and prove missing, negative, or ambiguous responses leave them unchanged.
- [x] 3.4 Implement strict `--backfill` parsing, read-only default reporting, selected-change containment, and model/Team-invocable frontmatter/description behavior.

## 4. Environment consistency validation

- [x] 4.1 Run GitNexus upstream impact analysis for `check_skill_consistency` and warn before implementation if the refreshed result is HIGH or CRITICAL.
- [x] 4.2 Add setup environment unit tests for a valid model-invocable skill that omits both `allowed-tools` and `disable-model-invocation`, while retaining Bash preapproval mismatch diagnostics.
- [x] 4.3 Update `setup-skills-env.py` so permission preapproval and invocation policy are evaluated independently and normal automatic invocation is not reported as a missing guardrail.
- [x] 4.4 Run GitNexus `detect_changes` before any implementation commit and verify only the expected setup flow and skill/document surfaces are affected.

## 5. Documentation and specification synchronization

- [x] 5.1 Update README guidance to distinguish current-model inheritance, intent-based invocation, write authorization, tool permission, and deterministic safety validation.
- [x] 5.2 Apply the approved `skill-invocation-governance`, `worktree-targeting`, and `target-aware-verification` deltas to their canonical specifications without changing unrelated requirements.
- [x] 5.3 Remove obsolete tests and documentation that require Runtime activation assertions, explicit-only routing, or model/nested invocation rejection.

## 6. Final verification

- [x] 6.1 Run `bash tests/worktree-lifecycle-safety.sh` and `bash tests/target-aware-verification-safety.sh` and record totals and exit codes.
- [x] 6.2 Run `python3 -m unittest tests/test_setup_skills_env.py` and record the test count and exit code.
- [x] 6.3 Run strict OpenSpec validation for `relax-skill-invocation-authorization-gates` and `enable-target-aware-autonomous-rd-workflow`, then run `git diff --check`.
- [x] 6.4 Review the final diff for preserved worktree safety, exactly-once authorization boundaries, model inheritance, Team/GitNexus compatibility, and absence of unrelated changes.
