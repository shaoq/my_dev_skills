## Why

当前 actionable blocker 虽然给出多种可复制回复，却没有明确告诉普通用户“现在最建议回复哪一条、为什么”。UNIDRAG-12 还证明：用户用“我负责提供”等清晰自然语言表达意图时，严格消费契约会正确拒绝该回复，但没有立即给出唯一可执行的纠错，导致 Issue 长时间保持 blocked。

## What Changes

- 让 portable `architecture-design-workflow` 为 blocker 产出平台无关的推荐意图、普通语言理由、置信度、适用边界和有序备选；证据不足时默认建议继续有界调查，而不是猜测责任人。
- 让 optional `multica-architecture-approval-adapter` 把推荐绑定 current Action ID，并在评论前部渲染完整可复制回复、理由和回复后行为。
- 对准确 Owner、current request、单一明确意图但格式不合规的回复，最多自动发布一次不改变状态的友好纠错；canonical reply 的严格消费规则保持不变。
- 增加 core/adapter 行为 fixtures、首屏预算、幂等和失败关闭回归。
- 不修改 Multica 核心代码，不降低 Review、approval、风险接受或实现授权门禁。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `architecture-workflow-operation-automation`: actionable blocker 从平级回复列表升级为基于证据的决策就绪推荐，并定义不构成批准的 portable recommendation contract。
- `multica-architecture-adapter-activation`: 增加 Multica 首屏推荐投影与严格、一次性、状态不变的无效回复纠错。

## Impact

- Portable core：`architecture-design-workflow` 的 blocker reference、template、Skill 入口和 fixtures。
- Optional adapter：`multica-architecture-approval-adapter` 的 projection/reply reference、comment template、Skill 入口和 fixtures。
- 验证：本仓库 OpenSpec、Python 契约测试与 Skill package 校验。
- 映射：与 `uni-architecture` 同名 change 保持需求、边界与验收证据一致；Multica runtime/core、Team、Agent、Issue 创建能力均不在实现范围内。
