# Implementation Evidence

## Baseline

- Branch: `main`
- Baseline HEAD: `ec7b7fd87f742404e3f61c1ccf7e0c836ece5392`
- GitNexus indexed commit: `ec7b7fd87f742404e3f61c1ccf7e0c836ece5392`
- GitNexus query/impact: unavailable because the indexed LadybugDB storage version is 43 while the MCP runtime supports 42; reported risk is `UNKNOWN`.
- Source fallback blast radius: `tests/architecture-design-workflow-safety.sh` is the single parser/validator for all architecture workflow fixtures and behavior evidence; `tests/test_architecture_design_workflow_runner.py` exercises that runner; `tests/test_setup_skills_env.py` covers the shared Claude Code/Codex symlink installation boundary. The bounded test-pipeline risk is `MEDIUM`; no application runtime flow is involved.
- Pre-existing dirty files left untouched: `AGENTS.md`, `CLAUDE.md`.

## Pre-change validation

| Check | Result |
|---|---|
| architecture skill quick validation | PASS |
| `tests/architecture-design-workflow-safety.sh` | PASS, 9 fixtures |
| `tests/test_architecture_design_workflow_runner.py` | PASS, 7 tests |
| `tests/test_setup_skills_env.py` | PASS, 10 tests |

## Final validation

| Check | Result |
|---|---|
| skill quick validation | PASS; validator `/Users/jie.hua/.codex/skills/.system/skill-creator/scripts/quick_validate.py` |
| static architecture safety | PASS, 22 fixtures |
| Codex behavior safety | PASS, 22 fixtures; `codex-cli 0.151.0` |
| Claude Code behavior safety | PASS, 22 fixtures; `Claude Code 2.1.14` |
| runner unit tests | PASS, 11 tests |
| temporary-HOME installer tests | PASS, 10 tests |
| full Python test discovery | PASS, 21 tests |
| OpenSpec strict validation | PASS, 1 change / 0 issues |
| `git diff --check` | PASS |
| GitNexus `detect_changes(scope=all)` | UNAVAILABLE; LadybugDB file version 43 / runtime storage version 42 |

## Delivery boundary

- Branch: `main`.
- Implementation payload commit: `1d4b860b48e15f678d78a71bf2c38557ab9c2951` on `main`. GitNexus change detection remained unavailable, so the commit was created only after the recorded bounded source audit and complete validation matrix passed.
- Core contract revision for a later adapter change: OpenSpec change `add-portable-architecture-approval-packets` at implementation payload commit `1d4b860b48e15f678d78a71bf2c38557ab9c2951`. The evidence-only follow-up commit does not change the portable core contract.
- Behavior evidence: 22 shared fixtures and 44 normalized evidence files across Codex and Claude Code.
- Installation tests redirected both Runtime links and settings to temporary directories; real HOME and Runtime configuration were not modified.
- Repository scope contains Markdown instructions/templates, OpenSpec artifacts, fixtures, evidence, and test-runner changes only. No service, database, network dependency, platform adapter skill, or external Agent/Team/Project/Issue was created.
- `AGENTS.md` and `CLAUDE.md` were dirty before implementation and remain outside this change's delivery scope.

## Known limitations

- GitNexus query, impact, and final `detect_changes` cannot read the existing index until the MCP runtime supports storage version 43 or the index is rebuilt with its current version. Bounded source inspection and the full relevant test matrix were used instead; impact risk remains `UNKNOWN` in GitNexus terms and `MEDIUM` for the local test pipeline assessment.
- This core defines `local_file`, current-interaction binding, and portable extension semantics. Platform-specific readable delivery, attachment/comment mapping, rendered documents, and external resource activation remain a separate future adapter change.
