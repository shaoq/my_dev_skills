## 1. 建立目标基线与回归测试

- [x] 1.1 新增 `tests/target-aware-verification-safety.sh`，在临时 Git 仓库中创建 `develop`、feature 和目标侧独有 commits，验证只有 `BASE_HEAD` 为 `CURRENT_HEAD` 祖先时才归因 `<BASE_HEAD>..<CURRENT_HEAD>`。
- [x] 1.2 为 `verify-impl-consistency` 覆盖显式 change + `--base`、纯项目级模式、缺值、重复、未知参数、不存在的本地分支、非祖先基线、target ref 漂移和 current HEAD 漂移。
- [x] 1.3 为 `check-changes-completed` 覆盖 `--target` + 重复 `--change`、无/重复/无效 change、D3/D5 同一冻结 commits、空范围、非祖先基线、漂移零写，以及两个目标组之间的扫描和回填隔离。
- [x] 1.4 增加非归档 source `SKILL.md` 固定基线扫描，阻止可执行的 `main..HEAD`/`refs/heads/main` 比较，同时允许 conventional target fallback 描述和禁止性反例文本。

## 2. 实现 Issue 授权的自治 Worktree Apply

- [x] 2.1 更新 `new-worktree-apply/SKILL.md` frontmatter、argument hint、示例和严格参数解析，增加唯一的 `--authorized-by-issue <issue-id>`，并要求自治模式显式提供 `--target`。
- [x] 2.2 定义 Runtime 控制面 `issue-authorization/v1` 输入契约，明确只有不可由 user content、仓库文件、环境变量或模型推断填充的可信元数据通道才可提供 envelope；无该能力的 Runtime 只保留交互模式。
- [x] 2.3 验证 schema、authorization/issuer/Issue/Team 标识、`ready|in_progress` 状态、RFC3339 UTC 且不超过 30 分钟的有效窗口、跨 invocation 防重放、同 invocation envelope digest 复检、`isolated-worktree-apply` scope、仓库/OpenSpec root/change/target、standard 风险和空外部副作用列表，任何未知或冲突均零写失败。
- [x] 2.4 将 Step 6 实现为默认交互确认与自治授权快照双路径，保证两种模式输出相同的 target、canonical identity、artifact manifest、planned writes 和风险证据；自治审计输出不得泄露 token 或签名材料。
- [x] 2.5 更新 Step 7，使交互模式漂移重新确认、自治模式漂移直接失败关闭，并禁止自动更新授权、模式回退、换目标或使用新快照继续。
- [x] 2.6 保持 Step 1–5 与 Step 8–11 的冻结 hash、目标 worktree 不变、canonical branch/path、manifest blob、失败现场保留和来源提交不变量，并在成功/失败报告中记录授权来源、时效和边界。
- [x] 2.7 扩展 `tests/worktree-lifecycle-safety.sh`，验证默认模式仍需确认、可信授权可自治执行，以及 user JSON 伪造、未知 schema、issuer 未认证、过期/重放、Issue/Team/scope/目标不匹配、高风险和快照漂移均在首次写入前停止。

## 3. 实现显式基线的一致性验证

- [x] 3.1 更新 `verify-impl-consistency/SKILL.md` frontmatter、argument hint 和参数解析，仅支持纯项目级无参数模式或 `<change-name> --base <target-branch>`，拒绝孤立 `--base`、自动 active-change 选择及所有歧义输入。
- [x] 3.2 将显式本地 `refs/heads/<base>` 与当前 `HEAD` 分别冻结为 `BASE_HEAD`、`CURRENT_HEAD`，要求 `git merge-base --is-ancestor <BASE_HEAD> <CURRENT_HEAD>` 成功，并以两个 commit hash 替换 OpenSpec incremental 中固定的 `git diff main..HEAD`。
- [x] 3.3 让所选 change 的文档、实现、测试覆盖和 spec-grounded assertion 归因共用同一冻结范围，同时保持项目级 D1/D2/D3 全仓扫描不被 `--base` 裁剪。
- [x] 3.4 在报告中增加显式 change、基线参数来源、target branch、`BASE_HEAD`、`CURRENT_HEAD`、比较范围及 target/current 最终稳定性；非祖先时将增量维度标记为未执行，漂移时标记冻结结果为 stale evidence。
- [x] 3.5 保持 `verify-impl-consistency` 纯诊断、只读、无自动修复和无最终 pass/fail verdict，并验证未选择的 active changes 不参与增量诊断。

## 4. 实现显式选择集的完成度与合规验证

- [x] 4.1 更新 `check-changes-completed/SKILL.md` frontmatter、description、argument hint 和参数解析，要求唯一 `--target <target-branch>` 与一个或多个唯一 `--change <active-change>`，拒绝缺失、重复、未知或 archive-only change。
- [x] 4.2 在扫描前构建排序后的 `SELECTED_CHANGES`，证明每项精确匹配 active change，并把五维检查、blocking reasons、可存档结论和任务回填严格限制在该集合；未选择 change 不读取 change-level artifacts 且不修改。
- [x] 4.3 冻结 `BASE_HEAD` 与 `CURRENT_HEAD` 并验证祖先关系；失败时阻塞全部所选 changes 且禁止任何回填、stage 或 commit。
- [x] 4.4 将 D3 提交证据改为 `git log <BASE_HEAD>..<CURRENT_HEAD> -- <expected-files>`，不得使用 branch name 或字面 `HEAD`。
- [x] 4.5 将 D5 配套产出范围改为 `git diff <BASE_HEAD>..<CURRENT_HEAD> --name-only`，确保 D3/D5 不重新解析 ref 且使用同一对快照。
- [x] 4.6 在完成度汇总与 blocking reasons 中显示 `SELECTED_CHANGES`、target branch、冻结 commits、比较范围及 target/current 漂移；不同目标分支的 changes 要求调用方分组运行。
- [x] 4.7 在任何参数、选择集、祖先关系或最终稳定性验证失败时保持零回填、零 stage、零 commit；漂移时可显示冻结诊断，但可存档状态必须为 unknown/blocked。

## 5. 文档、规范与最终验证

- [x] 5.1 更新 `README.md` 或现有调用文档，展示默认/Issue 授权 worktree 模式、`verify-impl-consistency <change> --base`、`check-changes-completed --target --change ...`、多目标分组和非祖先失败示例。
- [x] 5.2 核对 `openspec/specs/worktree-targeting`、`target-aware-verification`、`doc-code-consistency`、`test-code-consistency` 和 `compliance-check` 与最终 skill 行为逐项一致。
- [x] 5.3 运行 `bash tests/worktree-lifecycle-safety.sh` 和新增的 target-aware verification test，确认授权安全、选择集隔离与非 `main`/非祖先基线场景全部通过。
- [x] 5.4 运行 `python3 -m unittest tests/test_setup_skills_env.py`，确认 skill 安装、frontmatter 和权限声明没有回归。
- [x] 5.5 运行 `openspec validate enable-target-aware-autonomous-rd-workflow --type change --strict`、固定基线全仓扫描和 `git diff --check`，记录最终验证证据。
