## ADDED Requirements

### Requirement: Level-1 automatic backfill via 4-rule parser
When a change passes D3 (Code Delivery) but fails D1 (Tasks), the system SHALL parse each `- [ ]` task description using four extraction rules (backtick-enclosed paths, directory creation patterns, frontmatter patterns, implementation keyword patterns), verify the referenced file/directory exists on disk, and automatically change matching items from `- [ ]` to `- [x]` without user confirmation.

#### Scenario: Backtick path matches existing file
- **WHEN** a task description contains a backtick-enclosed file path (e.g. `` `SKILL.md` ``) and that file exists on disk
- **THEN** the system SHALL auto-mark that task as `- [x]` without confirmation

#### Scenario: Directory creation pattern matches existing directory
- **WHEN** a task description contains "创建 `xxx/` 目录" pattern and that directory exists on disk
- **THEN** the system SHALL auto-mark that task as `- [x]` without confirmation

#### Scenario: No matchable path in task description
- **WHEN** a task description contains no extractable file/directory path via the 4 rules
- **THEN** the system SHALL leave that task as `- [ ]` and include it in the Level-2 candidate list

### Requirement: Level-2 backfill with user confirmation for residual tasks
When D3 fully passes (files exist AND git commits found) but Level-1 backfill leaves remaining `- [ ]` items, the system SHALL present all residual unmarked tasks to the user via AskUserQuestion and mark them as `- [x]` only after explicit user confirmation.

#### Scenario: Residual tasks exist and user confirms
- **WHEN** D3 passes fully and Level-1 backfill completes but some `- [ ]` tasks remain
- **THEN** the system SHALL display the list of residual tasks and ask the user to confirm marking them all as complete
- **AND** upon user confirmation, the system SHALL change all listed tasks from `- [ ]` to `- [x]`

#### Scenario: Residual tasks exist but user declines
- **WHEN** the user declines the Level-2 confirmation prompt
- **THEN** the system SHALL leave the residual tasks as `- [ ]` and continue to the blocking reasons step

#### Scenario: No residual tasks after Level-1
- **WHEN** Level-1 backfill marks all previously unmarked tasks
- **THEN** the system SHALL skip Level-2 and proceed directly to the updated report

### Requirement: Backfill results commit via force-add
After backfill completes (either level), the system SHALL stage all modified tasks.md files using `git add -f openspec/changes/*/tasks.md` to bypass .gitignore, and commit with message `fix: auto-backfill task markers (N changes)`.

#### Scenario: Multiple changes have backfilled tasks
- **WHEN** backfill modifies tasks.md in 3 changes
- **THEN** the system SHALL execute `git add -f` for all 3 tasks.md files and commit once with message containing "3 changes"

#### Scenario: No tasks were modified
- **WHEN** no tasks.md files were changed during backfill
- **THEN** the system SHALL NOT execute any git add or commit
