# Implementation evidence

## Scope and baseline

- Applied directly on branch `main` at base HEAD `381ca5ca7364108021809eb56dad3ef48e8cd237`, per explicit user instruction.
- Preserved the pre-existing dirty worktree and the completed prerequisite change `allow-owner-attested-formal-architecture-approval`; its focused tests and strict validation pass.
- GitNexus pre-edit impact was LOW for the concrete contract/installer symbols (`validate_fixture`: 3 direct test callers; `install_runtime_skill_links`: 1 main process caller plus test coverage). No HIGH/CRITICAL result occurred. Post-implementation `detect-changes --scope all` reported 44 files, 166 symbols, 0 affected processes, risk `low`.
- Current working-tree package aggregates (sorted path + file SHA-256 stream):
  - core `architecture-design-workflow`: `a0fb81124d07b142ce9260359f1e2a25a4b25c63e45ee7cb91999e23b849539a`
  - adapter `multica-architecture-approval-adapter`: `366b2c1feb19f8b7e8cf302d267f7b303f1817ccfe88cc476e7878e3166fb099`

## Delivered contract

- `ARCH-DESIGN-vN.md` is the only mandatory human artifact and carries `design_maturity=directional|spec_ready|implementation_ready`.
- `human_review_surface_v1` contains one Design entry, concise Review/findings, risks, recommendation/consequences and one current Action.
- `architecture_internal_evidence_v1` retains Research、Control、complete Review、machine-only Packet、digests、visual receipts、continuation/handoff/readback、retry、reconciliation and status evidence.
- `architecture_design_impact_v1` treats unknown as architecture impact, creates a new Design/Review and supersedes current Action/manifest; no-impact updates internal evidence only.
- New Multica writers use `multica_human_action_material_bundle_v2`, exactly one canonical Design attachment, internal handoff task evidence and v2 Action binding. Legacy three-attachment/handoff/comment readers remain frozen and audit-only.
- Required Archify visuals fail closed unless deliver/browser/visual/semantic gates pass. The static preview is the current successful receipt's light/1440x900 PNG; HTML/PDF/PNG are `derived_non_authoritative`.
- Repository deployment profile records `allen@qq.com` / `unidocs-rag`, the four target Agent instructions, non-target Agents, conflict-fail import and additive binding. No live Multica workspace write was executed.

## TDD and contract verification

- RED: `python3 -m unittest tests.test_simplified_architecture_deliverables_contract tests.test_architecture_execution_continuation_contract` initially ran 11 tests with 6 expected failures covering the missing new contracts.
- GREEN: the same focused command passes 11/11.
- Full Python: `python3 -m unittest discover -s tests -p 'test_*.py'` passes 57/57.
- Core safety: `bash tests/architecture-design-workflow-safety.sh` passes static validation and 27 fixtures.
- Target-aware safety: `bash tests/target-aware-verification-safety.sh` passes 48/48.
- Worktree lifecycle safety: `bash tests/worktree-lifecycle-safety.sh` passes 193/193.
- Skill quick validation:
  - `uv run --with pyyaml python .../quick_validate.py architecture-design-workflow` → `Skill is valid!`
  - `uv run --with pyyaml python .../quick_validate.py multica-architecture-approval-adapter` → `Skill is valid!`
- OpenSpec target strict validation passes.
- Full OpenSpec strict validation passes 25/25.
- `git diff --check` passes.
- Placeholder and legacy-writer scans found no unresolved marker or current writer that requires three human attachments, packet-digest copying or a dedicated Agent handoff comment; remaining terms are explicitly frozen legacy readers or negative prohibitions.

## Archify showcase

- Pinned source: version `2.17`, repository revision `bb71ccdd64cd3a74ba7cbd25bbacc7382da34410`, archive SHA-256 `ed178d2ddd8861db1b8e867f32be7764bdec221d44568c37b6ae157c5e7f111c`.
- Input: `archify/examples/web-app.architecture.json`.
- `validate --quality showcase --json`: 9/9 artifact checks, composition pass, 0 errors, 0 warnings.
- `deliver`: specification SHA-256 `483350f5297df682aba4e4a0fa491307ce3d3abd725ae4df07fab177490752cf`; HTML SHA-256 `3b6576e29920ce22343b48ab6ee8cb3c98aa1febc583b569e4af30543e37be96`.
- `visual-check`: automated-browser status pass at light 1440x900, 1600x1000, 1920x1080 and 2048x1320 with no overflow; receipt SHA-256 `ed88f5b80e0d4e2dcdf7026a22cf048545aa576fdabb037bd0f6ed4c1b209676`.
- Current light/1440x900 preview SHA-256: `9d346315c25ea6609c69d83ae83aacf672f2b0d28036214ca1cc2f391b371106`.
- Independent image review: title, primary request path, security/region boundaries, ten components, labeled cache/auth/static/queue flows and the three conclusion cards are legible and semantically consistent with the source; showcase `visual_review=passed`. This claim is separate from browser evidence.
- Stale-artifact guard: an invalid candidate (`components=[]`) made `deliver` exit 1 at schema validation; the existing HTML remained byte-identical at SHA-256 `3b6576e29920ce22343b48ab6ee8cb3c98aa1febc583b569e4af30543e37be96`. No `visual-check` was run for that failed candidate.
- Fixtures separately assert browser/visual `failed|skipped`, semantic-open and stale preview fail closed, and that an R&D architecture-impacting change returns to Architecture Team.

## Runtime and activation boundary

- Isolated installer coverage uses temporary Claude/Codex directories and passes; both runtime link paths resolve to the same source bytes without touching a test user's real home.
- Live Multica import/binding/sandbox/mobile-client acceptance: `not_run` because this repository implementation instruction did not authorize real workspace activation. The reusable profile and runbook provide the next explicit step.
- During implementation, an attempted `setup-skills-env.py --help` exposed that the script ignores unknown options and ran its normal real-home path. It reported 0 links created/replaced (all existing links skipped) and re-merged Claude settings as 24 standard permissions with 27 custom entries preserved. No rollback was attempted because the prior settings bytes were unavailable. Runtime docs now explicitly warn that this script has no help/dry-run mode and direct automation must use isolated injected paths.

## Historical objects

- No historical Multica comments, attachments, packets, Actions, decisions, tasks or workspace bindings were edited or deleted.
- Old attempts remain on their frozen reader contract. Upgrade requires a compatible core/adapter activation followed by an explicit superseding new attempt.
