## Context

`architecture-design-workflow` 已在 implementation payload commit `1d4b860b48e15f678d78a71bf2c38557ab9c2951` 实现 immutable portable approval packet、raw-byte SHA-256、external readiness envelope 和 current-packet human decision binding。它刻意不认识 Multica 的 comment、attachment、metadata 或移动端字段。

已确认的 Multica 通用能力事实如下：

- `multica issue comment add <issue> --parent <comment-id> --attachment <path> --output json` 支持回复关系和一个或多个附件；命令会在发布评论前预读全部本地附件。
- comment JSON 包含 `id`、`parent_id`、`author_type`、`author_id`、`content`、attachments 和 timestamps；`comment list --thread` 可读取包含目标评论的回复树。
- attachment response 区分短期 `download_url` 与可持久化 `markdown_url`；单附件读取可刷新下载 URL，Markdown/text 是服务端允许预览的文本类型。
- 移动端在评论下展示附件卡片；非图片附件可点击 canonical download URL，回复关系在移动端可见且可操作。
- Issue metadata 是单 key 原子更新的 primitive KV，key 最长 64、最多 50 个、总量 8 KiB，适合保存轻量 current projection，不适合保存完整 artifact。
- Multica workspace 支持 `.skill`/`.zip` 或 URL import，并支持 `agent skills add` 的 additive 绑定及 `agent skills list` 核验。

GitNexus 已在 `my_dev_skills` 和 Multica 当前工作树重建，但 MCP 的 LadybugDB reader storage v42 无法打开 analyzer 写出的 v43 数据库。因此以上事实来自有界源码调查；索引同时报告部分动态调用候选和 process tracing 被截断，不能把未覆盖路径理解为不存在。

设计推断：这些现有接口足以实现第一版 adapter，不需要修改 Multica 核心代码。该结论由有界源码事实、apply 阶段的轻量 contract validation 和可选人工 sandbox acceptance 支撑；任何 capability preflight 缺口均失败关闭，而不是在本 change 内越界修补 Multica。

## Goals / Non-Goals

**Goals:**

- 新增与 core 相对独立的 `multica-architecture-approval-adapter` sibling skill。
- 在 Multica Issue 中提供简洁审核评论、Architecture Team recommendation/理由及手机可打开的完整材料。
- 从 Multica refs 产生满足 core 语义的 `durable_platform_ref` 和 `review_packet_ready|unavailable` evidence。
- 允许人类在手机或桌面直接回复 packet 评论，用短 decision token 绑定准确 packet。
- 对上传、评论、metadata 部分失败和重试提供确定 reconciliation，避免重复 packet 评论。
- 通过手工授权的 import/bind 配置激活 adapter，不自动创建或修改真实平台资源。

**Non-Goals:**

- 不修改 Multica server、web、desktop、mobile、CLI、数据库或 built-in skills。
- 不修改 `architecture-design-workflow` 的 portable schema、canonical stage 或 human gate。
- 不让 Multica metadata、Agent 评论、recommendation、reaction、Issue status 或模糊回复成为人工批准。
- 不要求 PDF；PDF 可以作为可选派生预览件，但 Markdown 原始 bytes 和 digest 始终是权威输入。
- 不在自动测试中访问真实 workspace、创建 Skill/Agent/Issue 或写用户真实 HOME。
- 不自动归档前序 OpenSpec change，也不创建 branch、worktree 或 commit。

## Decisions

### 1. Adapter 是独立 sibling skill，而不是 core 条件分支或 Multica 服务端状态机

新增根目录 `multica-architecture-approval-adapter/`，包含独立 `SKILL.md`、references、templates 和 Runtime metadata。它只在以下条件成立时接管平台映射：

1. `architecture-design-workflow` 已生成 delivered current packet；
2. Review conclusion 为 `APPROVABLE_WITH_WARNINGS|APPROVABLE`；
3. Work Item 被确认是可访问的 Multica Issue；
4. 当前 Runtime 可调用匹配契约的 `multica` CLI。

adapter 输出 portable evidence，由 core 继续计算 canonical transition。core 在没有 adapter 时仍可使用 standalone profile；adapter 在没有 core packet 时不得自行构造架构状态。

备选方案一是在 core 中加入 Multica 分支，会破坏平台中立性和 standalone fixtures；备选方案二是在 Multica 服务端实现架构审批状态机，会把领域规则写入通用协作平台。两者均不采用。

### 2. Capability preflight 以行为契约为准，缺失即失败关闭

delivery capability 分为两阶段。首笔写入前只检查无副作用的当前 Issue/workspace read、已安装 CLI/profile/command surface、任何既有且 scope-matched 的 capability certificate、授权输入路径/raw-byte digest 和 metadata read。CLI help、源码或记忆中的接口不能单独冒充 live 行为证明。

首次已授权的 comment+三附件写入之后，JSON response、actual `--parent`、附件 bindings、thread reread、稳定 attachment identity/raw-byte re-download 和 metadata write/read-back 都是 fail-closed postconditions。任一 gate 或 postcondition 缺失时输出 `review_packet_unavailable`，包含 failed check、Owner 和 closing condition，并保持真实 Reviewer conclusion/已有对象。skill import 和 Agent binding 只属于 activation preflight，不属于每次 Issue delivery；adapter 不尝试安装/升级 CLI 或调用 Multica 内部 API 绕过契约。

### 3. 一条人类可读 packet 评论承载简报，完整正文只放附件

使用 `templates/multica-approval-comment.md` 生成简短 Markdown 评论，固定包含：

- packet ref/version 和缩短展示但机器 marker 中完整保存的 digest；
- design/review versions 与 Reviewer conclusion；
- `ARCHITECTURE_RECOMMENDATION`、中文理由、适用条件和关键风险；
- 审核对象、待确认项和合法 decision tokens；
- “建议不构成人工批准”的显著说明；
- “完整方案、完整评审、完整 packet 请打开下方附件”的指引。

评论尾部使用稳定 machine marker：

```text
<!-- multica-architecture-approval-adapter:v1 packet_ref=ARCH-APPROVAL-PACKET packet_version=vN packet_digest=sha256:<hex> -->
```

附件至少包含原始 `ARCH-DESIGN-vN.md`、`ARCH-REVIEW-vN.md` 和 `ARCH-APPROVAL-PACKET-vN.md`。它们保持 core 冻结 bytes，不为平台重排空白或换行。若部署提供 PDF renderer，可附加标记为 `derived_non_authoritative=true` 的 PDF；PDF 失败不得替代或改变原始 digest，也不是 baseline readiness 必需项。

若当前 Agent task 是 comment-triggered，packet 评论通过 `--parent <trigger-comment-id>` 发布；否则可作为顶层评论。无论 packet 评论处于哪一级，后续绑定都以其 comment ID 和父链为准，而不是假定它是 thread root。

### 4. `multica_attachment` profile 保存稳定 ID/URL，并精确绑定目标审批人

每个 artifact 映射为：

```text
verification_profile=durable_platform_ref
platform_profile=multica_attachment_v1
artifact_ref=multica://issues/<issue-id>/comments/<comment-id>/attachments/<attachment-id>
artifact_version=<core version>
media_type=<upload response content_type>
expected_digest=sha256:<core digest>
verified_digest=sha256:<downloaded raw bytes>
stable_access_ref=<markdown_url or stable attachment endpoint>
availability_scope=multica_workspace:<workspace-id>/issue:<issue-id>
human_actor=<target member id>
human_actor_binding_ref=<packet-bound mapping evidence ref>
verifier=<adapter actor/runtime>
verified_at=<RFC3339 UTC>
```

不得把可能过期的 signed `download_url` 持久化为 stable ref。发布后必须重新列出 packet 评论，确认三个 attachment IDs 均绑定该 comment，再通过单附件读取/下载获取当前 bytes 并核对 SHA-256。

目标审批人采用确定的 `multica_target_human_v1` 绑定规则：portable packet 中 design/review 的 `Target human actor` 必须非空且一致，并且必须通过以下一种方式唯一映射到一个 Multica member UUID：packet 已使用 canonical `multica_member:<uuid>`；或当前 delivery 输入附带由 user-role 明确确认、绑定 packet ref/version/digest 的 actor-mapping evidence。mapping evidence 至少记录 portable actor、member UUID、Issue/workspace scope、confirmer、evidence ref 和 RFC3339 UTC recorded time。不得按显示名、邮箱片段、Issue assignee、评论作者或 Agent 推断目标审批人；零个或多个匹配、design/review actor 不一致、mapping 与 current packet 不匹配时均输出 `review_packet_unavailable`。readiness 中的 `human_actor` 使用 canonical Multica member UUID，并保存 mapping evidence ref。

目标 member 还必须在当前 Issue/workspace scope 中可识别；仅 Agent 自身能下载不等于 human access。任何其他 member 的评论都保留为 non-binding audit text，不得进入有效决定集合。

手机可读 baseline 是：移动端时间线能看到 packet 评论和三个附件卡片、稳定 access ref 可由已认证目标成员打开、原始 Markdown 小于平台/预览限制。adapter 不声称“已人工阅读”，只证明可检索性。

### 5. Delivery 使用单调 fencing reconciliation，不假设跨 API 原子性

Multica 的附件上传、评论创建和 metadata 更新不是一个 adapter 级事务。adapter 使用以下状态：

```text
absent → delivering → delivered_unverified → ready
                    ↘ unavailable
```

每次 delivery 分配唯一 `delivery_attempt_id`，开始前读取 metadata current projection，并扫描 Issue comments 中匹配 adapter marker、packet ref/version/digest 且由当前 adapter Agent 发布的 comment。所有写入都携带本次 packet identity；version 比较只接受严格正整数 `vN`，无法比较时失败关闭：

- 找到一个 exact delivery：复用并重新验证，不重复发评论。
- 找到多个 exact deliveries：选择最早完整可验证者作为 canonical，记录 duplicates 供人工清理，不自动删除评论或附件。
- 同 version 但 digest 不同：视为冲突/潜在改写，失败关闭；不得覆盖 metadata 指针。
- 只找到孤立附件或 comment 缺附件：记录 partial failure，重试可以创建新的完整 delivery，但不得把残留对象标为 ready。
- 新 packet supersedes 旧 packet：创建新评论；旧评论保留审计，不编辑、不删除，metadata current projection 指向新 packet。
- 扫描发现更高 packet version：当前运行成为 stale writer，停止所有后续写入，不输出 readiness，并报告 superseded closing condition。

metadata projection 使用一个 primitive string key，避免多个单 key 写入形成 torn projection：

```text
key=arch.packet.current
value=profile=v1;version=vN;digest=sha256:<hex>;comment_id=<id>;status=<state>;evidence_ref=<ref>;core_revision=<sha>;attempt_id=<id>;updated_at=<RFC3339 UTC>
```

值必须使用固定字段顺序和转义规则、保持在平台配额内，并拒绝未知/重复字段。projection 写入采用以下 fencing：写前扫描 comments 与 projection，发现更高 version 或同 version 不同 digest 即停止；原子写入单 key；写后回读该 key并再次扫描全部 marker；如果更高 version 已出现、projection 不再等于本次 identity 或 duplicate canonical 发生变化，则本次不得输出 ready。最终扫描完成后本次不得再执行平台写入。若更高版本在本次完成后才开始，其运行负责推进 projection；core 始终以 current packet ref/version/digest 拒绝旧 readiness，因此 metadata 不承担 gate authority。

metadata 只是快速 current projection；canonical evidence 仍由 comment/attachment refs、回读 digest 和 core `ARCH-CONTROL` 共同构成。metadata 写失败时 delivery 可被后续扫描找回，但本次不得输出 ready。

### 6. Readiness envelope 由全部验证完成后一次性产生

`templates/multica-readiness-evidence.md` 记录 core 所需 packet/design/review refs、versions、digests、Review conclusion、target human、access refs、verifier/time，并增加 adapter delivery comment/attachment IDs、capability profile 和 reconciliation outcome。

只有以下全部成立才输出 `review_packet_ready`：

1. core identity 与固定 consumed revision 兼容；
2. comment marker 精确匹配 current packet；
3. 三份 required attachments 绑定正确 comment；
4. 回读 raw bytes 的 digest 全部匹配；
5. durable access 和 target human scope 已确认；
6. comment 简报完整且 recommendation 非授权声明存在；
7. metadata current projection 回读与 delivery 一致，写后 final fence 未发现更高版本、digest 冲突或 canonical delivery 变化。

任何失败输出独立 `review_packet_unavailable`，保留 Review conclusion 和已有 objects，不通过删除/修改 packet 来“回滚”。

### 6a. Durable evidence 只写入已确认 shared scope，且 final record 不可变

`shared_workspace_sidecar_v1` 只使用用户确认的既有 durable shared scope，不创建 workspace/resource。mapping、readiness、decision 都是完整 Markdown sidecar，拥有自身 `workspace://<scope>/<relative-path>` evidence ref，final ref 采用唯一 record identity、write-once no-clobber atomic publish 和 reread；已存在 bytes 仅在完全相同时幂等复用，否则 conflict fail closed。路径必须在解析 symlink 后的确认 scope real root 内，拒绝 symlink/TOCTOU escape；scope 不提供安全 no-clobber 时 unavailable。readiness sidecar 只在 final no-more-platform-writes scan 后生成；decision sidecar 只在 readiness/comment reread 后、并且当前任务额外明确授权该 shared-scope write 时生成。没有 scope/授权/re-read，mapping/readiness unavailable 或 decision 仅为 audit、不得生效。

### 7. Human decision 使用精确 target-human binding 和确定的 replacement 顺序

支持两种 profile：

- `multica_packet_comment_reply_v1`：由 readiness 中 exact canonical `human_actor` 发布的 comment，其父链包含 exact current packet comment，正文去除首尾空白后必须恰好等于一个合法 decision token。packet ref/version/digest 从已重新验证的父 comment marker 和 attachments 继承，因此手机端人类可以只回复 `approved_for_spec` 等短 token。
- `multica_explicit_packet_reference_v1`：由同一 canonical `human_actor` 在同一 Issue 发布的 comment，正文明确包含一个合法 decision、packet ref/version 和完整 digest；未知或重复 identity 字段无效。

合法 token 仍只有 `approved_design_only|approved_for_spec|revision_requested|rejected`。读取时必须：

1. 重新验证 current packet delivery/readiness；
2. 重建 parent chain，不能只相信 thread root；
3. 要求 `author_type=member`、`author_id` 精确等于 readiness 的 canonical target member UUID，并重新验证 target-human mapping evidence；
4. 记录 decision comment ID、revision（如提供）、content digest、created/updated time；
5. 只比较独立 comment，按 server ordering `(created_at, comment_id)` 全序排列；同一 actor 的后续合法 comment 自动替换其先前决定，保留全部历史 evidence 并只标记最后一条为 effective；编辑同一 comment 不构成替换，revision/content digest 漂移会使已捕获 evidence invalidated，必须另发新评论；
6. 如果 legacy evidence、mapping 漂移或损坏数据导致多个 actor 同时被识别为有效 current-packet 决策者，则保持 `waiting_human`、报告全部 refs 并要求重新建立唯一 target-human mapping，不按时间静默选择跨 actor 决定。

Agent/system 评论、reaction、引用他人决定、Reviewer conclusion、recommendation、Issue status、任务分派、`OK`/“继续”等模糊文本均不合法。绑定 superseded packet 的有效回复保留审计，但对 current gate no-op。

### 8. Activation 是明确授权的配置流程，不是 apply 副作用

implementation 只交付可打包 skill 和 runbook。实际激活由人类另行执行并确认：

1. 在临时 HOME 验证 Claude/Codex 两个链接分别指向 repository sibling sources；
2. 生成 `.skill`/`.zip`，静态检查不含 secret、本地绝对路径或测试 evidence；
3. `multica skill import --file ... --on-conflict fail --output json`；
4. 使用 `multica agent skills add` additive 绑定，禁止用 replace-all `set`；
5. 以 `agent skills list` 核对 core 与 adapter skill IDs 均存在；
6. 用专用 sandbox Issue 完成桌面/手机 delivery、打开附件、reply decision 和 supersession acceptance。

proposal/apply 不执行上述真实写入，也不自动创建缺失 Agent、Team、Project 或 Issue。activation 发现平台能力缺口时记录独立 issue/proposal 建议，不在本 change 修改 Multica。

### 9. 自动验收保持最小且无外部副作用

apply 只保留 normalized schema/contract fixtures、skill quick validation、隔离 installer/package 检查和 OpenSpec strict validation。normalized schema 分开记录 core review conclusion、packet readiness、delivery ref/attempt/fence outcome、target-human mapping/access confirmation、recommendation、human decision、decision evidence status、stage/wait/blocker。

按实施期用户决定，本 change 不新增 fake `multica` CLI、双 Runtime behavior evidence、adapter safety runner或额外回归测试。自动验证不得调用网络、真实 `multica` profile、用户 HOME 或 workspace；delivery/reconciliation/decision 的真实平台行为只能在每次 capability preflight 通过后执行，并由另行明确授权的 sandbox acceptance 最终确认。

## Risks / Trade-offs

- **[Multica comment/metadata 写入非事务，可能留下孤立附件或重复评论]** → marker、metadata projection、comment scan 和 digest reconciliation；自动化不删除历史对象。
- **[评论可编辑，decision evidence 可能随时间漂移]** → 记录 comment revision/timestamps/content digest，每次消费前回读；漂移时 evidence invalidated 并请求确认，不伪造历史不可变性。
- **[目标人类身份或访问不能由显示名、assignee、Agent 下载成功单独证明]** → 使用 packet-bound canonical member mapping、workspace/Issue/member scope 和稳定 access ref；映射歧义失败关闭，sandbox activation 额外做真实手机验收。
- **[Markdown 在不同手机上打开体验不同]** → baseline 保证附件卡片和可检索 bytes；PDF 是可选派生件。若产品要求原生内嵌统一预览，应另建 Multica 平台 change。
- **[CLI/API 后续变化导致 adapter 漂移]** → capability preflight、source-traced mapping 和固定 core revision；未知输出失败关闭，真实兼容性不从静态校验推断。
- **[metadata 配额或并发更新]** → 单个 bounded primitive projection、单调 version fence和写前/写后 marker scan；metadata 不承载完整 payload或 gate authority，sandbox 未运行前并发行为保持 `not_run`。
- **[两个 skill 同时安装可能被误认为强依赖]** → 独立 frontmatter/触发规则；core 无 adapter 仍可运行，adapter 无 core packet 必须拒绝构造状态。

## Migration Plan

1. 保持已实施 core contract 不变，新增 adapter references/templates 和失败测试。
2. 实现 delivery/reconciliation、readiness 和 decision evidence contract，并保留最小 normalized fixtures。
3. 更新 repository README、validator、临时 HOME 隔离安装检查和 package runbook，不新增额外回归测试。
4. 记录 implementation revision evidence：若另获 commit 授权则记录 commit；本次 no-commit 则记录 `not_committed`、baseline HEAD 与 working-tree scope，同时记录 consumed core revision、Multica observed commit `5fa65bd12585e29c2b52c44007ba3046a06c246b`、CLI capability matrix 和验证限制。
5. implementation 完成后由人类决定是否先归档 core change，再在真实 Multica workspace 导入和 additive 绑定。
6. sandbox acceptance 通过后，才由人类把 adapter 配置到 Architecture Team 的正式 Agent。

回滚只移除/停用 adapter skill binding，并保留已发布评论、附件、metadata 和 decision evidence 作为审计历史。不得删除已批准架构文档；core 退回 standalone profile。

## Open Questions

无。第一版明确以现有 attachment-card + stable access ref 为手机可打开基线，PDF 为可选派生件；任何“必须在 Multica App 内原生渲染统一文档”的新要求都属于独立平台能力变更。
