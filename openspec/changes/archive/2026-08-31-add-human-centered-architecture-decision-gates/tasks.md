## 1. RED behavior coverage

- [x] 1.1 Add core fixtures for Subject Project routing, multi-owner risk acceptance, current packet approval consequences, and revision without actionable context
- [x] 1.2 Extend the behavior runner to validate atomic action ownership, stable human-accessible evidence refs, exact responses, per-option consequences, and post-response state/writes
- [x] 1.3 Run the new core fixtures against the current skill and record the expected RED failures

## 2. Portable Human Action Request contract

- [x] 2.1 Add the platform-neutral Human Action Request reference and template with action types, authority, evidence, response, consequence and supersession fields
- [x] 2.2 Route every human-dependent core next action through the shared contract in `SKILL.md` without changing canonical enums
- [x] 2.3 Update intake, design, review, packet, publication and handoff references for routing, risk acceptance, approval outcome and revision-context semantics
- [x] 2.4 Update `ARCH-CONTROL`, `ARCH-REVIEW`, `ARCH-APPROVAL-PACKET` and `ARCH-RD-HANDOFF` templates to lead with actionable summaries and stable material refs

## 3. GREEN verification and specification sync

- [x] 3.1 Run the core behavior fixtures with the updated skill and retain GREEN evidence for every new human gate
- [x] 3.2 Sync the new/modified core capability requirements into main OpenSpec specs
- [x] 3.3 Run quick validation, core safety/runner tests, strict change/main-spec validation and diff checks
