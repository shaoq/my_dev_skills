## MODIFIED Requirements

### Requirement: Configure Claude Code completion reminders without duplicate delivery
The installer SHALL add managed Claude hooks for `Stop` and `Notification(permission_prompt)` that invoke the shared notification helper. It SHALL NOT install a managed `Notification(idle_prompt)` hook in the default configuration.

#### Scenario: Claude finishes a turn
- **WHEN** Claude triggers the managed `Stop` hook
- **THEN** the managed helper is invoked with a completion event
- **AND** the user receives exactly one managed completion reminder for that completed turn

#### Scenario: Claude requests permission
- **WHEN** Claude emits managed `Notification(permission_prompt)`
- **THEN** the managed helper is invoked with an approval-needed event
- **AND** the permission reminder remains enabled

#### Scenario: Upgrade from previous managed three-event configuration
- **WHEN** the installer is run on a machine where a previous managed install added `Notification(idle_prompt)`
- **THEN** the installer removes the managed `idle_prompt` hook group
- **AND** leaves the managed `Stop` and `permission_prompt` hook groups installed once each

### Requirement: Shared helper suppresses duplicate Claude completion reminders
The shared helper SHALL maintain Claude-specific deduplication state and SHALL suppress duplicate completion-class reminders that refer to the same managed Claude turn.

#### Scenario: Duplicate Stop delivery
- **WHEN** the managed helper receives the same Claude completion event more than once within the deduplication window
- **THEN** it emits only the first completion reminder
- **AND** suppresses the duplicate deliveries

#### Scenario: Legacy idle prompt arrives after completion
- **WHEN** the managed helper receives a Claude `idle_prompt` notification for a session that has already emitted a managed completion reminder for the same turn
- **THEN** it suppresses that `idle_prompt` reminder
- **AND** the user does not receive a second completion-class notification

## REMOVED Requirements

### Requirement: Configure Claude Code completion and idle reminders
**Reason**: `Notification(idle_prompt)` overlaps with `Stop` for the "completed turn and now waiting" flow, which causes duplicate reminders for a single Claude task completion.
**Migration**: Reinstall the managed Claude hooks so the installer removes the old managed `idle_prompt` hook group and keeps only `Stop` plus `Notification(permission_prompt)`.
