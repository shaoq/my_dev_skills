---
name: verify-impl-consistency
description: "Deep consistency verification between docs, API schema, and integration tests vs actual code implementation. Runs project-level diagnostics with no arguments, or incremental verification for exactly one explicitly selected active OpenSpec change and target baseline. Pure diagnostic tool (no pass/fail judgment, no auto-fix)."
argument-hint: "[<change-name> --base <target-branch>]"
allowed-tools: Bash(openspec *) Bash(git *) Read Glob Grep AskUserQuestion
---

Deep consistency verification between documentation, API schema, and integration tests vs actual code. Two-layer strategy: precise matching then semantic analysis. Pure diagnostic — reports findings only, no modifications.

**Input**: Either no arguments for project-level D1/D2/D3, or exactly one active change plus an explicit
local baseline: `/verify-impl-consistency <change-name> --base <target-branch>`.

Examples:

```text
/verify-impl-consistency
/verify-impl-consistency add-auth --base develop
```

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

   Then parse the complete original argument vector with this closed grammar:

   - No arguments: set `MODE=project-level`. Do not resolve a baseline, run `openspec list`, or select a
     change. 不得自动选择 active change。
   - Exactly `<change-name> --base <target-branch>`: set `MODE=change-scoped`,
     `SELECTED_CHANGE=<change-name>`, `BASE_BRANCH=<target-branch>`.
   - Reject an isolated `--base`, missing option value, repeated positional change, duplicate or
     重复的 `--base`, an unknown option（未知选项）, an extra positional argument, or either ordering/
     spelling outside the grammar. Report the exact offending argument and perform no change-scoped work.

   In `MODE=change-scoped`, before any baseline query prove `SELECTED_CHANGE` is one exact active directory
   `openspec/changes/<change-name>/` and is not `archive`, absent, ambiguous, or archive-only. Do not infer a
   similarly named change. Then require the explicit local ref and freeze both commits once:

   ```bash
   git rev-parse --verify --quiet refs/heads/<BASE_BRANCH>
   BASE_HEAD=$(git rev-parse refs/heads/<BASE_BRANCH>)
   CURRENT_HEAD=$(git rev-parse HEAD)
   git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>
   ```

   Never fetch, guess `main`, use `origin/HEAD`, substitute a merge base, or re-resolve the branch for an
   individual dimension. If the local branch is absent, stop change-scoped verification with the exact ref
   error. If the ancestor check fails, continue project-level D1/D2/D3 but mark OpenSpec incremental as
   `not executed: BASE_HEAD is not an ancestor of CURRENT_HEAD`.

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
   - Files under `openspec/changes/**`; a selected change's artifacts are added only by Step 6
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

   ### 5d. Spec-grounded assertion verification (conditional)

   **Prerequisite**: This step executes ONLY when spec files (from `DOC_FILES` or OpenSpec change specs) contain WHEN/THEN scenarios. If no WHEN/THEN scenarios are found → skip this step with informational note "No spec scenarios found for assertion verification".

   **Overview**: Extract quantifiable expected values from spec THEN clauses → match against actual test assertions → report deviations graded by severity.

   #### 5d-i. Extract spec expected values

   For each WHEN/THEN scenario found in spec files:

   Apply structured extraction rules to the THEN clause:

   **Status code extraction**:
   ```
   Pattern: (returns?|返回|responds?\s+with)\s+(status\s+)?(\d{3})
   Extract: expected_status = <3-digit number>
   ```

   **Response field extraction**:
   ```
   Pattern: (returns?|返回|response\s+contains?)\s*\{([^}]+)\}
   Extract: expected_fields = [split by comma, trim whitespace]
   Also match: "returns field <name>", "returns <name> and <name2>"
   ```

   **Error type extraction**:
   ```
   Pattern: (throws?|raises?|抛出)\s+(\w+Error|\w+Exception)
   Extract: expected_error = <Error/Exception name>
   ```

   **Fallback**: When no pattern matches → store full THEN text as `expected_behavior` (free text) for Layer 2 semantic analysis.

   Collect into `SPEC_EXPECTATIONS`:
   ```
   { spec_source, scenario_name, expected_status?, expected_fields?, expected_error?, expected_behavior? }
   ```

   #### 5d-ii. Match test assertions against spec expectations

   For each entry in `SPEC_EXPECTATIONS`, locate the corresponding test (by matching scenario context from 5c coverage results):

   **Status code comparison**:
   - Test asserts same status as expected → `ALIGNED`
   - Test asserts different status than expected → `CRITICAL`: "Test asserts status <actual> but spec expects <expected>"

   **Response field comparison**:
   - Test asserts all expected fields → `ALIGNED`
   - Test asserts subset of expected fields → `WARNING`: "Test verifies partial spec expectations (<found>), missing: <missing_fields>"

   **Error type comparison**:
   - Test asserts same error type as expected → `ALIGNED`
   - Test asserts different error type or no error → `CRITICAL`: "Test expects <actual_error> but spec requires <expected_error>"

   **Extra assertions**: Test contains assertions for fields/values not mentioned in spec → `INFO` (not a problem, just noted): "Test verifies additional behavior beyond spec: <description>"

   **Unstructured expectations**: For `expected_behavior` entries → use Layer 2 semantic analysis: Read the test code and assess whether it verifies the described behavior. Classify as `ALIGNED` or `UNCERTAIN`.

   Record findings as:
   ```
   { dimension: "D3", sub_dimension: "spec-grounded", severity, spec_source, scenario_name, expected, actual, finding, suggestion }
   ```

6. **OpenSpec incremental verification (explicit and conditional)**

   Run this step only when `MODE=change-scoped` and the Step 1 ancestry check passed. In
   `MODE=project-level`, record `not executed: no change selected; no change-scoped baseline required` and
   do not inspect active-change artifacts. Never loop over `openspec list` or include unselected active
   changes.

   ### 6a. Read change artifacts

   Read only `SELECTED_CHANGE`'s:
   - `proposal.md` — extract all verifiable claims (same patterns as D1)
   - `design.md` — extract file path references and technical decisions
   - `specs/*/spec.md` — extract WHEN/THEN scenarios as verifiable requirements

   ### 6b. Verify claims against change scope

   Determine the selected change's implementation scope using only the frozen commit pair:
   ```bash
   git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only
   ```

   For each extracted claim:
   - Verify the claim is satisfied within that exact change scope
   - Check if WHEN/THEN scenarios have corresponding code in the frozen diff
   - Check if test files in the frozen diff cover the selected change's spec scenarios
   - Feed the selected change's scenarios into Step 5d spec-grounded assertion verification; documentation,
     implementation, test coverage, and assertions must all use the same `<BASE_HEAD>..<CURRENT_HEAD>`
     attribution boundary

   Project-level D1/D2/D3 always remain whole-repository diagnostics; `--base` MUST NOT crop their discovery
   sets or rewrite their findings.

   ### 6c. Append findings

   Add selected change-level findings to the main findings list, tagged with:
   ```
   { dimension: "OpenSpec", change_name, severity, source_artifact, finding, suggestion }
   ```

7. **Finalize baseline evidence and generate diagnostic report**

   Before reporting, in change-scoped mode resolve both moving endpoints one final time, only for stability
   comparison:

   ```bash
   OBSERVED_BASE_HEAD=$(git rev-parse refs/heads/<BASE_BRANCH>)
   OBSERVED_CURRENT_HEAD=$(git rev-parse HEAD)
   ```

   Do not recompute findings. Report `target stability=stable|drifted|unknown` by comparing
   `OBSERVED_BASE_HEAD` to `BASE_HEAD`, and `current stability=stable|drifted|unknown` by comparing
   `OBSERVED_CURRENT_HEAD` to `CURRENT_HEAD`. Any difference or failed final resolution marks all frozen
   incremental results as `stale evidence`; retain the original findings and exact frozen range as diagnostic
   evidence. This tool remains read-only and does not retry against new commits.

   Compile all findings from D1, D2, D3, and OpenSpec incremental into a structured report.

   ### 7a. Baseline evidence

   Always state `MODE` and parameter source. In change-scoped mode report:

   ```text
   Selected change: <SELECTED_CHANGE> (explicit positional argument)
   Target branch: <BASE_BRANCH> (explicit --base)
   BASE_HEAD: <frozen commit>
   CURRENT_HEAD: <frozen commit>
   Comparison range: <BASE_HEAD>..<CURRENT_HEAD>
   Target stability: <stable|drifted|unknown> (observed: <hash|unavailable>)
   Current stability: <stable|drifted|unknown> (observed: <hash|unavailable>)
   Evidence status: <current|stale evidence|incremental not executed>
   ```

   If `BASE_HEAD == CURRENT_HEAD`, explicitly report an empty comparison range and do not invent delivered
   files, commits, or tests. On non-ancestry, include both frozen commits and why incremental was not executed.
   In project-level mode state that no change was selected and no change-scoped baseline was required.

   ### 7b. Summary table

   Count findings per dimension and severity:
   ```
   | Dimension | Findings | CRITICAL | WARNING | INFO | Assertion Drift |
   |-----------|----------|----------|---------|------|-----------------|
   | D1 Doc ↔ Code      | N | X | Y | Z | — |
   | D2 Schema ↔ API    | N | X | Y | Z | — |
   | D3 Tests ↔ Code    | N | X | Y | Z | D (spec-grounded) |
   | OpenSpec Incremental| N | X | Y | Z | — |
   ```

   The "Assertion Drift" column counts findings from Step 5d (spec-grounded assertion verification). Use `—` for dimensions that do not perform assertion checking.

   ### 7c. Detailed findings

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

   **D3 additional sub-section** (when Step 5d was executed):

   ```
   ##### Spec-grounded Assertion Verification

   ###### CRITICAL: Test asserts wrong status code
   - **Spec**: <spec_source> — scenario "<name>"
   - **Expected**: status <expected>
   - **Actual**: test asserts status <actual>
   - **Suggestion**: Update test to assert status <expected> per spec

   ###### WARNING: Test verifies partial spec expectations
   - **Spec**: <spec_source> — scenario "<name>"
   - **Expected fields**: <field_list>
   - **Verified**: <found_fields>
   - **Missing**: <missing_fields>
   - **Suggestion**: Add assertions for missing fields

   ###### INFO: Test verifies extra behavior beyond spec
   - **Spec**: <spec_source> — scenario "<name>"
   - **Extra assertions**: <description>
   ```

   ### 7d. Skipped dimensions

   For any skipped dimension (no files found), note:
   - "D2: Skipped — no API schema files found and no code-first framework detected"
   - "D2: Schema-file mode (X endpoints checked)" or "D2: Code-first mode (X routes, Y models checked)"
   - "D3: Skipped — no test files found"
   - "D3 Step 5d: Skipped — no spec scenarios found for assertion verification"
   - "D3 Step 5d: N scenarios checked, M assertion drifts found"

**Output On Success**

```
# Implementation Consistency Diagnostic Report

## Baseline Evidence

(mode, explicit selection/baseline, frozen range, and final stability)

## Summary

| Dimension | Findings | CRITICAL | WARNING | INFO | Assertion Drift |
|-----------|----------|----------|---------|------|-----------------|
| D1 Doc ↔ Code       | N | X | Y | Z | — |
| D2 Schema ↔ API     | N | X | Y | Z | — |
| D3 Tests ↔ Code     | N | X | Y | Z | D (spec-grounded) |
| OpenSpec Incremental | N | X | Y | Z | — |

## Detailed Findings

### D1: Doc ↔ Code
(grouped by severity)

### D2: Schema ↔ API Code
(grouped by severity)

### D3: Tests ↔ Code
(grouped by severity)

#### Spec-grounded Assertion Verification (if applicable)
(CRITICAL: assertion contradicts spec → WARNING: partial coverage → INFO: extra assertions)

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
- OpenSpec incremental verification runs for exactly one explicitly selected active change; unselected active
  changes are neither read nor included in change-scoped conclusions
- `--base` is valid only with one explicit change; no argument mode never guesses a baseline or active change
- Every incremental Git query uses the frozen `<BASE_HEAD>..<CURRENT_HEAD>` pair; never use a branch name,
  literal `HEAD`, fixed `main`, or a synthesized merge base in that range
- Non-ancestor baseline means incremental not executed; endpoint drift means stale evidence
- When unable to determine tech stack, fall back to generic pattern matching across all supported frameworks
