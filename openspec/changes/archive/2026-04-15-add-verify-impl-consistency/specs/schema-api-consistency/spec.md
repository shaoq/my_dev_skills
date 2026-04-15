## ADDED Requirements

### Requirement: Schema file discovery
The skill SHALL discover API schema files by scanning for common formats: OpenAPI/Swagger (openapi.yaml, swagger.json, openapi.json, swagger.yaml), Protocol Buffers (*.proto), GraphQL Schema (schema.graphql, *.graphql), and JSON Schema files.

#### Scenario: OpenAPI schema discovered
- **WHEN** project contains openapi.yaml in root or docs/ directory
- **THEN** skill SHALL include it in D2 verification

#### Scenario: No schema files found
- **WHEN** project has no API schema files
- **THEN** D2 dimension SHALL be skipped with informational note "No API schema files found"

### Requirement: Schema endpoint extraction
The skill SHALL parse schema files and extract: endpoint paths with HTTP methods, request parameter/field names with types, response field names with types, and documented status codes.

#### Scenario: OpenAPI endpoints extracted
- **WHEN** openapi.yaml defines `paths: /api/users: post:` with request body and 201 response
- **THEN** skill SHALL extract: POST /api/users, request fields, response fields, status 201

#### Scenario: Proto service methods extracted
- **WHEN** .proto file defines `rpc CreateUser(CreateUserRequest) returns (CreateUserResponse)`
- **THEN** skill SHALL extract: CreateUser method, request type, response type

### Requirement: Multi-language route matching
The skill SHALL match extracted schema endpoints against route definitions in source code using framework-specific patterns. Supported frameworks: Express/Fastify (router.get/app.post), NestJS (@Get/@Post), FastAPI/Flask (@app.get/@app.route), Django (path/re_path), Go net/http/Gin/Echo (mux.HandleFunc/r.GET), Spring (@GetMapping/@RequestMapping).

#### Scenario: Express route matched
- **WHEN** schema defines GET /api/users and code contains `router.get('/api/users'`
- **THEN** endpoint SHALL be classified as FOUND

#### Scenario: FastAPI route matched
- **WHEN** schema defines POST /api/users and code contains `@app.post("/api/users")`
- **THEN** endpoint SHALL be classified as FOUND

#### Scenario: No matching route found
- **WHEN** schema defines DELETE /api/users/:id but no matching route exists in any source file
- **THEN** endpoint SHALL be classified as NOT_FOUND with CRITICAL severity

### Requirement: Request/response type comparison
The skill SHALL compare schema-defined request/response fields with actual code implementation. Layer 2 semantic analysis SHALL be applied when field presence or types are ambiguous.

#### Scenario: Missing required field in code
- **WHEN** schema declares `email` as required but code's request handler does not reference `email`
- **THEN** finding SHALL be reported as WARNING with field name and location

#### Scenario: Extra undocumented field in code
- **WHEN** code processes `phone` field but schema does not declare it
- **THEN** finding SHALL be reported as INFO suggesting schema update

#### Scenario: Type mismatch
- **WHEN** schema declares `age: number` but code treats it as string
- **THEN** finding SHALL be reported as WARNING with type details
