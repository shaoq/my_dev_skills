## Why

`architecture-design-workflow` 已能生成并验证 portable approval packet，但在 Multica Issue 中仍缺少一套确定的 delivery、readiness 和 human-decision 映射，因此完整方案、评审和建议无法稳定地以手机可打开的材料交付，也无法把人类回复可靠绑定到准确 packet。Multica 当前已有评论回复、附件、Issue metadata、移动端附件打开和 Skill/Agent 配置能力，本 change 应在 Skill/配置层复用这些通用能力，而不是修改 Multica 核心代码。

## What Changes

- 新增独立 sibling skill `multica-architecture-approval-adapter`，固定消费 `architecture-design-workflow` portable core contract implementation commit `1d4b860b48e15f678d78a71bf2c38557ab9c2951`，不得反向修改或替代 core 状态机。
- 将 delivered `ARCH-DESIGN`、`ARCH-REVIEW` 和 `ARCH-APPROVAL-PACKET` 映射为 Multica Issue 中的简短审核评论与可打开附件；评论只展示版本、Reviewer conclusion、Architecture Team recommendation/理由、关键风险、待确认项和合法决定，不复制完整方案正文。
- 定义 `multica_attachment` durable access profile：保存 comment/attachment refs，回读 canonical download URL 对应 bytes 并核对 raw-byte SHA-256；为手机端至少提供稳定附件卡片和可打开的 UTF-8 readable copy，PDF 仅可作为非权威可选派生件。
- 将上传、评论创建和 metadata 更新设计为可重试 reconciliation workflow；以 Issue、packet ref/version/digest、adapter marker 和单调 version fence 识别既有 delivery，避免重试重复发布、旧运行覆盖新 packet projection 或把孤立上传误记为 ready。
- 从 packet 评论线程读取 member-authored decision reply；只有精确绑定 packet target human、唯一映射到 Multica member ID 且包含合法 decision 的回复才生成 portable human decision evidence。同一 actor 的后续独立合法评论按服务器顺序替换其先前决定；模糊 `OK`、非目标 member、Agent 回复、旧 packet 回复、编辑漂移和引用文本均为 no-op 或失败关闭。
- 使用单个 Issue metadata primitive key 原子记录轻量 current projection 和 reconciliation refs，并在写前、写后重新扫描 current packet；metadata 不充当 packet 原文、人工批准或唯一审计证据，平台写入/回读失败或发现 stale writer 时产生 `review_packet_unavailable` 并保持 core canonical stage。
- 定义 `shared_workspace_sidecar_v1`：仅使用用户确认的既有 durable shared scope，以安全 write-once、atomic no-clobber publish 与 reread 保存完整 mapping/readiness/decision evidence；scope/授权/回读缺失时 readiness unavailable 或 decision 不生效，不创建任何 resource。
- 保留无网络的 normalized contract fixtures 和轻量静态校验，用于约束 fail-closed evidence 边界；本 change 不新增 fake `multica` CLI、双 Runtime behavior evidence 或额外回归测试，真实平台行为由 capability preflight 与另行授权的 sandbox acceptance 验证。
- 提供显式 activation runbook：本地双 Runtime 链接、`.skill`/`.zip` 打包、workspace import、以 additive `agent skills add` 绑定及最终只读核验；实施过程不自动创建或修改真实 Skill、Agent、Team、Project、Issue 或配置。
- 不修改 Multica、`uni-architecture` 或 `architecture-design-workflow` 核心文件；若 capability preflight 发现现有 Multica 接口不满足契约，adapter 必须失败关闭并另行提出平台通用能力 change。

## Capabilities

### New Capabilities

- `multica-architecture-approval-delivery`: 定义 portable artifacts 到 Multica 审核评论、附件、手机可读引用、digest 回读验证、metadata projection 和失败关闭的映射。
- `multica-architecture-approval-decision-binding`: 定义从 Multica 评论线程识别准确 current-packet 人工决定、拒绝模糊/Agent/旧版本回复以及幂等审计的规则。
- `multica-architecture-adapter-activation`: 定义 adapter 的双 Runtime 安装、Multica workspace import、additive Agent 绑定、版本核验和不自动激活边界。

### Modified Capabilities

无。portable core、架构状态机和现有 Multica 平台契约保持不变。

## Impact

- 在 `my_dev_skills` 新增 `multica-architecture-approval-adapter/` 的 `SKILL.md`、references、templates/metadata，并更新 `README.md`。
- 使用 repository 既有 installer/validator 路径做隔离校验，确认新 sibling skill 与 `architecture-design-workflow` 分别安装且不会产生反向依赖；不新增额外回归测试。
- 新增最小 normalized result schema/contract fixtures；不新增 adapter safety runner、fake CLI 或 Codex/Claude 双 Runtime behavior evidence。
- 运行时只消费 Multica 已有 CLI/API 行为：`issue comment add/list --parent/--attachment`、attachment download URL、`issue metadata`、`skill import` 和 `agent skills add/list`；不在本仓库复制 Multica 客户端实现。
- 本 change 不修改 `/Users/jie.hua/Documents/Developments/Projects/github/multica`、`uni-architecture`、真实 Runtime HOME、远程 workspace 或任何外部资源，也不创建 branch、worktree 或 commit。
