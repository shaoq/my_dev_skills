# `multica_target_human_v1` target-human mapping

## Required input and equality rule

Read the frozen packet's design and review `Target human actor` values before every delivery or decision read. Both values must be non-empty and byte-for-byte identical. That single portable actor must resolve to exactly one canonical Multica member UUID for the supplied Issue/workspace scope.

The adapter must never infer a target from display names, email fragments, Issue assignee, comment author, prior author, workspace membership, Agent identity, reactions, or any fuzzy lookup. Zero matches and multiple matches are equally unavailable.

When mapping can be derived uniquely from current portable actor and existing Issue/workspace facts, include the candidate member UUID and the selected durable evidence profile in the current derived manifest. A shared sidecar profile freezes final/temporary paths and no-clobber behavior; an `owner_attested` packet profile freezes the exact `multica_issue_task_evidence_v1` task/request/Control readbacks. If a human choice is required because zero/multiple candidates remain, stop the mandate and request a new task instruction; do not render operational authorization. Mapping evidence、access evidence and architecture approval remain distinct.

## Allowed resolution forms

Only one of the following is acceptable:

1. The portable actor exactly matches `multica_member:<uuid>`. Extract the UUID and verify that exact member is recognizable in the supplied Issue/workspace scope. Create an external, re-verifiable direct-canonical binding record; it must not be written back into the frozen packet. The record and its durable `evidence_ref` must contain:

   ```text
   mapping_profile=multica_target_human_v1
   evidence_profile=shared_workspace_sidecar_v1|multica_issue_task_evidence_v1
   mapping_source=packet_canonical_member
   portable_actor=<exact canonical multica_member:<uuid> value>
   design_target_human_actor=<exact frozen design field>
   review_target_human_actor=<exact frozen review field>
   member_uuid=<extracted canonical Multica UUID>
   workspace_scope=multica_workspace:<workspace-id>
   issue_scope=issue:<issue-id-or-ref>
   evidence_ref=<workspace-sidecar-ref-or-current-multica-task-evidence-ref>
   packet_ref=<current packet ref>
   packet_version=<current packet version>
   packet_digest=<current packet digest>
   verifier=<adapter actor/runtime>
   verified_at=<RFC3339 UTC Z>
   ```

   Re-reading the record, frozen design/review actor fields, packet identity, and Issue/workspace member scope must reproduce the same member UUID. The record is external verification evidence only; it neither changes frozen packet bytes nor asserts human approval.
2. A packet-bound, user-role-confirmed mapping evidence record uniquely maps the portable actor to a member UUID. The evidence must contain all of:

   ```text
   mapping_profile=multica_target_human_v1
   evidence_profile=shared_workspace_sidecar_v1
   portable_actor=<exact design/review actor>
   member_uuid=<canonical Multica UUID>
   workspace_scope=multica_workspace:<workspace-id>
   issue_scope=issue:<issue-id-or-ref>
   confirmer=<explicit human user-role identity>
   evidence_ref=workspace://<confirmed-scope>/<relative-mapping-path>
   packet_ref=<current packet ref>
   packet_version=<current packet version>
   packet_digest=<current packet digest>
   recorded_at=<RFC3339 UTC Z>
   ```

The mapping must be re-verifiable, bind the exact current packet identity, and match the explicit workspace and Issue. It must be persisted and reread under one profile in [durable evidence records](durable-evidence-records.md): external no-clobber `shared_workspace_sidecar_v1`, or manifest-bound `multica_issue_task_evidence_v1` for an owner-attested formal packet. It may not be created from a platform guess, Agent observation, local path, or comment/metadata ref alone.

## Result and failure

On success, readiness uses only the canonical member UUID as `human_actor`. `human_actor_binding_ref` is the selected durable profile's rereadable evidence ref. Verify Issue/workspace and durable attachment access separately for each requested `desktop|mobile` scope under the current manifest; Agent access does not prove human access. `owner_attested` records `manual_check_required` until the exact Owner response includes `materials_opened`. New workflows do not generate a separate `access_confirmation` Human Action.

The following exact fifteen-line desktop/mobile payload is retained only for historical access-evidence parsing. New workflows record automated per-client evidence in task/readiness records and do not ask the user to submit it:

```text
access_profile=multica_artifact_access_confirmation_v1
packet_ref=<canonical-percent-escaped-current-ref>
packet_version=vN
packet_digest=sha256:<64-lowercase-hex>
human_actor=<canonical-percent-escaped-member-uuid>
availability_scope=<canonical-percent-escaped-workspace-and-issue-scope>
design_ref=<canonical-percent-escaped-stable-ref>
design_desktop=opened|unavailable
design_mobile=opened|unavailable
review_ref=<canonical-percent-escaped-stable-ref>
review_desktop=opened|unavailable
review_mobile=opened|unavailable
packet_access_ref=<canonical-percent-escaped-stable-ref>
packet_desktop=opened|unavailable
packet_mobile=opened|unavailable
```

Use the delivery marker's canonical percent encoding. All refs and packet/member/scope fields must exactly match current readiness inputs, and the adapter rereads this unedited comment before recording confirmation. Missing response remains `unconfirmed`; any explicit `unavailable` fails that item. A generic acknowledgement, reordered/unknown field, attachment card, Agent download, or one client result cannot close another artifact/scope. Automatic mode requires all `opened` values and the selected evidence reread. Owner-attested mode instead requires stable entries, `manual_check_required`, a current named Action and complete platform task evidence; no access scope is silently promoted to `opened`.

On empty/different actors, malformed canonical form, absent/stale/mismatched evidence, non-human confirmer, scope mismatch, zero/multiple member matches, or unavailable target-member access, emit deterministic unavailable evidence:

```text
evidence_type=review_packet_unavailable
review_conclusion=<actual supplied conclusion>
failed_checks=multica_target_human_v1
owner=Architecture Lead
closing_condition=provide one re-verifiable packet-bound user-confirmed mapping or canonical member actor with confirmed Issue/workspace access
```

Do not publish a delivery, mark readiness, or consume a decision after this failure. Other members' comments remain non-binding audit text. A later decision profile may only accept `author_type=member` and `author_id` exactly equal to this canonical UUID; no other actor can become authorized by a legal-looking token.
