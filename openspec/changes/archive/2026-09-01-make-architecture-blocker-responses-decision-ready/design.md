## Context

`require-actionable-architecture-blockers` 已把 dependency input 改写成普通业务问题，并提供三类带 current Action ID 的回复。UNIDRAG-12 的真实交互仍暴露两个缺口：回复被平级陈列而没有当前建议；准确 Owner 使用“我负责提供”等单一明确自然语言时，严格消费正确 fail closed，但用户没有得到下一步的准确修复文本。

`architecture-design-workflow` 必须继续平台中立；它只决定 recommendation 的业务语义。`multica-architecture-approval-adapter` 才负责 Member mention、Action ID、本地化回复、评论布局、Issue 状态和幂等纠错。Multica 核心不在本 change 范围内。

## Goals / Non-Goals

**Goals:**

- 每个需要人类输入的 current blocker 只有一个明确推荐意图，并说明理由、置信度、边界与备选后果。
- 在 Multica 评论首部展示完整 canonical Action，使网页和手机端读者无需展开审计内容即可复制。
- 对唯一、明确但格式无效的回复给出一次友好纠错，同时保持严格消费与状态门禁。
- 通过可执行 fixtures 验证推荐、纠错、幂等与 fail-closed 行为。

**Non-Goals:**

- 不把自然语言模糊匹配升级为有效回复消费。
- 不自动决定领域责任，不降低 Review、approval、风险接受或实现授权。
- 不让 portable core 依赖 Team、Agent、Issue、comment、mention、URL、CLI 或 Multica 状态。
- 不修改 Multica runtime/core，也不创建 Team、Agent 或 Issue。

## Decisions

### 1. Core 只产出平台无关推荐投影

current blocker 增加以下语义：

```text
recommendation_intent=provide_self|provide_candidate|request_discovery
recommendation_reason=<plain-language reason grounded in current evidence>
recommendation_confidence=high|medium|low|unknown
recommendation_boundary=<what this response does and does not decide>
ordered_alternatives=<remaining intents with condition and consequence>
```

唯一 verified binding 直接 continuation，不发布 blocker。只有证据可明确支持当前用户或某个候选时才推荐 `provide_self|provide_candidate`；多个候选不可排序、`unavailable_with_evidence`、低置信度或 unknown 时推荐 `request_discovery`。禁止用 Issue creator、assignee、最近评论者或 instruction owner 身份猜测 domain Owner。

### 2. Adapter 负责 current Action 和首屏布局

Adapter 把 portable intent 与 current Action ID、本地化语句组合。评论顺序固定为：准确 Member mention、暂停原因、唯一业务问题、推荐完整 Action、理由/置信度/边界、备选、回复后行为、可选依据。推荐 Action 必须位于 mention 后 800 个 Unicode code points 内，并早于 evidence link、digest、control 和 machine fields。

### 3. 纠错是独立、非消费、非状态变更投影

`reply_correction_candidate_v1` 仅在准确 Owner、同一 Issue、created-after current request、revision 未编辑、single current blocker 且意图唯一时成立。缺 Action ID、非 canonical 措辞或额外正文仍不可消费，但 adapter 可为同一 `action_id + request_revision` 至多发布一次 `reply_correction_v1`，说明未生效原因并给出唯一完整 Action。

纠错不得 mention Architecture Agent、触发 task、修改 Issue/blocker state 或改变任何 gate。它绑定 invalid comment ref、revision、raw digest 和 current Action；重复事件 reconciliation no-op。wrong actor、多意图、占位值、旧/superseded Action 或意图不明继续静默 fail closed。

### 4. Canonical reply 路径保持严格

只有 current canonical reply 才进入既有消费流程；且只有 resume/discovery handoff task 回读 `accepted|active` 后，Issue 才可由 `blocked` 恢复 `in_progress`。纠错路径始终保持 `BLOCKER_ACTION_STATE=awaiting_input` 与 Issue `blocked`。

## Risks / Trade-offs

- [自然语言意图识别过宽] → 只识别 fixtures 明确定义的有限表达；存在多个意图或额外权限语义时静默 fail closed。
- [纠错评论重复] → 以 `action_id + request_revision` 为幂等键，并绑定原评论 digest；容量或回读失败时保留 blocked，不重试同一写入。
- [首屏内容仍过长] → 对 mention 后 800 code-point 预算做确定性测试，审计字段全部后置。
- [推荐被误读为批准] → recommendation boundary 明确它只协助补齐 dependency input，不能构成 domain acceptance 或任何架构/实施 gate。

## Migration Plan

1. 先添加失败 fixtures，锁定当前缺失的 recommendation 与 correction 行为。
2. 更新 portable core reference/template/Skill，再更新 optional Multica adapter reference/template/Skill。
3. 运行两个 Skill 的静态安全检查、行为 fixtures、OpenSpec strict validation 与 package validation。
4. 与 `uni-architecture` 同名 change 对齐 affected-surface manifest 后覆盖安装既有两个 Skill identity。
5. 用 UNIDRAG-12 的 superseding blocker attempt 做真实人工验收；旧无效回复仅保留为审计证据。

回滚时恢复两个 Skill package 的上一版本；已发布评论和旧回复保持不可变审计记录，不追溯消费。

## Open Questions

无。真实手机端可读性由当前 instruction owner 在 live acceptance 中手动确认。
