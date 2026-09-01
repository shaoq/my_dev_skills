# Multica actionable blocker projection and reply

## Projection boundary

Adapter 读取 `architecture_blocker_action_v1|v2|v3`；v1/v2 只作审计，任何新写入必须先生成 current `architecture_blocker_action_v3` 并 supersede 旧 action。它把 `resolution_instruction_owner_ref` 唯一映射到既有 Member，把 resume/discovery actor 与 responsibility 唯一映射到既有 Agent；任何映射不唯一都在写入前返回 `needs_new_mandate_v1`，Issue unchanged。

```text
BLOCKER_ACTION_STATE=discovering|awaiting_input|received|discovery_needed|superseded|unavailable
```

blocker 固定 `requires_human_review=false`，使用 `discovery_policy=automatic_before_human`。交付前先在 manifest 授权范围内只读查询 current artifacts、evidence、ownership/config、既有 directory 与 Issue history：唯一 verified binding 直接生成 resume handoff；多个 verified candidates 发布含建议/理由/置信度/后果的简单选择；`unavailable_with_evidence` 才自动设 `blocked --no-start` 并发布 dedicated blocker comment。v3 必须把机器缺口改写成一个 `business_question`，首屏按“为什么暂停→团队建议→一个问题→最多三个直接回复→回复后行为→可选依据”渲染，不得用治理记录类型或机器字段代替问题。它不是 `in_review`，也不请求 operational authorization。

写 blocker/continuation/manifest/task-evidence metadata 前必须执行 operation-manifest 的 8 KiB aggregate budget gate。容量不足时只能用保留 current Action、attempt、instruction owner/authority、resume actor/responsibility、state 和 evidence refs 的紧凑 current projection 原子取代已确认 superseded 的 **stale current metadata**；完整历史继续保存在不可变评论、task result 或 shared evidence。不得删除历史对象，也不得重试同一 oversized value。

紧凑投影写入并逐 key 回读成功后，正常保持 `BLOCKER_ACTION_STATE=awaiting_input`。若 mandatory current identity/evidence 仍无法装入容量，返回 `metadata_capacity_exceeded`，Issue 保持 blocked，已发布 comment 保留但不得宣称 metadata/readback 完成；后续恢复必须使用新 attempt 或新的容量条件，不重复 comment、Action 或下游 task。

## Reply consumption

只消费准确 instruction owner 在同一 Issue 的 created-after-request、未编辑、唯一 current Action ID、single action 回复。`response_modes=provide_input|request_discovery`：verified-binding provide-input 仍必须包含全部 verified fields；v3 `human_declaration` provide-input 准确表达为 `ACTION <action-id>: 由我负责` 或 `ACTION <action-id>: 负责人是 <可识别的人或团队>`；request-discovery 准确表达为 `ACTION <action-id>: 我不确定，请团队给出建议`。

`human_declaration` 只提供候选责任主体，权限范围使用 current Action 已冻结的 `business_question`，adapter 按 `derive_machine_evidence_from_reply` 从 comment author、comment ref/revision/created/updated time 与 reread 结果派生机器证据，状态保持 pending verification。它不得被解释为 domain acceptance、方案批准或实现授权。`formal_source_policy=conditional`：只有用户明确表示已有正式记录但未提供入口，或 deployment policy 明确要求外部 authority record，才追加一个普通语言的来源问题；否则来源链接不是默认必填项。

规范化只允许移除一个首尾 current Architecture Agent canonical mention、Markdown mention 转义和无语义空白/换行。不得用子串或宽松自然语言匹配消费普通讨论。错误 actor、edited reply、空值、示例占位符、缺字段、多个 action、superseded action、旧回复或 discovery authority 越界均 no-write，Issue 保持 blocked。

有效 `provide_input` 先把状态记为 `received` 并映射 resume actor；其中 `human_declaration` 必须由 resume actor 验证候选而非直接闭合 binding。有效 `request_discovery` 记为 `discovery_needed` 并映射既有 `coordination|research` discovery actor。两者都自动派生 single-consumption continuation/handoff。只有 mapping 唯一且 task readback 为 queued/running（portable `accepted|active`）时，才执行 `in_progress --no-start` 并回读，随后清除 blocker。

若 handoff comment 已写但 task 未入队、映射漂移或 readback 失败，执行 blocked rollback：保留全部对象与 received reply evidence，把 Issue 恢复/保持 blocked，重新发布的 action 必须是新 attempt 并 supersede 旧 action；不得留下空闲的 in_progress。

## Idempotency

同一 blocker action 与回复各只消费一次。重复事件回读既有 task/evidence 并 reconciliation no-op；不重复评论、不重复触发 task、不编辑历史。自动交付、reply validation、handoff、status 和 readback 都属于 current mandate 的非 Review 操作。
