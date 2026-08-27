## 1. 建立目标基线与回归测试

- [x] 1.1 新增 `tests/target-aware-verification-safety.sh`，在临时 Git 仓库中创建 `develop`、feature 和目标侧独有 commits，验证只有 `BASE_HEAD` 为 `CURRENT_HEAD` 祖先时才归因 `<BASE_HEAD>..<CURRENT_HEAD>`。
- [x] 1.2 为 `verify-impl-consistency` 覆盖显式 change + `--base`、纯项目级模式、缺值、重复、未知参数、不存在的本地分支、非祖先基线、target ref 漂移和 current HEAD 漂移。
- [x] 1.3 为 `check-changes-completed` 覆盖 `--target` + 重复 `--change`、无/重复/无效 change、D3/D5 同一冻结 commits、空范围、非祖先基线、漂移零写，以及两个目标组之间的扫描和回填隔离。
- [x] 1.4 增加非归档 source `SKILL.md` 固定基线扫描，阻止可执行的 `main..HEAD`/`refs/heads/main` 比较，同时允许 conventional target fallback 描述和禁止性反例文本。

## 2. 将 Worktree Apply 简化为默认非交互执行

- [x] 2.1 更新 `new-worktree-apply/SKILL.md` frontmatter、argument hint、allowed tools、示例和严格参数解析，删除 `AskUserQuestion` 与 `--authorized-by-issue`，要求每次调用显式提供 `--target <target-branch>`，并对旧授权参数给出零写迁移提示。
- [x] 2.2 定义并验证 Runtime `explicit-skill-invocation/v1` trusted dispatch provenance，绑定 `runtime_id`、当前 invocation 的唯一 `dispatch_id`、`user-explicit-skill-command`、精确 skill name 和 raw arguments；Claude `/new-worktree-apply`、Codex `$new-worktree-apply` 或等价 Runtime dispatcher 才可进入默认执行。
- [x] 2.3 对模型自动选择、自然语言推断、嵌套 `Skill(...)` 转调、用户/仓库/环境伪造 metadata、dispatch 重放、skill/参数不匹配和来源 unknown 在任何写入前失败关闭，并在最终复检要求同一 dispatch id 与 provenance digest。
- [x] 2.4 删除 `issue-authorization/v1`、authorization/issuer/Issue/Team 标识、时效、防重放、风险 envelope、交互/自治模式选择及相关报告字段；显式 dispatch provenance 仅证明调用来源，不承载任务平台授权或高风险权限。
- [x] 2.5 删除创建前人工确认步骤；将已验证的用户显式调用视为对 canonical source worktree 创建、OpenSpec apply、来源验证和提交的有限授权，完整只读预检通过后直接进入最终写前复检。
- [x] 2.6 增加可选 `--dry-run`，要求相同的可信显式 dispatch，执行与默认模式相同的参数、目标、worktree topology、artifact manifest 和计划写入预检，但在任何情况下都不得创建 branch/worktree、调用 apply、stage 或 commit。
- [x] 2.7 保持目标 worktree clean、冻结 `TARGET_HEAD`、canonical branch/path、manifest blob identity、显式 commit-hash start point、创建后 CWD/identity 校验、失败现场保留和来源提交不变量。
- [x] 2.8 最终写前复检发现 provenance、参数、target ref/HEAD、worktree mapping、cleanliness、artifact manifest 或计划写入漂移时直接零写停止；不得刷新快照、换目标、自动重试或转为交互确认。
- [x] 2.9 明确默认执行不授权 merge、发布、部署、生产写入、不可逆迁移、真实凭据使用或无关 Git 清理；proposal/tasks 要求这些行为时在执行前阻塞并交由独立流程授权。
- [x] 2.10 扩展 `tests/worktree-lifecycle-safety.sh`，验证 Claude/Codex trusted dispatch 可默认执行，模型自动/嵌套/伪造/unknown provenance 零写失败，`--dry-run` 严格零写、旧授权参数与缺失 target 被拒绝、preflight 漂移失败关闭，以及 merge/并行 skill 仍需确认。

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

- [x] 5.1 更新 `README.md` 和调用文档，展示 Claude `/skill`、Codex `$skill` 的可信显式调用、来源不可证明时的零写失败、默认非交互 worktree apply、`--dry-run`、旧授权参数迁移、`verify-impl-consistency <change> --base`、`check-changes-completed --target --change ...`、多目标分组和非祖先失败示例。
- [x] 5.2 核对并同步 `openspec/specs/worktree-targeting` 的完整 MODIFIED requirement blocks（含必填 target/OpenSpec root/preflight terminology），以及 `target-aware-verification`、`doc-code-consistency`、`test-code-consistency` 和 `compliance-check` 与最终 skill 行为。
- [ ] 5.3 运行 `bash tests/worktree-lifecycle-safety.sh` 和 `bash tests/target-aware-verification-safety.sh`，确认可信显式 dispatch、隐式调用零写、默认执行、dry-run 零写、确认边界、选择集隔离与非 `main`/非祖先基线场景全部通过。
- [ ] 5.4 运行 `python3 -m unittest tests/test_setup_skills_env.py`，确认 skill 安装、frontmatter 和权限声明没有回归。
- [ ] 5.5 运行 `openspec validate enable-target-aware-autonomous-rd-workflow --type change --strict`、固定基线全仓扫描和 `git diff --check`，记录最终验证证据。
