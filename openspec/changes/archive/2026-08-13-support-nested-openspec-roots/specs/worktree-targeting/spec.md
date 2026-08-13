## ADDED Requirements

### Requirement: New worktree apply selects an explicit OpenSpec project root
`new-worktree-apply` SHALL accept at most one optional
`--openspec-root <repo-relative-directory>` in addition to its proposal and optional
`--target`. The value SHALL identify the Git-worktree-relative directory that directly
contains `openspec/`; omission SHALL be equivalent to `--openspec-root .`. The workflow
MUST validate the lexical and physical path, bind the normalized root and complete
repository-relative change prefix to confirmation, build the immutable artifact manifest
with that prefix, and run OpenSpec status/apply from the corresponding project directory in
the invocation and source worktrees. It MUST NOT discover, guess, or fall back to another
OpenSpec project.

#### Scenario: Existing root-level invocation remains compatible
- **WHEN** the user invokes `new-worktree-apply add-user-auth` and the proposal exists at `openspec/changes/add-user-auth`
- **THEN** the workflow records `OPENSPEC_ROOT=.`, uses `openspec/changes/add-user-auth` without a `./` prefix, and preserves the existing root-project behavior

#### Scenario: Explicit dot matches the default
- **WHEN** the same repository and proposal are invoked with `--openspec-root .`
- **THEN** the normalized project directory, change prefix, artifact manifest paths, digest inputs, and OpenSpec working directory are identical to the omitted-option invocation

#### Scenario: Nested OpenSpec project is selected
- **WHEN** the user invokes `new-worktree-apply add-user-auth --openspec-root twin-rag` and `twin-rag/openspec/changes/add-user-auth` exists
- **THEN** the workflow uses `twin-rag` as the OpenSpec CLI working directory and prefixes every manifest path with `twin-rag/openspec/changes/add-user-auth`

#### Scenario: OpenSpec root arguments are invalid
- **WHEN** `--openspec-root` is repeated, lacks a value, or is combined with otherwise invalid positional or unknown options
- **THEN** the workflow reports an argument error and performs no Git write or OpenSpec apply action

#### Scenario: OpenSpec root path is unsafe
- **WHEN** the value is absolute, begins with `~`, contains backslashes, whitespace, control characters, empty path segments, `.` or `..` segments, leading or trailing slash, or consecutive slashes
- **THEN** the workflow rejects it before target selection and performs no Git write

#### Scenario: Physical project path escapes the invocation worktree
- **WHEN** resolving the selected directory, its `openspec` directory, or its proposal directory traverses a symbolic link outside the invocation worktree or selected project boundary
- **THEN** the workflow fails closed without searching for another project or changing any Git state

#### Scenario: Selected project or proposal does not exist
- **WHEN** the normalized project directory, its `openspec` directory, or `openspec/changes/<proposal>` cannot be read
- **THEN** the workflow stops and reports the exact selected path without trying root-level or recursively discovered alternatives

#### Scenario: Confirmation binds the selected project
- **WHEN** read-only preflight succeeds for a selected OpenSpec project
- **THEN** the confirmation summary includes whether the option was explicit, the normalized root, invocation project directory, expected source project directory, repository-relative change prefix, manifest paths, and manifest digest

#### Scenario: Selected project changes while awaiting confirmation
- **WHEN** argument parsing, normalized or physical project paths, containment results, OpenSpec status, change prefix, manifest paths, blobs, digest, or target snapshot differs during pre-write revalidation
- **THEN** the prior confirmation is invalidated and no write occurs until the updated summary is explicitly confirmed

#### Scenario: Source project context is verified before apply
- **WHEN** the canonical source worktree is created from the confirmed target hash
- **THEN** the workflow verifies the source project remains inside that worktree, rechecks OpenSpec status and every repository-relative manifest blob, and invokes apply only from the verified source project directory

#### Scenario: Source project verification fails after creation
- **WHEN** the source project directory is missing, escapes its worktree, has incomplete OpenSpec artifacts, or differs from the confirmed target manifest
- **THEN** apply does not start and the canonical source branch and worktree are preserved without cleanup, root substitution, or creation retry

#### Scenario: Task backfill uses both project and repository contexts
- **WHEN** apply completes and the workflow reconciles `tasks.md`
- **THEN** it reads tasks from the selected source OpenSpec project, stages changes from the source worktree root, and force-adds the repository-relative `<CHANGE_PREFIX>/tasks.md`
