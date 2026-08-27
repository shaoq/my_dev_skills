# test-code-consistency Specification

## Purpose

Define discovery, target verification, scenario coverage, and assertion consistency for project and explicitly selected OpenSpec tests.

## Requirements

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
When the caller explicitly selects one active OpenSpec change and supplies `--base <target-branch>`, the skill SHALL additionally verify that tests exist for that change's scope by proving the frozen base commit is an ancestor of the frozen current commit, checking the immutable commit range for test files, and comparing test coverage against the selected change's spec scenarios. All change-level coverage and assertion attribution MUST use the same two frozen commits as document and implementation verification. The skill MUST NOT auto-select or combine multiple active changes.

#### Scenario: Change has corresponding tests
- **WHEN** active change adds POST /api/users endpoint, the caller supplies `--base develop`, and the frozen diff includes a test file testing that endpoint
- **THEN** change-level test coverage SHALL be reported as adequate against that target baseline

#### Scenario: Change missing tests
- **WHEN** active change adds new endpoint but the frozen target-to-HEAD diff has no test file changes
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

### Requirement: Spec-grounded assertion verification
When spec files containing WHEN/THEN scenarios are available, the skill SHALL extract quantifiable expected values from THEN clauses and compare them against actual test assertions. This verification SHALL execute after scenario coverage assessment (Step 5c) as a new Step 5d. When no spec files exist, this step SHALL be skipped entirely.

#### Scenario: Test assertion matches spec expected status code
- **WHEN** spec defines "THEN returns 201" and corresponding test asserts `expect(res.status).toBe(201)`
- **THEN** finding SHALL be reported as ALIGNED with no issue

#### Scenario: Test assertion contradicts spec expected status code
- **WHEN** spec defines "THEN returns 201" but test asserts `expect(res.status).toBe(200)`
- **THEN** finding SHALL be reported as CRITICAL: "Test asserts status 200 but spec expects 201"

#### Scenario: Test assertion partially covers spec expectations
- **WHEN** spec defines "THEN returns {id, name, email}" but test only asserts existence of `id`
- **THEN** finding SHALL be reported as WARNING: "Test verifies partial spec expectations (id), missing: name, email"

#### Scenario: No spec available
- **WHEN** no spec files contain WHEN/THEN scenarios
- **THEN** Step 5d SHALL be skipped with informational note "No spec scenarios found for assertion verification"

#### Scenario: Spec expected value not extractable
- **WHEN** THEN clause contains non-quantifiable text (e.g., "THEN system processes the request")
- **THEN** Layer 2 semantic analysis SHALL assess whether the test verifies the described behavior, classifying as ALIGNED or UNCERTAIN

### Requirement: Spec expected value extraction
The skill SHALL extract structured expected values from spec THEN clauses using pattern matching. Extractable value types SHALL include: HTTP status codes (numeric), response field names (in object notation), error/exception types, and boolean conditions. When pattern matching fails, the full THEN text SHALL be passed to Layer 2 semantic analysis.

#### Scenario: Status code extracted from THEN clause
- **WHEN** THEN clause contains "returns 201" or "returns status 201"
- **THEN** skill SHALL extract expected_status = 201

#### Scenario: Response fields extracted from THEN clause
- **WHEN** THEN clause contains "returns {id, name, email}"
- **THEN** skill SHALL extract expected_fields = [id, name, email]

#### Scenario: Error type extracted from THEN clause
- **WHEN** THEN clause contains "throws ValidationError" or "raises NotFoundError"
- **THEN** skill SHALL extract expected_error = ValidationError or NotFoundError

#### Scenario: Unstructured THEN clause
- **WHEN** THEN clause contains "system sends notification email"
- **THEN** skill SHALL pass full text to Layer 2 for semantic comparison with test assertions
