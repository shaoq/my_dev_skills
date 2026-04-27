## ADDED Requirements

### Requirement: Preserve existing Claude approval trigger rules during upgrade
The installer SHALL preserve the current three Claude-oriented trigger regex rules exactly as they are today. It SHALL NOT rewrite, remove, rename, or broaden those existing rules during upgrade.

#### Scenario: Upgrade from current working Claude setup
- **WHEN** the installer is run on a machine where the existing Claude trigger rules are already effective
- **THEN** those existing regex rules remain unchanged after upgrade

#### Scenario: Reinstall after previous managed install
- **WHEN** the installer is run multiple times
- **THEN** the existing Claude trigger rules remain present once each, without duplication or drift

### Requirement: Add Codex approval trigger patterns as incremental rules
The installer SHALL append managed iTerm2 trigger rules for Codex approval prompts without modifying the existing Claude rules.

#### Scenario: Codex asks to run a command
- **WHEN** the terminal output contains a Codex approval prompt such as `Would you like to run the following command?`
- **THEN** the matching managed trigger fires a notification and bell action for the active iTerm2 profile

#### Scenario: Codex asks to grant permissions
- **WHEN** the terminal output contains a Codex approval prompt such as `Would you like to grant these permissions?`
- **THEN** the matching managed trigger fires a notification and bell action

### Requirement: Approval triggers remain profile-wide and managed
The installer SHALL continue to apply approval triggers to all iTerm2 profiles and SHALL identify only its own managed triggers for update and removal.

#### Scenario: Profile contains unrelated user triggers
- **WHEN** a profile already contains triggers not managed by this installer
- **THEN** the installer leaves those unrelated triggers unchanged

#### Scenario: Remove managed approval triggers
- **WHEN** the uninstall mode is run
- **THEN** only triggers tagged as managed by this installer are removed
