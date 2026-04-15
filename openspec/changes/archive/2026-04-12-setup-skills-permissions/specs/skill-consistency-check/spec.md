## ADDED Requirements

### Requirement: Scan SKILL.md files for allowed-tools
The script SHALL scan all `*/SKILL.md` files in the project root, extract the `allowed-tools` frontmatter field, and parse all `Bash(xxx *)` patterns into a set of bash command prefixes.

#### Scenario: Extract bash patterns from allowed-tools
- **WHEN** the script scans `new-worktree-apply/SKILL.md` with `allowed-tools: Bash(git *) Bash(openspec *) Bash(grep *) ...`
- **THEN** it extracts the bash command prefixes: `git`, `openspec`, `grep`, etc.

#### Scenario: Skip skills without allowed-tools
- **WHEN** the script scans a SKILL.md without `allowed-tools` frontmatter (e.g., `parall-new-proposal`)
- **THEN** it skips that skill for bash pattern extraction (but may still warn about missing disable-model-invocation)

### Requirement: Warn on missing permissions
The script SHALL compare bash patterns from SKILL.md against the standard permissions list. If a skill declares `Bash(xxx *)` but no matching `Bash(xxx ...)` entry exists in standard permissions, it SHALL output a warning.

#### Scenario: Skill uses command not in standard permissions
- **WHEN** a SKILL.md declares `Bash(aws *)` but standard permissions has no `Bash(aws:*)` entry
- **THEN** the script prints a warning: "Warning: skill 'xxx' uses Bash(aws *) but no matching permission in standard list"

#### Scenario: All skill commands covered
- **WHEN** all bash patterns from skills have matching entries in standard permissions
- **THEN** no warnings are printed for this check

### Requirement: Warn on skills missing both allowed-tools and disable-model-invocation
The script SHALL flag SKILL.md files that have neither `allowed-tools` nor `disable-model-invocation: true` in their frontmatter.

#### Scenario: Skill has no guardrails
- **WHEN** a SKILL.md has neither `allowed-tools` nor `disable-model-invocation: true`
- **THEN** the script prints a warning: "Warning: skill 'xxx' has no allowed-tools and no disable-model-invocation — may be auto-invoked by model"

#### Scenario: Skill has proper guardrails
- **WHEN** a SKILL.md has either `allowed-tools` or `disable-model-invocation: true`
- **THEN** no warning is printed for this check
