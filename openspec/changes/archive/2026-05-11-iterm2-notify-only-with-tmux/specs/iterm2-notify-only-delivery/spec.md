## ADDED Requirements

### Requirement: Deliver managed agent reminders through iTerm2 notifications only
The managed notification setup SHALL deliver Claude Code and Codex reminders through iTerm2 notification delivery only. It SHALL NOT rely on managed BEL emission or managed BellTrigger rules as part of the reminder path.

#### Scenario: Claude reminder is emitted
- **WHEN** a managed Claude reminder event is raised
- **THEN** the managed path emits an iTerm2 notification
- **AND** the managed path does not emit BEL

#### Scenario: Codex reminder is emitted
- **WHEN** a managed Codex reminder event is raised
- **THEN** the managed path emits an iTerm2 notification
- **AND** the managed path does not emit BEL

### Requirement: Claude reminders use structured hook events
The managed setup SHALL keep Claude Code reminder events on structured hook entry points and SHALL map those events to iTerm2 notifications without falling back to BellTrigger matching.

#### Scenario: Claude completes a turn
- **WHEN** Claude triggers `Stop`
- **THEN** the managed helper emits a completion notification through iTerm2

#### Scenario: Claude requests permission
- **WHEN** Claude emits `Notification(permission_prompt)`
- **THEN** the managed helper emits an approval notification through iTerm2

#### Scenario: Claude waits for the next instruction
- **WHEN** Claude emits `Notification(idle_prompt)`
- **THEN** the managed helper emits an idle notification through iTerm2

### Requirement: Codex reminders use TUI OSC 9 notifications
The managed setup SHALL configure Codex to use TUI notifications with `notification_method = "osc9"` so that approval prompts and completed turns surface through iTerm2 notifications.

#### Scenario: Codex requests approval
- **WHEN** Codex shows an approval prompt in the TUI
- **THEN** the managed Codex configuration emits an iTerm2 notification through the TUI notification system

#### Scenario: Codex completes a turn
- **WHEN** Codex completes a turn
- **THEN** the managed Codex configuration emits an iTerm2 notification through the TUI notification system
