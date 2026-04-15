## 1. Skill Frontmatter 更新

- [x] 1.1 更新 `check-changes-completed/SKILL.md` 的 description 字段，反映诊断+补标记双重能力
- [x] 1.2 更新 Guardrail：将 "Never modify any change files — this is a read-only check" 改为条件性允许修改 tasks.md

## 2. 新增 Step 5.5 — 矛盾检测

- [x] 2.1 在 Step 4（汇总表格）之后插入矛盾检测逻辑：遍历所有 change，识别 D3=✓ 且 D1=✗ 的 change
- [x] 2.2 实现无矛盾时直接跳过补标记的逻辑

## 3. Level-1 自动补标记（4规则解析器）

- [x] 3.1 实现反引号路径提取：从 task 描述中提取反引号内的文件路径
- [x] 3.2 实现目录创建模式识别：匹配 "创建 `xxx/` 目录" 并检查目录存在
- [x] 3.3 实现 frontmatter 模式识别：匹配 "编写 frontmatter" 并检查文件含 `---`
- [x] 3.4 实现实现关键词模式：匹配 "实现 xxx" 并 grep 搜索相关代码文件
- [x] 3.5 实现文件存在性检查：对提取的路径执行 `test -f` 或 `test -d`
- [x] 3.6 实现自动标记：将匹配成功的 `- [ ]` 改为 `- [x]`

## 4. Level-2 兜底补标记

- [x] 4.1 实现 D3 全通过判断：文件存在 AND git commit 有记录
- [x] 4.2 实现残余 `[ ]` 收集：Level-1 完成后仍为 `[ ]` 的 task 列表
- [x] 4.3 实现 AskUserQuestion 提示：展示残余 tasks，提供"全部标记为完成"和"跳过"选项
- [x] 4.4 实现确认后批量标记：用户确认后全部 `- [ ]` → `- [x]`

## 5. Git 提交

- [x] 5.1 实现修改检测：判断是否有 tasks.md 被实际修改
- [x] 5.2 实现 `git add -f openspec/changes/*/tasks.md` force-add
- [x] 5.3 实现 commit：`fix: auto-backfill task markers (N changes)`

## 6. 报告更新

- [x] 6.1 实现补标记后重新统计 D1：更新 Tasks 列的 X/N 计数
- [x] 6.2 实现补标记报告输出：显示自动标记数、确认标记数、仍缺失数
- [x] 6.3 更新 Step 5（阻塞原因）和 Step 6（存档提示）使用补标记后的最新数据
