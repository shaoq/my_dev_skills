## Context

The return workflow currently equates proposal completion with cleanup eligibility by requiring `DONE == TOTAL` after merge. Users intentionally leave some tests unchecked with the exact `[post-merge-verification]` tag because those tests must be run manually later in the target worktree. Preserving the source worktree adds no recovery value once delivery is merged and all Git safety gates pass.

The workflow also has one unconditional write-boundary confirmation. In a manual invocation that omits `--target` or presents pending source changes, that confirmation resolves real choices: which inferred target to use and which files to commit. In a governed Team handoff or direct invocation with an explicit target and a clean canonical source, the same prompt repeats an already bounded return request without changing the plan. A global removal would be unsafe, while globally requiring explicit proposal/target and a clean source would unnecessarily remove the existing manual convenience path.

## Goals / Non-Goals

**Goals:**

- Let `merge-worktree-return` distinguish ordinary incomplete work from explicitly deferred user-run verification.
- Apply the same deterministic policy independently to every parallel child.
- Permit ordinary cleanup only when every unchecked task is explicitly deferred and all existing structural gates pass.
- Keep deferred tasks visible and keep the OpenSpec change incomplete/non-archivable.
- Let a clear return request with an explicit target and clean canonical source proceed after immutable preflight/revalidation without a second confirmation.
- Preserve proposal derivation, target inference, and confirmation-authorized source auto-commit for manual callers.

**Non-Goals:**

- Running, marking, staging, or committing deferred tests.
- Relaxing Git identity, containment, cleanliness, frozen-hash, merge, or cleanup gates.
- Changing proposal discovery, batching, dependency declaration, or merge ordering.
- Requiring proposal or `--target` globally, removing target fallback, or removing manual auto-commit support.
- Adding caller-runtime modes, Issue/task-platform authorization identifiers, or generic approval flags.
- Removing or changing the parallel workflow's existing material-write confirmation.

## Decisions

### Use an exact task-line tag

Only unchecked checkbox lines containing the exact literal `[post-merge-verification]` are deferred. Every other unchecked task is ordinary unfinished work and blocks cleanup. Missing/unreadable tasks, zero recognized tasks, or an unclassifiable result remain fail-closed.

Alternative: infer deferred tests from wording. Rejected because natural-language inference would make cleanup nondeterministic.

### Separate delivery cleanup from OpenSpec completion

The return workflow records `TASK_CLEANUP_POLICY_PASSED=true` when there are no ordinary unchecked tasks. Deferred tasks remain unchecked, are listed in the final report, and keep the change non-archivable. The Skill does not execute them.

Alternative: mark deferred tasks complete after merge. Rejected because the user explicitly owns their execution and marking them without evidence would be false reporting.

### Preserve every existing structural gate

`TASK_CLEANUP_POLICY_PASSED` is an additional explicit input to `CLEANUP_READY`; it does not replace target/source identity, frozen commit, containment, cleanliness, delivery, or post-merge integrity checks.

### A verified deferred child may advance the parallel controller

For each parallel child, the Worker and controller use the same exact classification. A child with only deferred tasks remains incomplete/non-archivable but, after its exact-hash merge and structural verification pass, it may be cleaned and may advance `EXPECTED_TARGET_HEAD` and dependent Waves. Deferred tasks are not project verification commands and are not run by the Worker or controller.

### Route authorization from observable facts, not caller identity

The single-return workflow records whether the current request clearly asks to perform the return, whether `TARGET_SOURCE=explicit`, and whether the canonical source status is strictly clean. Proposal identity may be explicit or deterministically derived from exactly one `worktree-` prefix; derivation does not by itself create an unresolved choice.

Define the deterministic path as:

```text
DETERMINISTIC_RETURN_READY =
  LIMITED_RETURN_AUTHORIZED
  AND TARGET_SOURCE == explicit
  AND SOURCE_CLEAN
  AND PREFLIGHT_PASSED
```

A direct user command, a clear natural-language return request, or an exact Team/subagent/Skill handoff may establish `LIMITED_RETURN_AUTHORIZED`; discussion, review, status inspection, or a request without return intent may not. This classification does not depend on Claude, Codex, a task platform, a runtime identifier, or an authorization token.

When `DETERMINISTIC_RETURN_READY=true`, the Skill prints the same complete audit plan, freezes it, performs an independent final read-only revalidation, and opens only the existing bounded return writes without asking a second question. Any drift fails closed and requires a fresh invocation.

Alternative: add `--team`, `--autonomous`, `--authorized`, or `--yes`. Rejected because caller identity does not determine safety, and approval flags would duplicate the observable preconditions without clarifying the return target or pending content.

### Preserve one interactive compatibility path for unresolved choices

An explicit return request with an inferred target, pending source changes, or both continues through the existing confirmation summary. The summary shows `TARGET_SOURCE`, the resolved target snapshot, every pending file, the proposed source commit, merge/verification/cleanup writes, and deferred-task status. One affirmative response authorizes that complete plan; final revalidation must prove it unchanged before any write.

The interactive path may keep the existing confirmation-authorized `git add -A`, force-add of the selected proposal's `tasks.md`, and source commit. The deterministic path never reaches those commands because `SOURCE_CLEAN` is one of its entry predicates. A dirty source therefore selects the interactive path rather than failing globally or being silently committed.

Alternative: require every source to be clean. Rejected because it removes the Skill's established manual “commit and return” behavior. Alternative: let the deterministic path auto-commit. Rejected because it could merge content that was not part of the clean reviewed snapshot.

### Treat conflicts as a new decision in the deterministic path

If rebase or merge conflicts arise after a no-second-confirmation start, the deterministic plan no longer describes the resulting code. The workflow aborts the incomplete Git operation when safe, preserves the canonical source, and stops for a fresh user or development decision. It does not silently resolve conflicts or downgrade into an already-authorized interactive write path.

The confirmed compatibility path retains its explicitly presented conflict behavior. A later implementation may unify conflict handling separately, but this change does not remove manual functionality beyond preventing unconfirmed conflict resolution in the deterministic path.

## Risks / Trade-offs

- [A tag is added accidentally] → Require the exact literal on the unchecked task line and display every deferred item in the confirmation and final report.
- [Cleanup is mistaken for completion] → State that the proposal remains incomplete/non-archivable and provide the target worktree/commit for later user verification.
- [A deferred child advances dependencies before manual testing] → Report the deferred evidence explicitly; dependency readiness represents verified code delivery, not OpenSpec archival readiness.
- [A routed request is mistaken for return authorization] → Require clear return intent plus an explicit target for the deterministic path; status, review, and exploratory requests remain read-only.
- [A manual caller loses proposal/target inference] → Keep the current optional grammar and fallback order; inferred targets stay behind the interactive plan confirmation.
- [Pending files bypass review in the deterministic path] → Require strict source cleanliness; dirty sources use the interactive plan that lists and confirms the exact pending set.
- [State changes while the audit plan is displayed] → Freeze an immutable preflight snapshot and compare a separate final revalidation snapshot; any difference requires a fresh invocation.
- [Conflict resolution changes reviewed code] → Stop the deterministic path on conflict and preserve the source rather than inventing an unreviewed resolution.
