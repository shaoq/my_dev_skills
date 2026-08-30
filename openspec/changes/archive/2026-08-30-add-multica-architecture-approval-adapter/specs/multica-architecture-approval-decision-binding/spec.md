## ADDED Requirements

### Requirement: A packet-comment reply can bind the current packet
The adapter SHALL support `multica_packet_comment_reply_v1`, in which the exact canonical target Multica member from current readiness replies beneath the exact verified current packet comment with exactly one legal human decision token after trimming surrounding whitespace. The adapter MUST derive packet ref/version/digest from the verified parent-chain delivery and MUST NOT require a mobile user to retype the full digest in that reply.

#### Scenario: Member replies with one legal decision
- **WHEN** an authorized target member replies beneath the current ready packet comment with `approved_for_spec`, `approved_design_only`, `revision_requested` or `rejected`
- **THEN** the adapter emits human decision evidence containing that member, comment identity, binding profile and inherited exact packet ref/version/digest

#### Scenario: Packet comment is nested below a trigger
- **WHEN** the packet comment is not the thread root and a decision reply is its descendant
- **THEN** the adapter reconstructs the parent chain and binds to the packet comment ID rather than incorrectly binding to the outer trigger thread

### Requirement: Explicit references can bind outside the packet reply chain
The adapter SHALL support `multica_explicit_packet_reference_v1` for a comment authored by the exact canonical target Multica member in the same Issue only when its content contains exactly one legal decision plus the exact current packet ref, version and full digest with no unknown or duplicate identity field.

#### Scenario: Member records an explicit current-packet decision
- **WHEN** a same-Issue member comment outside the packet subtree contains one legal decision and the complete current packet identity
- **THEN** the adapter may produce valid decision evidence using the explicit-reference profile

#### Scenario: Explicit identity is incomplete
- **WHEN** a comment contains a legal decision but omits or mismatches the current packet ref, version or digest and is not a descendant of the packet comment
- **THEN** it is retained as non-binding audit text and the human gate remains unchanged

### Requirement: Only recognizable target humans can decide
The adapter MUST require `author_type=member`, an `author_id` exactly equal to the canonical member UUID in current readiness, and re-verifiable packet-bound target-human mapping evidence. It MUST NOT infer authority from display names, email fragments, Issue assignment, prior authorship or workspace membership alone. Agent/system comments, non-target members, fixtures, quoted text, reactions, Issue status, recommendation, Review conclusion, readiness, assignments, urgency and ambiguous acknowledgements MUST NOT create human decision evidence.

#### Scenario: Agent repeats a legal token
- **WHEN** an Agent comment under the packet says `approved_for_spec`
- **THEN** the adapter rejects it as non-human and leaves the gate unchanged

#### Scenario: Human replies OK
- **WHEN** a target member replies `OK`, `继续`, an emoji or other ambiguous acknowledgement
- **THEN** no legal decision is inferred even though the reply is under the current packet

#### Scenario: A different workspace member uses a legal token
- **WHEN** a recognizable member whose ID is not the readiness target member replies `approved_for_spec`
- **THEN** the comment remains non-binding audit text and cannot change the human gate

#### Scenario: Target-human mapping no longer verifies
- **WHEN** the mapping evidence is missing, mismatches the current packet or resolves to zero or multiple members
- **THEN** decision consumption fails closed and requests a fresh unique packet-bound mapping

#### Scenario: Comment quotes another person's approval
- **WHEN** a member comment contains a legal token only inside a quotation or fixture block
- **THEN** the adapter treats it as quoted evidence rather than that member's explicit decision

### Requirement: Decision evidence is versioned and re-verifiable
Every accepted Multica decision evidence record MUST include decision, human actor, packet ref/version/digest, binding profile, Issue/comment refs, comment revision when available, content digest, created/updated time and adapter recorded time. The adapter MUST re-read current packet readiness and the decision comment before consumption. The platform-read-only decision route MUST NOT write Multica; for a candidate to be effective, the current task must additionally explicitly authorize a write-once+reread `shared_workspace_sidecar_v1` decision record in an existing user-confirmed durable shared scope. Its immutable no-clobber final path uses packet identity plus decision comment ID plus revision or content digest. Without that authority/scope/reread, retain only non-effective audit text.

#### Scenario: Decision evidence still matches
- **WHEN** packet delivery and decision comment re-read match their recorded identities and digests
- **THEN** core may consume the evidence for its canonical human gate transition

#### Scenario: Decision comment changed after capture
- **WHEN** the current comment revision/content digest differs from the recorded evidence
- **THEN** the adapter invalidates current consumption and requests an explicit fresh decision without pretending the prior content is immutable

### Requirement: Superseded and conflicting decisions do not silently change the current gate
The adapter MUST retain a valid decision for a superseded packet as auditable no-op. For one canonical target actor, distinct valid decision comments MUST be totally ordered by server `(created_at, comment_id)` and each later comment MUST automatically supersede that actor's prior decision while preserving all records. Editing an existing comment MUST invalidate captured evidence rather than count as a replacement. If legacy or corrupted evidence identifies more than one effective actor, it MUST remain `waiting_human` and request a fresh unique target-human mapping instead of selecting across actors by time.

#### Scenario: Late approval targets an old packet
- **WHEN** a member replies to a superseded packet comment with a legal approval token
- **THEN** the evidence is recorded with `decision_evidence_status=noop` and the current packet gate does not change

#### Scenario: Target actor records conflicting decisions in separate comments
- **WHEN** the canonical target member records two different valid current-packet decisions in distinct comments
- **THEN** the later comment by server `(created_at, comment_id)` is effective, the earlier evidence is retained as superseded and no ambiguous gate value is inferred

#### Scenario: Target actor records a later replacement
- **WHEN** the canonical target member records a later valid decision in a new comment
- **THEN** the adapter preserves both records and automatically marks the later evidence effective according to server `(created_at, comment_id)` ordering

#### Scenario: Existing decision comment is edited
- **WHEN** a previously captured decision comment changes revision or content digest
- **THEN** the adapter invalidates that evidence and requires a new independent decision comment instead of treating the edit as a replacement

#### Scenario: Multiple actors appear effective in legacy evidence
- **WHEN** legacy, mapping-drift or corrupted records identify decisions from more than one actor as current and effective
- **THEN** the adapter keeps `waiting_human`, reports all conflicting refs and requires one fresh unique target-human mapping
