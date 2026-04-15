## ADDED Requirements

### Requirement: Generate settings.local.json from standard permissions
The script SHALL contain a hardcoded `STANDARD_PERMISSIONS` list covering all bash commands used by the project's skills. When executed, it SHALL generate `.claude/settings.local.json` with these permissions in the `permissions.allow` format.

#### Scenario: Fresh environment without settings file
- **WHEN** the script is run and `.claude/settings.local.json` does not exist
- **THEN** the script creates the file with all standard permissions

#### Scenario: Existing settings file
- **WHEN** the script is run and `.claude/settings.local.json` already exists
- **THEN** the script merges standard permissions into the existing file, preserving any user-added custom entries that are not in the standard list

#### Scenario: Idempotent execution
- **WHEN** the script is run multiple times
- **THEN** the resulting settings file is identical each time (no duplicate entries, no drift)

### Requirement: Script runs with Python 3 standard library only
The script SHALL use only Python 3.6+ standard library modules (`json`, `os`, `re`, `glob`, `pathlib`). No third-party dependencies required.

#### Scenario: No pip install needed
- **WHEN** the script is executed on a system with Python 3.6+
- **THEN** it runs successfully without any pip install step

### Requirement: Clear output on execution
The script SHALL print a summary showing: number of permissions configured, number of custom entries preserved (if any), file path written.

#### Scenario: Successful generation
- **WHEN** the script successfully generates the settings file
- **THEN** it prints a summary like "Done. 22 permissions configured. 0 custom entries preserved. Written to .claude/settings.local.json"
