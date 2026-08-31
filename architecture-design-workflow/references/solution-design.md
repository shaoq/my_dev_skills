# Solution design

## Versioning

每次候选方案的实质变化生成新的 `ARCH-DESIGN vN`。它的 canonical 载体是独立 UTF-8 Markdown 文件 `ARCH-DESIGN-vN.md`；冻结后计算完整 raw-byte SHA-256，旧版本保持可引用，不覆盖 Review 或 Human Action Request 绑定的版本。设计列出输入 `ARCH-RESEARCH` 版本、仓库提交和关键证据。不得从多条 Issue 评论、摘要或 renderer 正文重建 canonical 设计；修订必须产生新版本和新 digest。

未批准的设计文件只作为 Issue/material delivery 的版本化输入，不写入架构仓库的正式 decisions/designs 目录。只有批准版本按发布流程进入正式文档目录。

`Design readiness` 是 artifact-local 质量字段，不新增 canonical stage：

- `incomplete`：缺少完整文档结构，不得发起内容决定；
- `draft_complete`：总体架构完整，但仍有具名决策或证据缺口；
- `decision_ready`：完整方案已绑定当前一个人类决定及可访问材料；
- `ready_for_review`：全部 Review entry criteria 已满足。

## Required structure

1. Identity、status、Design readiness、canonical filename/encoding/raw-byte digest 与输入证据；
2. 执行摘要，以及 Architecture Team 的 Recommendation / rationale / confidence；
3. 问题、当前状态、架构驱动因素、事实、假设、约束和未知项；
4. Goals / Non-goals；
5. 系统上下文、责任/信任边界和简化架构图；
6. 组件、数据流、控制流、接口和一致性语义；
7. 正常流程与关键失败流程；
8. 安全、隐私、可靠性、性能、容量、成本、可观测和评测设计；
9. 至少两个真实可行候选及“不改变”的基线、权衡矩阵、推荐与淘汰理由；
10. 迁移、分阶段发布、回滚/前滚和退出路径；
11. 运维/RACI、组织和跨项目影响；
12. 已确定与尚未确定内容、风险、验证/验收计划和研发拆分建议。

评分必须解释尺度和证据；不得用未经证实的数字制造精确感。缺少会改变推荐结果的事实、关键边界或验证路径时，留在 `researching|designing` 并记录 blocker，但仍须完整写出已冻结的平台无关架构、当前默认/PoC 推荐、每个未决变量及会改变推荐的证据。不能用问卷或零散评论代替方案本体。

设计完成只意味着可以独立 Review，不意味着获批，也不授权 Spec 或实施。

## Blocking clarification output

当 `critical_evidence_gaps` 的关闭需要人类选择或确认设计输入时，不得只列未知项或空白问卷。Lead 为每个 authority scope 和原子决定创建独立 `action_type=design_input` Human Action Request，并在 `ARCH-CONTROL` 中引用它。面向一个当前读者的请求只呈现其唯一 authority scope 内的一项可操作决定；其他 Owner 只列为 non-actionable dependencies。Owner 未唯一绑定时先请求 routing/owner-binding，不让当前读者代替专业 Owner 决定内容。请求填写：

1. `Decision required`：当前人类可以决定的准确问题；
2. `Candidate recommendation`：基于现有证据的具体候选值，或显式 `no_recommendation`；
3. `Basis`：支持该候选的事实、推断或原则；
4. `Material risks / consequences`：接受该候选的主要代价；
5. `Missing evidence / Owner / closure condition`：不能由当前确认替代的测量或责任决定；
6. `Exact response`：`接受 / 修改 / 拒绝` 的最小可复制回复形式；
7. `After response`：各选项对应的 next stage、remaining blockers、Next Owner 和 planned writes；
8. `Stable human-accessible evidence refs`：完整设计或依据的稳定入口。

Human Action Request 使用 [Human Action Request](human-action-request.md) 的 `Architecture Decision Brief`，只摘要方案并导航到完整 `ARCH-DESIGN-vN.md`；不得把完整设计正文或多个 Owner 的回复表单复制进同一决策入口。

能够给出安全默认值时应给出候选方案，并把未经测量的数值标为 provisional。不能给出可靠候选时使用 `no_recommendation`，说明哪些证据会改变选择，并给出有限选项或确定的取证路径。两种情况都必须区分事实、推断、建议和未决证据。

澄清回复只关闭其明确绑定的设计输入。它不是测量证据、另一责任 Owner 的决定、Review conclusion、packet recommendation/readiness 或 packet-bound 人工批准。

若有效 `revision_requested` 没有可执行 revision brief，保留该决定和到 `designing` 的转换，在 `ARCH-CONTROL` 标记 `revision_scope=missing`，再用同一契约请求范围、优先级和验收变化。范围与稳定 context ref 验证后改为 `revision_scope=provided`。revision brief 使用独立 context ref，明确为非授权说明；旧 packet 和旧设计保持不变。

## Approval packet preparation

设计必须给出可冻结的 artifact ref、version、media type 和 raw-byte SHA-256 digest 输入边界。设计 revision 生成新 `ARCH-DESIGN`；只有 matching `ARCH-REVIEW` 给出 approvable conclusion 后才创建 approval packet。Reviewer `NEEDS_REVISION` 时不得预建、占号或伪造 packet。
