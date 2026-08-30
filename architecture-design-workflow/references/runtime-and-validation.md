# Runtime and validation

## Canonical identity

- Skill name: `architecture-design-workflow`
- Source: repository root `architecture-design-workflow/`
- Claude Code link: `~/.claude/skills/architecture-design-workflow`
- Codex link: `~/.codex/skills/architecture-design-workflow`
- Codex invocation: `$architecture-design-workflow`

Automatic discovery remains enabled. Human gates authorize publication/handoff, not skill invocation.

## Dependency preflight

- Research requires `openspec-explore` in the current Runtime catalog.
- Ambiguous intake additionally requires `superpowers:brainstorming`.
- GitNexus is preferred for existing-code evidence; unavailable时记录限制并做有界调查。
- Missing dependencies are reported; this skill never installs them or changes Runtime configuration.
- Approval packet core uses Markdown, raw-byte SHA-256 and portable evidence only; it remains executable with shared local files and current-session human confirmation, without a separate adapter.

## Repository validation

Run from repository root:

```bash
uv run --with pyyaml python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" architecture-design-workflow
bash tests/architecture-design-workflow-safety.sh
python3 -m unittest tests/test_setup_skills_env.py
openspec validate add-portable-architecture-approval-packets --type change --strict --json
git diff --check
```

If `CODEX_HOME` is unset, use the current Codex installation's `.codex/skills/.system/skill-creator/scripts/quick_validate.py` path. Record the resolved validator path and Runtime version.

Behavior evidence uses the same fixtures:

```bash
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime codex
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime claude
```

## Installation boundary

Automated implementation uses `tests/test_setup_skills_env.py`, which redirects both Runtime targets and settings into temporary directories. It must not run the installer against the user's real HOME.

After reviewing delivery, the user may choose to run:

```bash
python3 setup-skills-env.py
readlink ~/.claude/skills/architecture-design-workflow
readlink ~/.codex/skills/architecture-design-workflow
```

Both links must resolve to the same source. A regular file/directory conflict is preserved and warned.

Existing persisted `waiting_human` records are not rewritten during installation. New packet rules apply after explicit refresh or a new design/review version.

## Downstream version contract

`uni-architecture::bootstrap-architecture-design-team` records the consumed repository commit at handoff time with `git rev-parse HEAD` and verifies this canonical identity plus validation matrix. The source does not embed its own commit hash because that would be self-referential.
