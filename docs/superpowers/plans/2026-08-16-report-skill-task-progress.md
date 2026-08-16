# Skill Task Progress Summary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 让 `new-worktree-apply` 和 `parall-new-proposal` 的最终总结只用数量报告任务进度，并按有证据的原因类别概述未完成任务。

**Architecture:** 直接扩展两个现有 `SKILL.md` 的任务统计和总结输出契约，不引入公共脚本。两个 skill 共用相同的 checkbox 统计、未知状态和互斥原因分类规则，但分别按单提案 apply 与批量提案创建的职责输出。

**Tech Stack:** Markdown skill instructions、OpenSpec、shell/`rg` 静态契约检查、`quick_validate.py`、GitNexus。

## Global Constraints

- 数量输出固定包含 `DONE/TOTAL` 和 `REMAINING`，不输出 task 编号、正文或逐项清单。
- 每个未完成任务只计入一个原因类别，所有原因计数之和必须等于 `REMAINING`。
- 原因只能来自 workflow 直接证据；没有证据时归入“原因未知”。
- `tasks.md` 缺失、不可读或没有可识别 checkbox 时报告 unknown，不得把 `0/0` 视为完成。
- 不改变 Git/worktree、proposal artifact、Wave/Batch 或 apply 行为。

---

### Task 1: `new-worktree-apply` 单提案进度契约

**Files:**
- Modify: `new-worktree-apply/SKILL.md`
- Test: shell static contract checks against `new-worktree-apply/SKILL.md`

**Interfaces:**
- Consumes: Step 11 最终 `tasks.md` checkbox 状态及 apply/测试/依赖等直接执行证据
- Produces: `DONE`、`TOTAL`、`REMAINING`、进度状态和互斥原因类别计数

- [x] **Step 1: 运行失败基线**

运行一个 shell 契约检查，要求文件同时包含 `REMAINING`、`未完成原因概要`、`原因未知`、unknown 状态和“不输出 task 明细”的约束。

Expected: FAIL，至少报告当前缺少 `REMAINING` 或原因概要契约。

- [x] **Step 2: 更新任务核对规则**

在 Step 11 中定义 checkbox 统计、`REMAINING=TOTAL-DONE`、六类互斥原因、证据门槛、类别计数求和约束以及 unknown 处理。

- [x] **Step 3: 更新成功输出模板**

保留当前字段并增加：

```text
Proposal progress: <complete|partial|unknown>
Tasks: <DONE>/<TOTAL>
Remaining: <REMAINING>
Unfinished reason summary: <category=count; ... | none | unknown: reason>
```

- [x] **Step 4: 运行 GREEN 验证**

重跑 Step 1 的契约检查并运行：

使用 `uv --with pyyaml` 实际运行 `quick_validate.py`，并与 `HEAD` 基线比较；只允许两边出现相同的既有 `argument-hint, disable-model-invocation` unknown-key 诊断。随后独立解析 YAML 并验证运行时字段。

Expected: 契约检查通过；通用校验器没有新增诊断；真实 frontmatter 解析和字段检查通过。

### Task 2: `parall-new-proposal` 批量进度契约

**Files:**
- Modify: `parall-new-proposal/SKILL.md`
- Test: shell static contract checks against `parall-new-proposal/SKILL.md`

**Interfaces:**
- Consumes: 每个成功创建提案的 `tasks.md` 以及提案创建成功/失败状态
- Produces: 每提案 `DONE/TOTAL`、`REMAINING`，已知提案覆盖范围、聚合任务进度和原因类别计数

- [x] **Step 1: 运行失败基线**

运行一个 shell 契约检查，要求文件同时包含逐提案进度列、聚合 `DONE/TOTAL`、`REMAINING`、已知进度覆盖范围、尚未进入实施阶段分类和“不输出 task 明细”的约束。

Expected: FAIL，报告当前没有任何任务进度汇总。

- [x] **Step 2: 增加创建后任务统计**

对成功提案读取并统计 checkbox；缺失、不可读或零任务时标记 unknown，且不计入已知聚合分母。新建未勾选任务归为“尚未进入实施阶段”。

- [x] **Step 3: 更新全部成功与部分失败模板**

创建表增加 `Tasks` 和 `Remaining`，新增聚合进度和原因概要；创建失败继续单独报告，不计入已知任务总数。

- [x] **Step 4: 运行 GREEN 验证**

重跑 Step 1 的契约检查并运行：

使用 `uv --with pyyaml` 实际运行 `quick_validate.py`，并与 `HEAD` 基线比较；只允许两边出现相同的既有 `argument-hint, disable-model-invocation` unknown-key 诊断。随后独立解析 YAML 并验证运行时字段。

Expected: 契约检查通过；通用校验器没有新增诊断；真实 frontmatter 解析和字段检查通过。

### Task 3: 跨 skill 一致性和交付验证

**Files:**
- Verify: `new-worktree-apply/SKILL.md`
- Verify: `parall-new-proposal/SKILL.md`
- Verify: `openspec/changes/report-skill-task-progress/`

**Interfaces:**
- Consumes: Task 1 和 Task 2 的最终文档契约
- Produces: 一致的统计口径、可验证的 OpenSpec 状态和预期变更范围

- [x] **Step 1: 检查规范覆盖和占位符**

确认两个文件都满足 OpenSpec scenarios，且没有未填写内容或未填充模板占位符。

- [x] **Step 2: 验证 OpenSpec change**

```bash
openspec validate report-skill-task-progress
openspec status --change report-skill-task-progress
```

Expected: change valid，4/4 artifacts complete。

- [x] **Step 3: 检测变更范围**

运行 GitNexus `detect_changes(scope: "all")`，并检查 `git diff --check` 与 `git diff --stat`。

Expected: 仅两个目标 skill、该 OpenSpec change 和本实施计划受到影响，无意外代码执行流。
