## 1. Regression Contract

- [x] 1.1 Add core contract tests that reject an incomplete or comment-dependent `ARCH-DESIGN` and require the standalone architecture sections, recommendation/confidence, determined/undetermined split and canonical Markdown digest.
- [x] 1.2 Add core Human Action Request tests for the fixed Decision Brief order, one current-reader authority scope, per-client access evidence and platform-neutral material refs.
- [x] 1.3 Add Multica adapter tests for `multica_human_action_material_bundle_v1`, mandatory Design Markdown attachment, conditional PDF, verified Research/Control entries and rejection of user-visible `multica://issues` refs.
- [x] 1.4 Add renderer tests for the approved brief fields, one actionable decision, dependency-only other Owners, post-publication exact-content verification and independent web/mobile results.
- [x] 1.5 Run focused tests before implementation and record the expected failures against the current Skill documents.

## 2. Complete Architecture Design Artifact

- [x] 2.1 Update the solution-design reference and `ARCH-DESIGN` template with the standalone senior-architect document structure and explicit recommendation/confidence/readiness fields.
- [x] 2.2 Require canonical UTF-8 Markdown bytes, version/digest binding and new-version supersession rather than reconstructing a design from Issue history.
- [x] 2.3 Keep drafts in the Issue/material bundle and preserve the existing rule that only approved versions enter `uni-architecture/docs`.

## 3. Portable Decision Brief

- [x] 3.1 Update the Human Action Request reference/template to use the approved nine-part Decision Brief order and link complete materials instead of copying them.
- [x] 3.2 Enforce one atomic action for the uniquely authorized current reader; render other Owner actions only as dependency summaries and route unbound Owners before content decisions.
- [x] 3.3 Require per-material, per-client accessibility evidence or an explicit unavailable Owner/closing condition while preserving existing state and approval boundaries.

## 4. Multica Attachment-First Renderer

- [x] 4.1 Define `multica_human_action_material_bundle_v1`, exact Design/Research/Control bindings, attachment filenames/digests and operational authorization scope.
- [x] 4.2 Render the compact Architecture Decision Brief and attach canonical `ARCH-DESIGN-vN.md`; add a source-digest-bound non-authoritative PDF only when a requested client cannot comfortably read Markdown.
- [x] 4.3 Define and verify `multica_web_comment_permalink_v1` for existing Research/Control comments, with Markdown attachment fallback and no unsupported custom URI exposure.
- [x] 4.4 Add post-publication attachment-card/link, exact identity, complete-content, raw-byte digest and separate web/mobile verification.
- [x] 4.5 Update sandbox acceptance for the full material bundle, mobile reading, one-Owner brief, unsupported-link failure and retained-object retry behavior.

## 5. Verification

- [x] 5.1 Run focused and related repository tests, Skill quick validation and OpenSpec strict validation.
- [x] 5.2 Run GitNexus change analysis and inspect the final diff for core/adapter separation and unchanged Multica core.
- [x] 5.3 Record `activation=not_run`, `sandbox_acceptance=not_run` and `UNIDRAG-12 retry=not_run`; request new exact operational authorizations only after local implementation is verified.

## 6. Authorization-response Parent Binding Regression

- [x] 6.1 Add valid and invalid comment-trigger fixtures covering symbolic authorization-response parent resolution, exact trigger attribution and no unplanned comments; record the expected RED failure against the current Skill.
- [x] 6.2 Define `multica_authorization_response_parent_v1` in operational authorization, preflight and material delivery guidance, including exact author/request/content/revision/Issue/workspace/task-attribution checks.
- [x] 6.3 Require unauthorized authorization-request and diagnostic output to use task results only, and preserve Issue `in_progress` unless an exact status write is separately authorized.
- [x] 6.4 Run focused/full tests, both Skill quick validators, OpenSpec strict validation and final diff/impact review; record `activation=not_run`, `sandbox_acceptance=not_run` and `UNIDRAG-12 retry=not_run`.

## 7. Platform-managed Authorization-request Binding Regression

- [x] 7.1 Add valid and invalid fixtures for a platform-managed task-result authorization request, `source_task_id`/trigger/Agent/content uniqueness and response-parent chaining; run the focused test and record the expected RED failure.
- [x] 7.2 Define `multica_task_result_authorization_request_v1` in the adapter entrypoint, operational authorization, preflight, material bundle and authorization template, including the expected retained-object selector and truthful platform-materialization wording.
- [x] 7.3 Require delivery to resolve the authorization response's direct parent through the preparation task result before resolving `multica_authorization_response_parent_v1`; reject missing, duplicate, edited or mismatched request comments without an Issue diagnostic write.
- [x] 7.4 Run focused/full tests, both Skill quick validators, OpenSpec strict validation and final diff/impact review; record the observed UNIDRAG-12 task-result comment as regression evidence and keep activation/sandbox/retry writes separately authorized.
