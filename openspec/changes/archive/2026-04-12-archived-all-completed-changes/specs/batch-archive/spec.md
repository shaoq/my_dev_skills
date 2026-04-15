## ADDED Requirements

### Requirement: Offer three archive strategies
The system SHALL present the user with three options after displaying the completion report: "Archive All", "Confirm One by One", and "View Only".

#### Scenario: User selects Archive All
- **WHEN** archivable changes exist and user selects "Archive All"
- **THEN** the system SHALL sequentially call `Skill("opsx:archive", args="<name>")` for each archivable change in alphabetical order

#### Scenario: User selects Confirm One by One
- **WHEN** archivable changes exist and user selects "Confirm One by One"
- **THEN** the system SHALL use AskUserQuestion for each archivable change to confirm, then call `Skill("opsx:archive")` only for confirmed ones

#### Scenario: User selects View Only
- **WHEN** the user selects "View Only"
- **THEN** the system SHALL end the flow without performing any archive operations

#### Scenario: No archivable changes
- **WHEN** no changes pass the three-dimensional check
- **THEN** the system SHALL NOT show archive strategy options and SHALL only display the completion report with blocking reasons

### Requirement: Sequential archive with failure isolation
The system SHALL archive changes one at a time, where a failure on one change does NOT block archiving of subsequent changes.

#### Scenario: Archive succeeds
- **WHEN** `opsx:archive` completes successfully for a change
- **THEN** the system SHALL record it as succeeded and proceed to the next

#### Scenario: Archive fails
- **WHEN** `opsx:archive` fails for a change
- **THEN** the system SHALL record the error, skip to the next change, and include the failure in the final summary

### Requirement: Output final archive summary
After all archive operations complete, the system SHALL output a summary of results.

#### Scenario: Mixed success and failure
- **WHEN** some archives succeed and some fail
- **THEN** the system SHALL output a table with columns: Change, Status, Details

#### Scenario: All succeed
- **WHEN** all archives succeed
- **THEN** the system SHALL output a success summary with the list of archived changes and their archive locations
