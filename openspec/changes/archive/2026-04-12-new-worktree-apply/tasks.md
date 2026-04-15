## 1. Skill 目录与 Frontmatter

- [x] 1.1 创建 `new-worktree-apply/` 目录及 `SKILL.md` 文件
- [x] 1.2 编写 frontmatter：name, description, argument-hint, disable-model-invocation, allowed-tools

## 2. 前置检查与参数处理

- [x] 2.1 实现参数解析：提取提案名称 `$ARGUMENTS`，支持可选的 `--branch` 参数指定主分支
- [x] 2.2 实现 git 仓库检查：验证当前目录是 git 仓库
- [x] 2.3 实现 OpenSpec CLI 可用性检查
- [x] 2.4 实现提案存在性检查：验证 `openspec/changes/<name>/` 目录存在
- [x] 2.5 实现分支名称合法性验证：仅允许字母、数字、点、下划线、连字符，最长 64 字符

## 3. Git 状态检查与自动提交

- [x] 3.1 实现 `git status --porcelain` 检查未提交文件
- [x] 3.2 实现自动提交：`git add -A && git commit -m "chore: auto-commit before worktree for <name>"`
- [x] 3.3 实现无文件变更时跳过提交的逻辑

## 4. 主分支检测

- [x] 4.1 实现主分支自动检测：按优先级检查 main → master → trunk
- [x] 4.2 实现 fallback 检测：通过 `git remote show origin` 获取默认分支
- [x] 4.3 实现 `--branch` 参数覆盖逻辑

## 5. Worktree 创建

- [x] 5.1 实现分支重复检查：`git branch --list <name>` 确认分支不存在
- [x] 5.2 实现通过 `EnterWorktree` 工具创建 worktree，name 参数为提案名称
- [x] 5.3 实现创建失败的错误处理和回退

## 6. HEAD 一致性验证

- [x] 6.1 实现记录主分支 HEAD commit hash
- [x] 6.2 实现比较 worktree HEAD 与主分支 HEAD
- [x] 6.3 实现不一致时的自动合并：`git merge <main-branch>`

## 7. OpenSpec Apply 集成

- [x] 7.1 实现调用 Skill 工具执行 `openspec-apply-change`，传入提案名称参数
- [x] 7.2 实现 apply 失败时的错误报告

## 8. 输出格式与错误处理

- [x] 8.1 实现成功输出格式：显示 worktree 路径、分支名、apply 状态
- [x] 8.2 实现各步骤的错误输出格式和恢复建议
