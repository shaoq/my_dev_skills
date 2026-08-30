# Human-Centered Architecture Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every human-dependent architecture workflow action quick to locate, detailed enough to understand, and precise enough to decide without weakening existing approval or authorization gates.

**Architecture:** Core defines a platform-neutral Human Action Request and applies it to routing, design inputs, risk acceptance, formal approval, access, publication and handoff. The sibling Multica adapter renders that contract as decision-first comments and stable attachments, while separately presenting operational authorizations and retaining token-only decision authority.

**Tech Stack:** Markdown Codex skills, OpenSpec spec-driven artifacts, shell/Python contract tests, Codex behavior fixtures, Multica adapter fixtures.

**Spec:** `openspec/changes/add-human-centered-architecture-decision-gates/design.md` and `openspec/changes/add-multica-human-centered-architecture-gate-rendering/design.md`

## Global Constraints

- Keep `architecture-design-workflow` usable without Multica.
- Do not change canonical stages, Review conclusions, blockers or four packet decision tokens.
- Do not modify Multica core, CLI/API, Runtime configuration, `uni-architecture` or business repositories.
- Do not import/bind skills or perform live Multica writes during implementation.
- Do not create commits without separate user authorization.
- Complete RED→GREEN→verification for core before modifying adapter behavior.

---

### Task 1: Core behavior contract RED

**Files:**
- Modify: `tests/fixtures/architecture-design-workflow/`
- Modify: `tests/test_architecture_design_workflow_runner.py`
- Modify: `tests/architecture-design-workflow-safety.sh`

**Interfaces:**
- Consumes: existing behavior case/result format and runner validation.
- Produces: failing cases proving routing, risk, approval and revision outputs are not yet decision-ready.

- [ ] Add literal fixtures for each human gate and expected action semantics.
- [ ] Run targeted runner/safety tests and confirm failure is caused by missing Human Action Request behavior.
- [ ] Record RED output in the core change implementation evidence.

### Task 2: Core Human Action Request GREEN

**Files:**
- Create: `architecture-design-workflow/references/human-action-request.md`
- Create: `architecture-design-workflow/templates/human-action-request.md`
- Modify: `architecture-design-workflow/SKILL.md`
- Modify: relevant intake/design/review/packet/publication/handoff references and templates

**Interfaces:**
- Consumes: action types and invariants from the core delta specs.
- Produces: a portable action card with owner, authority, options, consequences, stable evidence, exact reply and post-response state.

- [ ] Implement the minimum shared reference/template required by the failing cases.
- [ ] Route each human-dependent next action without changing canonical enums.
- [ ] Run targeted tests until all new core cases pass.
- [ ] Run existing core regression matrix and quick skill validation.

### Task 3: Core spec sync and review

**Files:**
- Create: `openspec/specs/architecture-human-action-requests/spec.md`
- Modify: `openspec/specs/architecture-design-artifacts/spec.md`
- Modify: `openspec/specs/architecture-design-governance/spec.md`
- Modify: `openspec/specs/architecture-approval-packets/spec.md`

**Interfaces:**
- Consumes: validated delta specs.
- Produces: main specs matching implemented core behavior.

- [ ] Apply each ADDED requirement to the corresponding main spec.
- [ ] Strict-validate the core change and affected main specs.
- [ ] Check diff scope and whitespace before starting adapter work.

### Task 4: Adapter behavior contract RED

**Files:**
- Modify: `tests/fixtures/multica-architecture-approval-adapter/`
- Modify: `tests/test_multica_architecture_approval_adapter_contract.py`

**Interfaces:**
- Consumes: existing adapter result schema and local fake contract fixtures.
- Produces: failures for buried decisions, token/prose mixing, incomplete access and ambiguous write authorization.

- [ ] Add literal adapter fixtures and validator expectations.
- [ ] Run targeted adapter tests and confirm expected RED failures.
- [ ] Record RED output in adapter implementation evidence.

### Task 5: Multica rendering and authorization GREEN

**Files:**
- Create: `multica-architecture-approval-adapter/templates/multica-human-action-request.md`
- Create: `multica-architecture-approval-adapter/templates/multica-operational-authorization.md`
- Modify: adapter `SKILL.md`, approval comment, decision/readiness evidence and directly relevant references

**Interfaces:**
- Consumes: compatible portable Human Action Request fields.
- Produces: decision-first Multica comments, token/context separation, per-artifact access and scoped operational authorization.

- [ ] Implement minimum templates and reference rules for the failing cases.
- [ ] Keep marker grammar, packet bytes and legal token parser unchanged.
- [ ] Run targeted adapter tests until all new cases pass.
- [ ] Run existing adapter regression and quick skill validation.

### Task 6: Adapter spec sync and final verification

**Files:**
- Create: `openspec/specs/multica-architecture-human-action-rendering/spec.md`
- Modify: adapter delivery, decision-binding and activation main specs
- Create: implementation evidence in both change directories

**Interfaces:**
- Consumes: validated adapter delta specs and fresh test outputs.
- Produces: apply-complete changes with reproducible evidence and no live activation.

- [ ] Sync affected main specs.
- [ ] Strict-validate both changes and affected main specs.
- [ ] Run full repository-relevant test suites, quick validators and `git diff --check`.
- [ ] Inspect GitNexus/diff impact and record limitations, including `activation=not_run` and `sandbox_acceptance=not_run`.
