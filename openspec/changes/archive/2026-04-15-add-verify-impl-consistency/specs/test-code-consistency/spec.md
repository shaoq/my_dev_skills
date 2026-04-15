## ADDED Requirements

### Requirement: Test file discovery
The skill SHALL discover integration test files by scanning for common patterns: files matching *test*.* or *spec*.* (e.g., user.test.ts, test_api.py), directories named __tests__/, test/, tests/, or *_test/ (Go), and test configuration files (jest.config, pytest.ini, go test, etc.).

#### Scenario: Test files discovered
- **WHEN** project has tests/user.test.ts and tests/apihandler_test.go
- **THEN** both files SHALL be included in D3 verification

#### Scenario: No test files found
- **WHEN** project has no test files
- **THEN** D3 dimension SHALL be skipped with informational note "No test files found"

### Requirement: Test target extraction
The skill SHALL extract from test files: endpoint paths being tested (e.g., POST /api/users), function/module names being tested, expected status codes in assertions, and key assertion values.

#### Scenario: Endpoint test target extracted
- **WHEN** test contains `request(app).post('/api/users')` and `expect(res.status).toBe(201)`
- **THEN** skill SHALL extract: tests POST /api/users, expects 201

#### Scenario: Function test target extracted
- **WHEN** test contains `describe('UserService', () => { it('createUser', ...)`
- **THEN** skill SHALL extract: tests UserService.createUser

### Requirement: Test target existence verification
The skill SHALL verify that endpoints and functions referenced in tests still exist in the source code. Tests targeting non-existent code SHALL be flagged as orphaned tests.

#### Scenario: Test target exists
- **WHEN** test references POST /api/users and route exists in source
- **THEN** test target SHALL be classified as FOUND

#### Scenario: Orphaned test detected
- **WHEN** test references DELETE /api/users/:id but no matching route exists
- **THEN** test SHALL be flagged as orphaned with CRITICAL severity

#### Scenario: Renamed endpoint test
- **WHEN** test references GET /api/user/:id but code now uses GET /api/users/:id
- **THEN** finding SHALL be reported as WARNING suggesting test update

### Requirement: Scenario coverage assessment
The skill SHALL assess whether key scenarios from specs (WHEN/THEN scenarios) are covered by integration tests. Missing scenario coverage SHALL be reported as INFO.

#### Scenario: Key scenario covered
- **WHEN** spec defines "WHEN user submits invalid email THEN returns 400" and test has corresponding test case
- **THEN** scenario SHALL be marked as covered

#### Scenario: Key scenario missing coverage
- **WHEN** spec defines "WHEN user submits invalid email THEN returns 400" but no test verifies invalid email handling
- **THEN** scenario SHALL be reported as uncovered with INFO severity

#### Scenario: Error handling not tested
- **WHEN** code has error handling paths (try/catch, error middleware) but tests only cover happy paths
- **THEN** finding SHALL be reported as INFO suggesting error scenario tests

### Requirement: OpenSpec change-level test verification
When an active OpenSpec change is detected, the skill SHALL additionally verify that tests exist for the change's scope by checking git diff for test files and comparing test coverage against the change's spec scenarios.

#### Scenario: Change has corresponding tests
- **WHEN** active change adds POST /api/users endpoint and git diff includes a test file testing that endpoint
- **THEN** change-level test coverage SHALL be reported as adequate

#### Scenario: Change missing tests
- **WHEN** active change adds new endpoint but git diff has no test file changes
- **THEN** finding SHALL be reported as WARNING with suggestion to add tests
