# Implementation Evidence

## Scope

- Change：`add-multica-human-centered-architecture-gate-rendering`
- Target：`multica-architecture-approval-adapter`
- Baseline HEAD：`84668032ddb9cf2983263a1a116688ef98161520`
- Out of scope：Multica core/CLI/API、真实 import/binding/delivery、Team/Project/Agent/Issue 创建、业务仓库和 Runtime activation

## RED evidence

新 fixtures 的 schema/语义测试先通过，证明测试输入有效：

```text
python3 -m unittest tests.test_multica_architecture_approval_adapter_contract.MulticaArchitectureApprovalAdapterContractTest.test_human_action_fixtures_match_contract
Ran 1 test ... OK
```

修改 production adapter 前运行新渲染契约测试，得到预期失败：

```text
python3 -m unittest tests.test_multica_architecture_approval_adapter_contract.MulticaArchitectureApprovalAdapterContractTest.test_human_action_rendering_contract_is_present
FAILED
missing human action template(s):
- multica-architecture-approval-adapter/templates/multica-human-action-request.md
- multica-architecture-approval-adapter/templates/multica-operational-authorization.md
```

失败只由新行为所需模板缺失引起，不是 fixture、schema 或环境错误。

## GREEN evidence

### Independent forward behavior

独立只读 Agent 未读取 change/tests，未调用 Multica，按最新 adapter skill 处理五类场景：

1. ready packet：decision-first 首屏、四种中文后果、stable Design/Review/Packet refs、token-only reply 和审计后置均为 PASS；
2. token-plus-prose：混写评论为 invalid/non-authoritative，要求 fresh token-only comment，revision context 独立绑定；
3. generic access：不能关闭任何 artifact/client item，Design/Review/Packet 的 desktop/mobile 必须逐项记录；
4. missing authorization：delivery、metadata、mapping/readiness sidecar 均 no-write，并生成 scoped operational request；
5. partial retry：旧授权失效，新请求列出 C-1/A-1 等 retained objects、唯一 incremental write、no-clobber 与 failure retention。

首轮 GREEN 还识别 4 个跨实现一致性缺口，随后增加自动 RED 并修复：approval option 独立 blockers/Owner、`multica_revision_context_v1` 固定 7 行、`multica_artifact_access_confirmation_v1` 固定 15 行、`multica_operational_scope_v1` 固定 10 行 raw-UTF-8 scope digest。二次复核确认 token authority、delivery marker 和 core enums 均未改变。最后两个模板问题（blocker 值、deny escaping）也先 RED 后 GREEN，并由独立 Agent 最终确认 PASS。

### Verification commands

```text
uv run --with pyyaml python /Users/jie.hua/.codex/skills/.system/skill-creator/scripts/quick_validate.py multica-architecture-approval-adapter
Skill is valid!

python3 -m unittest tests.test_multica_architecture_approval_adapter_contract
Ran 6 tests ... OK

python3 -m unittest discover -s tests -p 'test_*.py'
Ran 30 tests ... OK

openspec validate multica-architecture-human-action-rendering --type spec --strict
Specification 'multica-architecture-human-action-rendering' is valid

openspec validate multica-architecture-approval-delivery --type spec --strict
Specification 'multica-architecture-approval-delivery' is valid

openspec validate multica-architecture-approval-decision-binding --type spec --strict
Specification 'multica-architecture-approval-decision-binding' is valid

openspec validate multica-architecture-adapter-activation --type spec --strict
Specification 'multica-architecture-adapter-activation' is valid

openspec validate add-multica-human-centered-architecture-gate-rendering --strict
Change 'add-multica-human-centered-architecture-gate-rendering' is valid

git diff --check
PASS
```

仓库级 `tests/worktree-lifecycle-safety.sh` 有 2 个与本变更无关的既有失败：脚本读取 baseline HEAD 和当前 working tree 均不存在的 active delta `openspec/changes/allow-deferred-post-merge-cleanup/specs/worktree-targeting/spec.md`；该脚本不在本变更 diff 中，其余 168/170 checks 通过。本次未修改该历史测试或伪造缺失 change。

## Runtime status

```text
activation=not_run
sandbox_acceptance=not_run
workspace=n/a
agent=n/a
```

没有真实 workspace/Issue/Agent identity 或写入授权，因此未执行 import、binding、delivery、sidecar、sandbox 或 retry；未声称平台生产可用。
