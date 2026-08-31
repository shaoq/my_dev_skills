## MODIFIED Requirements

### Requirement: Design output is independently reviewable
`ARCH-DESIGN vN` SHALL be understandable without an OpenSpec change, Issue history or other comment context and MUST exist as a canonical UTF-8 Markdown artifact suitable for immutable attachment delivery. It MUST contain identity and evidence inputs; executive summary; architecture recommendation, rationale and confidence; problem/current state and architecture drivers; goals and non-goals; system context, responsibility boundaries and a simplified architecture view; components, data/control flows, interfaces and consistency semantics; normal and critical failure flows; security, privacy, reliability, performance, capacity, cost, observability and evaluation design; alternatives, trade-offs and rejected reasons; migration, rollout, rollback, roll-forward and exit; operations/RACI; risks, assumptions, determined and undetermined matters; validation/acceptance plan; and R&D decomposition. Missing evidence MAY prevent `decision_ready` or a final product/platform choice, but the design MUST still distinguish the frozen architecture, current default or PoC recommendation, decisions that remain human-owned, and evidence that would change the recommendation.

#### Scenario: Solution Architect completes a candidate design
- **WHEN** sufficient research evidence exists to recommend a solution or a platform-neutral architecture while bounded decisions remain open
- **THEN** the Solution Architect publishes a versioned standalone `ARCH-DESIGN-vN.md` linked to its `ARCH-RESEARCH` inputs, records its raw-byte digest, labels its readiness and unresolved decisions accurately, and does not create OpenSpec artifacts

#### Scenario: A design is only a collection of prompts or comment fragments
- **WHEN** the candidate output lacks the complete architecture narrative, recommendation, architecture views, consequences, operational design or validation path and instead relies on questions or historical comments to reconstruct the solution
- **THEN** the workflow marks the design incomplete, does not request a content decision, and returns it to the Solution Architect with the missing sections
