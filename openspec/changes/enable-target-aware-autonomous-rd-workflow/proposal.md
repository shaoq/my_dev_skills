## Why

当前研发自动化链路存在两个会重复打断或误判非 `main` 分支工作的缺口：`new-worktree-apply` 已经是一个名称和作用域都明确的实施命令，却仍在完成只读预检后要求第二次人工确认；`verify-impl-consistency` 与 `check-changes-completed` 则曾使用固定 `main..HEAD` 归因实现、测试和合规产出。对于面向 `develop` 或其他集成分支的 OpenSpec 流程，前者增加了没有新增安全价值的交互门禁，后者会让验证范围包含无关差异。

当 Runtime 通过原生策略禁止模型隐式激活，仅允许用户显式调用 Claude `/new-worktree-apply ...`、Codex `$new-worktree-apply ...` 或等价受支持命令时，该激活即授权在规范化隔离 worktree 中创建来源分支、执行 apply 并提交来源变更。安全性由 Runtime 原生显式调用门禁、确定性参数、只读预检、不可变预检基线和独立写前复检共同提供，而不是依赖 Issue、Team、任务平台 envelope 或重复确认。

## What Changes

- **BREAKING**：`new-worktree-apply` 改为默认非交互执行。Runtime 证明用户显式调用、参数合法且只读预检通过后，skill 直接完成最终漂移复检、创建 canonical worktree、执行 apply 和提交来源变更，不再请求人工确认。
- **BREAKING**：删除 `--authorized-by-issue <issue-id>`、`issue-authorization/v1` Runtime envelope、交互/自治双模式以及相关 Issue、Team、issuer、时效和防重放协议。检测到旧参数时零写停止，并提示使用不带授权参数的新调用形式。
- 增加 Runtime 原生显式调用门禁：Claude 使用 `disable-model-invocation: true`，Codex 使用 `agents/openai.yaml` 的 `policy.allow_implicit_invocation: false`；其他 Runtime 必须提供等价的控制面策略。模型自动选择、自然语言推断、嵌套 skill 转调或用户/仓库/环境内容均不能替代 Runtime 激活断言。
- **BREAKING**：`new-worktree-apply` 要求显式提供 `--target <target-branch>`；不得为该 skill 从主工作树、`origin/HEAD` 或 `main/master/trunk` 推断目标。
- 为 `new-worktree-apply` 增加可选 `--dry-run`。该模式执行完整只读预检并输出计划快照，但永不创建 branch/worktree、调用 apply、stage 或 commit。
- 保留冻结目标、artifact manifest、canonical identity、目标 worktree clean、创建父目录物理包含、最终漂移复检、失败关闭和现场保留等现有安全不变量。默认执行只创建一次不可变预检基线，并以独立复检快照逐字段比较；首次写入前发现任何漂移时直接停止，不自动刷新快照、换目标或降级为交互确认。
- `new-worktree-apply` 的可信显式调用授权范围只覆盖 canonical source worktree 创建、OpenSpec apply、来源测试与提交；不覆盖 merge、发布、部署或无关 Git 对象清理。
- `merge-worktree-return` 与 `parall-new-worktree-apply` 继续保留各自的显式人工确认，不因单 worktree apply 的默认非交互行为而放宽。
- 建立跨 skill 的显式目标基线契约：凡需把当前实现与目标分支比较的验证，都必须解析并冻结调用方明确提供的本地目标分支与当前 HEAD，证明目标 commit 是当前 commit 的祖先，并在整个调用中只使用这两个不可变 hash；不得固定或静默回退到 `main`。
- `verify-impl-consistency` 只有在调用方同时提供唯一 active change 名称和 `--base <target-branch>` 时才执行 OpenSpec 增量验证；无 change 名称时只执行项目级诊断。
- `check-changes-completed` 要求 `--target <target-branch>` 以及一个或多个重复的 `--change <active-change>`；仅扫描和回填显式选择的 changes，不同目标分支必须分组调用。
- 缺失、重复、无效、非祖先或运行中漂移的目标基线必须明确报告；会写回任务状态的完成度检查在任何快照漂移下必须保持零写。
- 对所有其他非归档 skill 执行固定 `main` 审计；已经使用显式目标、冻结 commit 或与比较基线无关的 skill 不作行为修改，只把审计结论纳入测试与交付证据。

## Capabilities

### New Capabilities

- `target-aware-verification`: 定义跨 skill 的显式目标分支参数、冻结 commit、比较范围、漂移处理、报告字段及禁止固定 `main` 的统一契约。

### Modified Capabilities

- `worktree-targeting`: 将 `new-worktree-apply` 改为 Runtime 可证明的用户显式调用即授权、默认非交互且支持只读 `--dry-run`，同时保持 merge 与并行集成的人工确认边界。
- `doc-code-consistency`: OpenSpec change-level 文档声明验证使用显式冻结基线，而不是固定 `main..HEAD`。
- `test-code-consistency`: OpenSpec change-level 测试存在性、场景覆盖和断言归因使用同一显式冻结基线。
- `compliance-check`: `check-changes-completed` 的配套产出检查使用显式冻结目标基线，并与 D3 代码交付验证共享该基线。

## Impact

- 修改 `new-worktree-apply/SKILL.md` 的参数契约、Runtime 原生显式调用门禁、默认执行语义、dry-run、不可变写前复检、父目录物理包含、报告与 guardrails；增加 Codex `agents/openai.yaml`，删除 Issue/Team/task-platform 授权协议和人工确认路径。
- 修改 `verify-impl-consistency/SKILL.md`，维持显式 change + `--base <target-branch>`、祖先关系/快照稳定性门禁和冻结比较范围。
- 修改 `check-changes-completed/SKILL.md`，维持 `--target <target-branch>`、显式 `--change` 选择集、冻结 D3/D5 范围和零写漂移门禁。
- 更新 `openspec/specs/worktree-targeting/`、`doc-code-consistency/`、`test-code-consistency/`、`compliance-check/` 与 `target-aware-verification` capability。
- 扩展 `tests/worktree-lifecycle-safety.sh`，解析验证 Claude/Codex 原生门禁，覆盖模型自动或嵌套调用拒绝、默认直接执行、`--dry-run` 零写、旧授权参数拒绝、缺失显式 target、双侧快照漂移、父目录符号链接逃逸和确认边界隔离。
- 不修改用户目录下的 skill，不改变 `merge-worktree-return` 或并行集成的人工确认，不引入自动 merge、自动回滚、强制 Git 清理或验证自动修复。
