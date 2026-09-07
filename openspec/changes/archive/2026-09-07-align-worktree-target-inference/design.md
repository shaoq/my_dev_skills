## Context

The three worktree lifecycle skills originally shared one target-selection order. Later authorization changes made `new-worktree-apply` require `--target`, while `merge-worktree-return` and `parall-new-worktree-apply` retained inference. The current single-apply workflow therefore has no compatibility path for an omitted target, even though the repository already has a confirmation pattern for inferred targets.

The repository also contains two related inconsistencies: `check-changes-completed` drops its known target in a suggested single-apply handoff, and the invocation-governance specification still describes unconditional return confirmation after the return skill adopted a deterministic path.

## Goals / Non-Goals

**Goals:**

- Restore the shared target-selection order for `new-worktree-apply`.
- Preserve a no-second-confirmation path when the caller supplies an explicit target.
- Require one complete-plan confirmation when the target is inferred.
- Preserve selected target identity through cross-skill handoffs.
- Align all three worktree skills, specifications, README guidance, and regression tests.

**Non-Goals:**

- Changing target-worktree cleanliness, registration, frozen-hash, artifact-manifest, or source-identity safety gates.
- Allowing an invalid explicit target to fall back to another branch.
- Inferring baselines for `check-changes-completed` or change-scoped `verify-impl-consistency`.
- Changing parallel apply or return target priority.

## Decisions

### Reuse one ordered target resolver

When `--target` is absent, single apply selects the named local ref recorded by the primary worktree, then the local ref named by `origin/HEAD`, then the first existing local ref among `main`, `master`, and `trunk`. Candidate eligibility uses only source resolution and local-ref existence. An explicit but invalid target fails immediately. Once a candidate wins selection, worktree ownership, topology, identity, HEAD/ref, cleanliness, and path checks are post-selection gates; failure stops the invocation instead of trying a lower-priority candidate.

The merge and parallel skill texts record the same standardized `TARGET_SOURCE` values and post-selection no-fallback rule, avoiding a second target-selection dialect.

### Separate target selection from write authorization

Single apply records `TARGET_SOURCE=explicit` or `TARGET_SOURCE=inferred:<source>`. An explicit target uses the deterministic path already authorized by the concrete implementation request. An inferred target uses an interactive path that displays the complete preflight snapshot and requires one affirmative confirmation before writes. Dry-run reports the same inferred snapshot but never asks for write confirmation.

Safety blockers remain non-overridable. Confirmation authorizes only the stable plan; it cannot approve a dirty target, missing worktree registration, artifact drift, unsafe paths, or an out-of-scope side effect.

### Revalidate each authorization path differently

Both paths use immutable snapshots. Deterministic-path drift fails closed and requires a fresh invocation. Each interactive confirmation creates a new immutable numbered snapshot, while `ACTIVE_CONFIRMED_SNAPSHOT` identifies the round used by revalidation. Interactive-path drift invalidates that pointer and rebuilds all read-only facts. A new blocker stops without another prompt; only a complete blocker-free plan can create the next confirmation round. `TARGET_SOURCE` is part of snapshot equality so an environmental change cannot silently alter why a target was selected.

### Preserve known targets across skill handoffs

`check-changes-completed` already has an explicit frozen `TARGET_BRANCH`. Its implementation hint passes that value to `new-worktree-apply` so the next workflow does not discard known scope and trigger inference unnecessarily.

### Keep verification baselines explicit

Completion and implementation-consistency checks attribute evidence to a caller-selected Git range and may influence backfill or archive conclusions. Their explicit `--target`/`--base` contracts remain unchanged.

## Risks / Trade-offs

- [The primary worktree branch may be an unintended target] → The inferred path displays the branch, source, worktree, frozen hash, and writes, then requires confirmation.
- [Target state may change while awaiting confirmation] → Independent revalidation compares every material field and invalidates stale confirmation.
- [Static wording tests may allow an incomplete behavioral contract] → Add assertions for optional syntax, fallback order, authorization-path separation, invalid-explicit no-fallback, and target-preserving handoff.
- [Existing lifecycle tests currently fail on an archived delta path] → Repair the path before using the suite as completion evidence.
