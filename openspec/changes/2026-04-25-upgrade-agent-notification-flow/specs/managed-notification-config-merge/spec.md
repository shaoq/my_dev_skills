## ADDED Requirements

### Requirement: Merge managed Claude hooks without overwriting unrelated hooks
The installer SHALL merge only its managed Claude hooks into `~/.claude/settings.json` and SHALL preserve unrelated existing hook entries.

#### Scenario: Existing custom Claude hooks
- **WHEN** `~/.claude/settings.json` already contains user-defined hooks
- **THEN** the installer adds its managed hook commands alongside them without deleting or replacing unrelated entries

#### Scenario: Reinstall managed Claude hooks
- **WHEN** the installer is run multiple times
- **THEN** the managed Claude hook entries are not duplicated

### Requirement: Merge managed Codex notify command without overwriting unrelated config
The installer SHALL add only its managed `notify` command entry to `~/.codex/config.toml` and SHALL preserve unrelated existing configuration.

#### Scenario: Existing Codex config without notify
- **WHEN** `~/.codex/config.toml` exists and does not contain a `notify` command
- **THEN** the installer adds the managed `notify` entry without altering unrelated keys

#### Scenario: Existing Codex config with other notify commands
- **WHEN** `~/.codex/config.toml` already contains user-defined notify commands
- **THEN** the installer preserves those commands and adds its managed command without duplication

### Requirement: Uninstall removes only managed notification config
The uninstall mode SHALL remove only the managed Claude hooks, Codex notify command, helper artifact, and iTerm2 triggers that were installed by this tool.

#### Scenario: Uninstall with unrelated user customizations present
- **WHEN** the uninstall mode is run on a machine that also contains unrelated Claude hooks, Codex config, or iTerm2 triggers
- **THEN** those unrelated user customizations remain unchanged

### Requirement: Check mode reports all managed integration points
The check mode SHALL report the current managed installation status for iTerm2 triggers, Claude hooks, Codex notify integration, and the shared helper path.

#### Scenario: Fully installed environment
- **WHEN** all managed integration points are present
- **THEN** check mode reports iTerm2, Claude, Codex, and helper status as installed

#### Scenario: Partially installed environment
- **WHEN** one or more managed integration points are missing
- **THEN** check mode reports which specific component is missing or incomplete
