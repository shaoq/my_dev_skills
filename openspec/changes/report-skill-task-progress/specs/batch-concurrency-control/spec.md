## ADDED Requirements

### Requirement: Parallel proposal creation reports numeric task progress

`parall-new-proposal` SHALL append task completion progress to its existing final report for each successfully created proposal and as an aggregate over proposals with readable progress. It SHALL report only `DONE/TOTAL`, `REMAINING`, reason-category counts, and a brief cause summary; it SHALL NOT list task identifiers or task text.

#### Scenario: Newly created proposals have pending implementation tasks
- **WHEN** successfully created proposals contain unchecked implementation tasks and no apply workflow has run
- **THEN** each proposal and the aggregate report numeric task progress and classify those remaining tasks as `尚未进入实施阶段`

#### Scenario: Aggregate progress covers all successful proposals
- **WHEN** every successfully created proposal has a readable `tasks.md` with recognized checkboxes
- **THEN** the aggregate `DONE`, `TOTAL`, and `REMAINING` equal the sums of the corresponding per-proposal values

#### Scenario: Some proposal progress is unknown
- **WHEN** a successfully created proposal has a missing or unreadable `tasks.md`, or no recognized task checkboxes
- **THEN** that proposal reports unknown progress, is excluded from known task totals, and the aggregate states how many successful proposals its numeric totals cover

#### Scenario: Some proposal creation fails
- **WHEN** one or more proposal creations fail while other proposals succeed
- **THEN** creation failures and their high-level causes remain separately summarized and are not included in known task progress totals

#### Scenario: Report omits task details
- **WHEN** any successfully created proposal has unfinished tasks
- **THEN** the final report contains no task identifier, task text, or per-task list and only reports counts and a categorized high-level cause summary
