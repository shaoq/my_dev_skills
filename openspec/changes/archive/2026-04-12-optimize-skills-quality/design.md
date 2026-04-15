## Context

当前项目根目录下有 5 个自定义 skill（new-worktree-apply、merge-worktree-return、parall-new-proposal、parall-new-worktree-apply、check-changes-completed），它们围绕 OpenSpec 核心技能构建了并行提案-实施-检查-归档的工作流管线。

经全面 review 发现 7 个问题，分布在数据格式、skill 间协作、配置完整性三个层面。这些问题不会导致功能完全不可用，但会造成维护困难、运行时频繁弹审批框、用户不知道下一步操作等问题。

## Goals / Non-Goals

**Goals:**
- 消除对 openspec artifact（proposal.md）的后修改，将 Dependencies 迁移到独立文件
- 统一 backfill 规则定义，消除三处重复实现中的不一致风险
- 让 Agent prompt 自包含，不依赖读取外部 skill 文件的步骤编号
- 修复 allowed-tools 使运行时不再频繁弹审批
- 为重量级 skill 补全 disable-model-invocation 防止误触发
- 增强结束引导，让用户清楚下一步操作
- 清理 settings.local.json 无效条目

**Non-Goals:**
- 不新增 skill
- 不修改 OpenSpec 核心技能（.claude/skills/ 和 .claude/commands/）
- 不修改 openspec CLI 或其 schema 定义
- 不解决 worktree 中 gitignored 文件的可访问性问题（独立议题）
- 不处理 openspec/changes/ 下的残留未归档 change（运维事项）

## Decisions

### Decision 1: Dependencies 存储格式 — YAML 而非 markdown

**选择**: `dependencies.yaml`（独立 YAML 文件）

**替代方案**:
- A) 写入 `.openspec.yaml` — openspec 管理的文件，CLI 可能覆盖自定义字段
- B) 写入 `dependencies.md` — 结构化程度低，仍需自定义解析
- C) 保持 `## Dependencies` 在 proposal.md — 当前方案，侵入 openspec artifact

**理由**: YAML 格式精确、无 sed 正则误匹配风险（当前 `\b[a-z][a-z0-9-]*\b` 会匹配 "Use" 等无关单词），完全独立于 openspec 管理范围。

### Decision 2: Backfill 统一策略 — 内嵌规则而非新建 skill

**选择**: 在每个需要 backfill 的 skill 中内嵌统一的四规则描述

**替代方案**:
- A) 新建 `backfill-tasks` skill 供其他 skill 调用 — 增加文件数量和 Skill 工具调用层级
- B) 在 `new-worktree-apply` 中定义规范，其他 skill 引用该文件 — 当前方案，脆弱

**理由**: 规则本身简短（4 条），内嵌在 Agent prompt 中更可靠，不依赖外部文件的步骤编号。`check-changes-completed` 在此基础上增加 Level-2 用户确认，自然扩展。

### Decision 3: Agent prompt 自包含 — 内嵌规则而非读取外部文件

**选择**: 将后处理步骤直接写入 Agent prompt

**替代方案**:
- A) 通过 Skill 工具调用 `new-worktree-apply` — 会执行完整的 worktree 创建流程，无法只执行部分步骤
- B) 读取 `new-worktree-apply/SKILL.md` 再按编号提取 — 当前方案，编号变更即失效

**理由**: Agent prompt 中嵌入具体操作步骤比引用外部文件编号更稳健，且规则已经通过 Decision 2 统一。

### Decision 4: settings.local.json 精简 — 删除 shell 语法片段，补充 git 子命令

**选择**: 删除 `Bash(for name:*)`、`Bash(do)` 等 6 条无效条目，补充 `Bash(git branch:*)` 等 7 条常用 git 子命令

**理由**: shell 关键字（do/done/for）不是可执行的 bash 命令前缀，永远不会匹配实际命令。补充的 git 子命令是各 skill 实际使用的。

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| Dependencies 格式向后不兼容 | 当前仅 1 个 change（parall-new-worktree-apply）有实际 Dependencies 数据 | 手动迁移该 change 的 proposal.md 内容到 dependencies.yaml |
| Agent prompt 内嵌规则与 new-worktree-apply 的规则可能不同步 | 修改规则时需同时更新两处 | 在 task 描述中明确标注"同步更新" |
| 移除 shell 语法片段权限后，若 settings 机制有意外匹配行为 | 低风险，这些条目本就无效 | 验证 skill 运行无回归 |
