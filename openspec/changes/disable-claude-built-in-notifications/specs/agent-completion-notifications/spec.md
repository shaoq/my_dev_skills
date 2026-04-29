## MODIFIED Requirements

### Requirement: Claude completion reminders are delivered through the managed immediate reminder path only
The managed Claude notification flow SHALL treat the managed helper as the only completion-reminder path when the notify setup is installed for immediate reminders. Claude built-in notification delivery SHALL NOT remain enabled in a way that can emit a later idle reminder for the same completed turn.

#### Scenario: Managed immediate reminder setup is installed
- **WHEN** the managed Claude immediate reminder setup is applied
- **THEN** Claude completion reminders are emitted through the managed helper path on `Stop`
- **AND** Claude built-in notification delivery is disabled for the managed configuration

#### Scenario: Completed turn is followed by prompt idle
- **WHEN** Claude completes a turn and the prompt remains idle for 60 seconds
- **THEN** the user receives no second built-in idle reminder for that same completed turn

#### Scenario: Permission prompt remains enabled
- **WHEN** Claude emits managed `Notification(permission_prompt)`
- **THEN** the managed helper still emits the approval-needed reminder
- **AND** disabling the built-in notification channel does not remove the managed permission reminder
