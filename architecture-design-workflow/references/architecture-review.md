# Architecture review

Reviewer 不修改 `ARCH-DESIGN`，不补写缺失证据，也不批准自己的方案。Review 必须绑定一个准确版本。

## Review dimensions

- 目标、非目标与 Subject Project 边界
- 事实新鲜度、来源、假设和未知项
- 候选方案真实性与权衡公平性
- 数据、接口、安全、可靠性、性能、容量、成本和可观测性
- 失败模式、迁移、回滚/前滚与运维责任
- 跨项目依赖、研发拆分和验证路径

## Finding contract

每个 finding 包含稳定 ID、`BLOCKER|MAJOR|MINOR`、证据、影响、建议、Owner、关闭条件和关联设计章节。

## Risk acceptance actions

若非阻断风险必须由人类显式接受，Reviewer 先为每项记录稳定 Risk ID、准确 Decision Owner、authority scope、条件、到期/复核点和所需 evidence。Architecture Lead 为每个 Risk ID 单独生成 `action_type=risk_acceptance` Human Action Request，分别展示接受、修改条件和拒绝的后果、准确回复及 After response。

不同 Owner 的风险不得合并为一个动作，不得使用“接受全部”。单项接受只绑定该 Risk ID、Owner、条件和证据；全部必需接受齐备前，Review conclusion 不能声称这些风险已接受，也不能据此生成 approval packet。风险接受是非批准信息，不替代 packet-bound human decision。

## Canonical conclusion

- `BLOCKED`：关键证据、边界或安全裁决缺失；不得进入人工批准。
- `NEEDS_REVISION`：方向可行但有必须修订的重要缺口。
- `APPROVABLE_WITH_WARNINGS`：仅剩已明确接受的非阻断风险。
- `APPROVABLE`：证据、设计和交付路径完整。

不得输出 `NO-GO`、`有条件待批准` 等新门禁值。`APPROVABLE*` 只表示版本可交给人类裁决，不等于 `approved_design_only` 或 `approved_for_spec`。

`APPROVABLE*` 也不直接进入 `waiting_human`。它触发 current approval packet 的生成与独立 readiness 验证；packet/access/digest 未验证时保持真实 Review conclusion，stage=`reviewing`，`BLOCKED_REASON=review_packet_unavailable`。`NEEDS_REVISION` 不创建 packet。

结论必须同时给出转换后的 canonical stage。关键事实或安全证据缺失的 `BLOCKED` 回到 `researching`；已有证据但设计本身必须修改的 `BLOCKED` 或 `NEEDS_REVISION` 回到 `designing`。只读测试或缺少持久化权限只限制实际写入，不改变应报告的状态转换。
