# HUMAN-DECISION-MATERIAL

> 【需要阅读并确认】`audience=human`；`review_requirement=required`；`bound_action=<action_id>`
>
> Material type：`canonical_design|decision_detail`。`decision_detail` 不是总体架构设计，也不能替代后续 `ARCH-DESIGN-vN.md`。

## 需要决定什么

<用一至两段普通语言完整说明当前唯一决定、业务/技术背景、范围边界，以及为什么现在必须决定。>

## 简化架构图

<嵌入或链接当前 Design 绑定的 Archify light/1440x900 静态预览；图可相对详细，至少显示主要组件、边界、关键流向与本次决定影响点。>

```text
<无 Archify 时使用可读的 portable diagram；不得用 receipt、digest 或机器日志代替架构语义。>
```

## 推荐方案

- 推荐：`<candidate_id>|no_recommendation`
- 理由：<关键事实、推断和原则>
- 置信度：`high|medium|low|unknown`
- 最关键收益与代价：<summary>

## 方案对比（最多 2～3 项）

| 方案 | 做法与适用条件 | 收益 | 代价 | 主要风险 | 不可逆影响 |
|---|---|---|---|---|---|
|  |  |  |  |  | `none known` 或具体影响 |

## 已确定、未确定与关闭条件

- 已确定：
- 未确定：
- Evidence gap / Owner / closing condition：
- Other-owner dependencies（non-actionable）：

## 回复后立即发生什么

| 回复 | Next stage | Next Owner | Direct planned writes | Remaining blockers / irreversible effect |
|---|---|---|---|---|
|  |  |  |  |  |

## 唯一 Action

```text
ACTION <action_id>: <type-specific exact response>
```

若入口打不开：`ACTION <action_id>: 材料打不开`

若能够打开但内容不足以决策：`ACTION <action_id>: 材料不可决策; reason=<原因>`

## Authority boundary

- Authorizes：
- Does not authorize：OpenSpec、实现、部署、资源创建或其他 Owner 的决定，除非当前 Action 明确包含该 authority scope。

## Internal binding（折叠/机器读取）

`human_surface_contract=human_review_surface_v2`；`material_access_state=opened|manual_check_required|unavailable|not_run`；`decision_readiness_state=validated|manual_check_required|unreadable|incomplete|not_run`；`current|superseded`。
