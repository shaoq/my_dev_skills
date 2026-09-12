## MODIFIED Requirements

### Requirement: A named current Action can bind an owner-attested packet decision
For `owner_attested` formal approval, the adapter SHALL accept only `current_action_reference_v1` from the exact canonical target Member in the same Issue. The normalized body MUST contain exactly the current Action ID, `materials_opened`, and one legal decision. The adapter MUST inherit packet ref/version/digest from the current request and MUST re-read request, attachments, readiness, candidate revision/content digest, task result, `arch.packet.current`, `ARCH-CONTROL` and supersession state before consumption.

#### Scenario: Owner attests reading and approves for specification
- **WHEN** the unique Owner replies `ACTION <current-action-id>: materials_opened; decision=approved_for_spec` after the current owner-attested request and every platform evidence readback remains exact
- **THEN** the adapter records a valid `multica_issue_task_evidence_v1` decision and the core may enter `approved_for_spec`

#### Scenario: Decision omits material attestation
- **WHEN** a current Owner supplies a legal decision without `materials_opened`
- **THEN** it remains non-binding audit text and the Issue stays in the human review gate

#### Scenario: Material is unavailable
- **WHEN** the unique Owner replies `ACTION <current-action-id>: 材料打不开`
- **THEN** the adapter records `content_decision=none` and routes only to material repair

### Requirement: Decision evidence is versioned and re-verifiable
Every accepted decision MUST bind the exact human actor, Action and packet identities, Issue/comment refs, revision/content digest, recorded time, target-human mapping and all current evidence readbacks. `shared_workspace_sidecar_v1` MAY provide external evidence. `multica_issue_task_evidence_v1` SHALL be sufficient for an owner-attested formal packet only when the manifest-bound immutable request/task result, exact candidate, projection, `ARCH-CONTROL`, status and supersession rereads all pass. Neither metadata nor an Agent statement alone can satisfy this requirement.

#### Scenario: Current platform evidence remains exact
- **WHEN** the owner-attested decision and every manifest-bound platform object re-read match the captured identities and digests
- **THEN** the decision evidence is effective without requiring an external shared-workspace sidecar

#### Scenario: Any platform evidence drifts
- **WHEN** request, attachment, candidate revision, projection, Control or supersession readback differs
- **THEN** the decision is invalid or no-op and no canonical approval transition occurs
