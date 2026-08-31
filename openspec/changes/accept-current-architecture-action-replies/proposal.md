## Why
UNIDRAG-12 证明当前 Skill 会拒绝准确 Owner 在 Issue 最新位置提交的明确 current Action 决定，因为 Multica 把评论挂到线程根并自动附加 Agent mention，而 Adapter 仍要求 direct parent 和 raw content 逐字匹配。需要让 Skill 遵循人的正常回复路径，同时保留 Action identity 与失败关闭保护。

## What Changes

- portable core 定义 `current_action_reference_v1`：准确 Owner、同一 work item、唯一 current Action ID 与合法决定值构成主要绑定，平台 parent 不进入 required fields。
- Multica adapter 将 parent chain 降为审计证据，并仅规范化首尾一个准确 current Architecture Agent canonical mention。
- 保留错误/过期/重复 Action、错误 actor、编辑、错误/多个 mention、额外 prose 与多决定的 no-op 行为。
- 有效 latest-position 回复自动投影 `in_progress` 并处理决定；无效回复保持 Review gate，不请求 operational authorization。

## Capabilities

### New Capabilities

<!-- none -->

### Modified Capabilities

- `architecture-workflow-operation-automation`: 实施具名 current Action 的位置无关绑定和 Multica mention 规范化。

## Impact

- 上游：`/Users/jie.hua/Documents/Developments/Projects/litata/uni-architecture/openspec/changes/accept-current-architecture-action-replies`。
- 修改 `architecture-design-workflow`、`multica-architecture-approval-adapter` 与现有测试。
- 不修改 Multica 代码/API/数据库，不创建或重绑平台资源。
