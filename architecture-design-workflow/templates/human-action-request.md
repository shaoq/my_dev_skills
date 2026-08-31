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

- Action ID / type / current status：`<action_id>` / `design_input|risk_acceptance|design_approval|routing|access_confirmation` / `current|answered|superseded`
- Why now：
- Decision Owner / authority scope：
- Current reader / authority binding：`unique|unbound|ambiguous` / `<evidence ref>`
- Content-decision activation gate：`ready|access_confirmation_required`；未验证材料时本 action 必须是 `access_confirmation|routing`，不得展示内容决定回复。
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

仅当 Current reader binding=`unique` 且 Content-decision activation gate=`ready` 时展示内容决定回复。否则这里只展示当前 `access_confirmation|routing` 的准确回复，并把内容决定列为 non-actionable pending action。

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
