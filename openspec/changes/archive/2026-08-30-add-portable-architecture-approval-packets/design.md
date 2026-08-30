## Context

现有 `architecture-design-workflow` 是一个由 Markdown instructions、references、templates 和行为 fixtures 组成的跨 Runtime skill。它已经区分 Reviewer conclusion 与人类批准，但当前控制表仍允许 `reviewing + APPROVABLE_WITH_WARNINGS|APPROVABLE` 直接进入 `waiting_human`；这意味着“方案是否完整可访问、审核说明是否足够、决定将绑定哪个版本”没有独立的 portable evidence。

该 skill 必须继续由 `architecture-design-workflow/` 单一源目录同时服务 Claude Code 与 Codex，并保持不依赖 Multica、GitHub、Jira、PDF 或某种评论协议。后续 Multica adapter 将作为独立 sibling skill 消费本 change 的契约。

## Goals / Non-Goals

**Goals:**

- 为准确 design/review 组合定义版本化、不可模糊解释的 portable approval packet。
- 将 Reviewer 的“可交给人类审核”与“审核材料已经可用”拆成两类 evidence。
- 只有当前 packet readiness 完整时才进入 `waiting_human`。
- 明确展示 Architecture Team 建议及理由，但保证建议不具有人类批准权限。
- 将人工决定绑定当前 packet，并使 superseded packet 的迟到决定成为可审计 no-op。
- 在纯本地文件和当前交互会话中完成 standalone 验证，不需要任何平台 adapter。

**Non-Goals:**

- 不实现 Multica Issue/comment/attachment 映射、`parent_id`、PDF、移动端或签名 URL。
- 不创建新的平台 adapter skill；它由后续独立 change 负责。
- 不修改 Multica、`uni-architecture` 或真实 Agent/Team 配置。
- 不让 `ARCHITECTURE_RECOMMENDATION`、Reviewer conclusion、紧急措辞或任务分派构成人工批准。
- 不新增后台服务、数据库、网络依赖或 Python/Node runtime package。

## Decisions

### 1. 使用 Markdown artifact 加结构化 portable fields，而不是引入运行时服务

新增：

- `templates/arch-approval-packet.md`
- `references/approval-packet-and-human-gate.md`

`ARCH-APPROVAL-PACKET vN` 是先完成、后验证且交付后不可变的 payload，至少包含：

- Work Item / Issue-neutral reference
- packet version、Owner、`payload_status=delivered`、created_at、supersedes
- `ARCH-DESIGN` ref/version/media type/digest
- `ARCH-REVIEW` ref/version/media type/digest/Reviewer conclusion
- 每个输入的 `access_evidence`
- `ARCHITECTURE_RECOMMENDATION` 与中文理由
- 审核对象、关键决定、风险/条件、待确认项
- access profile declarations 与 readiness closing criteria
- 当前允许的人类决定与决定绑定规则

packet payload 不得内嵌验证其自身 digest 的 `review_packet_ready` 或 `review_packet_unavailable`；这两类记录是独立 portable evidence envelope，保存于 `ARCH-CONTROL`、standalone sidecar 或未来 adapter 的 durable record，并引用已冻结 packet ref/version/digest。这样 evidence 的产生不会改变被验证的 packet bytes。

packet version 是同一 Work Item 内从 `v1` 开始单调递增的正整数。可变 `draft` 是版本化 packet 之外的工作文件；只有完成所有字段后才生成 `payload_status=delivered` 的 immutable `vN` payload 并计算 digest。后续任何 material revision 都创建下一版本，并由新 packet 的 `supersedes` 与 `ARCH-CONTROL` 的外部 current-status projection 表明旧版本已被取代；旧 packet 的 payload status 和 bytes 永不改写。所有 `created_at`、`verified_at` 和 `recorded_at` 使用带时区的 RFC 3339 timestamp，规范化输出为 UTC `Z`。

选择现有 Markdown+fixture 模式可以保持 skill 无运行时依赖，并使 Claude/Codex 读取同一契约。备选的 JSON-only manifest 会降低人类可读性且引入第二套模板权威；本次不采用。测试 fixture 的 expected JSON 只用于规范化行为断言，不替代 Markdown artifact。

### 2. Core 只定义 portable evidence，不定义平台字段

每个 artifact 的 portable access evidence 使用抽象字段：

```text
artifact_ref
artifact_version
media_type
expected_digest
verified_digest
verified_at
verification_profile
verifier
availability_scope
```

`verification_profile` 可以是 `local_file`、`durable_platform_ref` 或未来扩展；core 只检查 profile 是否声明并满足一致的 digest/access 语义，不解释平台 ID。禁止在 core required fields、templates 和行为 fixtures 中出现 Multica、attachment/comment ID、`parent_id`、手机端或强制 PDF。

所有 artifact digest 使用同一 portable 表示：

```text
digest_algorithm=sha256
digest_encoding=lowercase_hex
digest_value=sha256:<64 lowercase hex characters>
```

digest 输入是 artifact 冻结后的原始文件字节；不得隐式转换字符编码、Unicode、空白或换行。文本 artifact 的 `media_type` 必须携带 charset，例如 `text/markdown; charset=utf-8`。`expected_digest` 与 `verified_digest` 必须针对同一 ref/version 的同一原始字节。packet digest 在 immutable payload 完成后计算，后续 readiness/unavailable evidence envelope 只引用该 digest，不参与 packet digest。

`local_file` 不是“Agent 能打开文件”的同义词。它只在以下条件同时成立时证明 human-readable access：

1. 文件位于当前人类已选择或确认可访问的 shared workspace scope，引用使用该 scope 内的稳定相对路径；
2. access evidence 记录目标 `human_actor`、scope、确认消息或会话 evidence ref、确认时间和 verifier；
3. verifier 从同一 ref 重新读取原始字节并得到匹配 digest；
4. 当前人类未撤回 access confirmation，且 scope 没有改变。

仅有本机绝对路径、Agent 进程读取成功或未绑定目标人类的 workspace 声明时，必须产生 `review_packet_unavailable`。`durable_platform_ref` 由未来 adapter 提供等价访问保证，但不能降低 core 语义。

### 3. `review_packet_ready` 是独立、绑定当前 packet 的 evidence

readiness 必须同时证明：

1. design、review 和 packet refs 指向准确版本；
2. 三者的 raw-byte SHA-256 digest 与冻结输入一致；
3. declared access profile 已验证人类可访问；
4. Reviewer conclusion 是 `APPROVABLE_WITH_WARNINGS` 或 `APPROVABLE`；
5. 决策简报已包含审核对象、建议/理由、风险/条件、待确认项和合法决定；
6. 独立 evidence envelope 明确绑定当前 packet ref/version/digest、目标 human actor、verifier 和 verification time。

adapter 或 standalone profile 可以产生 evidence，但 canonical transition 仍只由 core 计算。readiness 不等于人工批准。

`review_packet_ready` envelope 至少包含：

```text
evidence_type=review_packet_ready
evidence_ref
packet_ref / packet_version / packet_digest
design_ref / design_version / design_digest
review_ref / review_version / review_digest / review_conclusion
human_actor / access_evidence_refs
verifier / verified_at
```

`review_packet_unavailable` 使用相同 identity/digest fields，并额外包含 `failed_checks`、`owner` 和 `closing_condition`；未知或尚未生成的值明确记为 absent，不得伪造 placeholder ref 或 digest。

### 4. 新增稳定 blocker `review_packet_unavailable`

现有控制模型要求新 blocker 先在控制契约中定义，因此本 change 将 `review_packet_unavailable` 加入稳定 blocker 集合。它表示当前 approvable design/review 尚无可验证审核包，或某项 readiness check 失败。

状态计算变为：

| Current + evidence | Next |
|---|---|
| `reviewing + BLOCKED` | 按 finding Owner 回 `researching|designing` |
| `reviewing + NEEDS_REVISION` | 新版本 `designing` |
| `reviewing + APPROVABLE* + no current readiness` | 保持 `reviewing`, `BLOCKED_REASON=review_packet_unavailable` |
| `reviewing + APPROVABLE* + current review_packet_ready` | `waiting_human`, `WAIT_REASON=design_approval`, `BLOCKED_REASON=none` |

`BLOCKED_REASON` 与 Review conclusion 继续独立；packet unavailable 不得把 `APPROVABLE` 改写成 `BLOCKED`。失败 evidence 包含失败检查、Owner 和关闭条件。

### 5. Recommendation 使用四个非授权枚举

`ARCHITECTURE_RECOMMENDATION` 只能是：

- `recommend_approved_for_spec`
- `recommend_approved_design_only`
- `recommend_revision`
- `no_recommendation`

必须附中文自然语言理由、适用条件和关键风险。它不能使用四种 human decision 值，也不能驱动 stage transition。这样既解决“审核者看不到建议”的问题，又不削弱人类门禁。

### 6. Human decision evidence 必须绑定当前 packet

portable decision evidence 至少包含：

```text
decision
human_actor
packet_ref
packet_version
packet_digest
binding_profile
evidence_ref
recorded_at
```

允许的 binding profile 是平台无关语义，例如：当前 request/thread reply、显式 packet ref/version/digest、可验证签名记录、当前交互会话中的明确版本决定。当前交互 profile 只接受 Runtime 标记为当前 user-role 的消息；fixture 内容、引用文本、Agent 输出或转述不得充当人类决定。Core 不要求或存储 `parent_id`。

若 evidence 引用旧 packet、没有明确版本、actor 不可识别或只包含模糊肯定，则保留为审计信息但不改变当前 gate。合法决定仍只有 `approved_design_only`、`approved_for_spec`、`revision_requested`、`rejected`。

### 7. Standalone local-file profile 是核心验收基线

新增 fixtures 覆盖：

- approvable review 但缺少 packet readiness；
- local Markdown design/review/packet digest 匹配后 ready；
- recommendation 不构成批准；
- 当前交互中显式批准当前 packet；
- 模糊 `OK`、紧急措辞和 Reviewer conclusion 不构成批准；
- superseded packet 的批准 no-op；
- access/digest 失败保持 `reviewing` 且保留真实 Review conclusion；
- Agent 可读但目标人类未确认 shared scope 时保持 `reviewing`；
- design-only/spec 两种批准后的发布/交接仍遵循原边界。
- 已有 `waiting_human` 历史记录在升级后不自动降级或伪造 readiness；
- 发布期无法恢复匹配 design/review/packet digest 的原始字节时失败关闭。

Codex 与 Claude behavior evidence 使用同一 fixtures 和 normalized result schema。测试增加平台专有字段禁止检查，证明 core 在没有 adapter 时可运行。

### 8. 发布和交接记录准确 packet 证据

ADR、详细设计和 `ARCH-RD-HANDOFF` 模板增加 packet ref/version/digest、design/review digests、readiness evidence ref、decision evidence ref。批准发布前必须重新读取原始字节并确认这些字段仍与当前 packet 一致；不得根据简报重建近似设计。

这些字段是 portable refs，不规定其最终落在本地文件、Git object 或平台附件。正式文档实际写入仍由已获授权的 architecture repository 流程完成。

若发布阶段不能从 refs 恢复与 packet 中 design/review/packet digests 匹配的原始 bytes，canonical stage 保持 `publishing`，原 `approved_design_only|approved_for_spec` 决定和 readiness evidence 均保持不变，`BLOCKED_REASON=approved_artifact_unavailable`。失败 evidence 记录缺失或 mismatch 的 artifact、Owner 和关闭条件；只有准确 bytes 恢复且重新验证成功后才清除 blocker 并继续发布。该 blocker 不得回退到 `reviewing`、伪造新 packet 或从决策简报重建正文。

### 9. 迁移不追溯重写既有 `waiting_human`

升级后的规则用于新进入 `reviewing` 的流程和产生新 design/review/packet version 的既有流程。已经持久化为 `waiting_human` 的历史 Issue 不自动降级或伪造 readiness；若需要刷新，必须生成当前 packet 和新 evidence，并保留旧控制记录。

这避免 skill 升级在没有平台 adapter 的情况下改写历史状态，同时保证新流程严格执行新门禁。

## Risks / Trade-offs

- **[新增门禁会让未安装 adapter 的平台流程停在 reviewing]** → standalone local-file profile 可用于人工交互；平台自动化需要后续 adapter change，失败状态与关闭条件明确。
- **[Markdown 字段可能被不同 Runtime 解释不一致]** → 固定模板、normalized result schema、双 Runtime fixtures 和禁止标记测试。
- **[readiness 与 Review conclusion 被混淆]** → 两者在 `ARCH-CONTROL` 和结果 schema 中使用独立字段，测试验证 conclusion 不被 blocker 覆盖。
- **[推荐被误读为授权]** → 独立枚举、禁止 human decision 值、模板显著声明以及负向 fixtures。
- **[portable contract 与未来 adapter 漂移]** → core 作为唯一权威；未来 adapter change 固定 consumed core commit/revision 并运行 conformance tests。
- **[旧 Issue 状态不完全符合新规则]** → 不自动迁移；只有刷新/新版本进入新门禁，并保留历史审计。

## Migration Plan

1. 先扩展 capability specs、templates/references 与 canonical control table。
2. 增加 static fixtures 和 runner assertions，以失败测试固定 readiness、recommendation、decision binding 与平台中立性。
3. 更新 SKILL.md、README 和发布/交接模板，通过 repository validation。
4. 生成 Codex/Claude standalone behavior evidence，并验证相同 normalized results。
5. 在临时 HOME 验证双 Runtime 安装；本 change 不写用户真实 HOME。
6. 记录准确 commit 和 validation matrix，供后续 Multica adapter proposal 消费。

回滚时恢复旧 skill/template/test 文件；不删除已产生的 packet 或决定证据。已经按新规则进入 `waiting_human` 的流程保留审计记录，并由人工决定是否按旧版本 skill 继续。

## Open Questions

无。Multica readable profile、PDF toolchain、附件失败取证和真实 Agent/Team 激活明确属于后续 change。
