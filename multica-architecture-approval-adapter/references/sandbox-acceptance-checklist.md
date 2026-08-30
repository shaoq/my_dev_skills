# Multica adapter sandbox acceptance checklist

## Preconditions

- A human has separately authorized sandbox activation and named an existing sandbox workspace, Issue, and Architecture Agent.
- The core and adapter IDs have been verified with the activation runbook's final `agent skills list` read-back.
- The Issue is dedicated to this acceptance; it is not a production Architecture Team Issue.
- Record adapter repository commit, consumed core revision, observed Multica/CLI version or commit, workspace/Agent/Issue identities, and verifier/time.

## Acceptance checks

1. Deliver one current compatible packet to the existing sandbox Issue. Confirm the concise comment shows the real Review conclusion, recommendation/non-approval statement, legal decision tokens, and instruction to open all complete attachments.
2. On desktop, use the target member account to open each exact `ARCH-DESIGN`、`ARCH-REVIEW` and `ARCH-APPROVAL-PACKET` attachment from the packet comment. Record comment/attachment IDs and stable access refs.
3. On mobile, use the same target member scope to open the three attachment cards and retrieve the same materials. Attachment cards alone are insufficient: an unavailable material fails this check.
4. Re-download each attachment by its durable identity and verify its raw bytes against the frozen SHA-256 digest. Do not treat rendered text, a signed URL, or an optional PDF as the canonical check.
5. Reply beneath the exact current packet comment with one short legal token only, such as `approved_for_spec`. Re-read the parent chain, author identity, packet marker, target-human mapping, and content digest before accepting the decision evidence.
6. Create a newer packet delivery, then verify that a reply bound to the superseded packet remains audit-only/no-op while a new exact-current short-token reply is the only effective decision.
7. Exercise one authorized retry/partial-failure path. Confirm reconciliation does not silently duplicate, relabel, delete, or mark incomplete delivery ready; metadata/comment conflicts, missing attachment, digest mismatch, missing stable ref, mapping uncertainty, or stale writer must close as `review_packet_unavailable` while preserving the real Review conclusion and existing objects.

## Outcome record

Record `sandbox_acceptance=passed` only when every check completes for the named sandbox scope. If any check cannot run, fails, or target-member mobile access is unavailable, record `sandbox_acceptance=not_run|failed`, keep production activation inactive, and capture failed checks plus observable closing conditions. Where platform capability—not configuration—prevents completion, recommend a separate platform capability proposal; that recommendation is not authorization to alter Multica or create resources.

## Implementation status

For this repository implementation, no real workspace import, Agent binding, sandbox Issue, network call, or platform write was authorized or performed:

```text
activation=not_run
sandbox_acceptance=not_run
workspace=n/a
agent=n/a
```
