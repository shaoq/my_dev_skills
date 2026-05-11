## ADDED Requirements

### Requirement: Install a shared runtime notification helper
The installer SHALL install a shared runtime notification helper to a stable user-local executable path and SHALL configure both Claude Code and Codex to invoke that helper.

#### Scenario: First-time install
- **WHEN** the installer is run on a machine without the helper present
- **THEN** it installs the helper to the managed executable path and marks it executable

#### Scenario: Reinstall updates helper
- **WHEN** the installer is run again after the helper already exists
- **THEN** it updates or verifies the helper in place without creating duplicate helper files

### Requirement: Configure Claude Code completion and idle reminders
The installer SHALL add managed Claude hooks for `Stop`, `Notification(permission_prompt)`, and `Notification(idle_prompt)` that invoke the shared notification helper.

#### Scenario: Claude finishes a turn
- **WHEN** Claude triggers the `Stop` hook
- **THEN** the managed helper is invoked with a `turn_completed` event

#### Scenario: Claude requests permission
- **WHEN** Claude emits `Notification(permission_prompt)`
- **THEN** the managed helper is invoked with an `approval_needed` event

#### Scenario: Claude is idle awaiting the next user instruction
- **WHEN** Claude emits `Notification(idle_prompt)`
- **THEN** the managed helper is invoked with an `idle_waiting` event

### Requirement: Configure Codex completion reminders through notify
The installer SHALL add a managed Codex `notify` command that invokes the shared notification helper after completed turns.

#### Scenario: Codex completes a turn
- **WHEN** Codex finishes a completed turn and runs the managed `notify` command
- **THEN** the shared helper is invoked with the completion payload and emits a completion reminder

### Requirement: Shared helper emits user-visible reminders
The shared helper SHALL support macOS notification output and BEL output so that completion and idle reminders can surface outside the terminal and also trigger iTerm2 visual bell behavior.

#### Scenario: Completion reminder
- **WHEN** the helper receives a `turn_completed` event
- **THEN** it emits a macOS notification and a BEL signal

#### Scenario: Idle reminder
- **WHEN** the helper receives an `idle_waiting` event
- **THEN** it emits a macOS notification and a BEL signal
