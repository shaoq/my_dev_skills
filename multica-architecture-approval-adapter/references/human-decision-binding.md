# Human decision binding

## Preconditions and non-authorities

Current v2 writers always use `current_action_reference_v1`. Re-read `human_review_surface_v1`、the unique Action ID/version/digest、exactly one Design attachment、internal Review/machine-only manifest、material readiness、request comment/time、target-human binding and supersession. The Owner does not repeat packet digest; Action inheritance binds the verified snapshot. Packet profiles below are frozen legacy readers only and never consume a current v2 Action.

Every candidate must be in the same Issue, have `author_type=member`, and have `author_id` byte-for-byte equal to the selected current binding's canonical UUID. Do not infer authority from display names, email fragments, assignments, membership, past comments, Agent access, reactions, Issue status, recommendation, Review conclusion, urgency, quoted text, fixture text, or a legal-looking Action/token from an Agent/system/non-target author. Such comments are retained as non-binding audit text only.

The only legal packet tokens are:

```text
approved_design_only
approved_for_spec
revision_requested
rejected
```

`OK`, `继续`, emojis, prose containing a decision, quotations, Markdown code/quote/fence content, multiple Actions/tokens, or an edited existing comment are never a replacement decision. Mapping missing/changed/ambiguous or selected request/readiness not current is fail-closed: retain evidence, keep the current Review gate, and request a newly established unique binding/readiness as applicable.

Human-readable option consequences and revision instructions are rendering context only. If a canonical member writes a legal decision plus prose in one candidate comment, retain that text as non-authoritative audit/context and require a new independent reply. Never strip arbitrary prose and consume an embedded decision.

## Profile: `current_action_reference_v1`

This profile applies to all current portable `design_input|architecture_review|architecture_approval` replies. Every exact syntax begins with `ACTION <action-id>:`. Automatic mode uses `ACTION <action-id>: decision=<legal-token>`; owner-attested uses the form below.

A candidate is valid only when all of these reread facts match:

1. the Action ID parses exactly once and resolves to exactly one current, unsuperseded Human Action Request in the same Issue;
2. candidate author equals the request's unique Decision Owner, `revision=1`, `updated_at` is absent/equal to `created_at`, and server `created_at` is not earlier than the request;
3. Action version/digest are inherited from that exact current request and reread without drift; users do not repeat them;
4. after the Multica envelope normalization below, the entire normalized content exactly matches one allowed response for that action type and candidate/risk identity;
5. task attribution identifies this candidate comment as the human trigger; no other current Action with the same ID or competing valid actor exists.

For `owner_attested architecture_approval`, the normalized content must be exactly:

```text
ACTION <action-id>: materials_opened; decision=<approved_design_only|approved_for_spec|revision_requested|rejected>
```

The Action ID must be the current packet-bound Action. Missing `materials_opened`, a bare token, a second decision, added prose, or an access claim from an Agent is invalid. `ACTION <action-id>: 材料打不开` is a separate no-decision repair response: record `content_decision=none` and invoke `repair_or_republish_material_entry`.

The candidate can be a child of the Issue thread root or another currently visible comment. Record its actual `parent_id` and full parent chain, but set `parent_chain_authority=audit_only`; neither direct parent nor membership of the Decision Brief chain grants or removes authority for this profile. Never select an action by latest timestamp: the exact current Action ID is the primary binding.

### Multica envelope normalization

Preserve and hash the raw UTF-8 content first. Then the Adapter MAY remove at most one canonical Multica mention from either the start or the end, separated from the decision by Unicode whitespace, only when the mention target is the exact current Architecture Agent reread for this Issue:

```text
[@<current-agent-display-name>](mention://agent/<current-agent-uuid>)
```

After removing that one edge mention and trimming only leading/trailing Unicode whitespace, hash the normalized UTF-8 content and require exact action grammar. A wrong Agent/member mention、two or more mentions、a mention in the middle、extra prose/punctuation、quote/fence、multiple Action IDs or multiple decisions is invalid. Mention normalization never changes actor authority and cannot repair a missing/wrong/superseded Action ID.

For distinct valid independent candidates from the one canonical Owner and same current Action, order by server `(created_at, comment_id)` and make the latest effective; earlier valid candidates are superseded audit. More than one effective actor or duplicate current Action identity fails closed.

## Frozen legacy profile: `multica_packet_comment_reply_v1`

Re-read the full thread and construct `parent_chain_ids` from candidate comment to root using each actual `parent_id`. Detect a missing parent or cycle as invalid. A candidate binds through this profile only when its chain contains the exact reread-verified **current packet comment ID**; it may be nested beneath that packet comment, which itself may be nested under a trigger comment. A thread-root match is insufficient.

After Unicode-safe string trimming of only leading/trailing whitespace, the full candidate content must be exactly one legal token and nothing else. No marker, identity fields, quote prefix, code fence, punctuation, mention, or explanatory sentence is allowed. The packet ref/version/digest are inherited solely from the exact verified packet comment marker and attached readiness evidence—not from root comments, metadata, or textual claims in the reply.

For an exact authorized reply to a superseded packet comment, record the inherited old identity in decision evidence with `decision_evidence_status=noop`; it is auditable but has no current-gate effect.

For revision guidance, accept a separate member comment only as `decision_context_ref` when it is authored by the same canonical target member, descends from the exact current packet comment and has exactly these seven LF-separated, fixed-order lines with no extra blank line, field, prose, quote or code syntax:

```text
context_profile=multica_revision_context_v1
packet_ref=<canonical-percent-escaped-current-ref>
packet_version=vN
packet_digest=sha256:<64-lowercase-hex>
packet_comment_id=<canonical-percent-escaped-current-comment-id>
revision_brief_ref=<canonical-percent-escaped-stable-ref>
revision_brief_digest=sha256:<64-lowercase-hex>
```

Use the marker profile's canonical percent encoding. The adapter rereads the context comment and the stable brief ref, hashes both raw UTF-8 byte sequences and requires the brief digest to match. The context comment ref becomes `decision_context_ref`; record its own content digest, author, parent chain and reread status. This profile is never parsed as a decision, never permits an inline token, and never supplies authority when the separate token-only decision is absent.

## Frozen legacy profile: `multica_explicit_packet_reference_v1`

An authorized same-Issue member comment outside the current packet-comment descendant chain may bind only if its trimmed content is exactly these four LF-separated, fixed-order lines, with no extra blank line, fields, prose, quote, or code syntax:

```text
decision=<one legal token>
packet_ref=<canonical-percent-escaped-current-ref>
packet_version=vN
packet_digest=sha256:<64-lowercase-hex>
```

Decode `packet_ref` using the marker's canonical percent-decoding rules. Reject unknown, missing, duplicate, reordered, malformed, non-canonical, or mismatching identity fields; reject a second legal token anywhere in the content. All three decoded identity fields must exactly equal current readiness. This explicit profile must not accept incomplete ref/version/digest or an identity that only matches metadata. Record `explicit_packet_identity=exact_current` on success.

## Evidence, re-read, and replacement

For every accepted or audited candidate, record the fields in [the decision-evidence template](../templates/multica-decision-evidence.md): Issue/comment refs and IDs, full parent-chain IDs, parent authority, author ID/type, revision, raw and normalized UTF-8 SHA-256, normalized mention identity, created/updated/recorded UTC timestamps, current Action or packet identity, profile, mapping/readiness refs, reread statuses, and evidence status. Multica discovery remains read-only. For `design_input|architecture_review` and `owner_attested architecture_approval`, the current manifest may record `multica_issue_task_evidence_v1` in the platform-managed task result and next `ARCH-CONTROL` projection; reread of exact member comment、status、packet projection and control/task attribution makes it effective without inventing a shared scope. Automatic packet approval may retain its shared-workspace no-clobber decision sidecar. No additional authorization token is requested.

Immediately before core consumption, re-read the selected current Human Action Request/readiness, mapping evidence, and decision comment by ID. If revision、raw or normalized content digest、Action/packet identity changes or reread fails, set captured evidence to `invalid`, retain it for audit, and require a new independent comment. An edit never becomes a replacement.

For a valid token-only `revision_requested`, separately re-read `decision_context_ref`. A current matching brief records `revision_scope=provided`; no readable brief records `revision_scope=missing`; changed bytes/identity record `revision_scope=changed`. Missing or changed context never creates, replaces, invalidates or edits the legal token evidence; it only asks core for a new `design_input` action or refreshed context.

For replacement, an independent comment means a distinct comment ID from the same canonical actor whose content independently satisfies one profile; a candidate that merely quotes, forwards, or edits a prior decision is not independent. For distinct valid independent comments from the one canonical actor and exact current packet, order lexicographically by `(created_at, comment_id)` using server values. Mark the latest as `valid`/effective and every earlier one `superseded`; retain all records and their original decision values. If legacy/corrupt/mapping-drift evidence identifies more than one actor as effective for the current packet, do not choose by timestamp: keep `waiting_human`, report all refs, invalidate the effective set for consumption, and require a fresh uniquely bound mapping plus a new decision.

Decision evidence is external to frozen packet content. Neither it nor metadata can alter `ARCH-APPROVAL-PACKET`, Review conclusion, recommendation, or canonical core rules.
