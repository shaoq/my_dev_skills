## ADDED Requirements

### Requirement: Scan all active OpenSpec changes
The system SHALL scan all subdirectories under `openspec/changes/`, excluding `archive/`, and list them as active changes.

#### Scenario: Active changes found
- **WHEN** `openspec/changes/` contains subdirectories other than `archive/`
- **THEN** the system SHALL return a list of all subdirectory names as active changes

#### Scenario: No active changes
- **WHEN** `openspec/changes/` is empty or contains only `archive/`
- **THEN** the system SHALL output "No active changes found" and stop execution

### Requirement: Check tasks completion
The system SHALL read each change's `tasks.md` and verify all task items are marked complete (`[x]`).

#### Scenario: All tasks complete
- **WHEN** a change's `tasks.md` has all items marked as `[x]`
- **THEN** the system SHALL mark that change's Tasks dimension as passed

#### Scenario: Incomplete tasks
- **WHEN** a change's `tasks.md` has one or more items marked as `[ ]`
- **THEN** the system SHALL mark that change's Tasks dimension as failed with the count of incomplete items

#### Scenario: No tasks.md file
- **WHEN** a change does not have a `tasks.md` file
- **THEN** the system SHALL mark that change's Tasks dimension as failed with "missing tasks.md"

### Requirement: Verify code delivery on current branch
The system SHALL verify that expected output files exist AND have been committed to the current git branch.

#### Scenario: Code files exist and committed
- **WHEN** expected output files (identified from `design.md` and `proposal.md`) exist on disk AND `git log <current-branch> -- <files>` returns commits
- **THEN** the system SHALL mark that change's Code dimension as passed

#### Scenario: Code files missing
- **WHEN** expected output files do not exist on disk
- **THEN** the system SHALL mark that change's Code dimension as failed, listing the missing files

#### Scenario: Files exist but not committed
- **WHEN** expected output files exist but `git log <current-branch> -- <files>` returns no commits
- **THEN** the system SHALL mark that change's Code dimension as failed with "files exist but not committed"

#### Scenario: No explicit file paths in design/proposal
- **WHEN** `design.md` and `proposal.md` do not contain explicit file paths
- **THEN** the system SHALL use heuristic: check if `<change-name>/SKILL.md` exists at project root

### Requirement: Check dependency integrity
The system SHALL read each change's `proposal.md` Dependencies section and verify all dependencies are satisfied.

#### Scenario: No dependencies
- **WHEN** a change has no Dependencies section or the section is empty
- **THEN** the system SHALL mark that change's Dependencies dimension as passed

#### Scenario: All dependencies archived or archivable
- **WHEN** all declared dependencies exist in `openspec/changes/archive/` or pass the same three-dimensional check
- **THEN** the system SHALL mark that change's Dependencies dimension as passed

#### Scenario: Dependency not satisfied
- **WHEN** a declared dependency does not exist in archive AND fails the three-dimensional check
- **THEN** the system SHALL mark that change's Dependencies dimension as failed, listing the blocking dependency and reason

### Requirement: Output completion report
The system SHALL output a markdown table summarizing all active changes with their dimensional check results.

#### Scenario: Mixed results
- **WHEN** active changes include both archivable and non-archivable ones
- **THEN** the system SHALL output a table with columns: Change, Tasks, Code, Dependencies, Archivable

#### Scenario: All archivable
- **WHEN** all active changes pass all three dimensions
- **THEN** the system SHALL output the table and mark all as archivable

#### Scenario: None archivable
- **WHEN** no active changes pass all three dimensions
- **THEN** the system SHALL output the table, show blocking reasons, and stop without offering archive options
