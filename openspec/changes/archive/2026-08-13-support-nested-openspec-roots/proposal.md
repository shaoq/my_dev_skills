## Why

`new-worktree-apply` 当前把 OpenSpec 项目固定为 Git 仓库根，因而无法处理
`twin-rag/openspec/changes/<proposal>` 这类嵌套项目。自动递归发现可能在
monorepo 中误选项目，移动 proposal 又会破坏既有目录边界，因此需要显式、可审计且
失败关闭的 OpenSpec 项目根选择。

## What Changes

- 为 `new-worktree-apply` 新增可选
  `--openspec-root <repo-relative-directory>`；参数值表示 Git 仓库内直接包含
  `openspec/` 的目录，省略时保持仓库根 `.` 的现有行为。
- 严格校验参数与路径：拒绝重复或缺值、绝对路径、空白、非规范路径段、越出仓库和
  符号链接逃逸；不自动搜索、猜测或回退到其他 OpenSpec 项目。
- 将 `OPENSPEC_ROOT`、OpenSpec 项目物理路径和仓库相对
  `CHANGE_PREFIX` 纳入只读预检、确认摘要与确认后快照复检。
- 让 artifact manifest 始终使用 Git 仓库相对完整路径；让 OpenSpec status、apply
  和任务核对始终从所选 OpenSpec 项目目录执行。
- 增加根目录兼容、嵌套项目和非法/逃逸路径的隔离场景验证，确保确认前零 Git 写入及
  既有 worktree 生命周期安全约束不变。

## Capabilities

### New Capabilities

无。

### Modified Capabilities

- `worktree-targeting`: 扩展单 worktree 创建流程的参数、OpenSpec 项目定位、
  artifact 快照、确认复检和 apply 执行上下文合同，使其安全支持仓库内显式嵌套
  OpenSpec 根目录。

## Impact

- 修改 `new-worktree-apply/SKILL.md` 的参数语法、Step 1、Step 4～11、摘要和成功输出。
- 修改现行 `openspec/specs/worktree-targeting/spec.md` 对应行为合同。
- 更新 `README.md` 中单 worktree apply 的嵌套 OpenSpec 示例与参数说明。
- 验证仅使用只读真实仓库检查及 `mktemp -d` 隔离仓库，不创建或修改用户现有
  worktree；不改变 `merge-worktree-return` 与 `parall-new-worktree-apply` 的参数。
