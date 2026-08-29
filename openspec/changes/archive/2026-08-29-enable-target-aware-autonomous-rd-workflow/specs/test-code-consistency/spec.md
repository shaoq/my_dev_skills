## MODIFIED Requirements

### Requirement: OpenSpec change-level test verification
When the caller explicitly selects one active OpenSpec change and supplies `--base <target-branch>`, the skill SHALL additionally verify that tests exist for that change's scope by proving the frozen base commit is an ancestor of the frozen current commit, checking the immutable commit range for test files, and comparing test coverage against the selected change's spec scenarios. All change-level coverage and assertion attribution MUST use the same two frozen commits as document and implementation verification. The skill MUST NOT auto-select or combine multiple active changes.

#### Scenario: Change has corresponding tests
- **WHEN** active change adds POST /api/users endpoint, the caller supplies `--base develop`, and the frozen diff includes a test file testing that endpoint
- **THEN** change-level test coverage SHALL be reported as adequate against that target baseline

#### Scenario: Change missing tests
- **WHEN** active change adds a new endpoint but the frozen target-to-HEAD diff has no test file changes
- **THEN** finding SHALL be reported as WARNING with suggestion to add tests

#### Scenario: Test exists only outside the selected change scope
- **WHEN** a test is present in the repository but is not part of the frozen target-to-HEAD range used for delivery attribution
- **THEN** the report SHALL distinguish repository-level coverage from change-level test delivery and MUST NOT claim the test was added by the change

#### Scenario: Selected base is not an ancestor
- **WHEN** the selected target commit is not an ancestor of the frozen current commit
- **THEN** change-level test coverage and assertion attribution SHALL be reported as not executed and MUST NOT count target-only tree differences as tests delivered by the change

#### Scenario: Multiple active changes are not combined
- **WHEN** several active changes exist and the caller explicitly selects one change with `--base develop`
- **THEN** only the selected change's specs and scenarios SHALL participate in change-level coverage and assertion attribution
