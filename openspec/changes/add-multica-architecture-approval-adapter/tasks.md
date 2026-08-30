## 1. 基线、依赖与红灯测试

- [x] 1.1 在 `my_dev_skills` 检查 GitNexus index/HEAD 和工作树，记录 core implementation commit `1d4b860b48e15f678d78a71bf2c38557ab9c2951`、当前 `architecture-design-workflow` contract files 与既有 validation baseline。
- [x] 1.2 对 Multica 只做只读 capability baseline，记录 observed repository commit/CLI help、comment reply/attachment/thread/metadata/mobile attachment contracts 和 GitNexus v43/v42 读取限制；不得改动或清理 Multica 既有工作树。
- [x] 1.3 先创建 adapter fixture/result schema 和失败断言，使 core-absent、capability-missing、delivery、digest、reconciliation、decision binding、activation 边界在 adapter 尚不存在时按预期失败。
- [x] 1.4 运行并保存现有 `architecture-design-workflow` quick validation、安全 runner、runner unit tests 和安装器测试基线，确保后续 adapter 工作不掩盖 core 回归。

## 2. 独立 adapter skill 骨架与触发边界

- [x] 2.1 新增 `multica-architecture-approval-adapter/SKILL.md` 和 `agents/openai.yaml`，定义仅在 compatible delivered core packet + Multica Issue context 下触发的职责，并明确无 packet 时拒绝构造 core 状态。
- [x] 2.2 固定 consumed core revision 和 compatible contract markers，提供清晰的版本不兼容报告，但不得把 Multica 字段加入 `architecture-design-workflow` required fields。
- [x] 2.3 在 skill 中定义平台写入授权边界：Issue delivery 属于当前明确任务时可执行；Skill import、Agent binding、Team/Project/Issue 创建和 Runtime 配置始终需要单独的人类授权。
- [x] 2.4 增加 two-phase capability reference：pre-write gate 只检查无副作用的 Issue/workspace read、CLI/profile/command surface、既有 capability certificate、输入路径/digest 与 metadata read；首笔已授权 comment+attachments 的 JSON/actual parent/bindings/redownload/metadata write-readback 是 postconditions。不得把 help/source 当作 live 行为证明，任一失败生成 deterministic unavailable evidence。
- [x] 2.5 定义 `multica_target_human_v1`：要求 design/review target actor 一致，使用 canonical `multica_member:<uuid>` 或 packet-bound user-confirmed mapping evidence 唯一解析 member UUID；拒绝显示名、邮箱片段、assignee 和评论作者推断。

## 3. 审核评论与附件交付

- [x] 3.1 新增 `templates/multica-approval-comment.md`，只展示 packet/design/review versions、Review conclusion、recommendation/中文理由、条件风险、待确认项、合法 decisions、非批准声明和完整附件指引。
- [x] 3.2 定义 `multica-architecture-approval-adapter:v1` machine marker，并以现有 normalized contract 的最小静态 surface 校验约束其存在，确保 comment content 可恢复 exact packet ref/version/digest 且不依赖可变 metadata；不新增额外回归测试。
- [x] 3.3 新增 delivery mapping reference，规定使用 `issue comment add --content-file --attachment ... --output json` 一次交付三份 frozen Markdown，并在 comment-triggered task 中正确使用实际 trigger comment parent。
- [x] 3.4 保持 design/review/packet 原始 bytes 不变；将任何 PDF 标记为 `derived_non_authoritative`，验证 renderer 缺失或失败不会替代 canonical Markdown/digest。
- [x] 3.5 解析 comment/attachment JSON，生成 `multica://issues/.../comments/.../attachments/...` refs，并只持久化 attachment ID、`markdown_url`/stable endpoint，不持久化短期 signed `download_url`。

## 4. Reconciliation、metadata 与 readiness

- [x] 4.1 新增 delivery/reconciliation reference 和 normalized states：`absent → delivering → delivered_unverified → ready|unavailable`，明确每个状态的允许写入与关闭条件。
- [x] 4.2 实现/指示发布前 comment scan + metadata projection 对账：exact delivery 复用、metadata-loss 修复、duplicate 报告、partial delivery 隔离、same-version digest conflict 失败关闭、superseded delivery 保留和 higher-version stale writer 停止。
- [x] 4.3 使用单个 bounded primitive `arch.packet.current` 按固定格式原子保存 current packet/version/digest/comment/status/evidence/core revision/attempt/timestamp；执行写前、写后 monotonic fence 和 final no-more-writes scan，不得将 metadata 当作 packet 或 approval authority。
- [x] 4.4 新增 `templates/multica-readiness-evidence.md`，包含 portable core fields 和 adapter delivery/capability/reconciliation refs；ready 还要求用户确认既有 shared scope 中 write-once+reread 的 `shared_workspace_sidecar_v1` 自身 evidence ref，readiness/unavailable envelope 均不得写回 frozen packet。
- [x] 4.5 发布后重新读取 packet comment、确认 required attachment bindings、逐一通过 attachment identity 下载 raw bytes 并核对 SHA-256；只有 target-member durable scope、brief 和 metadata 同时验证才输出 `review_packet_ready`。
- [x] 4.6 对 attachment missing、digest mismatch、stable ref missing、target human unconfirmed、metadata failure 和 comment identity conflict 输出 `review_packet_unavailable`，保留真实 Review conclusion 和已存在对象且不自动删除。

## 5. Multica 人工决定绑定

- [x] 5.1 新增 human decision binding reference 和 `templates/multica-decision-evidence.md`，分别定义 `multica_packet_comment_reply_v1` 与 `multica_explicit_packet_reference_v1`。
- [x] 5.2 对 packet reply profile 重建完整 parent chain；即使 packet comment 嵌套在 trigger thread 下，也只从 exact verified packet comment 继承 ref/version/digest。
- [x] 5.3 仅接受 `author_type=member`、`author_id` 精确等于 readiness canonical member UUID 且 mapping evidence 可重验的单一合法 token；拒绝非目标 member、模糊 actor mapping、Agent/system、reaction、引用文本、recommendation、Review conclusion、Issue status、紧急措辞和模糊 `OK/继续`。
- [x] 5.4 记录 decision comment ID、revision（如存在）、content digest、created/updated/recorded timestamps，并在消费前重新读取 packet readiness 与 decision content；有效决定还需要当前任务额外授权的 immutable decision sidecar write-once+reread，否则仅 audit。
- [x] 5.5 以 `(created_at, comment_id)` 实现同一 actor 的新独立合法评论自动替换旧决定；编辑旧评论只使 evidence invalidated，跨 actor legacy/mapping 冲突保持 `waiting_human` 并要求重新建立唯一 mapping。

## 6. 实施期范围收缩

按用户在实施期的明确决定，本 change 不实现 fake `multica` CLI、双 Runtime behavior evidence、adapter safety runner或额外回归测试。必要的禁止边界由 skill/reference 文档、现有 normalized contract fixtures、最终 diff 检查和 activation `not_run` evidence 覆盖。

## 7. 安装、打包与授权激活 runbook

- [x] 7.1 更新 `README.md`，说明 core 与 adapter 的独立触发/安装关系、审核评论展示内容、完整附件打开方式、失败关闭和非授权建议边界。
- [x] 7.2 使用现有 installer/validator 路径在临时 HOME 做一次隔离检查，确认 Claude/Codex 为 core 与 adapter 建立四个独立链接、冲突隔离且不写真实 HOME；不新增回归测试。
- [x] 7.3 在临时目录验证 `.skill`/`.zip` 打包内容、supporting files、frontmatter 和 secret/absolute-path 扫描，不向真实 Multica workspace 发起 import。
- [x] 7.4 编写 activation runbook：显式 workspace/Agent 确认、safe import conflict、additive `agent skills add`、最终 `agent skills list` 和无缺失资源自动创建。
- [x] 7.5 编写 sandbox acceptance checklist，覆盖桌面/手机打开附件、raw-byte digest、short-token reply、supersession、retry 和 failure closing；未实际授权运行时明确标记 `not_run`。

## 8. 完整验证与交付证据

- [x] 8.1 运行 adapter quick validation、现有 normalized contract 校验、隔离 installer/package 检查和必要的 core smoke validation；不新增或扩展回归测试。
- [x] 8.2 运行 `openspec validate add-multica-architecture-approval-adapter --strict`，逐项核对 proposal、design、三组 spec deltas 和实现任务的一致性。
- [x] 8.3 检查最终 diff、尝试 GitNexus change impact 并在 reader 不可用时记录 bounded Git/source fallback，同时核对跨仓库状态，确认只有 `my_dev_skills` adapter/测试/文档发生预期变化，Multica、`uni-architecture` 和真实 HOME/workspace 未被修改。
- [x] 8.4 记录 adapter implementation status（已提交时为 commit；本次 no-commit 边界下为 `not_committed` + baseline HEAD）、consumed core revision、observed Multica commit/CLI matrix、验证结果、GitNexus覆盖限制、activation `not_run|passed` 和任何需要独立平台 change 的缺口。
