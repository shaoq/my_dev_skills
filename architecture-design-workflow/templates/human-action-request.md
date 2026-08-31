# HUMAN-ACTION-REQUEST

## Architecture Decision Brief

## 当前方案摘要

<用一个自然段说明问题、推荐架构、主要价值和当前限制；不复制完整设计正文。>

## 简化架构图

```text
<portable simplified architecture diagram>
```

## Architecture Team 总体建议

- Recommendation / rationale / confidence：
- Candidate recommendation：`<candidate_id + recommendation>|no_recommendation`
- Basis — facts / inferences / principles：

## 已确定与尚未确定

- Determined：
- Undetermined：
- Other-owner dependencies (non-actionable)：

| Action / dependency | Owner / authority scope | Impact | Closure condition |
|---|---|---|---|
|  |  |  |  |

## 最重要的备选及后果

- Option consequences / material risks：

| Option | What this means | Benefits | Costs / material risks | Irreversible impact |
|---|---|---|---|---|
|  |  |  |  |  |

## 当前读者的一项决定

- Action ID / type / current status：`<action_id>` / `design_input|architecture_review|architecture_approval` / `current|answered|superseded`
- Requires human review：`true`；不满足 Review 前提时不得渲染本模板的可执行回复。
- Human Action State：`none|preparing|awaiting_response|received|unavailable|superseded`
- Wait reason：`none|target_project|design_approval|awaiting_human_confirmation`
- Platform status intent：`agent_working|human_review|hard_blocked|terminal`
- Why now：
- Decision Owner / authority scope：
- Current reader / authority binding：`unique|unbound|ambiguous` / `<evidence ref>`
- Content-decision activation gate：`ready|not_ready`；未验证材料时由 workflow mandate 自动完成验证或记录 evidence gap，不得展示内容决定回复。
- 一句话决定：
- Decision required：
- Bounded alternatives：见上一节；只有本 action 的回复格式可执行。

## 回复后会发生什么

| Response | Next stage / remaining blockers / Next Owner / planned writes | New artifact/version | Irreversible effect |
|---|---|---|---|
|  |  |  |  |

`planned_writes` 只列既有 canonical artifact 目标；本请求随控制评论呈现时使用 `issue:ARCH-CONTROL`，不创建新的 artifact type。

## 完整材料入口

- Stable human-accessible evidence refs：

| Material identity / version | Human-facing entry | Requested client scopes | Access status by scope (`opened|unavailable|not_run`) | Verifier / verification time | Evidence ref / closure condition |
|---|---|---|---|---|---|
| Design |  |  |  |  |  |
| Research |  |  |  |  |  |
| Control |  |  |  |  |  |

- Target-human access confirmation：`confirmed|unconfirmed|none`
- Missing evidence / Owner / closure condition：

## Exact response

仅当 Current reader binding=`unique`、`requires_human_review=true` 且 Content-decision activation gate=`ready` 时展示内容决定回复。否则只展示缺失证据、Owner 和恢复路径，不展示 operational、access confirmation 或 routing token。

复制一个合法回复，并补齐占位符：

```text
ACTION <action_id>: <type-specific exact response>
```

## Authority boundary

- Authorizes：
- Does not authorize：
- Non-authoritative context：candidate recommendation、说明性文字和 revision brief 不替代对应 canonical evidence 或正式批准 token。

## Minimal audit binding

- Bound artifact or routing version：
- Risk ID / packet digest / context ref：
- Current / superseded：`current|superseded`
- Recorded evidence / time：
