# Multica adapter activation runbook

## Mandate boundary

Skill package/import/binding 不是方案 Review，也不使用 operational authorization。只有用户明确要求“实施并激活”或等价的新任务指令时，才能建立绑定准确既有 workspace、Architecture Agent、core/adapter package identity 和 planned writes 的 activation mandate，并派生 `architecture_operation_manifest_v1`。

普通 Issue delivery mandate 不隐含 activation。activation mandate 也不授权创建 workspace、Agent、Team、Project、Issue、Skill fallback、Runtime 配置、CLI 安装/升级、replace-all binding、delete 或业务实现。

## Automatic activation procedure

1. 重验 reviewed local package aggregate 和用户指定的既有 workspace/Agent identities；目标不唯一或缺失时停止并说明需要新的任务指令。
2. 把 import/additive binding/readback 作为 manifest 的有序操作。首次安装或未声明 replacement 时使用 conflict-safe fail：

   ```bash
   multica skill import --file <skill-package> --on-conflict fail --output json
   ```

3. 如果 activation mandate 明确要求“把这两个新版 Skill 激活到现有 Agent”，且 preflight 已唯一重读同名 existing Skill ID、当前绑定、new package identity/digest 和 `overwrite` 的平台能力，则把该 exact replacement 作为 manifest 的既定 operation，使用 `--on-conflict overwrite` 自动更新；不拆分新的 conflict 授权。名称、workspace、existing ID、binding 或 package 任一不匹配时停止，保留 observed conflict 并要求新的任务指令；禁止 delete、rename-around 或替换其他 Skill。
4. 只对准确既有 Architecture Agent 执行 additive binding：

   ```bash
   multica agent skills add <existing-agent-id> <core-skill-id>
   multica agent skills add <existing-agent-id> <adapter-skill-id>
   ```

   已存在的 binding 在 readback 证明后复用；禁止 replace-all/set。
5. 最终只读：

   ```bash
   multica agent skills list <existing-agent-id> --output json
   ```

   记录 workspace/Agent、两个 Skill IDs/package aggregates、adapter repository revision 和 Multica/CLI identity。

## Failure and closing conditions

- 缺失/歧义 workspace 或 Agent：`activation=not_run`，请求新的任务指令。
- same-name conflict：`activation=not_run`，报告可选策略与后果；不请求复制 token。
- partial import/binding：保留对象，冻结 retained set；只有 current activation mandate 仍覆盖且 retry 未耗尽时自动 new manifest，否则停止。
- 最终 readback 缺 ID：`activation=not_run`，不创建或替换资源。
- import/binding 成功不等于 production acceptance；sandbox 需明确任务指令建立自己的 mandate。
