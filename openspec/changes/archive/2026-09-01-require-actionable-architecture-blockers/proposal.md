## Why

`architecture-design-workflow` 已通过 portable v2 actor contract 消除固定 Team 拓扑，但 `architecture_blocker_action_v1` 仍把 Owner、authority 与 evidence 内部字段直接交给用户填写。UNIDRAG-12 的真实验收中，空值和照抄占位符都被安全 no-op，却证明用户无法理解这些“正式值”。需要把 blocker 升级为 discovery-first v2：团队先调查，用户不知道时可以直接请求调查并获得建议。

## What Changes

- **BREAKING**：新增 `architecture_workflow_mandate_v2` 与 `execution_continuation_v2`，使用通用 actor、authority identity、受控 responsibility 和 portable evidence；v1 双读/audit-only，所有新 attempt 只写 v2。
- **BREAKING**：原 discovery-first `architecture_blocker_action_v2` 保留只读审计；新增 `architecture_blocker_action_v3`，以普通业务问题、人类声明和后台证据派生修复现场可用性，所有新 blocker、retry 和 superseding attempt 只写 v3。
- 在人类输入前执行授权范围内的只读发现；唯一 verified binding 自动继续，多个候选只要求用户作简单选择，没有候选时发布有证据的组织阻塞。
- 新增 `provide_input|request_discovery` 双回复模式；用户可直接表达“不知道，请调查并给出建议”，adapter 创建并回读既有 coordination/research actor 的发现任务后才投影 `in_progress`。
- 内部 `owner_identity`、`authority_scope`、`evidence_ref/version/date` 等字段保留为 machine evidence，不作为默认人类表单。
- 将零候选后的 blocker 改为“一个业务问题 + 最多三个自然语言回复选项”：用户只需说明“由我负责”“由某人负责”或“我不确定，请团队给出建议”；系统从评论作者、current Action、问题中已冻结的业务范围、revision 与时间自动派生 machine evidence。只有用户明确表示已有正式记录，或部署环境明确要求外部权威记录时，才追问可打开的来源链接。
- 无法唯一解析 instruction owner 时，在任何平台写入前返回 `needs_new_mandate_v1` 非成功结果，不创建 blocker/handoff 或孤儿 `in_progress`。
- `architecture-design-workflow` core 删除固定 Team/Agent required fields，并定义 standalone `local_session|shared_artifact` accepted/active evidence。
- optional `multica-architecture-approval-adapter` 读取 blocker v1/v2/v3，把通用 actor/responsibility 映射到既有 Member/Agent；v1/v2 只读审计，新写 v3，执行 discovery-first、发布一个普通业务问题，并在两类有效回复后回读恢复/发现 task 再投影 `in_progress`。
- 本 change 取代已通过 `--skip-specs` 归档的 `require-executable-architecture-continuations`，以 topology-neutral requirements 保留其连续性保证。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `architecture-workflow-operation-automation`: mandate/continuation v2、standalone evidence、discovery-first blocker v3、双回复模式、人类声明、后台证据派生、无 Owner 非成功结果与真实恢复状态。
- `multica-architecture-adapter-activation`: blocker v1/v2/v3 compatibility、Member/Agent mapping、普通业务问题 projection/reply consumption、task readback 和失败回滚。

## Impact

- Portable core：`architecture-design-workflow/SKILL.md`，workflow mandate、execution continuation、architecture review、solution design、human action request references，`arch-control`/`human-action-request` templates。
- Optional adapter：`multica-architecture-approval-adapter/SKILL.md`，core compatibility、execution handoff/task readback、operation manifest、status/reconciliation、blocker projection/consumption reference/template。
- Tests/fixtures：architecture workflow safety、execution continuation、adapter contract、v1/v2 compatibility、standalone 与 blocker cases。
- 人类可用性契约：阻塞首屏禁止默认出现 `RACI`、组织/服务目录、策略批准记录或 machine binding 字段清单；必须解释“为什么暂停”、给出团队建议、只问一个普通业务问题，并说明回复后由谁验证与继续。
- 材料访问契约：`design_input|architecture_review` 在唯一 Owner 已明确选择自行用网页/手机检查材料时，可使用 `owner_manual`；系统仍自动验证附件 identity/digest 和稳定入口，逐 scope 记为 `manual_check_required` 并进入 `in_review`，同时提供“材料打不开”的自动修复回复。正式 packet approval 仍使用严格 automatic readiness。
- Runtime：覆盖同步既有 Skill package；不修改 Multica core，不创建 Team、Agent、Issue、watchdog 或其他资源。
