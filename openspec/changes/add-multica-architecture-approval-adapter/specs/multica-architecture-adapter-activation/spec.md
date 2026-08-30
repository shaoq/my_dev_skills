## ADDED Requirements

### Requirement: Adapter remains an independently installable sibling skill
The repository SHALL maintain `multica-architecture-approval-adapter/` as its own valid skill source with independent frontmatter, references, templates and Runtime metadata. `architecture-design-workflow` MUST remain usable without the adapter, while the adapter MUST refuse platform delivery without a compatible core packet.

#### Scenario: Both skills are installed locally
- **WHEN** the repository installer scans the two root skill directories in an isolated HOME
- **THEN** Claude Code and Codex receive separate links for core and adapter, each pointing to its repository source

#### Scenario: Adapter is absent
- **WHEN** only `architecture-design-workflow` is installed
- **THEN** core standalone profiles continue to work and no Multica field becomes a required core dependency

### Requirement: Automated validation never activates real Multica resources
Repository validation and packaging verification MUST use temporary Runtime homes, local archives and static/local contract checks. They MUST NOT import a real workspace Skill, bind a real Agent, create an Issue or mutate Team/Project/configuration as a completion prerequisite. This change does not require a fake `multica` CLI or dual-Runtime behavior suite.

#### Scenario: Apply validates packaging and local installation
- **WHEN** implementation validates the package and repository skill links in isolated temporary directories
- **THEN** it verifies local contents and leaves every real Multica profile and workspace untouched without simulating import or Agent binding

#### Scenario: No authenticated Multica profile exists
- **WHEN** automated validation runs on a machine without Multica credentials
- **THEN** all required local validation still runs deterministically without network access

### Requirement: Workspace activation requires explicit human authorization
Delivery SHALL provide a runbook that packages the adapter, imports it with safe conflict handling, additively binds it to the selected existing Architecture Agent and verifies the final skill list. The runbook MUST NOT use replace-all binding by default or create missing resources.

#### Scenario: Human authorizes activation
- **WHEN** a human names the target workspace and existing Agent and explicitly requests activation
- **THEN** the operator imports the adapter, uses additive `agent skills add`, and confirms both core and adapter IDs through a final read-only list

#### Scenario: Skill import reports a conflict
- **WHEN** workspace import returns a same-name conflict
- **THEN** activation stops and reports existing identity and supported choices without overwriting unless the human separately authorizes an overwrite strategy

#### Scenario: Target Agent does not exist
- **WHEN** activation cannot resolve the selected Architecture Agent
- **THEN** it stops without creating an Agent, Team, Project or fallback binding

### Requirement: Activation verifies a sandbox review flow before production use
After authorized import/binding, the runbook MUST require a dedicated sandbox Issue acceptance that covers comment delivery, attachment opening on mobile, digest re-verification, short-token human reply, supersession and failure closing. Production Architecture Team activation MUST NOT be claimed from static installation alone.

#### Scenario: Sandbox acceptance passes
- **WHEN** desktop and mobile target members can open exact attachments and a valid reply produces current-packet decision evidence while stale replies remain no-op
- **THEN** the adapter may be reported ready for the explicitly selected Architecture Agent

#### Scenario: Mobile material cannot be opened
- **WHEN** attachment cards exist but the target member cannot retrieve the material from the mobile client
- **THEN** acceptance fails, the adapter remains inactive for production use, and a separate platform capability proposal is recommended if configuration cannot close the gap

### Requirement: Adapter version evidence is recorded for operations
Implementation and activation evidence MUST record implementation revision evidence: when a commit is separately authorized, the adapter repository commit; in a no-commit run, `not_committed` plus baseline HEAD and working-tree scope. It MUST also record consumed core contract revision, observed Multica/CLI version or commit, validation matrix, target workspace/Agent only when explicitly activated, and known tool limitations.

#### Scenario: Implementation is ready for review
- **WHEN** repository work is complete but no real activation was authorized
- **THEN** evidence records implementation revision evidence, consumed core and observed platform-contract versions while marking workspace, Agent and sandbox acceptance as `n/a|not_run`

#### Scenario: Platform capability later changes
- **WHEN** a newer Multica version changes a required comment, attachment or metadata contract
- **THEN** the adapter must re-run capability preflight and record the new observed version before claiming compatibility
