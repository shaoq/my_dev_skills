## MODIFIED Requirements

### Requirement: Merge managed Claude hooks without overwriting unrelated hooks
The installer SHALL merge only its managed Claude hooks into `~/.claude/settings.json`, SHALL preserve unrelated existing hook entries, and SHALL manage `SessionEnd` alongside `Stop` and `Notification(permission_prompt)` for the exit-suppression flow.

#### Scenario: Existing custom Claude hooks
- **WHEN** `~/.claude/settings.json` already contains user-defined hooks
- **THEN** the installer adds or refreshes only its managed `Stop`, `Notification(permission_prompt)`, and `SessionEnd` hook commands
- **AND** leaves unrelated user hooks unchanged

### Requirement: Check mode reports managed Claude hook composition
The check mode SHALL report the current managed Claude hook composition, including whether a managed `Stop`, managed `Notification(permission_prompt)`, managed `SessionEnd`, or managed `Notification(idle_prompt)` group is present.

#### Scenario: Exit suppression support is installed
- **WHEN** the managed `Stop`, managed `Notification(permission_prompt)`, and managed `SessionEnd` groups are installed
- **THEN** check mode reports those groups as present
- **AND** reports managed `idle_prompt` as absent
