---
name: verify-impl-consistency
description: Deep consistency verification between docs, API schema, and integration tests vs actual code implementation. Two-layer verification — precise pattern matching first, then semantic analysis for uncertain items. Auto-detects OpenSpec changes for enhanced verification. Pure diagnostic tool (no pass/fail judgment, no auto-fix). Supports multiple languages: TS/JS, Python, Go, Java.
argument-hint: "[change-name]"
allowed-tools: Bash(openspec *) Bash(git *) Read Glob Grep AskUserQuestion
---

Deep consistency verification between documentation, API schema, and integration tests vs actual code. Two-layer strategy: precise matching then semantic analysis. Pure diagnostic — reports findings only, no modifications.

**Input**: Optionally a change name. Example: `/verify-impl-consistency` or `/verify-impl-consistency add-auth`.

**Steps**

1. **Validate prerequisites**

   Run these checks in parallel:
   ```bash
   git rev-parse --is-inside-work-tree
   which openspec
   ```

   **If any check fails:**
   - Not a git repo → error: "Must be inside a git repository."
   - No openspec CLI → error: "OpenSpec CLI is required. Install it first."

2. **Project-level discovery**

   Scan the project for three artifact types. Always run regardless of whether an OpenSpec change exists.

   ### 2a. Discover documentation files

   Use Glob to find all markdown files, then apply heuristic filtering:

   **HIGH priority (always read)**:
   - `README*.md` (root level)
   - `docs/**/*.md`
   - `*.md` files co-located with source code (same directory as `.ts`, `.py`, `.go`, `.java` files)
   - Files whose names contain: `api`, `arch`, `design`, `spec`, `route`, `endpoint`, `schema`

   **SKIP (never read)**:
   - `CHANGELOG*`, `HISTORY*`, `CONTRIBUTING*`, `LICENSE*`, `CODE_OF_CONDUCT*`
   - Files in `node_modules/`, `vendor/`, `.git/`, `__pycache__/`
   - `i18n/` translation directories (read source language only)

   Store discovered docs as `DOC_FILES`.

   ### 2b. Discover API schema files

   Use Glob to find:
   - OpenAPI/Swagger: `**/openapi.{yaml,yml,json}`, `**/swagger.{yaml,yml,json}`
   - Protocol Buffers: `**/*.proto`
   - GraphQL: `**/schema.graphql`, `**/*.graphql`
   - Generic JSON Schema: `**/schema.json`

   Store discovered schemas as `SCHEMA_FILES`.

   ### 2c. Discover test files

   Use Glob to find:
   - `**/*test*.*` (e.g., `user.test.ts`, `test_api.py`, `handler_test.go`)
   - `**/*spec*.*` (e.g., `user.spec.ts`)
   - Directories: `**/__tests__/**`, `**/test/**`, `**/tests/**`

   Exclude `node_modules/`, `vendor/`, `.git/`, `__pycache__/`.

   Store discovered tests as `TEST_FILES`.

   ### 2d. Detect tech stack

   Detect the project's language(s) and framework(s) by checking for:
   - `package.json` → look for `express`, `fastify`, `nestjs`, `next`, `koa`
   - `requirements.txt` / `pyproject.toml` / `setup.py` → look for `fastapi`, `flask`, `django`
   - `go.mod` → Go (check imports for `gin`, `echo`, `fiber`, `chi`)
   - `pom.xml` / `build.gradle` → Java (check for `spring-boot`)

   Store as `TECH_STACK` for use in D2 route matching.

3. **D1 — Doc ↔ Code consistency**

   ### 3a. Extract verifiable claims from documentation

   For each file in `DOC_FILES`:
   - Read the file content
   - Extract claims using these patterns:

   | Claim Type | Pattern | Example |
   |------------|---------|---------|
   | Endpoint path | `GET /path`, `POST /api/users`, `(GET|POST|PUT|DELETE|PATCH)\\s+/[\\w/:{}-]+` | `POST /api/users` |
   | File path | Backtick-enclosed paths: `` `src/auth.ts` `` | `src/auth.ts` |
   | Function/class name | `function \\w+`, `class \\w+`, `def \\w+`, `func \\w+` | `function createUser` |
   | Parameter definition | `\\w+\\s*:\\s*(string|number|boolean|int|float|any)` | `email: string` |
   | Environment variable | `[A-Z_]{2,}(\\s*=\\s*\\S+)?` in config sections | `DATABASE_URL` |
   | Tech stack | "uses X", "built with X", "powered by X" | "Express + TypeScript" |

   Collect all claims into a list `DOC_CLAIMS`, each with:
   ```
   { source_file, claim_type, claim_text, line_number }
   ```

   ### 3b. Layer 1 — Precise verification

   For each claim in `DOC_CLAIMS`:

   - **Endpoint claims**: Use Grep to search for the path pattern in source code files. Match against route definitions appropriate for the detected `TECH_STACK`:
     ```
     Express/Fastify: router\.(get|post|put|delete|patch)\(['"]/path
     NestJS: @(Get|Post|Put|Delete|Patch)\(['"]/path
     FastAPI: @app\.(get|post|put|delete|patch)\(["']/path
     Flask: @app\.route\(['"]/path
     Django: path\(['"]/path
     Go: \.(GET|POST|PUT|DELETE|PATCH)\(["']/path
     Spring: @(Get|Post|Put|Delete|Patch|Request)Mapping\(["']/path
     ```

   - **File path claims**: Check if the file exists using `test -f <path>`.

   - **Function/class claims**: Use Grep for the function/class name in source files.

   - **Parameter claims**: Use Grep for the parameter name in the relevant source files (controllers, models, validation).

   - **Config/tech stack claims**: Check `package.json`, `requirements.txt`, `go.mod`, `pom.xml`, `.env.example` for evidence.

   Classify each claim:
   - `FOUND` — clear match in source code
   - `NOT_FOUND` — no match found → **severity CRITICAL**
   - `UNCERTAIN` — ambiguous or partial match → pass to Layer 2

   ### 3c. Layer 2 — Semantic analysis

   For each `UNCERTAIN` claim:
   - Read the relevant source code sections (functions, handlers, modules related to the claim)
   - Assess semantic consistency:
     - **ALIGNED** — behavior matches the documentation claim (INFO severity)
     - **DRIFTED** — partial match with minor differences (WARNING severity)
     - **CONFLICT** — clear semantic contradiction (CRITICAL severity)

   Record each finding as:
   ```
   { dimension: "D1", severity, source_file, claim, finding, suggestion }
   ```

4. **D2 — Schema ↔ API Code consistency**

   D2 operates in two modes based on available artifacts:

   | Condition | Mode | Sub-steps |
   |-----------|------|-----------|
   | `SCHEMA_FILES` is non-empty | **Schema-file mode** | 4a → 4b → 4c |
   | `SCHEMA_FILES` is empty AND `TECH_STACK` contains `fastapi` | **Code-first mode** | 4d → 4e → 4f |
   | `SCHEMA_FILES` is empty AND no code-first framework detected | **Skip** | informational note |

   If skipping → add note "No API schema files found and no code-first framework detected".

   **Schema-file mode** (standalone schema files exist):

   ### 4a. Extract schema definitions

   For each file in `SCHEMA_FILES`:
   - Read the file content
   - Identify the schema format (OpenAPI, Proto, GraphQL)

   **OpenAPI/Swagger extraction**:
   - Parse `paths` section → extract endpoint paths + HTTP methods
   - For each endpoint: extract `requestBody` fields (name + type + required), `responses` (status codes + field names + types)

   **Proto extraction**:
   - Parse `service` blocks → extract RPC method names
   - Parse `message` blocks → extract field names + types
   - Map RPC methods to HTTP endpoints via `google.api.http` annotations if present

   **GraphQL extraction**:
   - Parse `type Query` / `type Mutation` → extract field names + argument types + return types

   Collect into `SCHEMA_ENDPOINTS`:
   ```
   { schema_file, method, path, request_fields[], response_fields[], status_codes[] }
   ```

   ### 4b. Layer 1 — Route matching

   For each endpoint in `SCHEMA_ENDPOINTS`:
   - Use Grep to search for matching route definitions using the framework patterns appropriate for `TECH_STACK`
   - Match on: HTTP method + URL path (normalizing path parameters: `:id`, `{id}`, `[id]` → equivalent)
   - Classify: `FOUND` / `NOT_FOUND` / `UNCERTAIN`

   **NOT_FOUND** endpoints → **CRITICAL**: "Schema defines `<METHOD> <path>` but no matching route found"

   ### 4c. Layer 2 — Request/response field comparison

   For `FOUND` endpoints, perform deeper comparison:
   - Read the route handler function
   - Compare schema-defined request fields against code's input handling
     - Missing required field in code → WARNING
     - Extra field in code not in schema → INFO (suggest schema update)
     - Type mismatch → WARNING
   - Compare schema-defined response fields against code's output
     - Missing response field → WARNING
     - Extra undocumented field → INFO

   Record findings as:
   ```
   { dimension: "D2", severity, schema_file, endpoint, field_name, finding, suggestion }
   ```

   **Code-first mode** (no standalone schema files, but code-first framework detected):

   ### 4d. Build Pydantic Model registry

   Use Grep to find all Pydantic model definitions:
   ```
   pattern: class \w+\(.*BaseModel.*\):
   ```

   For each discovered model:
   - Read the source file
   - Extract field definitions:
     - Typed fields with Field(): `field_name: type = Field(...)` → parse Field() parameters
     - Bare typed fields: `field_name: type` → record with empty Field metadata
   - Extract Field() parameters when present:
     - `description=` → human-readable description
     - `examples=` / `example=` → example values
     - `ge=/gt=/lt=/le=` → numeric constraints
     - `min_length=/max_length=` → string length constraints
     - `pattern=` → regex validation pattern
   - Detect nested model references:
     - `List[X]`, `Optional[X]`, `Union[X, Y]` → extract inner type names
     - `Dict[str, X]` → extract value type name
     - Cross-reference inner type names against MODEL_REGISTRY
   - Skip fields with default values that are not Field() calls (e.g., `field: str = "default"`)

   Build `MODEL_REGISTRY`:
   ```
   { model_name, source_file, fields: [{ name, type, field_params: { description?, examples?, constraints? } }], nested_refs: [type_name] }
   ```

   ### 4e. Route metadata extraction & consistency checks

   Use Grep to find all FastAPI route decorators:
   ```
   pattern: @\w+\.(get|post|put|delete|patch|options|head)\s*\(\s*["'][^"']+["']
   ```
   Also scan for `add_api_route(` calls.

   For each route, extract metadata from the decorator and handler function:
   - HTTP method (from decorator name)
   - URL path (first positional argument)
   - Keyword arguments: `response_model`, `status_code`, `responses`, `tags`, `summary`, `description`, `response_model_include`, `response_model_exclude`, `response_model_exclude_unset`
   - Return type annotation from handler: `def handler(...) -> SomeType:`
   - Handler function docstring (triple-quoted string immediately after def)

   Perform the following checks for each route:

   | Check | Condition | Severity |
   |-------|-----------|----------|
   | Missing response model | No `response_model=` AND no `-> Type` return annotation (or `-> None` / `-> dict`) | WARNING |
   | status_code/body conflict | `status_code` is 204 or 304 AND has non-None `response_model` | ERROR |
   | Undocumented HTTPException | Handler body contains `raise HTTPException(status_code=N)` but `responses=` dict does not include N | WARNING |
   | Schema filtering mismatch | Route uses `response_model_include`, `response_model_exclude`, or `response_model_exclude_unset` | WARNING |
   | No tags | Route decorator has no `tags=` parameter | INFO |
   | No summary/description | No `summary=` or `description=` parameter AND no handler docstring | INFO |

   Record findings as:
   ```
   { dimension: "D2", severity, route, check_type, finding, suggestion }
   ```

   ### 4f. Pydantic Model quality checks

   For each model in `MODEL_REGISTRY`:

   | Check | Condition | Severity |
   |-------|-----------|----------|
   | Missing Field description | Field uses `Field()` but no `description=` parameter | INFO |
   | Missing Field examples | Field uses `Field()` but no `examples=` or `example=` parameter | INFO |
   | Unknown type reference | Field type is not a Python built-in AND not found in MODEL_REGISTRY | WARNING |
   | Circular dependency | Model A references B, B references A (direct or transitive chain) | WARNING |

   For circular dependency detection:
   - Build a directed graph from MODEL_REGISTRY's nested_refs
   - Detect cycles via depth-first traversal
   - Report the full cycle chain (e.g., "Order → OrderItem → Order")

   Record findings as:
   ```
   { dimension: "D2", severity, model_name, field_name?, check_type, finding, suggestion }
   ```

5. **D3 — Tests ↔ Code consistency**

   If `TEST_FILES` is empty → skip D3, add informational note "No test files found".

   ### 5a. Extract test targets

   For each file in `TEST_FILES`:
   - Read the file content
   - Extract test targets:

   | Target Type | Pattern |
   |-------------|---------|
   | HTTP endpoint | `(GET|POST|PUT|DELETE|PATCH)\s+['"]/[\w/:{}-]+` or `request\(app\)\.(get|post|put|delete|patch)\(['"]/path` |
   | Function/module | `describe\(['"](\w+)`, `it\(['"](\w+)`, `def test_(\w+)`, `func Test(\w+)`, `@pytest` |
   | Expected status | `expect.*status.*toBe\((\d+)\)`, `assert.*status_code\s*==\s*(\d+)`, `\.Status(\d+)` |

   Collect into `TEST_TARGETS`:
   ```
   { test_file, target_type, target_name, expected_status?, line_number }
   ```

   ### 5b. Layer 1 — Target existence verification

   For each target in `TEST_TARGETS`:
   - **Endpoint targets**: Grep for matching route in source code
   - **Function targets**: Grep for function/class definition in source code
   - Classify: `FOUND` / `NOT_FOUND` / `UNCERTAIN`

   **NOT_FOUND targets** → **CRITICAL**: "Test references `<target>` but no matching implementation found (orphaned test)"

   ### 5c. Layer 2 — Scenario coverage assessment

   For each test file, assess coverage:
   - Identify what scenarios the tests cover (happy path, error cases, edge cases)
   - If `DOC_FILES` or spec files contain WHEN/THEN scenarios:
     - For each WHEN/THEN scenario, check if a corresponding test exists
     - Missing coverage → INFO: "Scenario `<description>` not covered by tests"
   - Identify tests that only cover happy paths but code has error handling → INFO suggesting error scenario tests

   Record findings as:
   ```
   { dimension: "D3", severity, test_file, target, finding, suggestion }
   ```

6. **OpenSpec incremental verification (conditional)**

   Run:
   ```bash
   openspec list --json
   ```

   Parse the JSON. If `changes` array is non-empty, for each active change:

   ### 6a. Read change artifacts

   Read the change's:
   - `proposal.md` — extract all verifiable claims (same patterns as D1)
   - `design.md` — extract file path references and technical decisions
   - `specs/*/spec.md` — extract WHEN/THEN scenarios as verifiable requirements

   ### 6b. Verify claims against change scope

   Determine the change's code scope:
   ```bash
   git diff main..HEAD --name-only
   ```

   For each extracted claim:
   - Verify the claim is satisfied within the change scope
   - Check if WHEN/THEN scenarios have corresponding code in the diff
   - Check if test files in the diff cover the change's spec scenarios

   ### 6c. Append findings

   Add change-level findings to the main findings list, tagged with:
   ```
   { dimension: "OpenSpec", change_name, severity, source_artifact, finding, suggestion }
   ```

7. **Generate diagnostic report**

   Compile all findings from D1, D2, D3, and OpenSpec incremental into a structured report.

   ### 7a. Summary table

   Count findings per dimension and severity:
   ```
   | Dimension | Findings | CRITICAL | WARNING | INFO |
   |-----------|----------|----------|---------|------|
   | D1 Doc ↔ Code      | N | X | Y | Z |
   | D2 Schema ↔ API    | N | X | Y | Z |
   | D3 Tests ↔ Code    | N | X | Y | Z |
   | OpenSpec Incremental| N | X | Y | Z |
   ```

   ### 7b. Detailed findings

   Group by dimension, sorted by severity (CRITICAL first):

   ```
   #### D1: Doc ↔ Code

   ##### CRITICAL: <finding summary>
   - **Source**: <file>:<line>
   - **Claim**: <what the doc says>
   - **Verification**: <what was found/not found>
   - **Suggestion**: <how to fix>

   ##### WARNING: <finding summary>
   ...

   ##### INFO: <finding summary>
   ...
   ```

   Repeat for D2, D3, and OpenSpec incremental.

   ### 7c. Skipped dimensions

   For any skipped dimension (no files found), note:
   - "D2: Skipped — no API schema files found and no code-first framework detected"
   - "D2: Schema-file mode (X endpoints checked)" or "D2: Code-first mode (X routes, Y models checked)"
   - "D3: Skipped — no test files found"

**Output On Success**

```
# Implementation Consistency Diagnostic Report

## Summary

| Dimension | Findings | CRITICAL | WARNING | INFO |
|-----------|----------|----------|---------|------|
| D1 Doc ↔ Code       | N | X | Y | Z |
| D2 Schema ↔ API     | N | X | Y | Z |
| D3 Tests ↔ Code     | N | X | Y | Z |
| OpenSpec Incremental | N | X | Y | Z |

## Detailed Findings

### D1: Doc ↔ Code
(grouped by severity)

### D2: Schema ↔ API Code
(grouped by severity)

### D3: Tests ↔ Code
(grouped by severity)

### OpenSpec Incremental (if applicable)
(grouped by change name, then severity)

## Skipped Dimensions
(list of dimensions skipped with reasons)
```

**Error Output Format**

```
## Error: <error-type>

**Step:** <which step failed>
**Reason:** <why it failed>

**Recovery:**
- <suggestion 1>
- <suggestion 2>
```

**Guardrails**
- Pure diagnostic tool — NEVER modify any files
- No pass/fail judgment — only report findings with severity levels
- No auto-fix — only suggest remediation actions
- Read-only access to all source code, docs, schemas, and tests
- If a dimension has no relevant files (e.g., no schema files), skip it gracefully with an informational note
- OpenSpec incremental verification is additive — it supplements project-level findings, never replaces them
- When unable to determine tech stack, fall back to generic pattern matching across all supported frameworks
