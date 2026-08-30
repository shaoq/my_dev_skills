# Core contract compatibility

## Pinned producer

The only consumed core implementation is `architecture-design-workflow` revision `1d4b860b48e15f678d78a71bf2c38557ab9c2951`. The adapter is a portable-evidence consumer: it must not change that skill, add Multica-specific required core fields, or redefine its canonical state machine.

## Exact compatible packet markers and fields

The current packet must be an immutable `ARCH-APPROVAL-PACKET vN` with these exact portable markers/fields from the pinned core:

- `payload_status=delivered` and a strictly positive, current `vN` packet version;
- packet identity: packet ref, packet version, and externally computed `Packet digest` as `sha256:<64 lowercase hex characters>`;
- frozen design identity: `ARCH-DESIGN` ref, Version, Media type, Digest, Verification profile, Availability scope, `Target human actor`, Access confirmation ref / confirmed at, and Verifier / verified at;
- frozen review identity: `ARCH-REVIEW` ref, Version, Media type, Digest, `Reviewer conclusion`, Verification profile, Availability scope, `Target human actor`, Access confirmation ref / confirmed at, and Verifier / verified at;
- review conclusion exactly `APPROVABLE_WITH_WARNINGS` or `APPROVABLE`;
- exactly one `ARCHITECTURE_RECOMMENDATION` value: `recommend_approved_for_spec`, `recommend_approved_design_only`, `recommend_revision`, or `no_recommendation`, with Chinese rationale, applicable conditions, and key risks;
- human review brief containing the review subject, key decisions, risks/conditions, open confirmations, and only `approved_design_only|approved_for_spec|revision_requested|rejected` as legal decisions;
- `External verification boundary`: post-finalization readiness/unavailable evidence binds only packet ref/version/digest and is not written into the payload.

The adapter must obtain the exact current `ARCH-DESIGN`, `ARCH-REVIEW`, and `ARCH-APPROVAL-PACKET` bytes and verify their SHA-256 values over raw bytes. It must not change character encoding, Unicode, whitespace, newlines, media types, or any frozen content. A superseded packet remains immutable and cannot substitute for the current packet.

## Compatibility decision

Before platform reads or writes, verify all markers above, the pinned revision, identity consistency between packet and frozen inputs, and that the target packet is current/delivered. Do not treat an apparently approvable review alone as a packet.

On any absent, incompatible, unknown, malformed, stale, or unverifiable item, deterministically emit `review_packet_unavailable` with:

```text
evidence_type=review_packet_unavailable
packet_ref=<known ref or none>
packet_version=<known version or none>
packet_digest=<known digest or none>
design_ref/design_version/design_digest=<known values or none>
review_ref/review_version/review_digest=<known values or none>
review_conclusion=<actual supplied conclusion or none>
failed_checks=core_contract_compatible
owner=Architecture Lead
closing_condition=provide and verify the current delivered pinned-core packet and frozen inputs
```

The unavailable evidence preserves the actual Review conclusion. It does not synthesize a packet, alter `ARCH-CONTROL`, replace the conclusion with `BLOCKED`, or create a Multica comment, attachment, metadata value, Skill, Agent, Team, Project, or Issue.
