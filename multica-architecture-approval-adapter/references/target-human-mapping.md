# `multica_target_human_v1` target-human mapping

## Required input and equality rule

Read the frozen packet's design and review `Target human actor` values before every delivery or decision read. Both values must be non-empty and byte-for-byte identical. That single portable actor must resolve to exactly one canonical Multica member UUID for the supplied Issue/workspace scope.

The adapter must never infer a target from display names, email fragments, Issue assignee, comment author, prior author, workspace membership, Agent identity, reactions, or any fuzzy lookup. Zero matches and multiple matches are equally unavailable.

## Allowed resolution forms

Only one of the following is acceptable:

1. The portable actor exactly matches `multica_member:<uuid>`. Extract the UUID and verify that exact member is recognizable in the supplied Issue/workspace scope. Create an external, re-verifiable direct-canonical binding record; it must not be written back into the frozen packet. The record and its durable `evidence_ref` must contain:

   ```text
   mapping_profile=multica_target_human_v1
   evidence_profile=shared_workspace_sidecar_v1
   mapping_source=packet_canonical_member
   portable_actor=<exact canonical multica_member:<uuid> value>
   design_target_human_actor=<exact frozen design field>
   review_target_human_actor=<exact frozen review field>
   member_uuid=<extracted canonical Multica UUID>
   workspace_scope=multica_workspace:<workspace-id>
   issue_scope=issue:<issue-id-or-ref>
   evidence_ref=workspace://<confirmed-scope>/<relative-mapping-path>
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

The mapping must be re-verifiable, must bind the exact current packet identity, and must match the explicit workspace and Issue. It must be atomically persisted and reread under [shared workspace sidecar v1](durable-evidence-records.md); it may not be created from a platform guess, Agent observation, local path, or comment/metadata ref.

## Result and failure

On success, readiness uses only the canonical member UUID as `human_actor`. For the direct canonical branch, `human_actor_binding_ref` is the direct-canonical sidecar `evidence_ref`; for the user-confirmed branch, it is the re-verifiable packet-bound user-confirmed sidecar `evidence_ref`. Confirm that this target member can access the Issue/workspace and durable attachment refs; the Agent's own access does not prove human access. Without an explicitly authorized durable shared scope and reread sidecar, mapping is unavailable.

On empty/different actors, malformed canonical form, absent/stale/mismatched evidence, non-human confirmer, scope mismatch, zero/multiple member matches, or unavailable target-member access, emit deterministic unavailable evidence:

```text
evidence_type=review_packet_unavailable
review_conclusion=<actual supplied conclusion>
failed_checks=multica_target_human_v1
owner=Architecture Lead
closing_condition=provide one re-verifiable packet-bound user-confirmed mapping or canonical member actor with confirmed Issue/workspace access
```

Do not publish a delivery, mark readiness, or consume a decision after this failure. Other members' comments remain non-binding audit text. A later decision profile may only accept `author_type=member` and `author_id` exactly equal to this canonical UUID; no other actor can become authorized by a legal-looking token.
