## Context

现有架构流程把“严谨性”实现成了大量独立的人类可见产物：Design、Research、Control、Review、Approval Packet、continuation 和 handoff 均可能进入同一个 Issue 时间线。以 UNIDRAG-12 为代表的运行结果证明，流程能够保存详细证据，但审批人需要在多份附件和大量控制评论中重建总体方案；Agent 的执行记录也与需要人作决定的内容竞争注意力。

本变更不降低现有的版本、digest、独立评审、唯一 Owner、current Action、owner-attested/automatic access、supersession 和 fail-closed 门禁。它只重新划分两个 surface：

- `human_review_surface_v1`：人类评审和决定所需的最小完整界面。
- `architecture_internal_evidence_v1`：Agent 执行、状态机、审计、重试和可恢复性所需的完整证据。

核心 Skill 仍是 portable source of truth，Multica Adapter 只负责平台投影。已有 `allow-owner-attested-formal-architecture-approval` 完成变更作为兼容基线；其未提交工作树内容必须先完成集成，实施时不得覆盖。

Archify `v2.17` 已作为独立第三方 Skill 安装在本机 Runtime，源仓库当前 revision 为 `bb71ccdd64cd3a74ba7cbd25bbacc7382da34410`，候选导入归档 SHA-256 为 `ed178d2ddd8861db1b8e867f32be7764bdec221d44568c37b6ae157c5e7f111c`。它能够从 Typed JSON 生成 Architecture、Workflow、Sequence、Data Flow 和 Lifecycle 独立 HTML，并提供 `validate`、`deliver`、`visual-check` 和 Architecture Delta。当前 `unidocs-rag` Multica workspace 尚未导入该 Skill，也没有 Agent 绑定；Runtime 本机安装不得被当作 workspace 可用性证据。

## Goals / Non-Goals

**Goals:**

- 让 `ARCH-DESIGN-vN.md` 成为唯一必须由人类打开的完整总体方案，并能够独立支持内部评审和后续研发分解。
- 让 Reviewer 继续保持独立 authority，但只产生聚焦的 findings/verdict，避免复制 Design。
- 保留 machine-verifiable approval manifest，同时把 packet、Control、Research、readiness 和 Agent handoff 从默认人类时间线移出。
- 使 Multica 正式审批固定为一份 Design 附件、一个简短决策摘要和一个 current Action。
- 用明确的 Design maturity 和 impact classification 控制“是否可进入下一阶段”以及“是否真的需要重发版本”。
- 让复杂 Design 获得少量、语义明确、可复现且可独立核验的 Archify 图，同时保持 Design Markdown 是唯一 canonical 总体方案。
- 以职责最小化方式把 Archify 引入 Architecture Team 与 R&D Team，严格分离创作、只读评审和纯消费角色。
- 让 core 与 adapter 以兼容 revision 原子激活，新旧 attempt 互不重解释。

**Non-Goals:**

- 不取消独立评审、人类批准、风险接受、Owner binding、digest 或 supersession。
- 不删除历史 Issue 评论、附件、task evidence 或旧 packet。
- 不修改 Multica 应用代码、数据库或 API；本变更只更新 Skills、契约、模板、fixtures 和验证。
- 不改变 Architecture Team 的 Lead、Analyst、Architect、Reviewer 角色数量或组织归属。
- 不让 Design 承担运行日志、完整 raw evidence、重试记录或平台 readback 的存储职责。
- 不复制或修改 Archify 源码，不把第三方图表 schema 合并进 portable core，也不要求每个 Agent 或每个 Issue 都生成图。
- 不让图取代正文中的边界、接口、权衡、NFR、迁移、风险、Owner 或验收说明。
- 不自动迁移运行中的旧 attempt，也不把新合同应用于历史批准决定。

## Decisions

### 1. 一份 Design 是唯一必读的人类 canonical artifact

每个可进入正式 Review 的版本必须有一个完整的 `ARCH-DESIGN-vN.md`。它包含 executive summary、上下文、驱动因素、系统边界、组件、接口、数据/控制流、关键失败流、安全/隐私/可靠性/性能/容量/成本/可观测性、方案权衡、迁移/回滚、风险、已确定/未确定事项、验收方法和下一步分解。

Design 新增：

```text
design_maturity = directional | spec_ready | implementation_ready
```

- `directional`：方向和主要边界已形成，但仍存在会影响 spec 的未决事项。
- `spec_ready`：足以创建 OpenSpec proposal/spec/tasks；实现仍可能需要测量、详细设计或平台选择。
- `implementation_ready`：接口、约束、关键非功能目标、迁移/回滚和验收条件已足以直接指导实施。

任何非 `implementation_ready` Design 必须在同一文档列出剩余项、唯一 Owner、证据缺口、关闭条件及其阻止的下游阶段。maturity 是 Design 自身属性，不等同于 Reviewer conclusion 或 human approval。

选择这一方案而不是“保留三份主附件但增加索引”，因为索引仍要求审批人跨文档重建结论，也不能保证后续研发引用唯一方案版本。

### 2. Review 是独立判定，不是第二份方案

`ARCH-REVIEW-vN.md` 保留准确 Design ref/version/digest、reviewer authority、finding、证据、影响、Owner、关闭条件和唯一 conclusion。它不得重复 Design 的背景、组件说明和完整权衡。

- `BLOCKED|NEEDS_REVISION`：回到研究/设计，由 Architect 发布新 Design，旧 Review 保持只读。
- `APPROVABLE_WITH_WARNINGS|APPROVABLE`：向人类表面投影一段精简 Reviewer summary；完整 Review 仍保存为内部 evidence，可按需审计。

如果 finding 改变方案内容，必须先进入新 Design 版本，不能只在 Review 中附加“修正后视为通过”。这确保最终审批的 Design 本身就是完整结论。

### 3. Packet 保留为隐藏的 immutable approval manifest

不删除 `ARCH-APPROVAL-PACKET`，而是重新定义为 `machine_only` manifest。它继续冻结：

- work item、attempt、core/adapter contract revision；
- Design 和 Review refs/versions/raw-byte digests；
- Design maturity、Reviewer conclusion、accepted risks；
- Decision Owner/authority、current Action、合法决定；
- access/readiness profile、supersedes 和生成时间。

人类不需要打开 packet，也不需要在回复中复制 packet digest。current Action 从已验证 manifest 继承准确 snapshot；adapter 在消费回复前重读 action、Design attachment、Review evidence、manifest、Owner、projection 和 supersession。任何漂移都 fail closed。

选择隐藏 packet 而不是删除 packet，因为现有安全模型依赖其不可变 snapshot 和 supersession；删除会把复杂绑定重新分散到评论和 metadata，并降低审计可靠性。

### 4. 人类审批面固定为一个可读入口

`human_review_surface_v1` 包含：

```text
design: ref + version + digest + one human-readable attachment/link
design_maturity
review: conclusion + concise findings/warnings summary
recommendation: value + rationale + confidence
decision_owner
current_action_id
allowed_decisions + consequences
material_unavailable_response
minimal current/superseded identity
```

正式架构审批在 Multica 中必须表现为：

1. 首行准确 mention 唯一 Owner；
2. 一段方案摘要、成熟度、Reviewer conclusion、关键风险和推荐；
3. 恰好一份 canonical Design Markdown 附件；
4. 一个原子 current Action 及四种决定后果；
5. owner-attested 模式继续要求 `materials_opened`，材料打不开走专用恢复回复。

Research、Control、完整 Review、Packet、digests、task result、manifest 和 reconciliation 不作为必读附件。它们只能放在内部证据中，或作为首屏之后的可选“审计详情”入口；缺少可选入口不得阻止人类决定，只要机器能完成所需 readback。

### 5. 人类时间线与 Agent 执行通道分离

默认允许进入普通 Issue 时间线的事件只有：

- 需要人提供且自动 discovery 无法解决的单项 `dependency_input`；
- `design_input|architecture_review|architecture_approval` 的一个原子决定；
- 新 Design 正式交付或替代版本通知；
- 批准后的最终架构交付/研发交接摘要；
- 真实 blocked/rejected/terminal 状态摘要。

下列内容默认必须进入 `architecture_internal_evidence_v1`，不得各自生成普通评论：Research 中间结果、Control 状态转换、packet/readiness、continuation、Agent handoff/readback、delivery reconciliation、retry、digest 校验和状态投影回读。

内部 continuation 仍必须包含唯一 next actor/authority/responsibility、input refs、closing condition、state、evidence refs 和 supersession，并从 runtime task 或耐久 evidence 回读 `accepted|active`。可观测性通过 task evidence 保留，而不是通过人类评论数量实现。

### 6. impact-based revision 决定是否产生新的人类版本

新输入先生成 `architecture_design_impact_v1`，结果只能是：

- `no_architecture_impact`：仅补充原始证据、日志、状态、措辞或不改变结论的实现细节；更新内部 evidence，不创建新 Design/Review/审批评论。
- `architecture_impact`：改变 recommendation、系统/责任边界、外部接口或一致性、安全/隐私/可靠性、容量/性能/成本约束、迁移/回滚、accepted risk、未决人类决定、validation criteria 或 maturity；必须创建新 Design，重新独立 Review，并 supersede 旧 Action/manifest。

impact 记录必须给出 changed inputs、判断依据、受影响章节和 verifier。未知或无法证明时按 `architecture_impact` 处理，不能以减少评论为由复用旧批准。

### 7. 研发交接只从批准 Design 派生

`ARCH-RD-HANDOFF` 保留为 downstream Agent artifact，但它只引用批准 Design、maturity、Review conclusion、批准证据、目标项目、约束、开放项和建议的 OpenSpec 分解。handoff 的完整 payload/readback 存入内部 task evidence；人类时间线只显示一次简短交接摘要，不发布专门的 Agent-to-Agent handoff 评论。

`approved_for_spec` 最低要求 `design_maturity=spec_ready`；若只有 `directional`，批准可以是 `approved_design_only`，但不能生成可执行的 R&D handoff。`implementation_ready` 不是批准的前提，但必须准确传给下游。

### 8. core 与 adapter 采用兼容 revision 原子激活

core 输出新增 `human_surface_contract=human_review_surface_v1` 和 `internal_evidence_contract=architecture_internal_evidence_v1`；adapter 必须声明并验证兼容 core revision。激活顺序为：

1. 合并/归档前置 owner-attested change；
2. 更新 specs、core、adapter、templates、fixtures 和 tests；
3. 运行 focused/full contract tests 与 OpenSpec strict validation；
4. 生成并验证用户可执行的 Claude/Codex Skill 链接刷新步骤；仓库实现不得直接修改用户 home 下的 Skill；
5. 在 Multica sandbox workspace 原子导入/绑定 core 与 adapter；
6. 用新 Issue 验证一附件审批、内部 handoff、Owner reply 和 supersession；
7. 只让新 attempt 使用新 revision。

旧 attempt 继续按冻结 revision 读取；若要升级，必须创建明确 superseding attempt，保留旧评论、附件、packet、Action 和 decision evidence。不得原地把旧三附件 Action 解释成新单附件 Action。

### 9. Archify 是 Design 的受控 visual companion，不是第二份总体方案

`ARCH-DESIGN-vN.md` 保持唯一 `human_canonical`。需要图时，Solution Architect 在完成方案骨架和证据映射后创建 `architecture_visual_manifest_v1`，每张图绑定：

```text
diagram_id
diagram_type = architecture | workflow | sequence | dataflow | lifecycle
purpose + design_sections
source_ref + specification_sha256
artifact_ref + artifact_sha256
static_preview_ref + digest + capture(theme=light, viewport=1440x900)
repository_revision | not_applicable
delivery_validation
browser_evidence
visual_review
reviewer_findings
supersedes
```

Typed JSON 是可编辑图源；交互 HTML 和静态预览都是 `derived_non_authoritative`。对 required diagram，静态预览不得为 `none`：它必须取自绑定当前 HTML digest 的最新成功 `visual-check` receipt 中 light/1440×900 capture，并记录该 PNG 的原始字节 SHA-256。Design 内只冻结 artifact-local preview identity；Multica 上传后产生的平台 comment/attachment ref 作为外部 projection 写入 `architecture_internal_evidence_v1`，不得回写 Design bytes。只有 `diagram_not_applicable` 才没有 visual manifest 和静态预览。

Design 正文必须解释图的结论并引用准确 diagram ID，读者即使无法运行交互 HTML也能理解完整方案。静态预览通过 Design 中的内嵌预览或同一 Design surface 上的稳定 supporting-resource link 访问，但不增加第二个 mandatory human entry，也不改变 Design raw-byte digest 的权威性。activation sandbox 必须在 requested mobile scope 实际打开 preview projection，并确认标题、主要组件/边界和关键标注可辨认；仅上传成功、HTTP 200 或 digest 一致不能证明 mobile-readable。正式 Issue 的 `automatic` profile 复用同一检查；`owner_manual` profile 则验证 sandbox 已认证的 client route、当前 preview identity/digest 和稳定入口，记录 `manual_check_required`，由 Owner 的一次 `materials_opened` 声明覆盖完整 Design surface，不增加第二个材料声明。

每张正式图执行以下冻结顺序：

1. 作者使用当前请求语言，中文场景写入 `meta.locale=zh-CN`，默认 `quality_profile=showcase` 和静态表现；
2. `validate` 在每次候选编辑后执行，最多两轮聚焦修复；
3. 候选冻结后执行 `deliver`，记录 specification/artifact SHA-256 和 9/9 artifact checks；
4. 只有当前 `deliver` 成功后才能执行 `visual-check`，避免检查旧的 last-good HTML；
5. `visual-check` 必须对当前 artifact 返回 `passed`，并从同一 receipt 选择 light/1440×900 PNG capture、计算 preview digest；`failed|skipped` 都使 required diagram 未就绪，补充人工浏览记录只能作为附加证据，不能改写 browser status；
6. 独立 Reviewer 对冻结图执行语义、证据和视觉判断，只有 `visual_review=passed` 且无阻断语义 finding 才完成 visual chain；`failed|skipped` 都不得进入正式架构 Review；
7. adapter 投影后分别回读 HTML、preview 和 requested-client access；preview 缺失、digest 漂移或手机端不可辨认时 packet readiness 保持 unavailable，但不改变已形成的 Architecture Review conclusion。

required diagram 的 gate 矩阵固定如下，其他证据不得替代对应列：

| Evidence | 可进入正式 Architecture Review | 可进入 packet readiness | 恢复路径 |
|---|---:|---:|---|
| `deliver=passed`、`browser_evidence=passed`、`visual_review=passed`、语义 finding 已关闭 | 是 | 还需平台 preview/access 验证 | 继续 adapter 投影 |
| `deliver=failed` | 否 | 否 | 修复 Typed JSON 后重新 validate/deliver，禁止复用旧 HTML |
| `browser_evidence=failed|skipped` | 否 | 否 | 在 Chrome/Chromium 可用环境重新运行当前 artifact 的 `visual-check` |
| `visual_review=failed|skipped` 或存在阻断语义 finding | 否 | 否 | 作者发布修订 candidate，由独立 Reviewer 重新检查 |
| preview/platform digest 不匹配，automatic scope 不可读，或 owner-manual stable route 未验证 | Architecture Review conclusion 不变 | 否 | 重新投影当前 preview 或修复访问后重新 readback |

选择 visual companion 而不是把 HTML 定义为 canonical artifact，是为了同时获得更清晰的评审体验和单一方案来源；选择 Typed JSON 而不是手工截图，是为了让版本、差异和修复能够被机器验证。

### 10. 图表按决策价值触发，Architecture Design 与 R&D Design 使用不同默认值

Architecture Team 处理复杂架构议题，因此每份可正式 Review 的 `ARCH-DESIGN` 默认需要一张 6–12 个主要节点的 Architecture 总览图；只有图无法增加结构理解且 Reviewer 接受明确 `diagram_not_applicable` 理由时才可省略。额外图默认不超过两张，并按语义触发：

- 组件、服务、存储、部署或信任边界使用 Architecture；
- 多角色、审批、发布、回滚或 Runbook 使用 Workflow；
- API、鉴权、缓存回源、异步回调或跨服务关键路径使用 Sequence；
- RAG/ETL、数据血缘、PII、转换、存储和消费者使用 Data Flow；
- 状态、等待、重试、取消和终态使用 Lifecycle。

R&D Team 不默认重画上游方案。Product & Spec Engineer 首先引用批准 Design 的 diagram ID/ref，仅在 OpenSpec 需要实现级流程、时序、数据或状态细节且上游图不覆盖时生成一张 scope-local delta visual。Development Engineer、Code Review Engineer 和 QA Engineer 只能消费这些图；实现若发现视觉变化实际改变批准边界、接口、数据所有权、信任边界、NFR、风险或成熟度，必须返回 Architecture Team 并按 `architecture_impact` 生成新 Design。

### 11. Archify 采用角色级绑定与命令约束

portable core 只定义 `diagram_author|diagram_reviewer|diagram_consumer` responsibility，不写死 Team 名称或 Agent ID。当前 Multica deployment profile 映射如下：

| Team | Agent | Binding | 允许行为 |
|---|---|---|---|
| Architecture | Solution Architect | full author | 选择图型、创作 Typed JSON、validate、deliver、visual-check、修复并交付 |
| Architecture | Architecture Reviewer | review-only | inspect、validate、check、读取当前 visual-check receipt、必要时 compare architecture；不得修改源或重新 deliver |
| R&D | Product & Spec Engineer | conditional author | 仅为已授权 OpenSpec 创建 scope-local 实现图，优先引用批准架构图 |
| R&D | Solution Review Architect | review-only | 核对冻结图与 proposal/design/spec/tasks、代码证据及批准 Design 的一致性，不得改图 |

Architecture Lead、Architecture Analyst、R&D Lead、Development Engineer、Code Review Engineer、QA Engineer、Integration & Archive Engineer 和 Workflow Watchdog 默认不绑定 Archify。Lead 负责检查 manifest/receipt，Analyst 提供证据，后续角色消费结论；不为内部 handoff 生成展示图。

由于 Archify 当前没有技术上分离的 author/reviewer 子 Skill，review-only 首版由 Agent 指令和 acceptance fixtures 约束。若验证证明指令约束不足，后续另建最小只读 wrapper；本变更不修改 Archify 或把 wrapper 作为当前激活前提。

## Risks / Trade-offs

- **人类看不到完整 Review/Control 可能担心透明度下降** → 在审批摘要后提供可选审计入口，但它不属于作出决定的必读集合；完整内部 evidence 仍按 digest 可追溯。
- **单一 Design 可能变得过长** → 用固定摘要、正文和附录结构控制阅读层次，但不得把理解方案所必需的内容移回其他 artifact。
- **Review finding 回写会增加一次设计版本** → 以 Design 自洽性换取版本数量；impact classifier 避免仅证据补充触发无意义版本。
- **core/adapter 版本错配会产生错误附件数量或 decision binding** → 激活前验证 contract pair；不兼容时在任何平台写入前 fail closed。
- **内部 evidence 若平台不可见会降低运维可诊断性** → 要求 task result/sidecar 具有稳定 ref、保留最小 metadata projection，并允许按需生成审计导出。
- **历史 fixture 大量假设三附件** → 保留 legacy reader fixtures，新 writer fixtures 只产生单 Design；测试明确区分 frozen legacy attempt 与 current revision。
- **`directional` 被误用为可实施方案** → gate 明确禁止其生成 `approved_for_spec` handoff，并要求 Design 内列出 blocked downstream stage。
- **图表通过校验但架构语义错误** → 将 `deliver`、`visual-check` 和独立 Reviewer 结论建模为三项互不替代的证据，Reviewer 必须按 diagram/node/edge 绑定 finding 与来源。
- **视觉附件重新制造多材料负担** → Design 仍是唯一 mandatory entry；HTML、预览和 receipts 都标为派生资源，从 Design 内引用，审批评论不要求分别打开。
- **所有 Agent 绑定生成型 Skill 导致职责漂移** → 首期只绑定四个目标 Agent，作者与 review-only 指令分离，其余角色通过 manifest 消费。
- **R&D 图与批准架构分叉** → proposal 图必须引用上游 diagram/version；涉及架构影响时禁止局部更新并返回 Architecture Team。
- **第三方 Archify 版本漂移** → activation manifest 冻结来源 revision、版本和 archive digest，冲突或升级必须重新验证，不从可变工作目录直接宣称 workspace ready。
- **Chrome/Chromium 不可用会阻断 required diagram** → 这是有意的 fail-closed 选择；在 browser-capable runner 重跑当前 artifact 的 `visual-check`，不得用人工浏览、旧截图或 `diagram_not_applicable` 绕过已声明的 required 状态。

## Migration Plan

1. 先把 `allow-owner-attested-formal-architecture-approval` 完成变更集成或冻结为明确基线，记录当前 core/adapter revisions。
2. 冻结 Archify 候选归档的名称、版本、来源 revision、SHA-256 和 CLI 能力；确认它仍是外部依赖且不复制进本仓库。
3. 以 RED tests 固定新 contract：唯一 Design canonical entry、visual manifest、三层图质量声明、角色级绑定、packet/control/handoff 不进入普通评论、maturity gate、impact classification、旧 attempt 不被重解释。
4. 更新 core Skill、references 和 templates；再更新 adapter 与 schema/fixtures，保持中间状态不部署。
5. 更新 `README.md` 的 core/adapter 使用说明，删除三附件必读和人工复制 packet digest 的旧指导，说明单 Design、current Action、内部 evidence、required visual gate 和四个 Agent 角色边界。
6. 运行 focused tests、全仓 tests、Skill quick/safety checks、Archify showcase/visual checks、`openspec validate --strict`、GitNexus change analysis，以及 README/规范中的旧三附件和旧 binding 语义扫描。
7. 输出 Claude/Codex 刷新与 Multica workspace Team/Agent 原子绑定 runbook；只有用户另行明确授权具体运行时或 workspace/Agent 后才执行真实激活，任一 compatibility 或 role-profile check 失败时保持旧 revision 继续服务。
8. 在新的 sandbox Issue 执行端到端验收：Design 与总览图生成、独立图/文 Review、一 canonical Design 入口、桌面/手机静态预览、owner-attested/automatic 决定、材料打不开恢复、stale reply no-op、内部 handoff readback和 R&D 引用上游图。
9. 验收通过后只为新 attempt 启用；UNIDRAG-12 等历史记录保持只读。需要迁移当前工作时创建 superseding attempt，并明确通知 Owner 新 Action 取代旧 Action。

回滚时将新 attempt 停止在安全 stage，恢复上一对兼容 core/adapter revision；已经生成的新评论、附件和 evidence 保留审计，不删除或改写。未消费的新 Action 标记 superseded，不能转交给旧 reader 消费。

## Open Questions

无。人类交付原则、内部流转原则、兼容基线和激活策略已经由本次分析确认。
