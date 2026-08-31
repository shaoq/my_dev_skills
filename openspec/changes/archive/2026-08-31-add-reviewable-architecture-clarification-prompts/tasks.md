## 1. Regression Contract

- [x] 1.1 Add a `critical_evidence_gaps` regression fixture and static contract assertions for a reviewable clarification request.
- [x] 1.2 Run the new checks against the current skill and record the expected RED failure.

## 2. Skill Behavior

- [x] 2.1 Add the reviewable clarification request contract to `architecture-design-workflow/SKILL.md` and the designing-stage guidance.
- [x] 2.2 Extend `templates/arch-control.md` with per-decision candidate, basis, risk, evidence/Owner and editable-response fields.
- [x] 2.3 Preserve the boundary between clarification acceptance, measured evidence, responsibility Owner decisions and exact-packet human approval.

## 3. Specification Sync

- [x] 3.1 Apply the approved delta requirements to the main `architecture-design-artifacts` and `architecture-design-governance` specifications.

## 4. Validation and Evidence

- [x] 4.1 Run the same read-only behavior scenario with the updated skill and record GREEN evidence.
- [x] 4.2 Run skill validation, repository tests and OpenSpec validation.
- [x] 4.3 Run GitNexus change analysis and record implementation evidence without committing or modifying unrelated worktree changes.
