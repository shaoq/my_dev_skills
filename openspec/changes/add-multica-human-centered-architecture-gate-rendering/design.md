## Context

The Multica adapter currently has strong fail-closed delivery and decision binding. It intentionally requires token-only decision comments, immutable attachments and separate sidecars, but the human-facing approval comment exposes only a compact technical summary and token list. Operational authorization requirements are distributed across references and have no consistent human request format.

This change depends on `add-human-centered-architecture-decision-gates`. The adapter renders the portable action contract but does not add Multica fields to core or change core state computation.

## Goals / Non-Goals

**Goals:**

- Render core action requests into concise Chinese Multica comments whose first screen tells the target member what is needed, why, recommended choice, consequences and exact response.
- Keep the full Design, Review and Packet available as stable attachments suitable for desktop and mobile.
- Preserve exact token-only authority while enabling separate revision context.
- Make packet delivery, mapping/shared-scope writes, activation, conflict strategy, sandbox and retry authorizations independently reviewable and non-confusable with design approval.
- Extend local contract fixtures without performing real Multica writes.

**Non-Goals:**

- No Multica core, CLI/API or schema changes.
- No live Skill import, Agent binding, packet delivery or shared-scope write.
- No change to four human decision tokens, marker grammar, digest contract, immutable packet bytes or core canonical stages.
- No automatic creation of missing platform resources.

## Decisions

### 1. Adapter renders rather than redefines Human Action Request

Core fields and action semantics remain authoritative. Adapter templates may add Multica stable refs, comment identity and exact reply placement, but cannot change Owner, alternatives, consequences or canonical outcomes.

### 2. Approval comment uses decision-first layering

The first section contains: decision needed now, current packet/review identity, Team recommendation and reason, principal risks, four choices with Chinese consequences, and instruction to open all three attachments. Full digests, marker and delivery audit data remain below the human summary or in sidecars.

### 3. Token and revision context use separate comments

`multica_packet_comment_reply_v1` continues to accept exactly one legal token. A revision brief is a separate member comment or durable ref bound to the exact packet comment; it is stored as `decision_context_ref` and never becomes decision authority. For `revision_requested`, absence of context does not invalidate the legal token, but the result reports `revision_scope=missing` so core can issue a new design-input request.

### 4. Operational authorization has a dedicated request type

The adapter adds a positive template for `operational_authorization`. It lists existing target identities, exact planned writes, authorized paths/scope, retained objects, failure behavior, excluded operations, risks and exact authorize/deny response. Architecture approval tokens are forbidden in this request because they would falsely conflate two authorities.

Dedicated action variants cover delivery, target-human user-confirmed mapping/shared sidecar scope, activation, overwrite/conflict strategy, sandbox run and retry. Existing safety rules remain the execution gate.

### 5. Access confirmation is per artifact and per target member

The approval comment exposes stable Design/Review/Packet attachment refs. Readiness still requires technical raw-byte verification and scope evidence, while the human confirmation explicitly reports opened/unavailable for each artifact and desktop/mobile scope. A generic `可以访问` without exact items cannot close the action.

### 6. Existing immutable/audit behavior remains unchanged

No comment or sidecar is edited to improve presentation. A new packet version gets a new rendered comment. Superseded authorization/action requests are audit-only; retry needs a new explicit operational authorization showing existing objects and incremental writes.

## Risks / Trade-offs

- [Approval comment becomes too long] → Limit first screen to summary/options; full artifacts remain attachments and audit detail stays below.
- [Users add prose to token and invalidate it] → Show a copyable token-only response and a separate revision-context path with explicit warning.
- [Operational authorization is mistaken for approval] → Use separate action type, verbs and non-authorization statement; never show approval tokens in authorization templates.
- [Stable attachment ref is not usable on mobile] → Sandbox acceptance remains mandatory and fails closed; platform limitation becomes a separate capability proposal.
- [Revision context can drift] → Bind context to packet/comment identity and reread it, but never allow it to drive the gate.

## Migration Plan

1. Add failing adapter fixtures for verbose/buried approval, revision prose in token, per-artifact access and ambiguous operational authorization.
2. Add Multica rendering/authorization templates and route them from adapter references.
3. Extend evidence templates only with non-authoritative context/access fields; retain marker and decision token grammar.
4. Run local adapter contract and core compatibility validation.
5. Record activation/sandbox as `not_run`; live deployment requires a separate explicit instruction.

## Open Questions

No blocking question. If the actual Multica mobile client cannot open stable attachment refs, this skill change must remain locally valid while production activation stays failed/not-run and a separate platform proposal is required.
