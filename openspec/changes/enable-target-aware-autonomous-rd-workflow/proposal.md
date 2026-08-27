## Why

当前研发自动化链路存在两个会重复打断或误判非 `main` 分支工作的缺口：`new-worktree-apply` 即使已有明确 Issue 授权仍强制等待即时人工确认，而 `verify-impl-consistency` 与 `check-changes-completed` 使用固定 `main..HEAD` 归因实现、测试和合规产出。对于以 `develop` 或其他集成分支为目标的 `1 Issue = 1 OpenSpec change = 1 worktree` 流程，这既阻碍自治执行，也会让 Review 前后的验证范围包含无关差异。

## What Changes

- 为 `new-worktree-apply` 增加显式、可审计的 Issue 授权自治模式；仅接受 Runtime 通过不可由用户或模型伪造的控制面元数据通道提供的 `issue-authorization/v1` envelope。通过身份、时效、scope、目标与风险门禁后，可跳过即时人工确认并在隔离 worktree 中进入 apply。
- 保留 `new-worktree-apply` 的默认交互式确认模式，以及冻结目标、artifact manifest、canonical identity、失败关闭和现场保留等现有不变量。
- 建立跨 skill 的显式目标基线契约：凡需把当前实现与目标分支比较的验证，都必须解析并冻结调用方明确提供的本地目标分支与当前 HEAD，证明目标 commit 是当前 commit 的祖先，并在整个调用中只使用这两个不可变 hash；不得固定或静默回退到 `main`。
- **BREAKING**：`verify-impl-consistency` 只有在调用方同时提供唯一 active change 名称和 `--base <target-branch>` 时才执行 OpenSpec 增量验证；无 change 名称时只执行项目级诊断，不再自动把多个 active changes 绑定到一个猜测基线。
- **BREAKING**：`check-changes-completed` 要求 `--target <target-branch>` 以及一个或多个重复的 `--change <active-change>`；仅扫描和回填显式选择的 changes。不同目标分支的 changes 必须分组调用，且每次调用的选择集完全显式。
- 缺失、重复、无效、非祖先或运行中漂移的目标基线必须明确报告，不能以 `main`、merge-base 或其他推断值代替；会写回任务状态的完成度检查在任何快照漂移下必须保持零写。
- `verify-impl-consistency` 使用同一冻结、已证明祖先关系的基线归因一个显式 OpenSpec change 的文档声明、实现、测试覆盖和断言，并在诊断报告中披露 change、branch、commit、比较范围和最终稳定性。
- `check-changes-completed` 只对显式 `--change` 集合使用同一冻结目标基线完成 D3 代码交付提交检查和 D5 配套产出合规检查，并在汇总报告中披露选择集与基线证据。
- 对所有其他非归档 skill 执行固定 `main` 审计；已经使用显式 `TARGET_BRANCH`、冻结 commit 或与比较基线无关的 skill 不作行为修改，只把审计结论纳入测试与交付证据。

## Capabilities

### New Capabilities

- `target-aware-verification`: 定义跨 skill 的显式目标分支参数、冻结 commit、比较范围、漂移处理、报告字段及禁止固定 `main` 的统一契约。

### Modified Capabilities

- `worktree-targeting`: 将 `new-worktree-apply` 的确认规则扩展为默认人工确认和严格 Issue 授权自治两种模式，同时保持 merge 与并行集成的既有确认边界。
- `doc-code-consistency`: OpenSpec change-level 文档声明验证使用显式冻结基线，而不是固定 `main..HEAD`。
- `test-code-consistency`: OpenSpec change-level 测试存在性、场景覆盖和断言归因使用同一显式冻结基线。
- `compliance-check`: `check-changes-completed` 的配套产出检查使用显式冻结目标基线，并与 D3 代码交付验证共享该基线。

## Impact

- 修改 `new-worktree-apply/SKILL.md` 的参数契约、`issue-authorization/v1` 控制面元数据验证、授权模式、Step 6–7、报告与 guardrails。
- 修改 `verify-impl-consistency/SKILL.md`，增加显式 change + `--base <target-branch>` 契约、祖先关系/快照稳定性门禁，替换固定 `git diff main..HEAD` 并扩展报告上下文。
- 修改 `check-changes-completed/SKILL.md`，增加 `--target <target-branch>` 与重复 `--change <active-change>`，替换 D3 的 `git log main..HEAD` 和 D5 的 `git diff main..HEAD`，并把所有回填写入限制在显式选择集内。
- 更新 `openspec/specs/worktree-targeting/`、`doc-code-consistency/`、`test-code-consistency/`、`compliance-check/`，并新增 `target-aware-verification` capability。
- 扩展 `tests/worktree-lifecycle-safety.sh`，并为两个验证 skill 增加参数、显式 change 分组、非 `main`/非祖先基线、双侧快照漂移、零写隔离和固定 `main` 回归扫描测试。
- 不修改用户目录下的 skill，不改变 `merge-worktree-return` 的人工确认，不引入自动 merge、自动回滚、强制 Git 清理或验证自动修复。
