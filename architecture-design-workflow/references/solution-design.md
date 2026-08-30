# Solution design

## Versioning

每次候选方案的实质变化生成新的 `ARCH-DESIGN vN`。旧版本保持可引用，不覆盖 Review 绑定的版本。设计列出输入 `ARCH-RESEARCH` 版本、仓库提交和关键证据。

## Required structure

1. 摘要、目标、非目标
2. 背景、事实、假设、约束、未知项
3. 系统上下文、责任和信任边界
4. 至少两个真实可行候选及“不改变”的基线
5. 权衡矩阵：适配、复杂度、安全、可靠性、性能、成本、运维、迁移、锁定
6. 推荐方案、关键决定及未选理由
7. 数据、接口、安全、可靠性、性能、容量和可观测性设计
8. 失败模式、降级、迁移、回滚/前滚与分阶段发布
9. 成本、运维、组织和跨项目影响
10. 未决问题、验证计划与研发拆分建议

评分必须解释尺度和证据；不得用未经证实的数字制造精确感。缺少会改变推荐结果的事实、关键边界或验证路径时，留在 `researching|designing` 并记录 blocker。

设计完成只意味着可以独立 Review，不意味着获批，也不授权 Spec 或实施。

## Blocking clarification output

当 `critical_evidence_gaps` 的关闭需要人类选择或确认设计输入时，不得只列未知项或空白问卷。Lead 为每个 authority scope 和原子决定创建独立 `action_type=design_input` Human Action Request，并在 `ARCH-CONTROL` 中引用它。请求填写：

1. `Decision required`：当前人类可以决定的准确问题；
2. `Candidate recommendation`：基于现有证据的具体候选值，或显式 `no_recommendation`；
3. `Basis`：支持该候选的事实、推断或原则；
4. `Material risks / consequences`：接受该候选的主要代价；
5. `Missing evidence / Owner / closure condition`：不能由当前确认替代的测量或责任决定；
6. `Exact response`：`接受 / 修改 / 拒绝` 的最小可复制回复形式；
7. `After response`：各选项对应的 next stage、remaining blockers、Next Owner 和 planned writes；
8. `Stable human-accessible evidence refs`：完整设计或依据的稳定入口。

能够给出安全默认值时应给出候选方案，并把未经测量的数值标为 provisional。不能给出可靠候选时使用 `no_recommendation`，说明哪些证据会改变选择，并给出有限选项或确定的取证路径。两种情况都必须区分事实、推断、建议和未决证据。

澄清回复只关闭其明确绑定的设计输入。它不是测量证据、另一责任 Owner 的决定、Review conclusion、packet recommendation/readiness 或 packet-bound 人工批准。

若有效 `revision_requested` 没有可执行 revision brief，保留该决定和到 `designing` 的转换，在 `ARCH-CONTROL` 标记 `revision_scope=missing`，再用同一契约请求范围、优先级和验收变化。范围与稳定 context ref 验证后改为 `revision_scope=provided`。revision brief 使用独立 context ref，明确为非授权说明；旧 packet 和旧设计保持不变。

## Approval packet preparation

设计必须给出可冻结的 artifact ref、version、media type 和 raw-byte SHA-256 digest 输入边界。设计 revision 生成新 `ARCH-DESIGN`；只有 matching `ARCH-REVIEW` 给出 approvable conclusion 后才创建 approval packet。Reviewer `NEEDS_REVISION` 时不得预建、占号或伪造 packet。
