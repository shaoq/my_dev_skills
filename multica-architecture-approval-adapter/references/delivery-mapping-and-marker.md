# Delivery mapping and immutable packet marker

## Scope and write boundary

Apply this reference only after core compatibility、target-human mapping、capability preflight、current workflow mandate 与 derived manifest 已对准确既有 Issue、packet、input paths、comment/attachment/projection/sidecar scope 全部通过。Adapter 不执行 independent upload：一条 packet comment 携带三份冻结 Markdown。mandate/manifest 缺失、歧义、过期或范围不足时 no write；范围扩大只报告需要新的任务指令，不生成 operational request。

Before constructing a comment, calculate SHA-256 over the raw bytes of the exact delivered `ARCH-DESIGN`, `ARCH-REVIEW`, and `ARCH-APPROVAL-PACKET`. Preserve bytes, encoding, filenames, media types, whitespace, and newlines. The brief is a new concise comment, not a copy or reserialization of the attachments.

Render [the approval-comment template](../templates/multica-approval-comment.md) with the actual core Human Action Request and packet values. Its first screen must identify the Decision Owner, why the decision is ready, Team recommendation/reason, accepted warnings and four legal outcomes with Chinese consequences; accurate reply instructions and three stable attachment refs follow. Full marker, digest and reconciliation audit detail stays below those sections. Do not put full design/review/packet bodies in the comment.

Create a fresh `delivery_attempt_id` before reconciliation. If a task was triggered by comment `T`, use `T` as `--parent`; do not substitute the root of its thread. Record the returned packet-comment ID, not a trigger or thread-root ID, as the packet binding identity.

```bash
multica issue comment add <issue> \
  --content-file <rendered-approval-comment.md> \
  --attachment <ARCH-DESIGN-vN.md> \
  --attachment <ARCH-REVIEW-vN.md> \
  --attachment <ARCH-APPROVAL-PACKET-vN.md> \
  [--parent <actual-trigger-comment-id>] \
  --output json
```

There is exactly one comment-add write for a new complete delivery. Do not use a separate upload endpoint or append later attachments. The command may be used only after reconciliation has determined that no reusable exact complete delivery exists.

## `multica-architecture-approval-adapter:v1` marker

The final line of the rendered comment is exactly one ASCII marker:

```text
<!-- multica-architecture-approval-adapter:v1 packet_ref=<escaped-ref> packet_version=vN packet_digest=sha256:<64-lowercase-hex> -->
```

It has this fixed field order, one literal ASCII space between fields, no newline inside the marker, and no other marker of this profile in the comment. `packet_version` is `v[1-9][0-9]*`; the digest is the complete lower-case SHA-256 value, never a shortened display digest.

`<escaped-ref>` uses canonical percent encoding of UTF-8 bytes: preserve only `A-Z`, `a-z`, `0-9`, `.`, `_`, `-`, and `~`; encode every other byte as `%` plus two **uppercase** hexadecimal digits. The parser rejects malformed `%` sequences, lower-case escape digits, non-canonical escaping of an unreserved byte, invalid UTF-8, duplicate markers, duplicate/unknown/reordered fields, and any decoded ref/version/digest that differs byte-for-byte from the current core identity. It never obtains identity from Issue metadata, attachment names, a shortened visible digest, or comment display text outside this marker.

Reconciliation first scans **all syntactically legal profile markers** in the Issue before applying author eligibility. This syntax pass deliberately ignores metadata and author identity so a copied or conflicting current marker cannot hide behind an eligibility filter. For a marker with the current packet ref and version, a different digest is terminal `identity_conflict`; the exact current ref/version/digest with `author_type!=agent` or an `author_id` different from the preflight-recorded adapter delivery actor is terminal `marker_author_conflict`. Both outcomes prohibit any projection write. Only after these conflict checks may an exact-marker comment with the exact adapter author become eligible delivery evidence.

A marker for the same packet ref at a lower version remains a superseded delivery record, and a higher version participates in stale-writer fencing; neither is silently treated as current. Only a marker unrelated to the current packet ref is audit-only. Author identity is recorded beside the comment ID and re-read; mutable metadata is never marker identity or approval authority.

## Response parsing and durable attachment refs

Parse the JSON response and then re-read the actual packet comment through the thread API. Require an immutable comment ID and exactly the three required attachment records bound to that same comment. If no actual packet comment exists (including core absence or preflight failure), record both packet-comment ID and packet-comment ref as literal `none`; never interpolate either into a `comments/none` URL. For each required artifact, require a durable attachment ID and build:

```text
issue_ref=multica://issues/<issue-id>
comment_ref=multica://issues/<issue-id>/comments/<comment-id>
artifact_ref=multica://issues/<issue-id>/comments/<comment-id>/attachments/<attachment-id>
```

Persist `attachment_id`, `artifact_ref`, and only a returned `markdown_url` or documented stable attachment endpoint as `stable_access_ref`. Never persist `download_url`, query-string bearer token, signed URL, or an inferred browser path. A re-read can ask the platform for a fresh transient download URL solely to stream raw bytes and verify SHA-256.

These `multica://issues/...` values are opaque internal audit identities only. They MUST NOT be copied into a human-facing Design/Research/Control entry or described as clickable. Resolve and verify a separate attachment card, documented stable endpoint, or `multica_web_comment_permalink_v1` using [human-accessible evidence links](human-accessible-evidence-links.md); otherwise report the affected client scope unavailable.

Present those exact three stable refs to the canonical target member in the Decision Brief, then verify each `design|review|packet` artifact and requested `desktop|mobile` scope automatically under the current manifest. Record `opened|unavailable|not_run` separately; do not collapse results into generic confirmation or treat Agent download as human access. No `access_confirmation` Human Action is generated.

For each record also retain media type, expected/verified digest, Issue/workspace availability scope, canonical target member UUID, packet-bound mapping evidence ref, verifier, and RFC3339 UTC verification time. Once the comment marker and all three attachment bindings can be re-read, deterministically construct the pre-projection delivery evidence ref:

```text
multica://issues/<issue-id>/comments/<packet-comment-id>#adapter-delivery-evidence-v1
```

This fragment denotes verifiable evidence already present on that exact comment (marker, author identity, and attachment bindings); it creates no Multica resource and is not readiness authority. It is the only non-`none` `delivery_evidence_ref` eligible for the current projection and must be copied byte-for-byte into the readiness envelope. Use it only after that exact comment, marker, author, and required bindings re-read successfully. For core absence, preflight failure, no packet comment, or any marker/author/binding reread failure, record the literal `delivery_evidence_ref=none`; never construct a `comments/none` URL. A missing stable ref, attachment ID, expected comment binding, raw-byte re-download, or target-member scope produces unavailable evidence; retain any created objects.

## Optional PDF

A deployment may attempt to derive a PDF before the one packet-comment write. If available, it may be included only as an optional fourth attachment in that same write and its record must be labeled `derived_non_authoritative=true`. Exclude it from the three required artifacts, marker identity, readiness preconditions, and digest authority. Missing or failed renderer is a reported limitation; it must neither block canonical Markdown delivery nor replace, normalize, or recompute any frozen Markdown digest. Never add a PDF through a later standalone write.
