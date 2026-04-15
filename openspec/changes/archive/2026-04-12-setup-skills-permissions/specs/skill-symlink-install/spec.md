## ADDED Requirements

### Requirement: Create symlinks for root-level custom skills
The script SHALL scan the project root for `*/SKILL.md` files (excluding `.claude/` directory). For each found skill, it SHALL create a directory at `.claude/skills/<name>/` and a symbolic link `SKILL.md` inside it pointing to the source file via relative path `../../<name>/SKILL.md`.

#### Scenario: Install a custom skill via symlink
- **WHEN** the script finds `new-worktree-apply/SKILL.md` in the project root
- **THEN** it creates `.claude/skills/new-worktree-apply/SKILL.md` as a symlink pointing to `../../new-worktree-apply/SKILL.md`

#### Scenario: Symlink already exists and is valid
- **WHEN** `.claude/skills/new-worktree-apply/SKILL.md` already exists as a valid symlink pointing to the correct target
- **THEN** the script skips it without error

#### Scenario: Symlink exists but target is broken
- **WHEN** `.claude/skills/new-worktree-apply/SKILL.md` is a symlink but the target no longer exists
- **THEN** the script removes the broken symlink and recreates it

### Requirement: Preserve existing non-symlink files
If a regular file (not a symlink) already exists at `.claude/skills/<name>/SKILL.md`, the script SHALL NOT overwrite it and SHALL print a warning.

#### Scenario: User-created file exists
- **WHEN** `.claude/skills/my-skill/SKILL.md` is a regular file (not a symlink)
- **THEN** the script prints "Warning: .claude/skills/my-skill/SKILL.md is a regular file, skipping symlink creation" and does not modify it

### Requirement: Skip .claude directory during skill scan
The script SHALL NOT scan `.claude/` or `openspec/` directories for SKILL.md files. Only top-level directories (direct children of project root) containing `SKILL.md` SHALL be processed.

#### Scenario: OpenSpec change directory has SKILL.md-like structure
- **WHEN** the script encounters `openspec/changes/foo/tasks.md` or `.claude/skills/bar/SKILL.md`
- **THEN** these are ignored — only `<root>/<name>/SKILL.md` patterns are processed

### Requirement: Report symlink installation results
The script SHALL print a summary of symlink operations: created count, skipped count, warning count.

#### Scenario: Mixed results
- **WHEN** the script processes 5 skills — 3 new symlinks created, 1 already valid, 1 regular file conflict
- **THEN** it prints "Skills installed: 3 created, 1 already linked, 1 warning (regular file exists)"
