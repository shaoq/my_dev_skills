## 1. 前置检查

- [x] 1.1 验证当前目录是 git 仓库 (`git rev-parse --is-inside-work-tree`)
- [x] 1.2 验证 openspec CLI 可用 (`which openspec`)
- [x] 1.3 记录当前分支名称 (`git branch --show-current`)

## 2. 扫描与完成判定

- [x] 2.1 扫描 `openspec/changes/` 下所有子目录，排除 `archive/`，得到 ACTIVE_CHANGES 列表
- [x] 2.2 若 ACTIVE_CHANGES 为空，输出 "No active changes found" 并停止
- [x] 2.3 对每个 change 检查 D1（tasks.md 全部 `[x]`）：读取 tasks.md 统计完成/总数
- [x] 2.4 对每个 change 检查 D3（代码落地）：从 design.md/proposal.md 提取预期文件路径，验证文件存在
- [x] 2.5 对每个 change 检查 D3（已提交）：`git log <current-branch> -- <files>` 确认代码已 commit
- [x] 2.6 对每个 change 检查 D4（依赖完整性）：解析 proposal.md 的 Dependencies 段，验证依赖已归档或也可归档
- [x] 2.7 无预期文件路径时使用启发式 fallback：检查 `<change-name>/SKILL.md` 是否存在

## 3. 报告输出

- [x] 3.1 输出 markdown 表格：Change | Tasks | Code | Dependencies | Archivable
- [x] 3.2 对非 archivable 的 changes 列出阻塞原因
- [x] 3.3 若无 archivable changes，输出提示并停止

## 4. 确认与批量归档

- [x] 4.1 使用 AskUserQuestion 提供三选项："全部归档" / "逐个确认" / "仅查看"
- [x] 4.2 "全部归档"：按字母序对每个可归档 change 调用 `Skill("opsx:archive", args="<name>")`
- [x] 4.3 "逐个确认"：对每个可归档 change 使用 AskUserQuestion 确认后调用 `Skill("opsx:archive")`
- [x] 4.4 "仅查看"：结束流程不执行任何归档操作
- [x] 4.5 归档失败不阻塞后续 change，记录错误继续执行

## 5. 最终报告

- [x] 5.1 输出归档结果汇总表格：Change | Status | Details
- [x] 5.2 列出成功的归档位置和失败的错误详情
