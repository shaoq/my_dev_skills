## ADDED Requirements

### Requirement: Pydantic Model registry construction
The skill SHALL scan all source files for Pydantic `BaseModel` subclass definitions and build a `MODEL_REGISTRY` containing: model name, source file, field names, field types, and `Field()` parameters (description, examples, constraints).

#### Scenario: BaseModel discovered with Field metadata
- **WHEN** source code contains `class UserCreate(BaseModel):` with fields `name: str = Field(description="User name")` and `email: str`
- **THEN** skill SHALL add entry to MODEL_REGISTRY with model_name="UserCreate", fields containing name/email with their types, and description for name field

#### Scenario: BaseModel with no Field() calls
- **WHEN** source code contains `class Item(BaseModel):` with bare field `title: str` (no `Field()`)
- **THEN** skill SHALL still register the model with field_name="title", field_type="str", and empty Field parameters

#### Scenario: Nested model reference
- **WHEN** model `Order` contains field `items: List[OrderItem]` where `OrderItem` is another BaseModel
- **THEN** skill SHALL record the type reference and verify `OrderItem` exists in MODEL_REGISTRY

### Requirement: Route metadata extraction for FastAPI
The skill SHALL extract route decorator metadata from FastAPI source code, including: HTTP method, URL path, `response_model`, `status_code`, `responses`, `tags`, `summary`, `description`, `response_model_include`, `response_model_exclude`, `response_model_exclude_unset`.

#### Scenario: Route with response_model
- **WHEN** code contains `@router.post("/users", response_model=UserOut, status_code=201)`
- **THEN** skill SHALL extract: method=POST, path=/users, response_model=UserOut, status_code=201

#### Scenario: Route with no response_model
- **WHEN** code contains `@app.get("/health")` with no `response_model=` parameter and no return type annotation
- **THEN** skill SHALL flag the route as missing response_model

#### Scenario: Route with return type annotation as implicit response_model
- **WHEN** code contains `def get_user(user_id: int) -> UserResponse:` without explicit `response_model=`
- **THEN** skill SHALL recognize `UserResponse` as the implicit response model and NOT flag as missing

### Requirement: Route-to-model consistency checks
The skill SHALL verify consistency between route declarations and actual code behavior for each discovered route.

#### Scenario: status_code conflicts with response body
- **WHEN** route declares `status_code=204` with non-None `response_model`
- **THEN** skill SHALL report ERROR: "status_code 204 (No Content) should not have a response body"

#### Scenario: Undocumented HTTPException
- **WHEN** handler function body contains `raise HTTPException(status_code=404)` but route decorator has no `responses={404: ...}`
- **THEN** skill SHALL report WARNING: "Handler raises HTTPException(404) but route does not document 404 response"

#### Scenario: response_model_include or exclude causes schema inaccuracy
- **WHEN** route uses `response_model_include={"id", "name"}` or `response_model_exclude={"password"}` or `response_model_exclude_unset=True`
- **THEN** skill SHALL report WARNING: "response_model filtering parameter used — OpenAPI schema will not reflect runtime filtering"

#### Scenario: No tags on route
- **WHEN** route decorator has no `tags=` parameter
- **THEN** skill SHALL report INFO: "Route has no tags — consider adding for API documentation grouping"

#### Scenario: No summary or description
- **WHEN** route decorator has no `summary=` or `description=` and handler function has no docstring
- **THEN** skill SHALL report INFO: "Route lacks summary and description — generated schema will use auto-generated defaults"

### Requirement: Pydantic Model quality checks
The skill SHALL verify quality of Pydantic models registered in MODEL_REGISTRY.

#### Scenario: Field missing description
- **WHEN** model field uses `Field()` without `description=` parameter
- **THEN** skill SHALL report INFO: "Field '<field_name>' in model '<model_name>' lacks description"

#### Scenario: Field missing examples
- **WHEN** model field uses `Field()` without `examples=` or `json_schema_extra` containing example data
- **THEN** skill SHALL report INFO: "Field '<field_name>' in model '<model_name>' lacks examples"

#### Scenario: Unknown type reference
- **WHEN** model field references a type that is not a built-in type and not found in MODEL_REGISTRY
- **THEN** skill SHALL report WARNING: "Field '<field_name>' in model '<model_name>' references unknown type '<type_name>'"

#### Scenario: Circular model dependency
- **WHEN** model A references model B which references model A (direct or transitive)
- **THEN** skill SHALL report WARNING: "Circular dependency detected: <model_chain>"
