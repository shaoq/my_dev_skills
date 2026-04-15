## MODIFIED Requirements

### Requirement: Read-only diagnostic guardrail
The `check-changes-completed` skill MAY modify `tasks.md` files of changes that pass D3 (Code Delivery) and fail D1 (Tasks). All other change artifacts (proposal.md, design.md, specs/, .openspec.yaml) remain strictly read-only.

#### Scenario: D3 passes and D1 fails
- **WHEN** a change passes D3 (files exist + git commits found) but fails D1 (incomplete tasks)
- **THEN** the system SHALL be allowed to modify that change's `tasks.md` via the smart-task-backfill capability

#### Scenario: D3 fails
- **WHEN** a change fails D3 (code not delivered)
- **THEN** the system SHALL NOT modify any files of that change

#### Scenario: D1 already passes
- **WHEN** a change passes D1 (all tasks already marked)
- **THEN** the system SHALL NOT modify that change's tasks.md

### Requirement: Skill description reflects new role
The skill frontmatter `description` field SHALL be updated to indicate the skill can auto-backfill task markers when contradictions are detected, replacing the current "Pure diagnostic tool" characterization.

#### Scenario: Updated description
- **WHEN** the skill is loaded
- **THEN** the description SHALL mention both diagnostic and backfill capabilities
