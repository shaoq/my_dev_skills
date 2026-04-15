## ADDED Requirements

### Requirement: Dependencies stored in independent YAML file
Dependencies between OpenSpec changes SHALL be stored in a dedicated `openspec/changes/<name>/dependencies.yaml` file rather than a `## Dependencies` section in `proposal.md`. The file SHALL only be created when a change has dependencies. Files with no dependencies SHALL NOT have a `dependencies.yaml` file.

#### Scenario: Change with dependencies
- **WHEN** `parall-new-proposal` creates a change that depends on other changes
- **THEN** a file `openspec/changes/<name>/dependencies.yaml` is created with YAML format: `dependencies:` list containing kebab-case change names

#### Scenario: Change without dependencies
- **WHEN** `parall-new-proposal` creates a change with no dependencies (Wave 1 member)
- **THEN** no `dependencies.yaml` file is created

### Requirement: parall-new-proposal writes dependencies.yaml
`parall-new-proposal` Step 6 SHALL create `dependencies.yaml` instead of editing `proposal.md`. The Step 6.2 format spec SHALL describe YAML format (2-space indented list under `dependencies:` key). Step 6.3 SHALL skip file creation instead of skipping proposal.md modification. The Guardrails SHALL reference `dependencies.yaml` instead of `## Dependencies` section.

#### Scenario: Inject dependencies after proposal creation
- **WHEN** `parall-new-proposal` completes Step 5 batch creation for a change with dependencies
- **THEN** the skill writes `openspec/changes/<name>/dependencies.yaml` using the Write tool (not Edit on proposal.md)

#### Scenario: Error message references correct file
- **WHEN** a dependency-related error occurs in Step 7.2
- **THEN** the failure suggestion says "check dependencies.yaml file" (not "check proposal.md ## Dependencies section")

### Requirement: parall-new-worktree-apply reads dependencies.yaml
`parall-new-worktree-apply` Step 2.1 SHALL read `dependencies.yaml` to parse dependencies instead of reading `proposal.md`. The parsing logic SHALL: (1) test file existence, (2) if exists parse YAML dependencies list, (3) if not exists treat as no dependencies. Error messages in Steps 2.2 and 2.3 SHALL reference `dependencies.yaml`.

#### Scenario: Parse dependencies from YAML
- **WHEN** `parall-new-worktree-apply` encounters a change with `dependencies.yaml`
- **THEN** it reads the file and extracts the `dependencies` list as dependency names

#### Scenario: No dependencies file
- **WHEN** `parall-new-worktree-apply` encounters a change without `dependencies.yaml`
- **THEN** the change is treated as having no dependencies

#### Scenario: Error messages reference correct file
- **WHEN** dependency validation fails in Step 2.2 or circular dependency is detected in Step 2.3
- **THEN** error messages say "check dependencies.yaml" (not "check proposal.md ## Dependencies section")

### Requirement: check-changes-completed reads dependencies.yaml
`check-changes-completed` Dimension 4 SHALL read `dependencies.yaml` instead of using `sed` to parse `proposal.md`. The YAML parsing SHALL replace the current `sed -n '/^## Dependencies/,/^## /p' | grep -oE '\b[a-z][a-z0-9-]*\b'` approach. The empty-dependency check SHALL test file existence instead of section emptiness.

#### Scenario: Parse dependencies from YAML in diagnostic
- **WHEN** `check-changes-completed` runs Dimension 4 check on a change
- **THEN** it reads `dependencies.yaml` if it exists, and uses the YAML dependencies list (no sed/grep regex parsing)

#### Scenario: No false positive matches
- **WHEN** a proposal.md contains the word "Dependencies" in prose text
- **THEN** Dimension 4 does NOT incorrectly identify it as a dependency declaration
