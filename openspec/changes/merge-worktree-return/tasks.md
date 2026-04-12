## 1. Skill 目录与 Frontmatter

- [x] 1.1 创建 `merge-worktree-return/` 目录及 `SKILL.md` 文件
- [x] 1.2 编写 frontmatter：name, description, argument-hint, disable-model-invocation, allowed-tools

## 2. 前置检查与参数处理

- [x] 2.1 实现参数解析：提取可选的提案名称 `$ARGUMENTS`
- [x] 2.2 实现 git 仓库检查：验证当前目录是 git 仓库
- [x] 2.3 实现当前在 worktree 中的检查：验证 session 处于 worktree 状态

## 3. OpenSpec 提案验证（可选）

- [x] 3.1 实现参数存在时的 OpenSpec 状态检查：`openspec status --change <name> --json`
- [x] 3.2 实现任务完成度验证：检查所有 tasks 是否已完成
- [x] 3.3 实现未完成时的提示和确认：使用 AskUserQuestion 询问是否继续

## 4. Git 提交当前分支

- [x] 4.1 实现 `git status --porcelain` 检查未提交文件
- [x] 4.2 实现自动提交：`git add -A && git commit -m "chore: auto-commit before merge from worktree"`
- [x] 4.3 实现无文件变更时跳过提交的逻辑

## 5. 主分支检测与 Rebase

- [x] 5.1 实现主分支自动检测：main → master → trunk 优先级
- [x] 5.2 实现获取 worktree 对应的主目录路径
- [x] 5.3 实现 `git rebase <main-branch>` 执行
- [x] 5.4 实现冲突自动解决：读取冲突标记，分析并解决冲突
- [x] 5.5 实现冲突无法解决时的回退：`git rebase --abort` 并报告

## 6. 合并回主分支

- [x] 6.1 实现切换到主分支目录
- [x] 6.2 实现 `git merge <worktree-branch-name>` 合并操作
- [x] 6.3 实现合并冲突的自动解决
- [x] 6.4 实现合并后验证：`git log <main>..<worktree-branch>` 确认无遗漏提交

## 7. 安全退出 Worktree

- [x] 7.1 实现退出前最终检查：确认主分支包含所有变更、无未提交文件
- [x] 7.2 实现通过 `ExitWorktree` 工具退出，action: "remove"
- [x] 7.3 实现退出后验证：确认 CWD 已恢复到主目录、`git branch --show-current` 显示主分支

## 8. 输出格式与错误处理

- [x] 8.1 实现成功输出格式：显示合并状态、退出状态、当前分支
- [x] 8.2 实现各步骤的错误输出格式和恢复建议
