## MODIFIED Requirements

### Requirement: Claude completion reminders exclude prompt-exit session termination
The managed Claude notification flow SHALL distinguish a normal completed turn from a prompt-driven session exit. A `Stop` event that belongs to a recent `SessionEnd(reason=prompt_input_exit)` flow SHALL NOT emit a managed completion reminder.

#### Scenario: Normal Claude turn completion
- **WHEN** Claude triggers the managed `Stop` hook for a normal completed turn
- **THEN** the managed helper emits one completion reminder

#### Scenario: User exits from prompt input
- **WHEN** Claude ends a session with `SessionEnd(reason=prompt_input_exit)`
- **AND** a managed `Stop` event for the same session occurs within the exit suppression window
- **THEN** the managed helper suppresses that completion reminder
- **AND** the user receives no managed completion notification for the exit flow

#### Scenario: Permission prompt remains enabled
- **WHEN** Claude emits managed `Notification(permission_prompt)`
- **THEN** the managed helper still emits the approval-needed reminder

### Requirement: Claude completion reminders suppress only the current focused iTerm2 session
The managed Claude notification flow SHALL suppress a completion reminder only when the notification belongs to the exact iTerm2 session that currently has keyboard focus. It SHALL NOT suppress reminders for other non-focused sessions in the same iTerm2 application.

#### Scenario: Focused session completes
- **WHEN** Claude triggers the managed `Stop` hook in the exact iTerm2 session that currently has keyboard focus
- **THEN** the managed helper suppresses that completion reminder

#### Scenario: Background session in same iTerm2 app completes
- **WHEN** Claude triggers the managed `Stop` hook in an iTerm2 session whose tty is different from the current focused iTerm2 session tty
- **THEN** the managed helper emits the completion reminder

#### Scenario: Foreground app is not iTerm2
- **WHEN** Claude triggers the managed `Stop` hook for an iTerm2 session
- **AND** the current foreground application is not iTerm2
- **THEN** the managed helper emits the completion reminder

#### Scenario: Focus query fails
- **WHEN** the managed helper cannot reliably determine the current focused iTerm2 session tty
- **THEN** it emits the completion reminder rather than suppressing it

#### Scenario: tmux background pane completes
- **WHEN** Claude triggers the managed `Stop` hook from a tmux pane that is not the pane currently visible in the focused iTerm2 session context
- **THEN** the managed helper emits the completion reminder

### Requirement: Managed Claude hooks include session-end exit semantics
The installer SHALL add a managed `SessionEnd` hook for Claude so the helper can detect `prompt_input_exit` and apply exit-specific reminder suppression.

#### Scenario: Managed install after upgrade
- **WHEN** the installer updates the managed Claude hook set
- **THEN** it leaves managed `Stop` and managed `Notification(permission_prompt)` installed
- **AND** it also installs one managed `SessionEnd` hook
