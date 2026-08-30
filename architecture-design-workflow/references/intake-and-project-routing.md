# Intake and project routing

## Applicability

本 skill 适用于复杂架构升级、全新系统、跨系统混合方案、架构方案评审、批准后 ADR 发布和研发交接。以下请求不由它主导：普通 bug 调查、任务状态查询、已批准 OpenSpec 实施、源代码 Review、局部无架构影响的重构。

## Intake record

开始时为 `ARCH-CONTROL` 收集：Issue、请求者、角色 Owner、Subject Project、涉及项目/仓库、设计类型、当前 stage、输入版本、预期产物、`WAIT_REASON`、`BLOCKED_REASON`、人工 gate 和下一动作。

Issue 未提供时不得伪造。可以在回复中生成待发布的 `ARCH-CONTROL`，并把缺少 Issue 记录为证据限制。

## Project routing

- 单项目：Subject Project 承担架构决策与长期文档；目标研发项目可相同。
- 多项目：选择一个 Subject Project 保存共同决策，逐项列出受影响项目、边界与 Owner。不得默认把第一个代码仓库当作架构归属。
- Subject Project 未定：保持 `waiting_human`，`WAIT_REASON=target_project`，`BLOCKED_REASON=missing_subject_project`。
- 已有 `approved_for_spec` 但目标研发项目未定：保留批准证据，保持 `waiting_human`，`WAIT_REASON=target_project`。

两种缺失都必须生成 `action_type=routing` 的 Human Action Request，而不是只要求“给出项目名”。请求应基于已知所有权、共同协议、文档长期归档和跨项目责任给出候选建议或 `no_recommendation`；备选只包含已存在且确实可承担该责任的项目，并逐项说明选择后的 owner、文档归属、remaining blockers 和 planned writes。提供稳定可访问的归属证据引用与准确回复，例如 `ACTION <id>: select subject_project=<existing_project>; reason=<reason>`。

路由确认只改变明确绑定的项目归属。它不批准设计，不授权创建缺失 Project、仓库、Issue、Team、Agent、OpenSpec 或实现。

本 skill 不创建缺失的 Project、Issue、仓库、Team 或 Agent。

## Transition and handoff

只有 `SKILL.md` 列出的 canonical stages 可持久化。`revision_requested` 是 decision；`BLOCKED` 等 Review conclusion 不是 stage。

- 非法或不明转换：保持原 stage，报告期望输入。
- 依赖/证据缺失：保持原 stage，记录 `BLOCKED_REASON`。
- `rejected`、`handed_off`、`completed_design_only` 是终态；不得隐式重开。

每次 Owner 改变都记录 from、to、消息证据、交付版本、未决事项和下一动作。仅写角色名不算完成交接。

## Canonical blockers

| `BLOCKED_REASON` | Meaning |
|---|---|
| `none` | 当前没有 blocker |
| `missing_subject_project` | 架构决策归属未定 |
| `missing_target_project` | 已批准交接但目标研发项目未定 |
| `missing_openspec_explore` | 研究必需依赖不可用 |
| `missing_brainstorming` | 输入有实质歧义且澄清依赖不可用 |
| `critical_evidence_gaps` | Review 无法裁决的关键证据缺失 |
| `review_packet_unavailable` | approvable design/review 尚无绑定 current packet digest 的完整 readiness，或 human access/digest 检查失败 |
| `approved_artifact_unavailable` | 发布阶段无法从 refs 恢复匹配已批准 packet 的准确原始 bytes |

不得使用 `blocked` 作为 stage，也不得为同一含义临时创造新的 blocker 字符串。

`BLOCKED_REASON` 不等于 Review gate。路由或依赖预检失败时只设置 blocker，gate 保持 `none`；`BLOCKED` 仅是完成架构评审后允许出现的结论。

`review_packet_unavailable` 不得覆盖 `APPROVABLE_WITH_WARNINGS|APPROVABLE`，并保持 stage=`reviewing`。`approved_artifact_unavailable` 不得撤销已验证 readiness 或 human decision，并保持 stage=`publishing`。两者都必须记录 failed checks、Owner 和 deterministic closing condition。

升级前已持久化为 `waiting_human` 的记录仅在产生新 design/review version 或显式 refresh 后进入新 packet gate；否则保持历史 stage 和 evidence，不伪造 readiness。
