## Why

当前 `architecture-design-workflow` 只在 `critical_evidence_gaps` 下要求可审核澄清结构；Subject/Target Project 路由、非阻断风险接受、正式批准、修订、拒绝、发布与研发交接仍可能只展示状态、技术字段或合法 token，导致人类难以快速理解决定对象、备选项及其后果。需要一个平台无关、贯穿全部人工推进点的统一呈现契约，同时保持既有状态机、证据门禁和批准语义不变。

## What Changes

- 新增平台无关的 `Human Action Request` 契约；凡 `Next action` 需要可识别人类选择、确认、接受风险、批准或路由，都必须生成可独立理解和准确回复的决策卡片。
- 要求每张卡片绑定单一 action type、准确版本、具名 decision owner、候选建议或 `no_recommendation`、有限备选、逐项后果、移动端可访问证据、未决证据、准确回复格式、回复后的状态变化及非授权边界。
- 将 Subject/Target Project 路由、brainstorming conclusion、`critical_evidence_gaps`、非阻断风险接受、正式 packet 决定、发布目标与 R&D handoff 路由纳入统一契约，但保持各门禁不同的合法决定值。
- 改进 `ARCH-APPROVAL-PACKET` human review brief，使四种合法决定以中文解释真实后果；为 `revision_requested` 支持与权威 token 分离的可执行修订说明引用。
- 保持技术审计字段与面向人的决策摘要分层，完整设计/评审/packet 继续通过稳定、可访问的完整材料引用提供，不把本机绝对路径当作人类访问证据。
- 增加跨门禁行为 fixtures 和契约验证，证明输出不仅字段齐全，而且一个 action item 不混合多个权限域或多个独立决定。
- 不改变 canonical stage、Review conclusion、human decision token、OpenSpec 边界或任何平台专有字段。

## Capabilities

### New Capabilities

- `architecture-human-action-requests`: 定义平台无关的人工动作类型、决策卡片结构、Owner/版本绑定、回复和状态后果契约。

### Modified Capabilities

- `architecture-design-artifacts`: 使控制记录、Review、approval packet 和 handoff 的人工入口使用统一且可访问的决策摘要。
- `architecture-design-governance`: 将所有人工推进点纳入明确、非歧义且不越权的决定语义和状态转换规则。
- `architecture-approval-packets`: 扩展 human review brief 的中文选项后果、风险接受和修订说明边界，同时保持 packet 不可变性及四种合法 token。

## Impact

影响 `architecture-design-workflow` 的主说明、路由/设计/Review/packet/发布/handoff references、相关模板、行为 fixtures/runner、主 OpenSpec 规格与验证证据。该变更不依赖 Multica，可在 standalone local-file/current-session profile 下独立使用；不修改业务代码、Multica 核心或 Runtime 配置。
