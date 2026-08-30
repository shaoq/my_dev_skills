## 1. RED adapter coverage

- [x] 1.1 Add adapter fixtures for buried approval choices, token-plus-prose revision, per-artifact mobile access, missing operational authorization and partial-failure retry
- [x] 1.2 Extend adapter contract validation for first-screen action fields, exact option consequences, decision-context separation and scoped authorization semantics
- [x] 1.3 Run the new adapter fixtures against the current skill and record the expected RED failures

## 2. Multica rendering and authorization

- [x] 2.1 Add Multica Human Action Request rendering and operational authorization templates without changing core enums or marker grammar
- [x] 2.2 Update approval delivery, target-human/access and readiness references to verify decision-first comments and per-artifact stable access
- [x] 2.3 Update decision binding and evidence templates to keep token authority separate from packet-bound revision context
- [x] 2.4 Update activation, conflict, sandbox and retry guidance to require reviewable operational authorization requests

## 3. GREEN verification and specification sync

- [x] 3.1 Run the adapter contract fixtures with the updated skill and retain GREEN evidence for approval, access, authorization and revision flows
- [x] 3.2 Sync the new/modified adapter capability requirements into main OpenSpec specs
- [x] 3.3 Run quick validation, adapter contract/unit tests, strict change/main-spec validation and diff checks without real Multica activation
