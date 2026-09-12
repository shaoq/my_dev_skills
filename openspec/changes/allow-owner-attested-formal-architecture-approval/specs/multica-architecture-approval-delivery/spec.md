## MODIFIED Requirements

### Requirement: Readiness verifies the delivered platform bytes
After comment creation the adapter MUST re-read the packet comment, confirm all required attachment IDs are bound to it, download each attachment through its stable identity and compare raw-byte SHA-256 with the frozen design/review/packet digests. `review_packet_ready` SHALL be emitted only after comment brief, stable same-Issue entries, digests, target human and metadata projection all verify.

The adapter SHALL support `automatic` and `owner_attested` evidence modes. `automatic` records actual per-artifact/per-client UI opening evidence. `owner_attested` MAY be used when automatic rendering evidence is unavailable and SHALL record every requested scope as `manual_check_required`; it MUST bind a unique current `architecture_approval` Action and MUST NOT claim `opened`. Ready evidence SHALL be persisted and reread using either `shared_workspace_sidecar_v1` or `multica_issue_task_evidence_v1`. The latter MUST bind immutable request/task result, exact packet/comment/attachment identities and digests, target Member, `arch.packet.current`, `ARCH-CONTROL`, status timeline and supersession readbacks.

#### Scenario: Owner-attested packet is ready for review
- **WHEN** an approvable packet has one unique Owner, exact three-attachment identity/digest readback, stable same-Issue human entries and complete platform task/control evidence, but automatic client rendering and an external shared scope are unavailable
- **THEN** the adapter emits `review_packet_ready` with `evidence_profile=multica_issue_task_evidence_v1`, marks requested scopes `manual_check_required`, creates one current named approval Action and enters `in_review`

#### Scenario: Platform task evidence is incomplete
- **WHEN** owner-attested delivery lacks exact task result, `ARCH-CONTROL`, packet projection, Owner, Action or supersession readback
- **THEN** readiness is unavailable and the adapter MUST NOT create or expose an actionable approval request

### Requirement: Readiness verifies the rendered human entry point
Readiness SHALL verify that the approval comment contains the current Human Action Request summary, option consequences, accepted-risk summary or `none`, exact stable attachment access guidance and non-approval boundary. In `automatic` mode every requested scope MUST be actually opened. In `owner_attested` mode the Adapter MUST verify clickable stable same-Issue entries and mark scopes `manual_check_required`; the exact Action response MUST require `materials_opened` before any content decision can become effective.

#### Scenario: Owner cannot open a material
- **WHEN** the Owner replies `ACTION <current-action-id>: 材料打不开`
- **THEN** the adapter records no content decision, returns the Action to preparing and starts `repair_or_republish_material_entry`
