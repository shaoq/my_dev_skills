# Implementation Evidence

## Scope

- Change：`add-reviewable-architecture-clarification-prompts`
- Target：`architecture-design-workflow`
- Out of scope：Multica core、`multica-architecture-approval-adapter`、业务项目实现与正式批准协议
- Worktree：保留并未改写既有 `AGENTS.md`、`CLAUDE.md`、已归档 change 和其他主规格改动

## RED evidence

1. `UNIDRAG-12` 的 `ARCH-CONTROL v4` 只列五组待确认问题，没有候选建议、理由、风险或可编辑回复方式。
2. 修改前的独立只读 Agent 行为样例严格遵循当时的 skill 后，仍只输出五组空白确认表和完成条件；没有提供任何候选默认值、逐项理由或风险。
3. 新增结构检查后、修改 skill 前运行：

```text
python3 -m unittest tests.test_architecture_design_workflow_runner.ArchitectureWorkflowRunnerSafetyTest.test_static_contract_accepts_repository_skill
FAILED
ARCH-CONTROL missing reviewable clarification slots:
## Reviewable clarification request, Decision required,
Candidate recommendation, Basis, Material risks / consequences,
Missing evidence / Owner / closure condition, Editable response
```

该失败证明测试捕获的是本次缺失结构，而不是语法或环境错误。

## GREEN evidence

- `SKILL.md` 与 `references/solution-design.md` 要求 `critical_evidence_gaps` 的人类澄清请求逐项提供候选建议或 `no_recommendation`、依据、风险、待补证据/Owner/关闭条件及可编辑回复。
- `templates/arch-control.md` 增加七个必填结构槽位，并明确候选回复属于非批准信息。
- 独立 Codex 复测为五组输入分别提供了候选建议；容量/SLO 因缺少测量证据使用 `no_recommendation`，其余项目包含 provisional 默认值、理由、风险和关闭条件。
- Codex 行为证据：`tests/evidence/architecture-design-workflow/reviewable-clarification-request.codex.md`

## Fresh verification

| Command | Result |
|---|---|
| `uv run --with pyyaml python /Users/jie.hua/.codex/skills/.system/skill-creator/scripts/quick_validate.py architecture-design-workflow` | PASS，`Skill is valid!` |
| `python3 -m unittest discover -s tests` | PASS，27 tests |
| `bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime codex` | PASS，static + Codex behavior，23 fixtures |
| `openspec validate add-reviewable-architecture-clarification-prompts --type change --strict --json` | PASS |
| `openspec validate architecture-design-artifacts --type spec --strict --json` | PASS，仅 INFO |
| `openspec validate architecture-design-governance --type spec --strict --json` | PASS，仅 INFO |
| `git diff --check` | PASS |
| `gitnexus detect-changes --scope all --repo .` | `risk=low`，affected processes=0 |

## Declared limitations

- Claude CLI 的最小 `CLI_OK` 探针成功，但三次只读行为生成在限定时间内均未返回内容；因此没有新增 `.claude.md` GREEN 证据，也不声称 Claude 行为矩阵通过。
- `openspec validate --all --strict --json` 中本次 change 与两个目标主规格均有效，但全仓仍有 4 个既有规格因缺少 `Purpose/Requirements` 失败：`claudemd-loading`、`code-first-schema-analysis`、`compliance-extraction`、`schema-api-consistency`。它们不在本次授权范围，未修改。
- GitNexus 分析覆盖整个脏工作树，包含用户既有 archive/说明文件改动；本次没有提交，也没有把这些既有改动归因于当前 change。
