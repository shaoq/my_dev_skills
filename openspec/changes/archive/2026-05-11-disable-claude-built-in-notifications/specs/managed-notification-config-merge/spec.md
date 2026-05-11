## MODIFIED Requirements

### Requirement: Merge managed Claude notification settings without overwriting unrelated settings
The installer SHALL merge only its managed Claude notification settings into `~/.claude/settings.json`, SHALL preserve unrelated existing settings, and SHALL manage `preferredNotifChannel` alongside the existing managed Claude hooks so the built-in notification channel does not duplicate the managed immediate reminder flow.

#### Scenario: Existing custom Claude settings
- **WHEN** `~/.claude/settings.json` already contains unrelated user-defined settings
- **THEN** the installer adds or refreshes only its managed Claude notification settings
- **AND** it sets `preferredNotifChannel` to `notifications_disabled`
- **AND** it leaves unrelated user settings unchanged

#### Scenario: Existing custom preferred notification channel
- **WHEN** `~/.claude/settings.json` already contains a user-defined `preferredNotifChannel`
- **THEN** the installer records the original presence and value in managed state before changing it
- **AND** it still sets the active value to `notifications_disabled`

#### Scenario: Uninstall restores previous preferred notification channel
- **WHEN** uninstall runs after the installer previously changed `preferredNotifChannel`
- **THEN** the installer restores the original value if one existed
- **AND** removes the field if it was absent before managed install

### Requirement: Check mode reports managed Claude notification channel state
The check mode SHALL report the current managed Claude notification-channel state in addition to the managed Claude hook composition.

#### Scenario: Built-in channel is correctly disabled
- **WHEN** `preferredNotifChannel` is set to `notifications_disabled`
- **THEN** check mode reports that the Claude built-in notification channel is disabled for the managed setup

#### Scenario: Built-in channel is still enabled
- **WHEN** `preferredNotifChannel` is absent or set to a value other than `notifications_disabled`
- **THEN** check mode reports that the Claude built-in notification channel remains enabled
- **AND** warns that it may duplicate the managed immediate reminder path
