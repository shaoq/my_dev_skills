# Multica adapter sandbox acceptance checklist

## Preconditions

- A current `operation variant=sandbox` authorization names the existing sandbox workspace, Issue, Architecture Agent, exact test writes, retained objects, failure behavior and excluded production scope.
- The core and adapter IDs have been verified with the activation runbook's final `agent skills list` read-back.
- The Issue is dedicated to this acceptance; it is not a production Architecture Team Issue.
- Record adapter repository commit, consumed core revision, observed Multica/CLI version or commit, workspace/Agent/Issue identities, and verifier/time.

## Acceptance checks

1. Deliver one current compatible packet to the existing sandbox Issue. Confirm the first screen shows why a decision is ready, target Decision Owner, recommendation/reason, accepted risks, four Chinese option consequences, exact response and After response before marker/digest audit detail.
2. On desktop, use the target member account to open each exact `ARCH-DESIGN`、`ARCH-REVIEW` and `ARCH-APPROVAL-PACKET` stable ref. Record `design.desktop`、`review.desktop`、`packet.desktop` independently with comment/attachment IDs and refs.
3. On mobile, use the same target member scope to open and retrieve each of the same three exact materials. Record `design.mobile`、`review.mobile`、`packet.mobile` independently. Attachment cards or a generic `OK` are insufficient.
4. Re-download each attachment by its durable identity and verify its raw bytes against the frozen SHA-256 digest. Do not treat rendered text, a signed URL, or an optional PDF as the canonical check.
5. Reply beneath the exact current packet comment with one short legal token only. Re-read the parent chain, author identity, packet marker, target-human mapping, and content digest before accepting the decision evidence. Separately verify that token-plus-prose is non-binding and produces `fresh_token_required=yes`; a revision brief uses a different packet-bound `decision_context_ref`.
6. Create a newer packet delivery, then verify that a reply bound to the superseded packet remains audit-only/no-op while a new exact-current short-token reply is the only effective decision.
7. Exercise one authorized retry/partial-failure path. Before the retry, require a new operational request listing every retained object and exact incremental write. Confirm reconciliation does not silently duplicate, relabel, delete, overwrite or mark incomplete delivery ready; metadata/comment conflicts, missing attachment, digest mismatch, missing stable ref, mapping uncertainty, or stale writer must close as `review_packet_unavailable` while preserving the real Review conclusion and existing objects.

## Outcome record

Record `sandbox_acceptance=passed` only when every named human checklist item completes for the authorized sandbox scope. Desktop-only results, generic confirmation, missing supersession/token-context/retry evidence or unavailable target-member mobile access remain `not_run|failed`; keep production activation inactive and capture each failed check plus observable closing condition. Where platform capability—not configuration—prevents completion, recommend a separate platform capability proposal; that recommendation is not authorization to alter Multica or create resources.

## Implementation status

For this repository implementation, no real workspace import, Agent binding, sandbox Issue, network call, or platform write was authorized or performed:

```text
activation=not_run
sandbox_acceptance=not_run
workspace=n/a
agent=n/a
```
