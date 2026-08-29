## Context

The repository currently mixes five independent controls:

1. **Model selection** — the optional `model:` skill frontmatter override.
2. **Invocation routing** — whether a user, the current model, a Team/subagent, or another skill may select a workflow.
3. **Authorization** — whether the user's request or a later confirmation permits a material write.
4. **Tool permission** — whether a tool call is pre-approved, represented by `allowed-tools` on supporting Runtimes.
5. **Safety validation** — deterministic target, snapshot, containment, cleanliness, and drift gates.

The affected skills set `disable-model-invocation: true`, and `new-worktree-apply` additionally disables implicit Codex invocation. Those controls do not pin the current model; they prevent model/Team routing. The resulting behavior conflicts with autonomous R&D orchestration and is redundant where a workflow already pauses at a complete write-boundary confirmation.

## Goals / Non-Goals

**Goals:**

- Keep the caller-selected model unchanged by omitting `model:` overrides.
- Permit explicit command, natural-language, Team/subagent, and nested-skill routing for the affected workflows.
- Express authorization once, at the narrowest material side-effect boundary.
- Preserve deterministic worktree and Git safety gates independently of invocation source.
- Make completion checking genuinely read-only unless backfill is explicitly requested.
- Prevent the environment checker from treating normal model-invocable skills as malformed or unsafe.

**Non-Goals:**

- Removing target, cleanliness, immutable hash, snapshot, path containment, manifest, verification, or cleanup gates.
- Allowing deployment, production mutation, remote publication, irreversible migration, credential use, or unrelated destructive cleanup.
- Adding or selecting a different model for any skill.
- Removing the write-boundary confirmation from parallel proposal creation, parallel apply/merge, or worktree return/cleanup.

## Decisions

### Decision 1: Separate model inheritance from invocation policy

The affected skills SHALL omit `model:` so the Runtime continues with the caller's current model. `disable-model-invocation` and Codex `allow_implicit_invocation` SHALL not be used as model-pinning controls.

Alternative considered: retain user-only invocation because its name appears to concern the model. Rejected because Runtime documentation defines it as an invocation-routing control, and it hides the workflow from model and subagent selection rather than preserving a model choice.

### Decision 2: Route by user intent, not by command syntax

`new-worktree-apply`, `parall-new-proposal`, `parall-new-worktree-apply`, `merge-worktree-return`, and the corrected completion workflow SHALL be model-invocable. Their descriptions MUST narrowly identify action intent so discussion, review, or exploration does not trigger an implementation or merge workflow. A user may still invoke them explicitly.

Natural-language routing and Team/nested routing are equivalent entry paths; none gains broader authority than the initiating user request. Repository text, environment values, or inferred metadata cannot enlarge the workflow's documented scope.

### Decision 3: Use one authorization boundary per material operation

- `new-worktree-apply`: a user request to implement/apply the selected proposal authorizes its limited canonical source-worktree operation. After read-only preflight and stable revalidation, it writes without a second confirmation.
- `parall-new-proposal`: routing may be automatic, but proposal artifacts are created only after the displayed split/dependency plan receives one affirmative confirmation.
- `parall-new-worktree-apply`: routing and read-only planning may be automatic, but spawn, worktree creation, apply, merge, and conditional cleanup start only after one complete batch-plan confirmation.
- `merge-worktree-return`: routing and preflight may be automatic, but commit/rebase/merge/cleanup start only after one complete return-plan confirmation.
- `check-changes-completed`: default mode is strictly diagnostic. `--backfill` explicitly authorizes deterministic Level-1 task-marker changes after final drift checks; ambiguous Level-2 completion still requires an interactive confirmation before it is added to the plan.

Safety failures are never converted into confirmation prompts. A user cannot confirm past a dirty target, identity mismatch, containment escape, stale snapshot, incomplete evidence, or out-of-scope operation.

### Decision 4: Remove the Runtime activation-assertion protocol

Delete the Codex implicit-invocation prohibition when it contains no other metadata, remove the Claude user-only invocation field from affected skills, and remove Runtime-gate reporting and tests. Invocation source is no longer a safety fact in `PREFLIGHT_SNAPSHOT`; the exact parsed arguments and repository state remain material facts.

### Decision 5: Correct environment consistency validation

`allowed-tools` is a permission preapproval list, not an invocation or model-selection guard. `check_skill_consistency` SHALL continue checking declared Bash preapprovals against the standard permission set, but SHALL not warn merely because a skill has neither `allowed-tools` nor `disable-model-invocation`. Tests SHALL cover a valid model-invocable skill with neither field.

### Decision 6: Test behavioral boundaries, not restrictive keywords

Tests SHALL assert:

- no affected skill declares a model override;
- the affected workflows remain discoverable/model-invocable;
- `new-worktree-apply` has no Runtime activation gate and still has no second confirmation;
- parallel proposal, parallel apply, and return retain exactly one pre-write confirmation boundary;
- completion default mode is zero-write and `--backfill` is required for deterministic edits;
- safety gates remain unchanged and GitNexus/other MCP tools remain available through normal Runtime permissions.

## Risks / Trade-offs

- [A vague natural-language request could select a write workflow] → Tighten descriptions to action verbs and require concrete proposal/change/target inputs; discussion and review remain outside apply descriptions.
- [Removing entry gates increases the number of possible orchestrators] → Keep authority scope identical for every entry path and retain all deterministic pre-write validation.
- [Completion behavior changes for existing callers] → Default to the safer read-only mode and document `--backfill`; reject obsolete ambiguous write expectations rather than silently committing.
- [Cross-Runtime metadata differs] → Define behavior in terms of observable routing and authorization, while omitting Runtime-specific policy unless it provides non-policy interface metadata.
- [Confirmation could be duplicated by an outer Team workflow] → Treat the skill's documented write boundary as authoritative; outer orchestration may summarize but MUST NOT add a second confirmation for the same operation.

## Migration Plan

1. Update specs and README terminology to separate model, routing, authorization, permission, and safety.
2. Update skill frontmatter/descriptions and remove the Codex-only invocation policy file.
3. Refactor `new-worktree-apply` to remove Runtime activation checks while preserving snapshots and safety gates.
4. Keep existing confirmation checkpoints in parallel proposal, parallel apply, and return workflows while allowing automatic routing.
5. Make completion checking read-only by default and add strict `--backfill` parsing/authorization.
6. Correct setup consistency validation and add regression tests.
7. Run the existing worktree, target-aware verification, setup environment, and OpenSpec strict suites.

Rollback is a normal revert of this change. No repository history, worktree, remote branch, or production state migration is required.

## Open Questions

None. The user has selected current-model inheritance, normal model/Team routing, no repeated confirmation for single-worktree apply, and one write-boundary confirmation for the higher-impact workflows.
