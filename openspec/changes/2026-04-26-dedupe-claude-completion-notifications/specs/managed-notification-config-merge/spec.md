## MODIFIED Requirements

### Requirement: Merge managed Claude hooks without overwriting unrelated hooks
The installer SHALL merge only its managed Claude hooks into `~/.claude/settings.json`, SHALL preserve unrelated existing hook entries, and SHALL remove any previously managed Claude `Notification(idle_prompt)` hook group during reinstall.

#### Scenario: Existing custom Claude hooks
- **WHEN** `~/.claude/settings.json` already contains user-defined hooks
- **THEN** the installer adds or refreshes only its managed `Stop` and `Notification(permission_prompt)` hook commands
- **AND** leaves unrelated user hooks unchanged

#### Scenario: Reinstall after previous managed idle configuration
- **WHEN** the installer is run after an older managed version that installed `Notification(idle_prompt)`
- **THEN** the installer removes that managed `idle_prompt` group
- **AND** does not remove unrelated non-managed `idle_prompt` hook groups

### Requirement: Check mode reports managed Claude hook composition
The check mode SHALL report the current managed Claude hook composition, including whether a managed `Stop`, managed `Notification(permission_prompt)`, or managed `Notification(idle_prompt)` group is present.

#### Scenario: Current managed configuration is clean
- **WHEN** only the managed `Stop` and managed `Notification(permission_prompt)` groups are installed
- **THEN** check mode reports those groups as present
- **AND** reports managed `idle_prompt` as absent

#### Scenario: Legacy managed idle group remains
- **WHEN** a managed `Notification(idle_prompt)` group is still present
- **THEN** check mode reports that the installation is in a legacy duplicate-prone state
