## 1. RED contract

- [x] 1.1 Add an owner-attested formal packet fixture based on the UNIDRAG-12 failure shape
- [x] 1.2 Add validator and surface assertions for formal `owner_attested`, `materials_opened` and platform task evidence
- [x] 1.3 Run the focused adapter contract and confirm it fails for the missing behavior
- [x] 1.4 Add a core/adapter mapping contract and confirm the stale automatic-only packet gate fails it

## 2. GREEN contract implementation

- [x] 2.1 Extend the fixture schema/validator with strict profile-specific evidence references and manual access state
- [x] 2.2 Update adapter entry, manifest, human-access, material, readiness, durable evidence and target-human contracts
- [x] 2.3 Update human action/readiness/decision templates with owner-attested exact response and non-approval boundaries
- [x] 2.4 Preserve automatic/shared-sidecar behavior and invalid/superseded failure cases
- [x] 2.5 Align portable `owner_manual` packet readiness and map Multica `owner_attested` to it without leaking platform fields into core

## 3. Verification and activation

- [x] 3.1 Run focused adapter contract tests and Skill quick validation
- [x] 3.2 Run the repository test suite and OpenSpec strict validation
- [x] 3.3 Run GitNexus detect-changes and review regression risk
- [x] 3.4 Confirm the runtime Skill symlink resolves to this repository and all changed bytes are active
- [x] 3.5 Start a new UNIDRAG-12 attempt against the current subject HEAD and verify it reaches one current human Action or reports a new exact blocker
