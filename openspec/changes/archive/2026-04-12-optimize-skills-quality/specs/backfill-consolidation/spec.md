## ADDED Requirements

### Requirement: Unified backfill four-rule definition
All skills that perform task backfill (new-worktree-apply, parall-new-worktree-apply, check-changes-completed) SHALL use the same four-rule definition for detecting completed tasks: (1) backtick-enclosed file path → test -f, (2) directory creation pattern → test -d, (3) frontmatter pattern → file contains ---, (4) implementation keyword → grep -rl.

#### Scenario: Consistent rule application across skills
- **WHEN** any skill applies backfill rules to an unmarked task
- **THEN** the same four rules with the same matching logic are applied, producing consistent results

### Requirement: Agent prompt self-contained backfill rules
`parall-new-worktree-apply` Agent prompt in Step 4.1 SHALL embed the four backfill rules directly in the prompt text instead of instructing the Agent to read `new-worktree-apply/SKILL.md` and follow steps by number. The prompt SHALL contain a "Step A — Task Backfill" section with all four rules and a "Step B — Force-add + Commit" section.

#### Scenario: Agent executes backfill without external file dependency
- **WHEN** an Agent spawned by `parall-new-worktree-apply` performs post-apply backfill
- **THEN** it follows the four rules embedded in its prompt, without reading `new-worktree-apply/SKILL.md`

#### Scenario: Resilient to external file changes
- **WHEN** `new-worktree-apply/SKILL.md` step numbers are changed or the file is renamed
- **THEN** `parall-new-worktree-apply` Agent execution is unaffected

### Requirement: Agent prompt references dependencies.yaml for dependency resolution
The Agent prompt in `parall-new-worktree-apply` Step 4.1 SHALL reference `dependencies.yaml` format (not `proposal.md ## Dependencies`) when describing the change context to the Agent.

#### Scenario: Agent prompt consistent with new dependency format
- **WHEN** an Agent processes a change that has dependencies
- **THEN** the prompt description uses `dependencies.yaml` terminology consistently
