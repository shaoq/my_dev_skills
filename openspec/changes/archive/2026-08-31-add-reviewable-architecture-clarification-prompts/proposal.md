## Why

`UNIDRAG-12` 的真实验证表明，工作流在 `critical_evidence_gaps` 下只列出待确认问题和“等待确认”，没有同时给出候选建议、理由、风险与可编辑回复方式，导致人类无法在 Issue（尤其移动端）高效审核。当前 packet 阶段虽已要求 recommendation，但该约束没有覆盖设计阶段的澄清门禁。

## What Changes

- 要求所有会阻塞架构流程、并请求人类选择或确认的评论包含一个可审核的 clarification proposal：逐项给出候选建议或明确的 `no_recommendation`、证据/理由、风险与待补证据、Owner，以及接受/修改/拒绝的回复方式。
- 明确候选建议、默认值或人类对候选值的接受不能替代测量证据、责任 Owner 决定、准确版本批准或其他既有门禁。
- 更新 `ARCH-CONTROL` 和设计阶段指导，使 `critical_evidence_gaps` 的下一动作可在 Issue 中独立理解与编辑，而不是只说“等待确认”。
- 增加覆盖该真实失败模式的行为 fixture、契约检查和运行时验证证据。
- 不修改 Multica 核心、平台 adapter、approval packet 决策绑定或业务项目实现。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `architecture-design-artifacts`：为阻塞性人类澄清请求增加可审核建议结构和必填内容。
- `architecture-design-governance`：保持候选建议、澄清回复、事实证据与正式人工批准之间的语义边界。

## Impact

影响 `architecture-design-workflow` 的主说明、solution-design reference、`ARCH-CONTROL` 模板、行为 fixtures/runner evidence，以及上述两项 OpenSpec 主规格；不改变 canonical stage、Review conclusion、packet schema、Multica CLI/API 或 adapter 合同。
