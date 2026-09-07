## 1. RED contracts

- [x] 1.1 扩展 execution continuation tests/fixtures，覆盖 v2 required fields、responsibility vocabulary/cardinality、authority identity、standalone evidence、v1 migration/supersession
- [x] 1.2 扩展 adapter tests/fixtures，覆盖 blocker schema/rendering、Member mapping、valid/invalid reply、resume task readback、rollback 和 needs-new-mandate
- [x] 1.3 运行 targeted tests，确认旧 Skill 因缺少 v2/blocker contract 产生预期 RED

## 2. Portable core v2

- [x] 2.1 更新 `architecture-design-workflow/SKILL.md`、workflow mandate 与 continuation references，实施 v2 fields/states/cardinality
- [x] 2.2 实施 v1 dual-read/audit-only、v2-only write、deterministic mapping 和 supersession
- [x] 2.3 更新 architecture review、solution design、human action request，使用 authority identity 并隔离 dependency input/human decision
- [x] 2.4 更新 arch-control/human-action templates，删除 portable fixed-role required table
- [x] 2.5 增加 architecture blocker reference/template 与 needs-new-mandate outcome
- [x] 2.6 运行 standalone/topology validation，确认 core 不依赖 Multica/Team；使用 `uv run --with pyyaml` 补齐 validator 运行依赖，两个 Skill 均通过 quick validation

## 3. Optional Multica adapter

- [x] 3.1 更新 adapter SKILL/core compatibility/execution handoff，实施 v1/v2 read 与 actor/responsibility mapping
- [x] 3.2 更新 operation manifest/status reconciliation 与 blocker projection template
- [x] 3.3 实施 reply validation、received→handoff→task readback→in_progress 顺序
- [x] 3.4 实施 no-owner prewrite failure、invalid reply no-op 与 resume failure blocked rollback
- [x] 3.5 验证 blocker reply 不扩大 Review/approval/implementation authority

## 4. Verification

- [x] 4.1 运行 targeted/full unit tests、architecture workflow safety 与两个 Skill quick validation
- [x] 4.2 运行 OpenSpec strict validation、`git diff --check` 与 topology scan
- [x] 4.3 运行 GitNexus detect-changes，记录仓库/HEAD/index、affected symbols/processes 与 Markdown 边界
- [x] 4.4 输出两个既有 Skill 的可覆盖同步 package/digest；不修改 Multica core 或创建 live 资源

## 5. Discovery-first Blocker v2

- [x] 5.1 增加 RED fixtures，覆盖 blocker v1 audit-only/v2-only-write、自动发现唯一/多个/零候选、`provide_input|request_discovery`、中文 normalization、placeholder no-op 和 authority 不扩张，并观察预期失败
- [x] 5.2 更新 portable core reference/template/SKILL，实施 `architecture_blocker_action_v2`、`automatic_before_human`、两种 response mode 与三类 discovery 完成结果
- [x] 5.3 更新 optional adapter reference/template/SKILL，实施 discovery-first、简明中文回复、发现 handoff/readback、失败回滚与 v1 supersession
- [x] 5.4 运行 targeted/full tests、两个 Skill quick validation、OpenSpec strict validation、`git diff --check`、topology scan 与 GitNexus detect-changes，并输出新的可同步 digest

## 6. 普通用户可理解的 Blocker v2 首屏

- [x] 6.1 先增加失败 fixtures/tests，覆盖唯一业务问题、三个自然语言回复、machine evidence 自动派生、条件性来源追问，以及默认首屏禁止企业治理术语
- [x] 6.2 更新 portable core reference/template/SKILL，以正向渲染 recipe 定义业务问题和人类声明 profile，同时保持 Team-topology-neutral
- [x] 6.3 更新 optional Multica adapter reference/template/SKILL，消费“由我负责 / 负责人是… / 我不确定，请团队给出建议”，并保持验证 handoff、task readback 与权限不扩张
- [x] 6.4 运行 targeted/full tests、两个 Skill quick validation、OpenSpec strict validation、`git diff --check` 与 GitNexus detect-changes，输出待同步 digest

## 7. Owner 手动材料检查

- [x] 7.1 增加 RED fixture/test，覆盖显式 owner-manual 成功、严格默认、identity/digest 失败和“材料打不开”修复路径
- [x] 7.2 更新 portable core 与 optional adapter，实施 `owner_manual`、`manual_check_required`、stable same-Issue entry 和不伪造 `opened` 的边界
- [x] 7.3 更新本仓库部署指令与 OpenSpec 记录，明确无需 Agent 登录浏览器即可进入 `in_review`，但正式 packet approval 继续严格门禁
- [x] 7.4 运行验证、同步两个既有 Skill/部署指令，并在 UNIDRAG-12 重试当前 A0 决策交付与状态回读
