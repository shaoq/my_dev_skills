## 1. 基线与安全合同

- [x] 1.1 在编辑前对 `new-worktree-apply/SKILL.md` 及可解析的相关符号/流程执行 GitNexus upstream impact，记录直接依赖、受影响流程和风险等级；HIGH/CRITICAL 时先向用户告警。
- [x] 1.2 用当前技能对一个已提交的嵌套 OpenSpec proposal 执行确认前只读流程，保存其在固定根路径检查处失败且零 Git 写入的 RED 基线。
- [x] 1.3 将 delta spec 的参数语法、三类路径、物理包含、确认快照、manifest 和 apply CWD 整理为实施检查表，确认不改变规范来源 branch/worktree 和冻结 hash 创建合同。

## 2. 参数解析与项目根验证

- [x] 2.1 更新 `new-worktree-apply/SKILL.md` 的 frontmatter、argument hint、示例和 Step 1 参数解析，支持至多一个 `--openspec-root <repo-relative-directory>`，允许其与 `--target` 任意排序，并保留省略值 `.` 的兼容行为。
- [x] 2.2 实现 `OPENSPEC_ROOT_REL` 的词法门禁，拒绝重复/缺值/未知参数、绝对或 home 路径、反斜杠、空白/控制字符、空/`.`/`..` 路径段及非规范斜杠。
- [x] 2.3 定义并验证 `INVOCATION_PROJECT_DIR`、`SOURCE_PROJECT_DIR` 和无 `./` 前缀的仓库相对 `CHANGE_PREFIX`；对物理路径、`openspec/` 和 proposal 目录执行 worktree/project 包含检查，任一错误或符号链接逃逸失败关闭。
- [x] 2.4 明确禁止自动递归发现、唯一候选推断、根目录回退、环境变量覆盖或 proposal 近似匹配，并让所有错误报告包含用户选择的精确项目路径。

## 3. 快照、创建与 Apply 上下文

- [x] 3.1 更新 Step 4～5，使 OpenSpec status 从 `INVOCATION_PROJECT_DIR` 运行，manifest 则以完整 `CHANGE_PREFIX` 从 Git 仓库根独立枚举当前路径与 `TARGET_HEAD` tree，并逐 blob 复验。
- [x] 3.2 更新 Step 6 摘要，显示参数是否显式、规范化根、当前/来源项目目录、完整 change prefix、manifest 路径与 digest，同时保留全部现有目标与来源风险说明。
- [x] 3.3 更新 Step 7，从参数开始重跑并逐字复检项目根、物理包含、OpenSpec status、manifest 和现有冻结目标信息；任一漂移使确认失效。
- [x] 3.4 保持 Step 8 的唯一 commit-hash worktree 创建命令和 Git 身份检查不变；创建后在 Step 9 验证 `SOURCE_PROJECT_DIR`、OpenSpec status 和仓库相对 manifest blobs。
- [x] 3.5 更新 Step 10～11，只从已验证的 `SOURCE_PROJECT_DIR` 调用 `openspec-apply-change` 和读取 tasks，从来源 worktree 根暂存，并用 `<CHANGE_PREFIX>/tasks.md` 强制纳入回填。
- [x] 3.6 更新失败与成功输出；创建后项目上下文失败时保留规范来源 branch/worktree，不自动清理、换根、重建或回退。

## 4. 文档与场景验证

- [x] 4.1 更新 `README.md` 的命令签名、参数表和示例，说明 `--openspec-root twin-rag` 表示 `twin-rag/openspec/changes/<proposal>`，省略值等价于 `.`。
- [x] 4.2 在 `mktemp -d` 隔离仓库验证省略参数与显式 `.` 的路径、manifest 和 OpenSpec CWD 完全一致，且不回归现有 `--target` 与旧 `--branch` 拒绝行为。
- [x] 4.3 在隔离仓库验证嵌套项目可完成 Step 1～5 并停在 Step 6 等待确认；确认前不创建 branch/worktree、不调用 apply。
- [x] 4.4 验证重复/缺值、绝对路径、home/反斜杠、空白、`.`/`..`/空路径段、未知目录、proposal 缺失、符号链接越界和确认后路径/manifest 漂移全部失败关闭。
- [x] 4.5 验证创建后的来源项目目录缺失、越界、status 不完整或 blob 漂移均阻止 apply 并保留来源现场；成功路径则从嵌套项目目录调用 apply 并正确定位 tasks。

## 5. 交付验证

- [x] 5.1 运行 skill-creator `quick_validate.py`；仅当当前与 `HEAD` 基线都只报告既有 `argument-hint`、`disable-model-invocation` unknown-key 诊断时记录已知兼容边界，并独立校验真实 YAML/runtime 字段；OpenSpec strict、Markdown/diff 及适用隔离场景必须无错误。
- [x] 5.2 用独立代理分别前向测试根目录、嵌套项目和非法路径调用，确认其能区分 Git 仓库根、OpenSpec 项目根与来源 worktree 根，且不会自动猜测或提前写入。
- [x] 5.3 提交前运行 GitNexus `detect_changes()`，核对仅影响预期 skill、README、OpenSpec artifacts/规范流程，并记录风险等级和受影响执行流。
