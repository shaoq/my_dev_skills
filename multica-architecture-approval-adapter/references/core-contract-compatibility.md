# Core contract compatibility

## Producer boundary

Current routes consume the compatible pair `human_review_surface_v1` + `architecture_internal_evidence_v1` and record the exact activated core/adapter package aggregates, including `SKILL.md`、workflow mandate、Human Action、solution-design、impact and visual contracts. The legacy immutable packet route may continue to read packets produced by revision `1d4b860b48e15f678d78a71bf2c38557ab9c2951`, but legacy operational requests and three-attachment surfaces remain audit-only. The adapter MUST NOT invent a Git revision for uncommitted bytes, add platform-specific required core fields, or redefine the portable state machine.

Current writer 只接受并产生 `architecture_workflow_mandate_v2` / `execution_continuation_v2` / `architecture_blocker_action_v3` side effects。reader 对 mandate/continuation 执行 v1 dual-read，对 blocker 读取 `architecture_blocker_action_v1|architecture_blocker_action_v2|architecture_blocker_action_v3`；mandate/continuation writer 执行 v2-only write，blocker writer 执行 v3-only write。历史 v1/v2 blocker identity 保留审计，任何 blocker 新写入都由一个 superseding v3 attempt 承担。blocker v3 必须包含 `automatic_before_human`、一个普通 business question、`provide_input|request_discovery`、reply-context evidence derivation、conditional formal-source policy 和既有 discovery actor binding。

## Portable responsibility mapping

responsibility mapping 必须来自 current mandate 的显式 actor/authority/responsibility bindings 与既有 Multica directory：`coordination|research|solution_design|independent_review|dependency_input|human_decision|downstream_delivery` 分别映射到一个准确既有 Agent 或 Member。legacy `Architecture Lead|Architecture Analyst|Solution Architect|Architecture Reviewer` 只在显式兼容 profile 唯一匹配时迁移；未知、冲突或多值时 fail closed，不使用显示名、assignee、最近作者或状态猜测。

## Exact compatible Human Action and Design markers

The `architecture_decision_brief_v1` material route requires:

- one current portable Human Action Request with `action_type=design_input|architecture_review|architecture_approval`、`requires_human_review=true`、stable action ID/version/status、one Decision Owner/authority scope and exactly one atomic current-reader action;
- a unique target-human binding; an absent/ambiguous Owner stops the mandate and requires a new task instruction rather than a routing Review action;
- the fixed Decision Brief order: solution summary, Design maturity, concise Review/findings, critical risks, Architecture recommendation/rationale/confidence, alternatives/consequences, one authorized decision, post-response behavior, exactly one canonical Design entry, exact response and minimal current/superseded audit binding;
- one complete standalone canonical UTF-8 `ARCH-DESIGN-vN.md`, its strictly positive version and externally computed raw-byte SHA-256 digest;
- Design readiness that accurately distinguishes incomplete, draft-complete, decision-ready and review-ready states; an incomplete design cannot request a content decision;
- exact Research、Control、complete Review and packet identities as `architecture_internal_evidence_v1` machine readbacks, never mandatory human entries; and
- explicit non-authorization boundaries and an Owner/observable closing condition for every unavailable material or unresolved dependency.

The adapter validates the complete Design section contract rather than reconstructing it from comments. It preserves the portable action semantics and Design bytes. Multica attachment IDs, client checks and permalinks are external delivery evidence only.

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

When the adapter receives a portable Human Action Request in addition to the packet, it applies the `human_review_surface_v1` checks and verifies that the packet is `machine_only`. Missing or unknown fields make that action rendering incompatible; they do not invalidate an otherwise compatible frozen packet or permit the adapter to invent content.

## Compatibility decision

Before platform reads or writes, select exactly one route. For the material route, verify current mandate/action、actual core package aggregate、standalone Design and exact Research/Control bindings; a packet is not required and MUST NOT be synthesized. For the packet route, verify packet markers、producer profile/package aggregate、identity consistency and current/delivered state. Do not treat an apparently approvable review alone as a packet.

An incompatible material route emits:

```text
evidence_type=human_action_material_unavailable
action_id=<known action ID or none>
design_ref/design_version/design_digest=<known values or none>
failed_checks=core_human_action_compatible|standalone_design_complete|material_binding_complete
owner=<Decision Owner|Architecture Lead|Platform Owner>
closing_condition=<specific observable compatible input or access behavior>
```

An incompatible packet route deterministically emits `review_packet_unavailable` with:

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
closing_condition=provide and verify a current delivered compatible-core packet and frozen inputs
```

The unavailable evidence preserves the actual Review conclusion. It does not synthesize a packet, alter `ARCH-CONTROL`, replace the conclusion with `BLOCKED`, or create a Multica comment, attachment, metadata value, Skill, Agent, Team, Project, or Issue.
