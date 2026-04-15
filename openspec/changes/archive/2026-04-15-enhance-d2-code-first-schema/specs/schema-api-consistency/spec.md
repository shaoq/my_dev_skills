## MODIFIED Requirements

### Requirement: Schema file discovery
The skill SHALL discover API schema files by scanning for common formats: OpenAPI/Swagger (openapi.yaml, swagger.json, openapi.json, swagger.yaml), Protocol Buffers (*.proto), GraphQL Schema (schema.graphql, *.graphql), and JSON Schema files. When no schema files are found, the skill SHALL check TECH_STACK for code-first frameworks (currently: FastAPI) and route to code-first analysis mode instead of skipping D2 entirely.

#### Scenario: OpenAPI schema discovered
- **WHEN** project contains openapi.yaml in root or docs/ directory
- **THEN** skill SHALL include it in D2 verification (existing schema-file mode)

#### Scenario: No schema files, but FastAPI detected
- **WHEN** project has no API schema files AND TECH_STACK contains fastapi
- **THEN** D2 dimension SHALL execute code-first analysis mode (steps 4d/4e/4f)

#### Scenario: No schema files, no code-first framework
- **WHEN** project has no API schema files AND TECH_STACK does not contain any supported code-first framework
- **THEN** D2 dimension SHALL be skipped with informational note "No API schema files found and no code-first framework detected"
