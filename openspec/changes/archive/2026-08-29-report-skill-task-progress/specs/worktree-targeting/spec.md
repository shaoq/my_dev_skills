## ADDED Requirements

### Requirement: Single worktree apply reports numeric proposal task progress

`new-worktree-apply` SHALL append a proposal completion progress section to its existing post-apply summary. The section SHALL report `DONE/TOTAL` and `REMAINING` from the final readable `tasks.md`, SHALL NOT list task identifiers or task text, and SHALL summarize unfinished tasks only as mutually exclusive reason-category counts whose sum equals `REMAINING`.

#### Scenario: All tasks are complete
- **WHEN** the final `tasks.md` contains eight recognized tasks and all eight are checked
- **THEN** the summary reports `Tasks: 8/8`, `Remaining: 0`, and no unfinished reason categories

#### Scenario: Some tasks remain incomplete
- **WHEN** the final `tasks.md` contains eight recognized tasks, three are checked, and five remain unchecked
- **THEN** the summary reports `Tasks: 3/8`, `Remaining: 5`, and reason-category counts totaling five without task-level details

#### Scenario: Unfinished reason lacks execution evidence
- **WHEN** an unchecked task cannot be associated with apply output, test or verification output, dependency state, or another direct workflow observation
- **THEN** that task contributes to the `原因未知` count and the skill does not infer a reason from its task text

#### Scenario: Task progress cannot be calculated
- **WHEN** `tasks.md` is missing, unreadable, or contains no recognized task checkboxes
- **THEN** the summary reports task progress and remaining count as unknown with a brief reason and does not claim `0/0` is complete
