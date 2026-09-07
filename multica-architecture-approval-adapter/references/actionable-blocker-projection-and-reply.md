# Multica actionable blocker projection and reply

## Projection boundary

Adapter 读取 `architecture_blocker_action_v1|v2|v3`；v1/v2 只作审计，任何新写入必须先生成 current `architecture_blocker_action_v3` 并 supersede 旧 action。它把 `resolution_instruction_owner_ref` 唯一映射到既有 Member，把 resume/discovery actor 与 responsibility 唯一映射到既有 Agent；任何映射不唯一都在写入前返回 `needs_new_mandate_v1`，Issue unchanged。

```text
BLOCKER_ACTION_STATE=discovering|awaiting_input|received|discovery_needed|superseded|unavailable
```

blocker 固定 `requires_human_review=false`，使用 `discovery_policy=automatic_before_human`。交付前先在 manifest 授权范围内只读查询 current artifacts、evidence、ownership/config、既有 directory 与 Issue history：唯一 verified binding 直接生成 resume handoff；多个 verified candidates 按 core 的 evidence order 投影；`unavailable_with_evidence` 才自动设 `blocked --no-start` 并发布 dedicated blocker comment。v3 必须把机器缺口改写成一个 `business_question`，并携带单一 `recommendation_intent`、普通语言理由、置信度、适用边界和有序备选。它不是 `in_review`，也不请求 operational authorization。

## Decision-ready comment projection

Adapter 把 `recommendation_intent=provide_self|provide_candidate|request_discovery` 与 current Action ID 组合成本地化完整 Action；不得更改 core 推荐语义，也不得从 Issue creator/assignee、最近评论者、显示名或 instruction owner 身份补造领域责任证据。

评论按以下顺序渲染：准确 Member mention → 为什么暂停 → 一个普通业务问题 → “建议你现在这样回复（推荐）”及唯一完整 Action → 推荐理由、置信度和适用边界 → 有序备选及适用条件/后果 → 回复后行为 → 可选依据。推荐 Action 必须位于 mention 后前 **800 Unicode code points** 内，并早于 evidence link、digest、control、metadata 或 machine field。首屏不得要求读者比较无差别选项。

当 core 推荐 `request_discovery` 时，渲染 `ACTION <current-id>: 我不确定，请团队给出建议`，并说明回复后只创建有界只读调查 task，不构成 domain acceptance、Review、approval 或实施授权。

写 blocker/continuation/manifest/task-evidence metadata 前必须执行 operation-manifest 的 8 KiB aggregate budget gate。容量不足时只能用保留 current Action、attempt、instruction owner/authority、resume actor/responsibility、state 和 evidence refs 的紧凑 current projection 原子取代已确认 superseded 的 **stale current metadata**；完整历史继续保存在不可变评论、task result 或 shared evidence。不得删除历史对象，也不得重试同一 oversized value。

紧凑投影写入并逐 key 回读成功后，正常保持 `BLOCKER_ACTION_STATE=awaiting_input`。若 mandatory current identity/evidence 仍无法装入容量，返回 `metadata_capacity_exceeded`，Issue 保持 blocked，已发布 comment 保留但不得宣称 metadata/readback 完成；后续恢复必须使用新 attempt 或新的容量条件，不重复 comment、Action 或下游 task。

## Reply consumption

只消费准确 instruction owner 在同一 Issue 的 created-after-request、未编辑、唯一 current Action ID、single action 回复。`response_modes=provide_input|request_discovery`：verified-binding provide-input 仍必须包含全部 verified fields；v3 `human_declaration` provide-input 准确表达为 `ACTION <action-id>: 由我负责` 或 `ACTION <action-id>: 负责人是 <可识别的人或团队>`；request-discovery 准确表达为 `ACTION <action-id>: 我不确定，请团队给出建议`。

`human_declaration` 只提供候选责任主体，权限范围使用 current Action 已冻结的 `business_question`，adapter 按 `derive_machine_evidence_from_reply` 从 comment author、comment ref/revision/created/updated time 与 reread 结果派生机器证据，状态保持 pending verification。它不得被解释为 domain acceptance、方案批准或实现授权。`formal_source_policy=conditional`：只有用户明确表示已有正式记录但未提供入口，或 deployment policy 明确要求外部 authority record，才追加一个普通语言的来源问题；否则来源链接不是默认必填项。

规范化只允许移除一个首尾 current Architecture Agent canonical mention、Markdown mention 转义和无语义空白/换行。不得用子串或宽松自然语言匹配消费普通讨论。错误 actor、edited reply、空值、示例占位符、缺字段、多个 action、superseded action、旧回复或 discovery authority 越界均 no-write，Issue 保持 blocked。

## Friendly correction without consumption

严格消费失败后，只有同时满足准确 instruction owner、同一 Issue、created-after-request、revision 未编辑、single current blocker 且文本能唯一映射到一个允许 intent 时，才标记 `reply_correction_candidate_v1`。候选可以缺 Action ID、使用已列入受控映射的非 canonical 短句或附带不改变意图的正文；它仍然不可消费。

Adapter 可为同一 `action_id + request_revision` 至多发布一次 `reply_correction_v1`。纠错必须说明原回复尚未生效、一个普通语言失败原因、唯一完整 canonical Action 和再次回复后的行为，并记录 `invalid comment ref/revision/raw digest`、current Action identity 与 correction comment readback。纠错不得 mention Architecture Agent、不得触发 task、不得修改 Issue/blocker state、不得清除 blocker 或改变任何 Review/approval/implementation gate；`BLOCKER_ACTION_STATE` 始终为 `awaiting_input`，Issue 始终为 blocked。

重复事件回读同一幂等键后 reconciliation no-op。容量门禁或纠错写后回读失败时返回 `correction_unavailable`，保留 blocked 且不重试同一写入。wrong actor、多个互斥意图、占位值、旧或 superseded Action、多个 current blocker 或无法唯一识别 intent 的文本继续静默 fail closed，不发布纠错。

有效 `provide_input` 先把状态记为 `received` 并映射 resume actor；其中 `human_declaration` 必须由 resume actor 验证候选而非直接闭合 binding。有效 `request_discovery` 记为 `discovery_needed` 并映射既有 `coordination|research` discovery actor。两者都自动派生 single-consumption continuation/handoff。只有 mapping 唯一且 task readback 为 queued/running（portable `accepted|active`）时，才执行 `in_progress --no-start` 并回读，随后清除 blocker。

若 handoff comment 已写但 task 未入队、映射漂移或 readback 失败，执行 blocked rollback：保留全部对象与 received reply evidence，把 Issue 恢复/保持 blocked，重新发布的 action 必须是新 attempt 并 supersede 旧 action；不得留下空闲的 in_progress。

## Idempotency

同一 blocker action 与回复各只消费一次。重复事件回读既有 task/evidence 并 reconciliation no-op；不重复评论、不重复触发 task、不编辑历史。自动交付、reply validation、handoff、status 和 readback 都属于 current mandate 的非 Review 操作。
