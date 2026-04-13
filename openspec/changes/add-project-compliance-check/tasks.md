## 1. D5 维度核心逻辑（插入 SKILL.md Step 3）

- [x] 1.1 在 SKILL.md Step 3 中 D4 之后插入 Dimension 5 — Project Compliance 子节，包含 Step 5a-5e 完整算法描述
- [x] 1.2 编写 Step 5a（定位 CLAUDE.md）：检查根目录和 EXPECTED_FILES 子目录中的 CLAUDE.md
- [x] 1.3 编写 Step 5b（跳过条件）：无 CLAUDE.md → `✓ (无项目规范)`；无合规要求 → `✓ (无合规要求)`；无法解析 → `✓ (无法解析)`
- [x] 1.4 编写 Step 5c（提取合规要求）：逐行正则匹配 test-sync / doc-sync / api-schema-sync / changelog-sync 四种内置类型，按 type 去重
- [x] 1.5 编写 Step 5d（触发判断）：基于 EXPECTED_FILES 和 design.md 内容判断变更是否触发各合规要求
- [x] 1.6 编写 Step 5e（合规检查）：通过 `git diff main..HEAD --name-only` 匹配套套产出文件名模式
- [x] 1.7 编写 D5 结果汇总逻辑：全部通过 → `✓`；存在缺失 → `✗ 缺失: <type-list>`；记录 `D5_GAPS`

## 2. SKILL.md 输出格式更新

- [x] 2.1 更新 frontmatter description：从"四维"改为"五维"，增加"项目规范合规性"
- [x] 2.2 更新 Step 5 汇总表：增加"合规"列（在"依赖"和"可存档?"之间）
- [x] 2.3 更新可存档逻辑：从"所有四个维度"改为"所有五个维度"
- [x] 2.4 更新 Step 6 Blocking Reasons：增加 D5 条目格式（含完整缺失描述和 `/opsx:explore` 建议）
- [x] 2.5 更新 Step 7 Archive Hint：增加 D5 合规缺失时的指导（`/opsx:explore` 分析建议）
- [x] 2.6 更新 Output On Success 模板：包含合规列

## 3. SKILL.md Guardrails 和回填交互更新

- [x] 3.1 在 Step 4 末尾增加说明：D5 不参与回填，仅作为提示报告
- [x] 3.2 在 Guardrails 中增加：D5 严格只读诊断，绝不自动创建或修改配套产出
- [x] 3.3 在 Guardrails 中增加：CLAUDE.md 无法解析时 D5 = `✓ (无法解析)`，不阻塞归档
- [x] 3.4 在 Guardrails 中增加：无 CLAUDE.md 时 D5 不阻塞归档

## 4. README.md 同步更新

- [x] 4.1 更新 Skills 一览表中 check-changes-completed 的描述为"五维完成度检查"
- [x] 4.2 更新详解中 check-changes-completed 的四维检查模型表格，增加 D5 行
- [x] 4.3 更新补标记机制描述中的维度说明
