# Archify Agent bindings

## Frozen dependency

- Skill：`archify` v2.17（package `2.17.0-dev.1`）
- Source repository：`/Users/jie.hua/Documents/Developments/Projects/github/archify`
- Repository revision：`bb71ccdd64cd3a74ba7cbd25bbacc7382da34410`
- Import archive SHA-256：`ed178d2ddd8861db1b8e867f32be7764bdec221d44568c37b6ae157c5e7f111c`
- Supported diagrams：Architecture、Workflow、Sequence、Data Flow、Lifecycle
- Required command chain：`validate` → `deliver` → `visual-check`; review-only 可使用 `inspect`、`validate`、`check`、读取 receipt，必要时 compare architecture。

本机 Runtime 可解析不等于目标 Multica workspace 已导入或绑定。activation 必须显式选择既有 workspace，冻结 Skill ID/version/revision/archive digest，使用 conflict-fail import 与 additive binding，并逐 Agent 回读完整指令；任何冲突或部分失败都停止，不执行 replace-all。

## Role-minimized deployment profile

| Team | Agent | Binding profile | Allowed | Forbidden |
|---|---|---|---|---|
| Architecture Team | Solution Architect | author | 选择图型、创作 Typed JSON、validate、deliver、visual-check、修复 | 代替 Reviewer 通过语义门禁 |
| Architecture Team | Architecture Reviewer | review-only | inspect、validate、check、读取 current receipt、必要时 compare architecture | 修改源、重新 deliver、覆盖作者 artifact |
| R&D Team | Product & Spec Engineer | conditional author | 优先复用批准图；仅为已授权 OpenSpec 补一张 scope-local 实现图 | 重画或改变批准架构 |
| R&D Team | Solution Review Architect | review-only | 对 proposal/design/spec/tasks、代码证据和批准 Design 做一致性核验 | 修改图源或重新 deliver |

Architecture Lead、Architecture Analyst、R&D Lead、Development Engineer、Code Review Engineer、QA Engineer、Integration & Archive Engineer 和 Workflow Watchdog 默认不绑定。Lead 只检查 manifest/receipt，Analyst 提供证据，其他角色消费结论。内部 handoff 不生成展示图。

## Activation and readback

1. 只在明确 activation mandate 下执行；普通 Issue delivery 不授权导入或绑定。
2. import 使用 `conflict-fail`；发现同名不同 digest 时停止并报告，不覆盖。
3. binding 使用 additive，逐一绑定四个目标 Agent；任何一项失败都保留已完成对象并报告部分状态，不隐式补绑其他 Agent。
4. 逐 Agent 回读 Skill ID、revision、archive digest、binding profile 和完整 author/review-only 指令。
5. 回读非目标 Agent，确认没有新增绑定；只对新 attempt 生效。
