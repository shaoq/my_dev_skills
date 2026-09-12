# Delivery mapping and immutable approval marker

## Scope and write boundary

Apply only after compatible `human_review_surface_v1` + `architecture_internal_evidence_v1`, target-human mapping, capability preflight, mandate and manifest pass for one existing Issue. A new writer publishes one approval comment with exactly one canonical `ARCH-DESIGN-vN.md` attachment. Review、Packet、Control、Research and execution records remain internal evidence.

Before delivery, hash the exact Design bytes and independently hash the internal Review and machine-only Packet. Preserve all bytes, encodings and media types. Render the comment from the portable human surface; never reconstruct Design content from Review or Packet.

```bash
multica issue comment add <issue> \
  --content-file <rendered-approval-comment.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  [--parent <actual-trigger-comment-id>] \
  --output json
```

There is exactly one comment-add write for a complete attempt. Supporting PDF/Archify HTML/static preview is `derived_non_authoritative` and exposed on the same Design surface, not as another canonical attachment or mandatory entry.

## Current marker

The final line is one marker:

```text
<!-- multica-architecture-approval-adapter:v2 action_id=<escaped-id> design_ref=<escaped-ref> design_version=vN design_digest=sha256:<64-lowercase-hex> -->
```

Fields use fixed order and canonical UTF-8 percent encoding. The parser rejects duplicate/unknown/reordered fields, malformed encoding, a mismatched Action/Design identity, stale version, changed digest or wrong adapter author. A v1 packet marker is a frozen legacy reader input and cannot satisfy a v2 writer/readiness fence.

## Readback and stable access

Re-read the exact comment by returned ID. Require the canonical Agent author, actual parent, one Owner mention, one current Action and exactly one Design attachment. Record stable Issue/comment/attachment identities, obtain raw bytes through fresh transient transport if necessary, and match the Design digest. A transient URL、HTTP 200、filename-only card or Agent download is not human access.

`automatic` opens the complete Design and required visual preview independently for every requested desktop/mobile scope. `owner_manual|owner_attested` verifies current identity/digest, stable same-Issue entry and certified route/policy evidence, then records `manual_check_required`; it never claims `opened`.

The delivery evidence ref binds the exact comment marker, author and Design attachment. Internal Review/packet/Control/Research refs bind through `architecture_internal_evidence_v1`. Any mismatch emits unavailable evidence and retains all objects.

## Visual projection

When `diagram_requirement=required`, project the artifact-local light/1440x900 PNG from the same successful current `visual-check` receipt to a stable platform ref outside Design bytes. Verify preview digest and requested-client readability. HTML MAY be offered, but it is never mandatory. Missing/failed/skipped/stale/mismatched visual evidence makes readiness unavailable and cannot be repaired by an older screenshot.

## Legacy

Old v1 packet comments and three required attachments stay read-only under their frozen revision. New writers never append, edit, delete or reinterpret them; migration creates a superseding attempt.
