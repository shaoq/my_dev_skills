## ADDED Requirements

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
