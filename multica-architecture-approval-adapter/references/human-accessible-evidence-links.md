# Human-accessible evidence links

## Identity boundary

A durable Multica object identity and a human-facing navigation entry are separate values. Internal audit refs may identify an object, but they MUST NOT be shown as `Stable human-accessible evidence refs` unless the current client renders and opens that exact scheme.

`multica://issues/...` is not a supported human-facing link merely because it is stable text. Unless an independently repeated current-client capability test proves otherwise, it MUST NOT appear in a human-facing template or be described as clickable or human-accessible.

## `multica_web_comment_permalink_v1`

For exact comment-backed materials, construct:

```text
<app_base_url>/<workspace_slug>/issues/<issue_identifier>#comment-<comment_id>
```

- `app_base_url` is the explicitly confirmed current human-facing deployment entry with trailing `/` removed; never infer `localhost`, daemon API base or Agent-only host.
- `workspace_slug` and human-visible `issue_identifier` are read back from Multica and encoded as URL path segments; do not substitute display names or Issue UUID.
- `comment_id` is the exact artifact comment ID read back from Multica and encoded as a URL fragment component.
- The rendered fragment shape is `comment-<comment-id>`; `<comment-id>` denotes the encoded value of `comment_id`, not a second identity.

Render the value as an actual Markdown anchor such as `[ARCH-RESEARCH v1](<verified-url>)`, not backticked or plain text.

## Stable attachment entries

For attachment-backed material, the preferred entry is a platform-rendered stable attachment card or anchor whose primary action opens a browser-rendered preview. It must resolve to the exact comment and attachment identity and render the complete artifact in the authenticated human-facing client. A `download_url`, signed query, bearer query token, expiring endpoint or other `download-only` route is not a stable human-access entry; a fresh transient URL may be used only to stream raw bytes for digest verification.

The stable identity may still be derived from `markdown_url` or the documented attachment endpoint, but the access evidence MUST bind the user-facing preview action, not the raw endpoint in isolation. The preview may reuse the platform attachment content proxy and Markdown renderer; it need not expose a new public raw-content route.

## Post-publication client verification

For each material and requested scope:

1. verify the attachment card or anchor exists and is clickable; an anchor has a non-empty expected `href`;
2. perform actual UI activation on that exact card or anchor in the requested human client;
3. verify the action opens a browser-rendered preview rather than a `download-only` flow, and verify exact comment/attachment and artifact type/version identity;
4. verify the complete content is rendered and readable, not only a filename, card, summary, raw bytes or partial preview;
5. separately, for canonical Markdown, re-download and match the raw-byte digest; and
6. record actual scope, verifier and RFC3339 UTC time.

Record each requested `web|mobile` scope independently as `opened|unavailable|not_run`. Existing protocol fields may name desktop Web as `desktop`; it is the `web` scope, not evidence for mobile. Web success MUST NOT imply mobile success. Agent HTTP, CLI, a raw-byte fetch, HTTP 200, matching digest, a Chrome download, or a saved local file MUST NOT imply either human client result. In particular, downloaded files may carry host provenance/quarantine metadata and may be inaccessible from another device even when the bytes are correct.

If any required artifact lacks a preview action or the actual activation downloads instead of rendering, the Adapter MUST NOT enter `in_review`. Keep the workflow in `in_progress` while an automatic recovery remains, or use `blocked` only when no Agent or human execution path exists; record the observable closing condition.

Use this ordered fallback:

1. stable attachment entry for attachment-backed complete material;
2. verified `multica_web_comment_permalink_v1` for exact complete comment-backed material;
3. stable attachment fallback included in a newly authorized material bundle;
4. `unavailable` with material, client scope, Owner and observable closing condition.

Local paths, code-fenced URLs, plain text without navigation, guessed browser paths and unsupported custom URI schemes are never fallbacks. If no route passes opening, exact identity and complete-content verification, keep the Decision Brief as an unavailable report but do not claim content-decision readiness.
