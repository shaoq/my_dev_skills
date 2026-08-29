# openspec-proposal-review Specification

## Purpose
TBD - created by archiving change add-openspec-review-change-skill. Update Purpose after archive.
## Requirements
### Requirement: Review resolves a valid OpenSpec project and one active change

The `openspec-review-change` skill SHALL accept `[change-name] [--openspec-root <repo-relative-path>]`, resolve the selected OpenSpec project without escaping the current Git repository, and review exactly one active, unarchived change. It MUST fail safely when Git, OpenSpec, the project root, or the change selection is invalid.

#### Scenario: Explicit active change is valid
- **WHEN** the user names an existing active change in a valid OpenSpec project
- **THEN** the skill selects that change and reports the resolved OpenSpec root and change name before reviewing it

#### Scenario: Exactly one active change exists
- **WHEN** the user omits a change name and exactly one active change exists in the resolved OpenSpec project
- **THEN** the skill selects that change automatically and states which change was selected

#### Scenario: Change selection is ambiguous
- **WHEN** the user omits a change name and multiple active changes exist without one uniquely established by the conversation
- **THEN** the skill requests a change selection and MUST NOT review an arbitrary change

#### Scenario: No active change exists
- **WHEN** the resolved OpenSpec project has no active change
- **THEN** the skill reports that no review target is available and does not inspect archived changes as substitutes

#### Scenario: Named change is invalid or archived
- **WHEN** the user names a missing change or a change that exists only under the archive
- **THEN** the skill reports a recoverable selection error and lists active candidates without reviewing the invalid target

#### Scenario: Nested OpenSpec root is valid
- **WHEN** `--openspec-root` identifies a repository-relative nested project containing a valid OpenSpec configuration
- **THEN** the skill runs all OpenSpec discovery and validation commands against that project while repository grounding remains scoped to the enclosing Git repository

#### Scenario: OpenSpec root is unsafe or invalid
- **WHEN** `--openspec-root` is absolute, escapes the Git repository, does not exist, or does not contain an initialized OpenSpec project
- **THEN** the skill stops with `BLOCKED`, explains the invalid root, and does not fall back to a different project silently

#### Scenario: Required command or repository context is unavailable
- **WHEN** the current location is not inside a Git repository or the `openspec` CLI is unavailable
- **THEN** the skill stops with `BLOCKED` and reports the missing prerequisite without modifying the environment

### Requirement: Review supports the spec-driven Schema and discovers its artifacts dynamically

The skill SHALL fully review changes using the `spec-driven` Schema. It MUST treat the active Schema's generated artifact instructions as the normative content and structure contract, and derive artifact identities, output paths, dependencies, completion state, and apply requirements from OpenSpec status and those instructions rather than assuming that every declared artifact exists at a fixed path. A Schema without an implemented semantic rubric MUST fail closed.

#### Scenario: Supported Schema uses declared artifact paths
- **WHEN** OpenSpec status identifies the change as `spec-driven`
- **THEN** the skill loads the Schema-declared artifacts and resolves their paths from OpenSpec instructions before semantic review

#### Scenario: Artifact violates its generated instruction
- **WHEN** an artifact omits a section, mapping, normative form, or other content required by its current OpenSpec instruction even if a parser accepts the file
- **THEN** the skill reports the concrete instruction mismatch and assigns severity according to whether the omission prevents safe implementation

#### Scenario: Artifact output path matches multiple files
- **WHEN** a declared artifact output path is a glob that matches multiple files such as delta Specs
- **THEN** the skill reviews every matching file in stable path order and preserves its artifact identity in the report

#### Scenario: Required artifact output path matches no files
- **WHEN** a required or completed artifact declares an output path that matches no file
- **THEN** the skill records the contradiction as a `BLOCKER` and continues reviewing artifacts that can be loaded

#### Scenario: Unsupported Schema is selected
- **WHEN** the selected change uses a Schema other than `spec-driven`
- **THEN** the skill reports the detected Schema, explains that no matching semantic rubric is available, and returns `BLOCKED` without pretending to complete a semantic review

### Requirement: Review performs structural preflight without treating it as semantic approval

The skill SHALL run OpenSpec strict validation and inspect required artifact status before semantic review. A successful structural validation MUST NOT by itself produce a `READY` conclusion.

#### Scenario: Strict validation fails
- **WHEN** `openspec validate <change> --type change --strict --json` reports one or more validation issues
- **THEN** the skill records the issues as `BLOCKER` findings and sets the overall conclusion to `BLOCKED`

#### Scenario: Apply-required artifact is incomplete
- **WHEN** an artifact required for apply is missing, blocked, or incomplete
- **THEN** the skill reviews available artifacts, reports each missing prerequisite, and sets the overall conclusion to `BLOCKED`

#### Scenario: Strict validation passes
- **WHEN** strict validation reports the change as valid
- **THEN** the skill continues with semantic, consistency, traceability, and task-readiness review before deciding the overall conclusion

### Requirement: Review identifies the change implementation stage

The skill SHALL classify the selected active change as `pre-apply`, `in-progress`, or `all-tasks-done` from task markers and repository evidence. It SHALL adapt its evidence language to the stage without turning proposal review into implementation verification or archive readiness approval.

#### Scenario: No task is completed
- **WHEN** all implementation tasks are unchecked and no clearly attributable implementation evidence is found
- **THEN** the skill reports the stage as `pre-apply` and evaluates the artifacts as an implementation plan

#### Scenario: Change is partially implemented
- **WHEN** some tasks are checked or repository evidence indicates that in-scope implementation has begun
- **THEN** the skill reports the stage as `in-progress`, compares material proposal claims with observable current behavior, and labels conclusions that depend on an unknown implementation baseline

#### Scenario: All tasks are marked complete
- **WHEN** every implementation task is checked while the change remains active
- **THEN** the skill reports `all-tasks-done`, reviews proposal quality and consistency, and explicitly states that this review does not replace implementation consistency or archive-completion verification

#### Scenario: Working tree contains unrelated or unattributable changes
- **WHEN** repository changes cannot be reliably attributed to the selected OpenSpec change
- **THEN** the skill reports the dirty-worktree limitation and does not present those changes as proof for or against the proposal

### Requirement: Review evaluates proposal quality across defined dimensions

The skill SHALL evaluate all applicable artifacts across Schema compliance, goal and scope clarity, project grounding, design completeness, Spec testability, cross-artifact consistency, end-to-end traceability, and task implementation readiness. It MUST mark a dimension as not applicable when the supported Schema or change scope legitimately omits that concern.

#### Scenario: Goal and scope are ambiguous
- **WHEN** the proposal does not make the problem, intended outcome, in-scope change, or relevant non-goals sufficiently clear to guide implementation
- **THEN** the skill reports the specific ambiguity with artifact evidence and explains what decision or content is needed

#### Scenario: Conditional design concern does not apply
- **WHEN** a change has no data migration, external API, security boundary, performance-sensitive path, or deployment impact
- **THEN** the skill does not create findings merely because those conditional design sections are absent

#### Scenario: Applicable design concern is omitted
- **WHEN** the proposed scope introduces a compatibility, security, migration, rollback, performance, or operational concern that the design does not address
- **THEN** the skill reports the omission with severity based on its implementation risk

### Requirement: Review grounds proposal claims in project evidence

The skill SHALL read the instruction chain applicable to the current runtime and verify material claims about existing files, symbols, interfaces, constraints, and impact against the repository. It SHALL use configured code-intelligence tooling when required by those project instructions and SHALL degrade to file search and source inspection when such tooling is unavailable or stale.

#### Scenario: Codex project instructions apply
- **WHEN** the review runs in Codex and applicable `AGENTS.md` files define repository rules
- **THEN** the skill follows the resolved Codex instruction chain and records material constraints used by the review

#### Scenario: Claude Code project instructions apply
- **WHEN** the review runs in Claude Code and applicable `CLAUDE.md` files define repository rules
- **THEN** the skill follows the resolved Claude Code instruction chain and records material constraints used by the review

#### Scenario: Project requires GitNexus
- **WHEN** applicable project instructions require GitNexus for code exploration or impact analysis
- **THEN** the skill follows those instructions and cites relevant repository evidence in its findings

#### Scenario: GitNexus is unavailable or stale
- **WHEN** no GitNexus capability exists or its index cannot establish current repository facts
- **THEN** the skill uses file and text search plus source inspection, states the reduced evidence scope, and does not claim that an unverified fact is proven

#### Scenario: Existing symbol may be changed by the proposal
- **WHEN** the proposal identifies an existing public or key symbol as an implementation target and project instructions require impact analysis
- **THEN** the skill runs upstream impact analysis for that symbol and reports its blast radius without editing it

#### Scenario: Referenced target does not match the repository
- **WHEN** an artifact names a file, symbol, API, or existing behavior that repository evidence contradicts
- **THEN** the skill reports the mismatch, its evidence location, likely implementation impact, and a correction path

### Requirement: Review detects cross-artifact conflicts and traceability gaps

The skill SHALL compare artifact claims and build a traceability view from problem and change scope through capabilities, requirements and scenarios, design decisions, tasks, and verification. It MUST report conflicting claims and material links that cannot be established.

#### Scenario: Artifacts specify contradictory behavior
- **WHEN** two artifacts define incompatible values, behaviors, scope boundaries, terminology, or decisions for the same concern
- **THEN** the skill reports a `MAJOR` or `BLOCKER` finding that cites both evidence locations and states which decision must be reconciled

#### Scenario: Requirement scenario has no delivery path
- **WHEN** an in-scope Requirement or Scenario cannot be mapped to a design decision, implementation task, or verification task as applicable
- **THEN** the skill identifies the uncovered Requirement or Scenario and the missing link

#### Scenario: Task has no requirement source
- **WHEN** a task introduces behavior or scope that cannot be traced to the proposal or Specs
- **THEN** the skill reports the task as ungrounded and recommends adding the missing requirement or removing the task from scope

#### Scenario: Traceability is many-to-many but complete
- **WHEN** multiple requirements share one design decision or implementation task and the relationship remains clear and verifiable
- **THEN** the skill accepts the many-to-many mapping without requiring artificial one-to-one links

### Requirement: Review determines whether tasks are implementation-ready

The skill SHALL evaluate whether tasks are ordered by dependency, bounded enough for an implementation session, linked to concrete outcomes, and verifiable. It SHALL distinguish an implementation task from a still-unresolved design decision.

#### Scenario: Task is actionable and verifiable
- **WHEN** a task identifies a concrete action and target, has a clear completion condition, and includes or maps to an appropriate validation step
- **THEN** the skill treats the task as implementation-ready

#### Scenario: Task uses vague completion language
- **WHEN** a task only says to implement, improve, check, or validate something without a concrete target or observable completion evidence
- **THEN** the skill reports the missing action, target, or acceptance evidence and suggests a more verifiable task formulation

#### Scenario: Task hides an unresolved design choice
- **WHEN** completing a task would require the implementer to choose between materially different architectures, interfaces, compatibility behaviors, or data models not resolved by the artifacts
- **THEN** the skill reports a design-readiness finding rather than treating the choice as ordinary implementation detail

#### Scenario: Verification coverage is missing
- **WHEN** in-scope behavior has implementation tasks but no task or clearly mapped step for tests, contract checks, validation, documentation, migration, or another applicable verification mechanism
- **THEN** the skill reports the missing verification path with severity based on behavior risk

### Requirement: Review emits a deterministic evidence-based gate report

The skill SHALL output an overall conclusion of `BLOCKED`, `NEEDS_REVISION`, `READY_WITH_WARNINGS`, or `READY`. Each non-informational finding MUST include a stable identifier, severity, review dimension, evidence, implementation impact, and a concrete correction recommendation. The report MUST deduplicate findings with the same root cause and sort them deterministically.

#### Scenario: Blocker exists
- **WHEN** one or more `BLOCKER` findings exist
- **THEN** the overall conclusion is `BLOCKED` regardless of findings in other dimensions

#### Scenario: Major issue exists without blockers
- **WHEN** no `BLOCKER` exists and one or more `MAJOR` findings exist
- **THEN** the overall conclusion is `NEEDS_REVISION`

#### Scenario: Only minor issues exist
- **WHEN** no `BLOCKER` or `MAJOR` exists and one or more `MINOR` findings exist
- **THEN** the overall conclusion is `READY_WITH_WARNINGS`

#### Scenario: No material issues exist
- **WHEN** no `BLOCKER`, `MAJOR`, or `MINOR` finding exists
- **THEN** the overall conclusion is `READY`

#### Scenario: One root cause appears in multiple dimensions
- **WHEN** the same omission creates related symptoms in proposal, design, Specs, or tasks
- **THEN** the report emits one primary finding with all relevant evidence and cross-references rather than inflating the finding count

#### Scenario: Large review produces many findings
- **WHEN** the review produces more findings than fit comfortably in the primary summary
- **THEN** the skill keeps the gate and severity totals visible, lists findings in severity and stable-identifier order, and preserves every finding in a structured detail section

#### Scenario: Finding evidence is uncertain
- **WHEN** available repository or artifact evidence is insufficient to prove a suspected problem
- **THEN** the skill states the uncertainty and required confirmation rather than presenting the suspicion as a proven defect

### Requirement: Review remains read-only by default

The skill MUST NOT edit OpenSpec artifacts, application code, project configuration, task markers, or user runtime configuration during a review. It SHALL provide proposed corrections in the report and require a separate explicit revision action before files are changed.

#### Scenario: Review finds correctable issues
- **WHEN** the review produces one or more actionable findings
- **THEN** the skill reports suggested corrections without changing any reviewed file

#### Scenario: User requests review only
- **WHEN** the user asks to review, audit, assess, or check a change without explicitly requesting revisions
- **THEN** the skill performs only read operations and returns the review report

#### Scenario: User combines review and revision in one request
- **WHEN** the user asks the skill invocation itself to review and immediately fix the selected change
- **THEN** the skill completes and presents the review first, preserves read-only behavior for that invocation, and requires an explicit follow-up revision workflow
