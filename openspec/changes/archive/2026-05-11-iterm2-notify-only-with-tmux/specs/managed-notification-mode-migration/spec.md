## ADDED Requirements

### Requirement: Installer migrates managed bell-era configuration to notify-only mode
The installer SHALL migrate previously managed bell-era configuration to the notify-only mode so that older managed bell behavior does not remain active after reinstall.

#### Scenario: Old BellTrigger rules exist
- **WHEN** the installer finds managed BellTrigger rules from the previous setup
- **THEN** it removes or replaces those managed rules during migration

#### Scenario: Old helper behavior exists
- **WHEN** the installer updates the managed runtime helper from an earlier bell-based version
- **THEN** the resulting managed helper no longer emits BEL as part of reminder delivery

### Requirement: Installer stops managed bell profile mutation
The installer SHALL stop applying managed `Flashing Bell` and `Silence Bell` mutations as part of the notification setup.

#### Scenario: Fresh install in notify-only mode
- **WHEN** the installer runs in notify-only mode
- **THEN** it does not add new managed bell profile changes

### Requirement: Installer manages Codex TUI notification fields
The installer SHALL manage the Codex notification settings through the `[tui]` table rather than the previous managed top-level `notify` command path when operating in notify-only mode.

#### Scenario: Existing managed top-level notify is present
- **WHEN** the installer detects the previous managed top-level `notify` block
- **THEN** it removes or migrates that managed block and installs managed `[tui]` notification settings

#### Scenario: Existing user TUI settings are present
- **WHEN** `~/.codex/config.toml` already contains user-defined `[tui]` settings
- **THEN** the installer updates only the managed notification-related fields without removing unrelated user fields

### Requirement: Check mode reports notify-only migration state
The managed check mode SHALL report whether legacy managed bell paths have been removed and whether notify-only paths are active.

#### Scenario: Legacy bell path remains
- **WHEN** managed bell-era configuration is still present after migration
- **THEN** check output reports that legacy bell configuration still exists

#### Scenario: User custom bell settings remain
- **WHEN** bell-related settings exist but are not managed by the installer
- **THEN** check output distinguishes them from managed notify-only compliance
