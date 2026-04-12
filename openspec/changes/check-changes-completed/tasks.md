## 1. Skill 目录与 Frontmatter

- [x] 1.1 创建 `check-changes-completed/` 目录及 `SKILL.md` 文件
- [x] 1.2 编写 frontmatter：name, description, argument-hint

## 2. Active Changes 扫描

- [x] 2.1 实现扫描 `openspec/changes/` 目录，排除 `archive/` 子目录，列出所有 active changes
- [x] 2.2 实现无 active changes 时的退出逻辑

## 3. 维度 1 — Tasks 完成度检查

- [x] 3.1 实现读取每个 change 的 `tasks.md` 文件
- [x] 3.2 实现统计 `- [x]`（已完成）和 `- [ ]`（未完成）的计数和比例
- [x] 3.3 实现 tasks.md 不存在时的"缺失"标记

## 4. 维度 2 — Artifacts 齐全性检查

- [x] 4.1 实现调用 `openspec status --change "<name>" --json` 获取 artifact 状态
- [x] 4.2 实现检查所有 artifacts 的 status 是否均为 "done"
- [x] 4.3 实现未完成 artifacts 的名称列出

## 5. 维度 3 — Code 落地验证

- [x] 5.1 实现解析 design.md 识别预期产出文件路径（如 SKILL.md 等）
- [x] 5.2 实现检查产出文件是否存在于磁盘
- [x] 5.3 实现通过 `git log --oneline` 检查是否有与 change 相关的实质提交
- [x] 5.4 实现产出文件存在但无提交时的"警告"标记

## 6. 维度 4 — 依赖完整性检查

- [x] 6.1 实现解析每个 change 的 `proposal.md` 中 `## Dependencies` 段
- [x] 6.2 实现依赖名称提取和引用有效性校验
- [x] 6.3 实现递归检查依赖 change 的四维状态
- [x] 6.4 实现循环依赖检测
- [x] 6.5 实现无依赖时直接通过

## 7. 汇总表格输出

- [x] 7.1 实现汇总表格：Change | Tasks | Artifacts | Code 落地 | 依赖 | 可存档?
- [x] 7.2 实现四维全部通过标记"可存档"
- [x] 7.3 实现任一维度未通过标记"不可存档"并附带阻塞原因
- [x] 7.4 实现无可存档 changes 时显示阻塞原因总览

## 8. 存档引导

- [x] 8.1 实现筛选可存档 changes 候选列表
- [x] 8.2 实现使用 AskUserQuestion 提供存档策略选择：全部存档 / 逐个确认 / 仅查看
- [x] 8.3 实现"全部存档"策略：依次调用 `/opsx:archive <name>`
- [x] 8.4 实现"逐个确认"策略：逐个 AskUserQuestion 确认后存档
- [x] 8.5 实现"仅查看"策略：结束流程不执行存档
- [x] 8.6 实现存档失败的错误处理和跳过继续逻辑
