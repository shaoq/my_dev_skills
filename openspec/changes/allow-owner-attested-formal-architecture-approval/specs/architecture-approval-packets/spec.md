## MODIFIED Requirements

### Requirement: Readiness evidence is complete and packet-specific
The skill SHALL accept `review_packet_ready` only when design, review and packet refs/versions match the current packet, expected and verified raw-byte SHA-256 digests match, review guidance is complete, Reviewer conclusion is approvable, and the external evidence envelope identifies current packet ref/version/digest, the unique target human actor, verifier and verification time. Readiness MUST NOT itself count as approval.

The default `automatic` access mode SHALL require actual human-readable rendering for every requested client scope. The portable `owner_manual` mode MAY instead make the content-decision activation gate ready when the unique Decision Owner has explicitly selected manual inspection, all exact artifact identities/digests and stable human-navigable entries have been machine-verified, and every requested scope is recorded as `manual_check_required`. It MUST NOT claim `opened`; a legal content decision MUST include the Owner's explicit declaration that the complete materials were opened, while a material-unavailable response MUST trigger repair and MUST NOT count as a decision.

#### Scenario: Explicit Owner-manual packet is ready for inspection
- **WHEN** automatic rendering is unavailable, the unique Owner's current policy authorizes manual inspection, exact packet/design/review identity and raw-byte digests match, stable human-navigable entries and the current named Action are verified, and all requested scopes are `manual_check_required`
- **THEN** the workflow emits current-packet `review_packet_ready`, enters the human gate without claiming that any scope was opened, and requires the Owner's explicit material-opened declaration together with one legal decision

#### Scenario: Owner reports that materials cannot be opened
- **WHEN** the current Owner uses the packet action's exact material-unavailable response
- **THEN** the workflow records no content decision, returns the action to preparation, and repairs or republishes the material entry before issuing a new attempt

#### Scenario: Owner-manual machine evidence is incomplete
- **WHEN** any artifact identity, digest, stable entry, unique Owner, current Action or durable readiness readback is absent or changed
- **THEN** the workflow emits `review_packet_unavailable` and MUST NOT enter the human gate
