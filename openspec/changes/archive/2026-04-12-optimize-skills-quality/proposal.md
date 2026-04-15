## Why

根目录下 5 个 skill 经全面 review 后发现 7 个问题：Dependencies 注入方式侵入 openspec artifact、Backfill 逻辑三处重复、Agent 引用外部 skill 文件的方式脆弱、allowed-tools 不匹配实际使用、部分重量级 skill 缺少 disable-model-invocation、结束引导不完整、settings.local.json 含无效权限条目。需要一次性修复以提升 skill 体系的健壮性和可维护性。

## What Changes

- **Dependencies 迁移**: 将 `parall-new-proposal` 注入到 `proposal.md` 的 `## Dependencies` 段迁移为独立的 `dependencies.yaml` 文件，消除对 openspec artifact 的后修改
- **Backfill 规范化**: 统一 3 个 skill 中的 task backfill 规则定义，将 `parall-new-worktree-apply` 的 Agent prompt 改为内嵌四规则而非读取外部 skill 文件
- **Agent prompt 自包含**: 重写 `parall-new-worktree-apply` 的 Agent prompt，不再依赖读取 `new-worktree-apply/SKILL.md` 的步骤编号
- **allowed-tools 修复**: 补全 `new-worktree-apply`、`merge-worktree-return`、`check-changes-completed` 中缺失的 bash 命令权限
- **disable-model-invocation 补全**: 为 `parall-new-proposal` 和 `parall-new-worktree-apply` 添加此标志，防止模型自动触发重操作
- **结束引导增强**: 为 `merge-worktree-return`、`parall-new-worktree-apply`、`check-changes-completed` 增加下一步操作提示
- **settings.local.json 清理**: 删除无效 shell 语法片段权限条目，补充常用 git 子命令权限

## Capabilities

### New Capabilities
- `dependencies-yaml-migration`: 将 Dependencies 声明从 proposal.md markdown 段迁移到独立 YAML 文件，涉及 3 个 skill 的读写逻辑变更
- `backfill-consolidation`: 统一 backfill 四规则定义，重写 Agent prompt 为自包含形式，消除外部文件依赖
- `skill-config-fixes`: 修复 allowed-tools、disable-model-invocation、结束引导、settings.local.json 等配置类问题

### Modified Capabilities
（无）

## Impact

- 修改 5 个 SKILL.md 文件（new-worktree-apply、merge-worktree-return、parall-new-proposal、parall-new-worktree-apply、check-changes-completed）
- 修改 1 个配置文件（.claude/settings.local.json）
- 无新增 skill，无删除 skill
- Dependencies 数据格式变更：`proposal.md` 内 `## Dependencies` 段 → `dependencies.yaml`（向后不兼容，但当前仅 1 个 change 有实际 Dependencies 数据）
- 运行 `parall-new-worktree-apply` 后 Agent 不再读取 `new-worktree-apply/SKILL.md`，行为不变但实现路径改变
