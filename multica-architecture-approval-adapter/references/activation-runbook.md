# Multica adapter activation runbook

## Mandate boundary

Skill package/import/binding 不是方案 Review，也不使用 operational authorization。只有用户明确要求“实施并激活”或等价的新任务指令时，才能建立绑定准确既有 workspace、四个目标 Agent、core/adapter/Archify package identity、revision/digest 和 planned writes 的 activation mandate，并派生 `architecture_operation_manifest_v1`。本机 Runtime 可解析 Archify 不等于目标 workspace 已导入或绑定。

普通 Issue delivery mandate 不隐含 activation。activation mandate 也不授权创建 workspace、Agent、Team、Project、Issue、Skill fallback、Runtime 配置、CLI 安装/升级、replace-all binding、delete 或业务实现。

## Automatic activation procedure

1. 重验 reviewed local package aggregate 和用户指定的既有 workspace/Agent identities；目标不唯一或缺失时停止并说明需要新的任务指令。
2. 把 core/adapter/Archify import、additive binding 和 readback 作为 manifest 的有序操作。当前 revision 首次安装使用 conflict-safe fail：

   ```bash
   multica skill import --file <skill-package> --on-conflict fail --output json
   ```

3. same-name/different-digest 冲突时停止并报告；当前 profile 不自动 overwrite/delete/rename-around。需要替换必须由新的、精确命名现有 Skill ID 与 digest 的 activation mandate 承担。
4. 按 [Archify Agent bindings](archify-agent-bindings.md) 只对准确四个目标 Agent 执行 additive binding：Solution Architect 与 Product & Spec Engineer 使用 author/conditional-author；Architecture Reviewer 与 Solution Review Architect 使用 review-only。core/adapter 仍按既有职责绑定。

   ```bash
   multica agent skills add <existing-agent-id> <skill-id>
   ```

   已存在的 binding 在 readback 证明后复用；禁止 replace-all/set。
5. 最终逐 Agent 只读回读：

   ```bash
   multica agent skills list <existing-agent-id> --output json
   ```

   记录 workspace/Agent、Skill IDs/package aggregates、Archify full revision/archive digest、完整 author/review-only 指令和 Multica/CLI identity。同时确认 Architecture Lead、Architecture Analyst、R&D Lead、Development Engineer、Code Review Engineer、QA Engineer、Integration & Archive Engineer、Workflow Watchdog 未被隐式绑定。

6. compatibility pair、导入和 bindings 只对新 attempt 生效；旧 attempt 继续 frozen reader。任一 Agent 部分绑定失败时保留已完成对象，报告精确差异，不把 workspace 标为 active。

## Failure and closing conditions

- 缺失/歧义 workspace 或 Agent：`activation=not_run`，请求新的任务指令。
- same-name conflict：`activation=not_run`，报告可选策略与后果；不请求复制 token。
- partial import/binding：保留对象，冻结 retained set；只有 current activation mandate 仍覆盖且 retry 未耗尽时自动 new manifest，否则停止。
- 最终 readback 缺 ID：`activation=not_run`，不创建或替换资源。
- import/binding 成功不等于 production acceptance；sandbox 需明确任务指令建立自己的 mandate。
