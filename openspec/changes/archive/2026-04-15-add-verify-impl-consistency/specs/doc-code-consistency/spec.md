## ADDED Requirements

### Requirement: Doc scanning with heuristic filtering
The skill SHALL scan project documentation files using a three-tier heuristic filter: HIGH (README*, docs/**/*.md, source-co-located *.md, filenames containing api/arch/design/spec/route/endpoint/schema), MEDIUM (other root *.md, GitHub templates), SKIP (CHANGELOG, HISTORY, CONTRIBUTING, LICENSE, CODE_OF_CONDUCT, node_modules/, vendor/, .git/, i18n/).

#### Scenario: High-priority docs are always scanned
- **WHEN** project has README.md and docs/api-guide.md
- **THEN** both files SHALL be included in doc scan

#### Scenario: Skip files are excluded
- **WHEN** project has CHANGELOG.md and CONTRIBUTING.md
- **THEN** both files SHALL be excluded from doc scan

### Requirement: Claim extraction from documentation
The skill SHALL extract verifiable claims from documentation, including: HTTP method + URL paths, backtick/quote-enclosed file paths, function/class names, parameter definitions (name: type), environment variables/config values, and technology stack declarations.

#### Scenario: Extract endpoint claims
- **WHEN** doc contains "POST /api/users — creates a user"
- **THEN** skill SHALL extract claim: endpoint POST /api/users

#### Scenario: Extract file path claims
- **WHEN** doc contains "`src/auth.ts` handles authentication"
- **THEN** skill SHALL extract claim: file src/auth.ts exists and handles authentication

#### Scenario: Extract parameter claims
- **WHEN** doc contains "name: string, email: string"
- **THEN** skill SHALL extract claims: parameter name (string), parameter email (string)

### Requirement: Layer 1 precise verification
The skill SHALL verify extracted claims against source code using Grep for exact pattern matching. Each claim SHALL be classified as FOUND, NOT_FOUND, or UNCERTAIN.

#### Scenario: Claim matches code
- **WHEN** doc claims "POST /api/users" and source contains `router.post('/api/users'`
- **THEN** claim SHALL be classified as FOUND

#### Scenario: Claim not found in code
- **WHEN** doc claims "DELETE /api/users/:id" but no matching route exists
- **THEN** claim SHALL be classified as NOT_FOUND with severity CRITICAL

#### Scenario: Claim uncertain
- **WHEN** doc claims "supports JWT authentication" but grep matches are ambiguous
- **THEN** claim SHALL be classified as UNCERTAIN and passed to Layer 2

### Requirement: Layer 2 semantic analysis
The skill SHALL perform semantic analysis on UNCERTAIN items by reading relevant code sections and using Claude's understanding to assess consistency. Items SHALL be classified as ALIGNED, DRIFTED, or CONFLICT.

#### Scenario: Semantic alignment confirmed
- **WHEN** doc says "validates email format" and code uses regex `/^[^@]+@[^@]+\.[^@]+$/`
- **THEN** finding SHALL be classified as ALIGNED (INFO severity)

#### Scenario: Semantic drift detected
- **WHEN** doc says "validates email format strictly" but code only checks for `@` presence
- **THEN** finding SHALL be classified as DRIFTED (WARNING severity)

#### Scenario: Semantic conflict detected
- **WHEN** doc says "requires email verification" but code has no verification logic
- **THEN** finding SHALL be classified as CONFLICT (CRITICAL severity)

### Requirement: OpenSpec change-level doc verification
When an active OpenSpec change is detected, the skill SHALL additionally read the change's proposal.md, design.md, and specs/*/spec.md to extract structured claims, and verify each claim against the change's scope (git diff main..HEAD).

#### Scenario: Change proposal claims verified
- **WHEN** active change's proposal.md declares "add refresh token endpoint"
- **THEN** skill SHALL verify refresh token endpoint exists in git diff scope

#### Scenario: Spec WHEN/THEN scenarios verified
- **WHEN** spec.md defines "WHEN user submits valid email THEN system sends verification"
- **THEN** skill SHALL check code for email sending logic after validation
