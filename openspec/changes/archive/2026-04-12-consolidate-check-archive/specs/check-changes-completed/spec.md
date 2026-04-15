## MODIFIED Requirements

### Requirement: Output summary table
The system SHALL output a markdown table summarizing all active changes with their four-dimensional check results, then output blocking reasons for non-archivable changes, and end with a hint to use `opsx:archive`.

#### Scenario: Archivable changes exist
- **WHEN** some active changes pass all four dimensions
- **THEN** the system SHALL output the completion report table, blocking reasons for non-archivable changes, and a hint listing archivable changes with instruction to use `opsx:archive <name>` to archive

#### Scenario: No archivable changes
- **WHEN** no active changes pass all four dimensions
- **THEN** the system SHALL output the completion report table, blocking reasons, and the message "No archivable changes found. See blocking reasons above."

#### Scenario: All archivable
- **WHEN** all active changes pass all four dimensions
- **THEN** the system SHALL output the completion report table and a hint listing all changes as archivable with instruction to use `opsx:archive <name>`

## REMOVED Requirements

### Requirement: Archive guidance with three strategies
**Reason**: Responsibility separation — `check-changes-completed` is now a pure diagnostic tool. Users run `opsx:archive` directly based on the report.
**Migration**: Use `opsx:archive <change-name>` to archive individual changes after reviewing the diagnostic report.
