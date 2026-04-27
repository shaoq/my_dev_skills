## ADDED Requirements

### Requirement: Claude notification helper supports tmux passthrough
The managed Claude notification helper SHALL preserve iTerm2 notification delivery when Claude Code is running inside tmux launched from iTerm2.

#### Scenario: Claude runs directly in iTerm2
- **WHEN** the managed helper emits a notification outside tmux
- **THEN** it writes a plain iTerm2 `OSC 9` notification sequence

#### Scenario: Claude runs inside tmux in iTerm2
- **WHEN** the managed helper emits a notification inside tmux
- **THEN** it wraps the iTerm2 notification sequence in a tmux-compatible passthrough envelope

### Requirement: Codex tmux delivery remains compatible with iTerm2 notifications
The managed setup SHALL preserve Codex notification delivery inside tmux by relying on the official Codex TUI `osc9` notification path rather than a BEL fallback.

#### Scenario: Codex runs inside tmux in iTerm2
- **WHEN** Codex emits a managed TUI notification while running inside tmux in iTerm2
- **THEN** the notification remains deliverable to the outer iTerm2 session

### Requirement: tmux support is part of notify-only acceptance
The notify-only design SHALL treat tmux compatibility as a required acceptance condition rather than an optional enhancement.

#### Scenario: Notify-only validation
- **WHEN** the managed notify-only setup is validated
- **THEN** validation covers both non-tmux and tmux sessions for Claude Code and Codex
