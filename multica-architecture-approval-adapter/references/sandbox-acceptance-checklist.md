# Multica adapter sandbox acceptance checklist

## Preconditions

- A current `operation variant=sandbox` authorization names the existing sandbox workspace, Issue, Architecture Agent, exact test writes, retained objects, failure behavior and excluded production scope.
- The core and adapter IDs have been verified with the activation runbook's final `agent skills list` read-back.
- The Issue is dedicated to this acceptance; it is not a production Architecture Team Issue.
- Record adapter repository commit, consumed core revision, observed Multica/CLI version or commit, workspace/Agent/Issue identities, and verifier/time.

## Acceptance checks

1. Deliver one current compatible design-input action using `multica_human_action_material_bundle_v1`. Confirm the comment follows the nine-part `Architecture Decision Brief` order, attaches exact `ARCH-DESIGN-vN.md`, provides complete Research/Control entries, and exposes exactly one actionable decision for the uniquely bound target member. Other Owners must appear only as dependency summaries.
2. On desktop Web, use the target member account to click and open exact Design, Research and Control entries. Confirm exact artifact/comment/attachment identity and complete content, then record each result independently with verifier/time. A filename-only card, `multica://issues/...`, local path, plain-text URL or Agent download must fail this check.
3. On mobile, repeat the same Design/Research/Control checks independently. Web success cannot populate mobile evidence. If Markdown is not comfortably readable, verify that a separately authorized superseding bundle carries a source-digest-bound `ARCH-DESIGN-vN.pdf` while canonical Markdown remains attached and authoritative.
4. Re-download canonical Design Markdown by durable attachment identity and verify raw bytes against its frozen SHA-256 digest. For comment-backed Research/Control, verify the exact `multica_web_comment_permalink_v1`; for a failed permalink, require the authorized exact Markdown attachment fallback.
5. Deliver one current compatible packet to the existing sandbox Issue. Confirm its approval comment also follows the Decision Brief order, adds exact Review/Packet materials and accepted risks, and preserves all four Chinese option consequences, exact response and After response before marker/digest audit detail.
6. On desktop and mobile, open exact `ARCH-DESIGN`, `ARCH-REVIEW` and `ARCH-APPROVAL-PACKET` entries. Record `design.desktop|mobile`, `review.desktop|mobile` and `packet.desktop|mobile` independently with comment/attachment IDs, human-facing entries, exact-content result, verifier and time.
7. Reply beneath the exact current packet comment with one short legal token only. Re-read the parent chain, author identity, packet marker, target-human mapping, and content digest before accepting the decision evidence. Separately verify that token-plus-prose is non-binding and produces `fresh_token_required=yes`; a revision brief uses a different packet-bound `decision_context_ref`.
8. Create a newer packet delivery, then verify that a reply bound to the superseded packet remains audit-only/no-op while a new exact-current short-token reply is the only effective decision.
9. Exercise authorized retry/partial-failure paths for both the material and packet routes. Before each retry, require a new operational request listing every retained object and exact incremental write. Confirm reconciliation does not silently duplicate, relabel, delete, overwrite or mark incomplete delivery ready; unsupported human-facing URI, attachment/link opening failure, metadata/comment conflict, missing attachment, digest mismatch, mapping uncertainty or stale writer closes as the appropriate `human_action_material_unavailable|review_packet_unavailable` while preserving real action/Review state and every existing object.

## Outcome record

Record `sandbox_acceptance=passed` only when every named human checklist item completes for the authorized sandbox scope. Desktop-only results, generic confirmation, unsupported links, multi-Owner action forms, missing supersession/token-context/retry evidence or unavailable target-member mobile access remain `not_run|failed`; keep production activation inactive and capture each failed check plus observable closing condition. Where platform capability—not configuration—prevents completion, recommend a separate platform capability proposal; that recommendation is not authorization to alter Multica or create resources.

## Implementation status

For this repository implementation, no real workspace import, Agent binding, sandbox Issue, network call, or platform write was authorized or performed:

```text
activation=not_run
sandbox_acceptance=not_run
unidrag_12_retry=not_run
workspace=n/a
agent=n/a
```
