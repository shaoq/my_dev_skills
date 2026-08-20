## ADDED Requirements

### Requirement: One source skill is discoverable in Codex and Claude Code

The project SHALL maintain one repository-root `openspec-review-change/` skill source that is valid and discoverable in both Codex and Claude Code. Its shared `SKILL.md` frontmatter SHALL use the cross-runtime field subset, while Codex-specific presentation metadata SHALL live in `agents/openai.yaml`.

#### Scenario: Shared SKILL frontmatter is validated
- **WHEN** the skill is validated for both runtimes
- **THEN** `SKILL.md` uses `name`, `description`, and `allowed-tools` without relying on runtime-exclusive frontmatter fields

#### Scenario: Codex metadata is generated
- **WHEN** the skill is initialized and validated for Codex
- **THEN** `agents/openai.yaml` contains quoted `display_name`, `short_description`, and a quoted `default_prompt` that explicitly invokes `$openspec-review-change`

#### Scenario: Claude Code invocation is used
- **WHEN** a Claude Code user invokes `/openspec-review-change [change-name]`
- **THEN** Claude Code discovers the shared skill and starts the documented review workflow

#### Scenario: Codex invocation is used
- **WHEN** a Codex user invokes `$openspec-review-change [change-name]`
- **THEN** Codex discovers the shared skill and starts the same documented review workflow

#### Scenario: Natural-language request matches the skill
- **WHEN** a user asks either runtime to review the quality or implementation readiness of an OpenSpec proposal
- **THEN** the skill description is specific enough to select `openspec-review-change`

#### Scenario: Unrelated code review request is made
- **WHEN** a user asks to review a pull request or source-code diff without asking for OpenSpec proposal review
- **THEN** the skill description does not claim that unrelated code-review task

### Requirement: Installer manages skill links for both runtimes independently

The setup installer SHALL discover each repository-root custom skill once and install it as a symbolic link in both `~/.claude/skills` and `~/.codex/skills`. Each runtime target SHALL retain the existing safe conflict behavior and SHALL be processed independently so that a conflict in one runtime does not prevent work in the other.

#### Scenario: First installation creates both links
- **WHEN** neither runtime contains a target for a discovered custom skill
- **THEN** installation creates one link in each runtime skill directory pointing to the same repository source

#### Scenario: Correct link already exists
- **WHEN** a runtime target is already a symbolic link to the discovered source
- **THEN** installation skips that target and reports it as already correct

#### Scenario: Wrong symbolic link exists
- **WHEN** a runtime target is a symbolic link to a different source
- **THEN** installation replaces that link with the discovered source link and reports the replacement

#### Scenario: Regular file or directory conflicts
- **WHEN** a runtime target exists as a regular file or directory
- **THEN** installation preserves it, emits a warning for that runtime, and continues processing the other runtime and other skills

#### Scenario: Runtime results are summarized separately
- **WHEN** dual-runtime installation finishes
- **THEN** the output distinguishes created, skipped, replaced, and conflicted targets for Claude Code and Codex

### Requirement: Uninstaller removes only owned links from both runtimes

The setup uninstaller SHALL inspect both runtime skill directories and remove a custom-skill target only when it is a symbolic link resolving to the corresponding repository source.

#### Scenario: Owned links exist in both runtimes
- **WHEN** both runtime targets resolve to the repository source
- **THEN** uninstallation removes both links and reports each removal

#### Scenario: Foreign link exists in one runtime
- **WHEN** one runtime target is a symbolic link to another source
- **THEN** uninstallation preserves the foreign link, warns for that runtime, and still removes an owned link in the other runtime

#### Scenario: Regular file or directory exists
- **WHEN** a runtime target is a regular file or directory
- **THEN** uninstallation preserves the target and reports that it is unmanaged

### Requirement: Setup grants required Claude command permissions without overwriting Codex configuration

The setup workflow SHALL include `openspec validate` in its standard Claude Code command permissions needed by proposal review. It SHALL continue to merge Claude settings safely and SHALL NOT write or replace Codex configuration merely to install file-system skill links.

#### Scenario: Claude settings are installed
- **WHEN** the user runs setup installation
- **THEN** the merged Claude allow-list contains the existing OpenSpec commands plus `Bash(openspec validate:*)`

#### Scenario: Existing Claude settings are present
- **WHEN** the Claude settings file already contains unrelated permissions or configuration
- **THEN** setup preserves them while adding only missing standard permissions

#### Scenario: Codex skill links are installed
- **WHEN** setup installs or updates Codex skill links
- **THEN** it does not create, replace, or merge a Codex configuration file

### Requirement: Dual-runtime installer tests are isolated from real user configuration

Installer regression tests SHALL run with temporary home and repository fixtures and MUST NOT depend on or mutate the operator's real `~/.claude`, `~/.codex`, or other user configuration.

#### Scenario: Installation regression suite runs
- **WHEN** the dual-runtime installer tests execute
- **THEN** they cover creation, idempotent skip, wrong-link replacement, regular-target preservation, independent runtime continuation, and per-runtime summaries under a temporary home

#### Scenario: Uninstallation regression suite runs
- **WHEN** the dual-runtime uninstaller tests execute
- **THEN** they cover owned-link removal and preservation of foreign links, regular files, and directories under a temporary home

#### Scenario: Tests finish or fail
- **WHEN** any installer test terminates
- **THEN** the real Claude Code and Codex skill directories and configuration files remain byte-for-byte unchanged
