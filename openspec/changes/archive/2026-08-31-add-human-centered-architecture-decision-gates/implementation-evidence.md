# Implementation Evidence

## Scope

- Change：`add-human-centered-architecture-decision-gates`
- Target：`architecture-design-workflow`
- Baseline HEAD：`84668032ddb9cf2983263a1a116688ef98161520`
- Out of scope：Multica core、adapter implementation、Runtime activation、业务仓库和真实平台写入

## RED evidence

### Independent old-skill behavior

修改 production skill 前，独立只读 Agent 使用当前 `architecture-design-workflow` 处理四类人工门禁，观察到：

1. Subject Project 路由只要求“回复项目名称”，没有推荐、备选后果、稳定材料入口、回复后的 stage/writes 或非授权边界。
2. 两个不同 Owner 的非阻断风险没有 pending acceptance 契约、逐项回复语法或拒绝/修改后的状态聚合规则。
3. current ready packet 只列四种 token，没有逐项中文后果、OpenSpec 边界、立即写入或可复制回复。
4. `revision_requested` 会进入 `designing`，但没有独立 revision brief、缺失范围处理或准确补充格式。

基线 Agent 未读取本 change artifacts，未修改文件，也未调用 Multica。

### Static contract RED

新增核心契约检查后、修改 production skill 前运行：

```text
python3 -m unittest tests.test_architecture_design_workflow_runner.ArchitectureWorkflowRunnerSafetyTest.test_static_contract_accepts_repository_skill
FAILED
architecture workflow safety: FAIL (2 issue(s))
- missing skill file: architecture-design-workflow/references/human-action-request.md
- missing skill file: architecture-design-workflow/templates/human-action-request.md
```

该失败只由新行为所需的两个核心文件缺失引起，不是语法、Runtime 或环境错误。

## GREEN evidence

### Independent forward behavior

同一独立只读 Agent 重新完整读取更新后的 core skill，未读取 change artifacts、tests 或预期结果，分别处理 routing、两个不同 Owner 的风险接受、current packet 四选一和缺失 revision brief 四个场景。结果：

1. routing 首屏包含建议、有限备选、长期归属后果、准确回复和非授权边界；
2. 两个 Risk ID 拆成不同 Owner 的原子 action，逐项给出 option consequences、exact response 和 after response；
3. packet 决策能比较四种中文后果、R&D/OpenSpec 边界、立即写入与终态影响；
4. 有效 `revision_requested` 保持生效，`revision_scope=missing` 通过独立 `design_input` 补齐，旧 packet 不改写。

Agent 初次 GREEN 复核发现并推动收口三个细节：`ARCH-CONTROL` 支持多个 current actions、`revision_scope` 使用独立字段、Human Action Request 不新增 canonical artifact 或 `planned_writes`。二次只读复核三项均为 PASS。

保留的 Codex behavior evidence：

- `tests/evidence/architecture-design-workflow/reviewable-subject-project-routing.codex.md`
- `tests/evidence/architecture-design-workflow/reviewable-multi-owner-risk-acceptance.codex.md`
- `tests/evidence/architecture-design-workflow/reviewable-current-packet-decision.codex.md`
- `tests/evidence/architecture-design-workflow/revision-requested-missing-brief.codex.md`

### Verification commands

```text
uv run --with pyyaml python /Users/jie.hua/.codex/skills/.system/skill-creator/scripts/quick_validate.py architecture-design-workflow
Skill is valid!

python3 -m unittest tests.test_architecture_design_workflow_runner
Ran 14 tests ... OK

bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime codex
architecture workflow safety: PASS (static + codex behavior, 27 fixtures)

openspec validate architecture-human-action-requests --type spec --strict
Specification 'architecture-human-action-requests' is valid

openspec validate architecture-design-artifacts --type spec --strict
Specification 'architecture-design-artifacts' is valid

openspec validate architecture-design-governance --type spec --strict
Specification 'architecture-design-governance' is valid

openspec validate architecture-approval-packets --type spec --strict
Specification 'architecture-approval-packets' is valid

openspec validate add-human-centered-architecture-decision-gates --strict
Change 'add-human-centered-architecture-decision-gates' is valid
```

## Verification limitations

真实 Skill import、Agent binding、平台 delivery 和 sandbox acceptance 均不在 core change 授权范围。题面未提供真实 Issue、具名 Decision Owner 与稳定 material refs，因此 behavior evidence 使用明确占位符，不声称完成人类访问验证。

GitNexus 索引已在 baseline HEAD 重建并保持 current，但 MCP graph reader 因本地 LadybugDB storage version 43 与 reader version 42 不兼容而不可用；实现调查降级为有界源码检查，没有把“未发现”写成“不存在”。
