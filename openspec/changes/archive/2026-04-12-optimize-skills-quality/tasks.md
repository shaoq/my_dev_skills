## 1. Dependencies 迁移 — parall-new-proposal

- [x] 1.1 修改 `parall-new-proposal/SKILL.md` Step 6.1：将 "Edit proposal.md 追加 ## Dependencies" 改为 "Write openspec/changes/<name>/dependencies.yaml"
- [x] 1.2 修改 `parall-new-proposal/SKILL.md` Step 6.2：格式规范从 markdown 标题+列表改为 YAML 格式（`dependencies:` 下缩进 2 空格，每项 `- <name>`）
- [x] 1.3 修改 `parall-new-proposal/SKILL.md` Step 6.3：将 "不修改 proposal.md" 改为 "不创建 dependencies.yaml"
- [x] 1.4 修改 `parall-new-proposal/SKILL.md` Guardrails 第 5 条：将 "Dependencies 段格式必须与 Step 2.1 兼容" 改为 "dependencies.yaml 格式必须与 Step 2.1 兼容"
- [x] 1.5 修改 `parall-new-proposal/SKILL.md` Step 7.2 失败建议：将 "检查 proposal.md 中的 ## Dependencies 段" 改为 "检查 dependencies.yaml 文件"

## 2. Dependencies 迁移 — parall-new-worktree-apply

- [x] 2.1 修改 `parall-new-worktree-apply/SKILL.md` Step 2.1：将 "读取 proposal.md，解析 ## Dependencies 段" 改为 "读取 dependencies.yaml，解析 YAML dependencies 列表"，解析逻辑改为 test -f 判断文件存在 + 解析 YAML
- [x] 2.2 修改 `parall-new-worktree-apply/SKILL.md` Step 2.2 错误提示：将 "请检查 proposal.md 中的 ## Dependencies 段" 改为 "请检查 dependencies.yaml"
- [x] 2.3 修改 `parall-new-worktree-apply/SKILL.md` Step 2.3 错误提示：将 "请修改 proposal.md 中的 ## Dependencies 段消除循环" 改为 "请修改 dependencies.yaml 消除循环"

## 3. Dependencies 迁移 — check-changes-completed

- [x] 3.1 修改 `check-changes-completed/SKILL.md` Dimension 4：将 sed/grep 解析 proposal.md 改为 Read dependencies.yaml 解析 YAML 列表
- [x] 3.2 修改 `check-changes-completed/SKILL.md` Dimension 4 判空逻辑：将 "无此段或段内容为空" 改为 "文件不存在或 dependencies 为空"

## 4. Backfill 规范化 + Agent prompt 自包含

- [x] 4.1 重写 `parall-new-worktree-apply/SKILL.md` Step 4.1 Agent prompt：删除读取 new-worktree-apply/SKILL.md 的指令，内嵌四规则 backfill（Step A）和 force-add+commit（Step B）
- [x] 4.2 在 Agent prompt 中将 dependencies 引用统一为 dependencies.yaml 术语

## 5. allowed-tools 修复

- [x] 5.1 修改 `new-worktree-apply/SKILL.md` allowed-tools：增加 `Bash(grep *)`、`Bash(test *)`、`Bash(head *)`、`Bash(sed *)`
- [x] 5.2 修改 `merge-worktree-return/SKILL.md` allowed-tools：增加 `Bash(grep *)`、`Bash(awk *)`、`Bash(sed *)`、`Bash(cat *)`、`Bash(head *)`、`Bash(test *)`
- [x] 5.3 修改 `check-changes-completed/SKILL.md` allowed-tools：增加 `Bash(head *)`

## 6. disable-model-invocation 补全

- [x] 6.1 为 `parall-new-proposal/SKILL.md` frontmatter 添加 `disable-model-invocation: true`
- [x] 6.2 为 `parall-new-worktree-apply/SKILL.md` frontmatter 添加 `disable-model-invocation: true`

## 7. 结束引导增强

- [x] 7.1 修改 `merge-worktree-return/SKILL.md` Output On Success：末尾增加 "建议运行 /check-changes-completed 检查整体完成度，或 /opsx:archive <name> 归档"
- [x] 7.2 修改 `parall-new-worktree-apply/SKILL.md` Step 7.2 最终报告：末尾增加差异化引导（成功→/check-changes-completed + /opsx:archive；失败→/new-worktree-apply <name> 重试）
- [x] 7.3 修改 `check-changes-completed/SKILL.md` Step 7 Archive hint：将单一提示改为差异化引导（可归档→/opsx:archive；未完成→/opsx:apply 或 /new-worktree-apply）

## 8. settings.local.json 清理

- [x] 8.1 删除 `.claude/settings.local.json` 中 6 条无效条目（`Bash(for name:*)`、`Bash(do)`、`Bash(echo "=== $name ===")`、`Bash(done)`、`Bash(do echo:*)`、`Bash(then sed:*)`）
- [x] 8.2 补充 `.claude/settings.local.json` 中 8 条常用 git 子命令权限（`Bash(git branch:*)`、`Bash(git checkout:*)`、`Bash(git rebase:*)`、`Bash(git rev-parse:*)`、`Bash(git log:*)`、`Bash(git diff:*)`、`Bash(git status:*)`、`Bash(git show:*)`）
