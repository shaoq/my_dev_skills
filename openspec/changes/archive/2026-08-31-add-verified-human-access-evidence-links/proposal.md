## Why

UNIDRAG-12 的真实回归表明，Human Action Request 把九个权限域的问题堆进一条评论，并以不可点击的 `multica://issues/...` 指向埋在历史评论中的设计。完整方案没有作为独立附件交付，决策者既无法在网页/手机端稳定打开方案，也难以从评论中快速理解总体架构、团队建议和自己真正有权决定的事项。后续授权交付验证还暴露出两个连续的未来身份循环：授权回复 ID 在 scope 冻结时尚未产生；而准备任务返回的授权请求又会由 Multica 自动投递成一条新的 task-result comment，其 comment ID 同样在 scope 冻结时未知。只解决回复 parent 而继续要求预先冻结请求 comment ID，仍会使授权 fail closed。

## What Changes

- 收紧 `ARCH-DESIGN` 契约：每个待人评审的版本都必须形成一份独立、完整、高级架构师可直接阅读的 canonical Markdown 文档，而不是依赖零散评论拼接方案。
- 在 Multica 人工决策入口把完整 `ARCH-DESIGN-vN.md` 作为版本化附件交付；若 Markdown 不能同时满足网页和手机阅读，则增加同内容 PDF 展示附件，Markdown 仍是权威版本。
- 把评论固定为 `Architecture Decision Brief`：一段式方案摘要、简化架构图、Architecture Team 总体建议/理由/置信度、已确定与未确定内容、最重要备选及后果、当前读者有权决定的一项内容、回复后行为，以及可点击的完整 Design/Research/Control 入口。
- Human Action Request 只向当前可识别且具备对应 authority scope 的 Decision Owner 请求一个原子决定；其他 Owner 的事项只作为依赖摘要，不再把多权限域问卷当作当前人的审批请求。
- 收紧平台无关材料访问契约：材料入口只有在目标人类可直接打开、指向准确材料且具有逐客户端验证证据时，才能标记为 human-accessible；否则必须显式报告不可用及关闭条件。
- 为 Multica 适配器定义附件优先的 `multica_human_action_material_bundle_v1`，并保留已验证的 Web 评论 permalink 用于 Research/Control 等既有评论材料。
- 禁止把未经当前 Multica 版本能力验证的自定义 URI（包括 `multica://issues/...`）放进面向人的材料入口。
- 在发布后验证 Design 附件卡片/链接、Research/Control 链接、准确材料身份和完整内容；网页与手机结果分别记录，未实测不得声称已确认。
- 无法交付并验证完整方案附件时，不得请求正式内容决定；不能以本地路径、临时下载 URL、附件名称或纯文本伪链接代替。
- 增加完整架构文档、决策简报、附件访问、单 Owner 决策、正向 permalink 与反向 `multica://issues` 的契约回归测试，并保持核心 Skill 不依赖 Multica。
- 为平台自动投递的授权请求增加 canonical request selector `multica_task_result_authorization_request_v1`：scope 冻结 preparation task、原 trigger、Agent、Issue/workspace、授权身份和唯一性条件；平台投递完成后通过 `source_task_id` 解析并重读准确 request comment。
- 为 comment-triggered 运维授权保留 canonical response-parent selector `multica_authorization_response_parent_v1`：执行时只在授权回复的 direct parent 等于已解析 request comment 且其他绑定全部通过后，解析为当前任务的 `trigger_comment_id`。
- 把 Multica 自动 materialize 的 task result comment 明确建模为平台管理的预期对象，而不是 Agent 主动 Issue write；禁止再声称任务结果“没有产生平台评论”，也不把该预期对象误判为未授权副作用。
- 禁止用未列入 `planned_writes` 的 Issue 评论请求授权、报告诊断或修补失败；没有评论写权限时，授权请求和失败原因只通过 task result 返回。
- 保持 Issue 在材料准备和交付期间为 `in_progress`；任何状态变更都必须作为独立、明确的 planned write 获得授权。
- 冻结材料交付的执行 cwd 与 external-file 模式；仅当 scope 明确列出 `allow_external_file=true` 时才可使用 Multica CLI `--allow-external-file`。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `architecture-design-artifacts`：把 `ARCH-DESIGN` 收紧为可作为独立附件交付的完整架构文档，并定义进入人工决策前的完整性门槛。
- `architecture-human-action-requests`：收紧“stable human-accessible evidence ref”的成立条件、验证证据和不可用处理。
- `multica-architecture-human-action-rendering`：定义附件优先的材料 bundle、Decision Brief、当前 Owner 决策过滤、Web comment permalink、发布后可点击性/定位验证及网页/手机证据。

## Impact

- 影响 `architecture-design-workflow` 的 `ARCH-DESIGN`、Human Action Request reference/template 与契约测试。
- 影响 `multica-architecture-approval-adapter` 的 Human Action Request renderer、附件交付映射、材料引用规则、验收清单及契约测试。
- 影响 adapter 运维授权的 request/result binding、parent-binding 和 comment-triggered delivery 校验，不改变 Multica CLI 的 `--parent <actual-id>` 接口，也不修改 Multica 的 task-result 自动投递行为。
- 不修改 Multica 核心代码、CLI、数据库或 API；不执行 Skill import、Agent binding、Issue 评论或任何平台写入。
- 既有架构决定和历史审批证据保持有效；未经验证的历史链接不会被追溯声明为可访问。
