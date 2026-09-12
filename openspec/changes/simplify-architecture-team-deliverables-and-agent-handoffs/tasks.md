## 1. 基线与影响门禁

- [x] 1.1 确认依赖变更 `allow-owner-attested-formal-architecture-approval` 已完成、严格校验通过并已集成或冻结为本次实施可引用的准确基线，保留当前未提交内容且不得覆盖
- [x] 1.2 刷新并绑定 `my_dev_skills` GitNexus 索引，对 core/adapter 入口及将修改的具体 contract symbols 执行 upstream impact；对 `UNKNOWN` 结果用文本引用和现有 specs/tests 交叉验证，对 `HIGH|CRITICAL` 在任何源文件编辑前报告风险
- [x] 1.3 建立当前行为清单，逐项映射三附件审批、Human Action、Control/Research/Review/Packet、continuation/handoff comment、owner-attested binding、历史 reader 和 runtime activation 到准确文件与现有 fixture
- [x] 1.4 回读并冻结 Archify 候选依赖的名称、版本、源仓库完整 revision、归档 SHA-256、支持图型和 CLI 命令契约；分别记录本机 Runtime 可用性与目标 Multica workspace 导入/绑定状态，不把两者混为一谈

## 2. Core RED contracts

- [x] 2.1 在 architecture workflow safety/runner 测试中加入失败断言：`ARCH-DESIGN` 是唯一 mandatory human artifact，Control/Research/完整 Review/Packet 不得进入主审批材料集合
- [x] 2.2 加入 Design maturity fixtures，分别固定 `directional` 禁止 `approved_for_spec`、`spec_ready` 允许 OpenSpec handoff、`implementation_ready` 保留直达实施指导语义
- [x] 2.3 加入 `architecture_design_impact_v1` fixtures，固定无架构影响只更新内部 evidence、有影响或未知影响必须新建 Design/Review/manifest 并 supersede Action
- [x] 2.4 更新 continuation/handoff RED contract，要求 accepted/active 内部 evidence 且禁止 dedicated human handoff comment，同时保留无人执行、错误 authority 和 stale attempt 的 fail-closed 用例
- [x] 2.5 加入旧 attempt compatibility fixture，证明旧三附件 Action 不会被新 reader 原地解释为单 Design Action
- [x] 2.6 加入 `architecture_visual_manifest_v1` RED fixtures，覆盖必需总览图、明确 `diagram_not_applicable`、最多两张附加图、三层质量声明、light/1440×900 preview receipt/digest、`browser_evidence=failed|skipped` 与 `visual_review=failed|skipped` 的 fail-closed 结果、stale digest、语义 Review 失败和纯渲染变化的 impact classification

## 3. Core Skill 与模板实现

- [x] 3.1 更新 `architecture-design-workflow/SKILL.md` 的 artifact taxonomy、责任边界、状态转换和 progressive disclosure，引入 `human_review_surface_v1` 与 `architecture_internal_evidence_v1`
- [x] 3.2 更新 solution-design reference/template，使 `ARCH-DESIGN-vN.md` 独立包含完整总体方案、`design_maturity`、开放项 Owner/关闭条件和下游阶段边界
- [x] 3.3 更新 architecture-review reference/template，将 Review 收敛为 version-bound findings/verdict，并强制任何改变方案的 finding 通过新 Design 版本关闭
- [x] 3.4 更新 approval packet/human gate reference/template，使 Packet 成为 machine-only immutable manifest，current Action 继承准确 snapshot，人类只打开 canonical Design
- [x] 3.5 更新 Human Action reference/template，使首屏包含方案摘要、maturity、简短 Review、关键风险、后果、一个 Design 入口和一个原子 Action，机器字段后置或隐藏
- [x] 3.6 更新 execution continuation、Control、Research 和 R&D handoff references/templates，将 Agent payload/result/readback 与中间状态默认写入内部 evidence，最多输出一次终态人类摘要
- [x] 3.7 实现 `architecture_design_impact_v1` 判断表、保守 unknown 处理、Design/Review/Action supersession 规则和对应 normalized result 字段
- [x] 3.8 运行 core focused tests，确认新增 RED cases 转绿且既有 project routing、OpenSpec prohibition、independent review、owner_manual、publication digest 和 human approval hard gates 继续通过
- [x] 3.9 更新 solution design、review、impact、approval packet 与 R&D handoff 契约，使 required Design 绑定 Archify Typed JSON/HTML、同一成功 `visual-check` receipt 的 light/1440×900 PNG preview 及 digests；明确只有 deliver/browser/visual/semantic 四项通过才能进入正式 Review，Reviewer 以 diagram/node/edge/message/state ID 报告只读 finding，R&D 优先复用批准图

## 4. Multica Adapter RED contracts

- [x] 4.1 扩展 adapter fixture schema/cases，固定正式审批 comment 恰好包含一个 canonical Design Markdown attachment，并明确禁止 Review、Packet、Control attachments
- [x] 4.2 增加 automatic 与 owner_attested 双模式用例，验证 Design human access、内部 Review/manifest digest、current Action、`materials_opened`、材料打不开恢复和 stale reply no-op
- [x] 4.3 增加 `multica_human_action_material_bundle_v2` 与内部 evidence 用例，证明 progress、continuation、handoff/readback、reconciliation 和 retry 不生成普通 Issue comment
- [x] 4.4 增加 legacy bundle/attempt reader 用例，证明旧对象保持可审计、新 writer 不修改或消费为 v2
- [x] 4.5 增加 core/adapter compatibility matrix 用例，证明 pair 错配在首笔平台写入前失败
- [x] 4.6 增加 Archify material/activation fixtures，固定一 canonical Design entry、derived visual resources、preview receipt/digest 与平台 ref 分离、手机静态预览实开验证、browser/visual skipped 或 failed 时 readiness unavailable、四个目标 Agent 的 author/review-only additive binding、部分绑定失败和非目标 Agent 不绑定

## 5. Multica Adapter 与展示实现

- [x] 5.1 更新 adapter `SKILL.md` 的 preflight、manifest、ordered writes、readiness、decision consumption、reconciliation 和 failure retention，消费新的双 surface contract
- [x] 5.2 更新 approval comment 与 Human Action templates，输出一份 Design、简短 Review/推荐/风险、四种决定后果和具名 Action，移除三附件与完整机器字段要求
- [x] 5.3 将 material bundle 升级为 `multica_human_action_material_bundle_v2`，绑定唯一 Design attachment；可选 PDF 仅作为 `derived_non_authoritative` 表示且不改变 canonical digest
- [x] 5.4 更新 durable evidence、human access、target-human mapping、readiness 和 decision evidence references/templates，使 Design 接受 client access/owner-attested 验证，Review/Packet/Control 使用内部 machine readback
- [x] 5.5 更新 operation manifest、task result、metadata projection、continuation/handoff/readback 与 reconciliation references，使内部对象保留稳定 ref/digest/supersession 且不创建 dedicated human comments
- [x] 5.6 更新 adapter validator 与 fixtures schema，只允许新 attempt 写 v2 surfaces，同时保留 frozen legacy readers 和 exact current-Action decision binding
- [x] 5.7 运行 adapter focused contract tests，确认新增 cases 转绿且 wrong actor、digest drift、mapping ambiguity、partial delivery、duplicate retry、superseded decision 和 owner-attested failure cases 继续 fail closed
- [x] 5.8 更新 material bundle、approval comment、durable evidence、readiness 和 manifest，使视觉资源始终标记 `derived_non_authoritative`，HTML 不成为 mandatory human entry；把 artifact-local light/1440×900 preview identity 投影为外部平台 ref 并回读 digest/requested-client 可读性，任何 required visual failed/skipped/stale/mismatched receipt、preview 或 review 都使 readiness unavailable

## 6. Runtime、导入与迁移说明

- [x] 6.1 更新本仓库安装/验证说明，记录 core/adapter compatibility revisions，并在隔离临时 HOME 验证 Claude/Codex 均解析到相同仓库 bytes；不得修改真实用户 home 下的 Skill
- [x] 6.2 更新 Multica activation runbook，要求显式选择现有 workspace、冻结 core/adapter/Archify 版本与 digest、使用 conflict-fail import 和 additive binding、冲突停止、版本回读并只对新 attempt 生效
- [x] 6.3 更新 sandbox acceptance 清单，验证单 Design canonical entry、Architecture 总览图、deliver/browser/visual/semantic 全部通过、automatic/owner-attested Design access、内部 Review/manifest readback、current Action、supersession、failure retention、light/1440×900 preview 在手机端实际可辨认且无 Agent handoff 评论
- [x] 6.4 记录历史迁移策略：旧 comments/attachments/packets/decisions 全部只读保留，live attempt 继续 frozen contract 或通过显式新 attempt supersede，绝不原地转换
- [x] 6.5 检查可复用的 workspace Team/Agent 配置与导出脚本；更新仓库内配置源以记录 Architecture Team 与 R&D Team 的四个目标 Agent、其 author/review-only 指令、默认不绑定角色和批准图复用规则，并提供重新导入说明而不执行未经授权的真实 workspace 写入
- [x] 6.6 在隔离 workspace 演练 Archify import 与 additive binding：Solution Architect/Product & Spec Engineer 为 author profile，Architecture Reviewer/Solution Review Architect 为 review-only profile；逐 Agent 回读 skill ID 与完整指令，确认其他 Lead/Analyst/Development/Code Review/QA/Integration/Watchdog 未被隐式绑定
- [x] 6.7 更新仓库 `README.md` 中 architecture core/adapter 的用户说明，明确唯一 mandatory Design、无需人工打开 Review/Packet/Control 或复制 packet digest、内部 Agent evidence、required visual fail-closed gate 和四个 Archify 目标 Agent；保留旧 attempt 只读兼容说明

## 7. 完整验证与交付证据

- [x] 7.1 运行所有 architecture core、execution continuation、Multica adapter、schema/fixture 和安装测试，保存准确命令、版本、通过数量与限制
- [x] 7.2 运行全仓测试与 Skill quick/safety validation，确认没有旧 writer 路径继续要求三附件、Research/Control 人类入口或 dedicated handoff comment
- [x] 7.3 运行 `openspec validate simplify-architecture-team-deliverables-and-agent-handoffs --type change --strict`、全量 OpenSpec validation 和 `git diff --check`
- [x] 7.4 扫描实现及 artifacts 中的未完成占位标记、相互矛盾的 mandatory materials、旧/new contract 名称漂移和未覆盖 requirement，并修正所有发现
- [x] 7.5 运行 GitNexus `detect-changes --scope all`；若结果 partial/truncated/UNKNOWN，则补充 compare 或文本/测试证据，不得报告干净影响
- [x] 7.6 输出最终实现 evidence，列出实际修改范围、core/adapter revision pair、未触碰的历史对象、真实 runtime/workspace activation 的 `not_run|authorized result` 和后续人工步骤
- [x] 7.7 运行 pinned Archify 的 showcase validate/deliver/visual-check 示例和图文语义 review fixture，验证失败的 deliver 不复用旧 HTML、browser evidence 不冒充 visual review、light/1440×900 preview 来自当前成功 receipt、任一 required status failed/skipped 都 fail closed、R&D 架构影响返回 Architecture Team，并记录全部 artifact digests 与限制
- [x] 7.8 对 `README.md`、core/adapter references/templates 和 current specs 执行旧契约扫描，断言新 writer/用户说明不再要求三附件必读、人工复制 packet digest 或 dedicated Agent handoff comment；仅 frozen legacy reader/fixture 可保留旧术语
