## Why

Several repository skills conflate model selection, skill invocation, and write authorization. In particular, user-only invocation gates block natural-language routing, Team/subagent orchestration, and nested skill workflows even when the real requirement is only to avoid repeated confirmation or to preserve a single confirmation immediately before material writes.

## What Changes

- Keep every affected skill on the caller's current model by leaving the optional `model:` frontmatter unset; do not use invocation policy as a model-selection control.
- Remove user-only invocation policy from `new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, and `merge-worktree-return`, allowing explicit commands, natural-language routing, Team/subagent orchestration, and nested skill workflows when their descriptions match the user's request.
- Remove the Codex-only `new-worktree-apply` implicit-invocation prohibition and the Runtime provenance/activation-assertion protocol built around it.
- Preserve `new-worktree-apply`'s requested behavior: after deterministic read-only preflight and stable pre-write revalidation, proceed without a second interactive confirmation.
- Preserve exactly one write-boundary confirmation for parallel proposal creation, parallel worktree apply/merge, and worktree return/cleanup.
- Make `check-changes-completed` read-only by default; require an explicit backfill mode or a write-boundary confirmation before editing, staging, or committing task markers, then allow normal model and Team routing.
- Correct the skill consistency checker so `allowed-tools` preapproval and model invocation policy are assessed independently; model-invocable skills are not warnings merely because they omit both fields.
- Update tests and documentation to distinguish model inheritance, invocation routing, authorization, permissions, and deterministic safety gates.

## Capabilities

### New Capabilities

- `skill-invocation-governance`: Defines cross-runtime rules for inheriting the current model, permitting model/Team/nested routing, and placing authorization at material side-effect boundaries instead of the skill entry point.

### Modified Capabilities

- `worktree-targeting`: Removes Runtime-native explicit-only activation from single-worktree apply while preserving no repeated confirmation and the existing target, snapshot, containment, merge, and cleanup safety contracts; keeps one confirmation for parallel apply and return writes.
- `target-aware-verification`: Makes completion checking read-only by default and requires explicit authorization before task backfill or commit.

## Impact

- Skills: `new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, `merge-worktree-return`, and `check-changes-completed`.
- Runtime metadata: `new-worktree-apply/agents/openai.yaml` and affected skill frontmatter.
- Environment validation: `setup-skills-env.py` and its unit tests.
- Safety/documentation: `tests/worktree-lifecycle-safety.sh`, target-aware verification tests, README, and the affected canonical OpenSpec specifications.
- No application runtime, public API, production deployment, remote write, or model override is introduced.
