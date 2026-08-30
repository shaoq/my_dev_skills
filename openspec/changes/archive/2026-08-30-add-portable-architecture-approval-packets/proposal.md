## Why

`architecture-design-workflow` 目前在 Reviewer 给出 `APPROVABLE*` 后即可直接进入人工门禁，但没有一个平台无关、可验证且绑定准确版本的审核包契约，导致审核材料是否完整可访问、团队建议是什么以及人工决定对应哪个版本都依赖具体协作平台的临时约定。需要先在核心 skill 中建立 portable approval packet 和 readiness/decision evidence，再由独立 adapter 映射到 Multica 或其他平台。

## What Changes

- 新增平台无关且不可变的 `ARCH-APPROVAL-PACKET vN` payload，绑定 Work Item、准确 `ARCH-DESIGN`/`ARCH-REVIEW` versions、media types、digests、access profile declarations、Reviewer conclusion、supersedes 与明确但非授权的 `ARCHITECTURE_RECOMMENDATION`。
- 固定 raw-byte SHA-256 digest 契约，并将 `review_packet_ready` / `review_packet_unavailable` 作为引用已冻结 packet digest 的独立 portable evidence envelope；它们不得嵌入或改写被哈希的 packet payload。
- 只有当前设计/评审可由目标人类访问、准确 raw bytes/digests 已验证、审核说明完整时才允许进入人工门禁；仅 Agent 进程可读本地文件不构成 access evidence。
- **BREAKING**：将 `reviewing + APPROVABLE_WITH_WARNINGS|APPROVABLE → waiting_human` 改为还必须具备当前 packet 的 `review_packet_ready`；缺失或失败时保持 `reviewing`，并与 Review conclusion 分开记录 blocker/evidence。
- 人工决定改为绑定当前 approval packet ref/version/digest；reply/thread、显式 packet version、签名记录或当前交互会话均可作为平台无关 binding profile，superseded packet 的迟到决定保留审计但对当前状态 no-op。
- 扩展 `ARCH-CONTROL`、设计、评审、ADR、详细设计和研发交接模板的 portable refs/digests/approval evidence 追踪字段。
- 发布期无法恢复与已批准 packet 匹配的原始 bytes 时保持 `publishing`，保留真实人工决定并记录稳定 `approved_artifact_unavailable` blocker，直到准确 bytes 恢复并重新验证。
- 增加完全不依赖 Multica、PDF、comment/attachment ID 或 `parent_id` 的 standalone local-file fixtures，以及 Codex/Claude 一致性、历史 `waiting_human` 非自动迁移和发布期 digest mismatch 失败关闭测试。
- 不实现 Multica adapter、PDF renderer、附件上传或手机端行为；这些能力由后续独立 skill change 提供。

## Capabilities

### New Capabilities

- `architecture-approval-packets`: 定义 immutable portable approval packet payload、非循环 digest/readiness evidence、非授权架构建议、准确 packet 人工决定绑定和 supersession 行为。

### Modified Capabilities

- `architecture-design-governance`: 将 Reviewer approvable conclusion 与进入人工门禁解耦，要求当前 packet readiness，并定义失败时的 canonical stage/blocker/evidence 行为。
- `architecture-design-artifacts`: 增加 `ARCH-APPROVAL-PACKET` 及 design/review/packet refs、digests、access/decision evidence 在控制、发布和交接材料中的追踪要求。

## Impact

- 修改 `architecture-design-workflow/SKILL.md`、相关 references/templates、`README.md` 和 skill metadata（如触发说明需要）。
- 扩展 `tests/architecture-design-workflow-safety.sh`、fixtures、result schema、Codex/Claude behavior evidence 和 runner tests。
- 更新现有 `openspec/specs/architecture-design-governance` 与 `architecture-design-artifacts`，新增 `architecture-approval-packets` capability。
- 保持根目录 `architecture-design-workflow/` 为 Claude Code 与 Codex 共用的唯一 skill source；不新增 Runtime 配置写入或真实 HOME 安装步骤。
- 本 change 不修改 Multica、`uni-architecture`、真实 Agent/Team、Project、Issue、worktree、branch 或 commit。
