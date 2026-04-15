## ADDED Requirements

### Requirement: allowed-tools covers actual bash usage
Each skill's `allowed-tools` frontmatter SHALL include all bash commands used in the skill's steps. Specifically: `new-worktree-apply` and `merge-worktree-return` SHALL include `Bash(grep *)`, `Bash(test *)`, `Bash(head *)`, `Bash(sed *)`, `Bash(awk *)`, `Bash(cat *)`. `check-changes-completed` SHALL include `Bash(head *)`.

#### Scenario: new-worktree-apply allowed-tools complete
- **WHEN** `new-worktree-apply` executes Step 9 backfill using `grep -cE`, `test -f`, `head -1`
- **THEN** these bash commands match the skill's allowed-tools and do not trigger user approval prompts

#### Scenario: merge-worktree-return allowed-tools complete
- **WHEN** `merge-worktree-return` executes Step 3 using `grep`, `awk` for main branch detection
- **THEN** these bash commands match the skill's allowed-tools

#### Scenario: check-changes-completed allowed-tools complete
- **WHEN** `check-changes-completed` executes backfill Rule 3 using `head -1`
- **THEN** `Bash(head *)` is in the allowed-tools

### Requirement: Heavyweight skills have disable-model-invocation
`parall-new-proposal` and `parall-new-worktree-apply` SHALL have `disable-model-invocation: true` in their frontmatter to prevent the model from automatically triggering these complex operations.

#### Scenario: parall-new-proposal not auto-invoked
- **WHEN** the model considers invoking `parall-new-proposal`
- **THEN** the `disable-model-invocation: true` flag prevents automatic invocation

#### Scenario: parall-new-worktree-apply not auto-invoked
- **WHEN** the model considers invoking `parall-new-worktree-apply`
- **THEN** the `disable-model-invocation: true` flag prevents automatic invocation

### Requirement: End-of-skill next-step guidance
Skills that complete a logical step in the workflow SHALL include a next-step suggestion in their output section. Specifically: (1) `merge-worktree-return` SHALL suggest `/check-changes-completed` or `/opsx:archive`, (2) `parall-new-worktree-apply` SHALL suggest `/check-changes-completed` and `/opsx:archive` with differentiated guidance for success vs failure, (3) `check-changes-completed` SHALL provide differentiated guidance for archivable vs non-archivable changes.

#### Scenario: merge-worktree-return suggests next action
- **WHEN** `merge-worktree-return` completes successfully
- **THEN** the output includes a suggestion to run `/check-changes-completed` or `/opsx:archive`

#### Scenario: parall-new-worktree-apply provides differentiated guidance
- **WHEN** `parall-new-worktree-apply` final report shows mixed results
- **THEN** the output suggests `/check-changes-completed` for verification, `/opsx:archive` for completed changes, and `/new-worktree-apply` for failed changes

#### Scenario: check-changes-completed provides action-oriented guidance
- **WHEN** `check-changes-completed` finds both archivable and non-archivable changes
- **THEN** archivable changes get `/opsx:archive <name>` suggestions, non-archivable changes get `/opsx:apply <name>` or `/new-worktree-apply <name>` suggestions

### Requirement: settings.local.json cleaned and supplemented
The `.claude/settings.local.json` permissions SHALL have 6 shell syntax fragment entries removed (`Bash(for name:*)`, `Bash(do)`, `Bash(echo "=== $name ===")`, `Bash(done)`, `Bash(do echo:*)`, `Bash(then sed:*)`) and 7 common git subcommand entries added (`Bash(git branch:*)`, `Bash(git checkout:*)`, `Bash(git rebase:*)`, `Bash(git rev-parse:*)`, `Bash(git log:*)`, `Bash(git diff:*)`, `Bash(git status:*)`, `Bash(git show:*)`).

#### Scenario: Invalid permission entries removed
- **WHEN** skills execute shell commands
- **THEN** no permission entries match shell syntax keywords (do, done, for) that never correspond to actual commands

#### Scenario: Common git subcommands pre-approved
- **WHEN** skills run `git branch --show-current`, `git rev-parse HEAD`, `git log --oneline`, etc.
- **THEN** these commands match the allowed permissions and do not trigger approval prompts
