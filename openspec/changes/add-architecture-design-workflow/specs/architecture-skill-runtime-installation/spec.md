## ADDED Requirements

### Requirement: Claude Code and Codex share one skill source
The implementation SHALL maintain one root `architecture-design-workflow/` source directory and SHALL expose that directory to both Claude Code and Codex through the repository's existing managed installation mechanism.

#### Scenario: Skill installation succeeds
- **WHEN** the repository installer scans a valid `architecture-design-workflow/SKILL.md`
- **THEN** it creates or preserves runtime links for both `~/.claude/skills/architecture-design-workflow` and `~/.codex/skills/architecture-design-workflow` pointing to the same source directory

#### Scenario: Runtime target conflicts with regular content
- **WHEN** either runtime already contains a regular file or directory with the same skill name
- **THEN** the installer preserves that content, reports a warning for that runtime, and independently processes the other runtime

### Requirement: Skill metadata is valid for both runtimes
The skill MUST use common frontmatter accepted by both runtimes, place Codex-specific display metadata in `agents/openai.yaml`, and keep references resolvable from the skill directory.

#### Scenario: Static validation runs
- **WHEN** implementation is ready for installation
- **THEN** both the Codex skill validator and the repository's Claude-compatible checks pass without broken reference or frontmatter errors

### Requirement: Trigger behavior is specific to complex architecture design
The skill description and instructions SHALL trigger for complex architecture upgrades, greenfield system design, hybrid cross-system design, and architecture review or handoff, and SHALL avoid taking over ordinary bug triage, status follow-up, direct implementation, or code review.

#### Scenario: Complex architecture request
- **WHEN** a user asks for a substantial system architecture redesign or a new supporting system design
- **THEN** the runtime selects `architecture-design-workflow` and starts at intake or the explicitly requested architecture stage

#### Scenario: Routine engineering request
- **WHEN** a user asks to investigate a bug, follow up task progress, implement an approved OpenSpec change, or review code
- **THEN** this skill does not claim primary ownership of the request

### Requirement: Behavioral tests preserve hard gates
Implementation MUST include repeatable pressure tests that verify project routing, OpenSpec prohibition, two-stage human approval, report version binding, and safe handling of missing evidence.

#### Scenario: Baseline failure is replayed after implementation
- **WHEN** the test asks an Agent to urgently bypass architecture routing and create a cross-project OpenSpec proposal
- **THEN** the Agent refuses the bypass, records the architecture project route, and waits for the correct explicit gate
