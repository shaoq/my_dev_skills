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
- Current compatibility pair is `human_review_surface_v1` + `architecture_internal_evidence_v1`; core uses one canonical Design Markdown、machine-only manifest、raw-byte SHA-256 and portable evidence, and remains executable without the adapter.
- Archify is optional for `diagram_not_applicable`, but a required visual pins full repository revision/archive digest and requires `validate`、`deliver`、`visual-check` plus independent semantic/visual Review. Local Runtime availability is distinct from Multica workspace import/binding.
- Workflow mandate、Review 分类和 action state 都是 portable fields；任何平台的 workspace、work item、actor、message、material delivery、status、URL 与 CLI 都不是 core 依赖。

## Repository validation

Behavior validation must keep architecture stage, Human Action state and platform projection independent. An actionable Human Action Request with a unique Owner and exact response uses `awaiting_human_confirmation`; it is waiting for review, not a hard blocker, even when `critical_evidence_gaps` remains recorded. A hard blocker requires evidence that no executable human or Agent path currently exists.

Run from repository root:

```bash
uv run --with pyyaml python "$CODEX_HOME/skills/.system/skill-creator/scripts/quick_validate.py" architecture-design-workflow
bash tests/architecture-design-workflow-safety.sh
python3 -m unittest tests/test_setup_skills_env.py
openspec validate simplify-architecture-team-deliverables-and-agent-handoffs --type change --strict
git diff --check
```

If `CODEX_HOME` is unset, use the current Codex installation's `.codex/skills/.system/skill-creator/scripts/quick_validate.py` path. Record the resolved validator path and Runtime version.

Behavior evidence uses the same fixtures:

```bash
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime codex
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime claude
```

## Installation boundary

Automated implementation uses `tests/test_setup_skills_env.py`, which injects temporary Claude/Codex target directories and settings, then verifies both links resolve to identical repository bytes. It must not run the installer against the user's real HOME. `setup-skills-env.py` has no help/dry-run mode; invoking it with an unknown option still runs installation, so automation must import its functions as the isolation tests do.

After reviewing delivery, the user may choose to run:

```bash
python3 setup-skills-env.py
readlink ~/.claude/skills/architecture-design-workflow
readlink ~/.codex/skills/architecture-design-workflow
```

Both links must resolve to the same source. A regular file/directory conflict is preserved and warned.

Existing persisted `waiting_human` records and three-attachment attempts are not rewritten during installation. The current pair applies only after compatible activation and a new/superseding attempt.

## Downstream version contract

`uni-architecture::bootstrap-architecture-design-team` records the consumed repository commit at handoff time with `git rev-parse HEAD` and verifies this canonical identity plus validation matrix. The source does not embed its own commit hash because that would be self-referential.
