## 1. Skill 目录与 Frontmatter

- [x] 1.1 创建 `parall-new-worktree-apply/` 目录及 `SKILL.md` 文件
- [x] 1.2 编写 frontmatter：name, description, argument-hint

## 2. 前置检查与 Auto-commit

- [x] 2.1 实现参数解析：支持可选参数（无参数则自动发现所有待执行 changes）
- [x] 2.2 实现 git 仓库检查和当前分支检查（确认在 main 分支）
- [x] 2.3 实现 `git status --porcelain` 检查未提交文件并自动 commit

## 3. Change Discovery

- [x] 3.1 实现扫描 `openspec/changes/` 目录，排除 `archive/` 子目录
- [x] 3.2 实现读取每个 change 的 `tasks.md`，检测 `[ ]` 未完成项
- [x] 3.3 实现过滤：仅保留含有未完成项的 changes
- [x] 3.4 实现待执行列表为空时的退出逻辑

## 4. 依赖解析与图构建

- [x] 4.1 实现读取每个待执行 change 的 `proposal.md`，解析 `## Dependencies` 段
- [x] 4.2 实现依赖引用校验：验证每个依赖名称在 `openspec/changes/` 中存在
- [x] 4.3 实现循环依赖检测
- [x] 4.4 实现拓扑排序，生成 Wave 列表
- [x] 4.5 实现执行计划展示：显示 Wave 分组和每个 Wave 内的 changes

## 5. 单个 Change 简化路径

- [x] 5.1 实现数量为 1 时的委托逻辑：通过 Skill 工具调用 `opsx:apply <name>`
- [x] 5.2 实现单个 change 完成后的 merge 和 worktree 退出流程

## 6. Wave 并行执行

- [x] 6.1 实现为每个 Wave 内的 change 并行 spawn Agent（`isolation: "worktree"`）
- [x] 6.2 实现 Agent prompt：指示执行 `/opsx:apply <change-name>` 并 git commit
- [x] 6.3 实现等待 Wave 内所有 Agent 完成
- [x] 6.4 实现 Agent 失败时的记录逻辑（不阻塞其他 Agent）

## 7. 串行合并

- [x] 7.1 实现 Wave 完成后按目录名字母序逐个 rebase + merge
- [x] 7.2 实现 `git rebase main <branch>` 执行
- [x] 7.3 实现 rebase 冲突检测（`git status --porcelain` 检查 `UU` 文件）
- [x] 7.4 实现冲突标记解析：读取 `<<<<<<<`、`=======`、`>>>>>>>` 标记
- [x] 7.5 实现非重叠冲突的自动解决：双方改动都保留
- [x] 7.6 实现语义可合并冲突的智能解决
- [x] 7.7 实现无法解决冲突的 `git rebase --abort` 和报告
- [x] 7.8 实现冲突解决后的 `git rebase --continue`
- [x] 7.9 实现 `git checkout main && git merge <branch>` 合并操作

## 8. 验证与报告

- [x] 8.1 实现全部 Wave 完成后重新扫描 `tasks.md`
- [x] 8.2 实现验证每个之前待执行的 change 的任务是否全部 `[x]`
- [x] 8.3 实现最终报告生成：执行总览、Wave 结果、验证状态、失败详情

## 9. 输出格式与错误处理

- [x] 9.1 实现成功输出格式：汇总表格显示每个 change 的 Agent 状态和合并状态
- [x] 9.2 实现各步骤的错误输出格式和恢复建议
