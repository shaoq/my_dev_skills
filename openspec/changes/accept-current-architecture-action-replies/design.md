## Context
Multica 最新位置回复会被保存为线程根 child，并可能带 current Agent mention。旧 Skill 把这些平台细节作为硬门禁，已将语义准确的 UNIDRAG-12 Action accept 判为 no-op。

## Goals / Non-Goals

**Goals:**

- 具名 current Action 可从同一 Issue 最新位置回复。
- Action ID、Owner、current version/digest、时间、revision 与 supersession 继续失败关闭。
- 只适配一个可验证的首尾 current Agent mention。
- portable core 不依赖 Multica。

**Non-Goals:**

- 不接受普通“OK/确认”、任意 prose、多 Action 或编辑评论。
- 不改变 token-only packet reply 兼容规则。
- 不修改 Multica 应用代码。
- 本地 symlink 只覆盖 Codex 使用面；Multica Agent 使用 Workspace Skill 快照，因此实施需要把同一已验证内容原 ID 就地同步并回读 digest，不创建 Skill 或 binding。

## Decisions

1. core 增加 `current_action_reference_v1`，以 work item + current unique Action ID + Owner + legal decision 绑定；version/digest 从 current request 继承。
2. adapter 对该 profile 记录但不强制 direct parent；candidate 必须同 Issue、创建于 request 后、revision 1 未编辑。
3. adapter 只剥离首端或尾端至多一个准确 current Architecture Agent canonical mention；规范化后必须精确匹配一个合法 Action response。
4. packet token-only 路径继续要求 descendant chain 或 explicit packet identity。
5. 有效回复先自动投影 `in_progress --no-start` 并回读，再处理决定；漂移时 no-op。

## Risks / Trade-offs

- [Action replay] → 要求唯一 current identity、version/digest、created-after-request 与 supersession。
- [mention 规范化过宽] → 仅一个准确 current Agent mention、仅首尾、其余内容精确匹配。
- [多个 current action] → 不按时间猜测，直接 fail closed。
