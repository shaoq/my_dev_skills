# my_dev_skills - 使用指南

基于 OpenSpec 工作流的 Claude Code Skills 集合，提供从需求分析到并行实施、归档的完整开发流水线。

## 安装

```bash
# 1. 克隆仓库
git clone git@github.com:shaoq/my_dev_skills.git
cd my_dev_skills

# 2. 全局安装（符号链接 + 权限合并，一次安装所有项目通用）
python3 setup-skills-env.py

# 卸载（移除全局符号链接和权限，不影响本仓库）
python3 setup-skills-env.py --uninstall
```

> **重要**：Skills 通过符号链接安装在 `~/.claude/skills/`，指向本仓库的实际文件。
> **不要删除或移动本仓库目录**，否则所有项目中已安装的 Skills 将失效。

### 依赖项

| 依赖 | 说明 | 检查方式 |
|------|------|---------|
| **git** | 版本控制 | `git --version` |
| **OpenSpec CLI** | 工作流引擎，管理 change/artifact 生命周期 | `openspec --version` |
| **Claude Code** | 运行环境（CLI / Desktop / IDE） | 内置 |
| **Python 3.6+** | 仅 `setup-skills-env.py` 需要 | `python3 --version` |
| **iTerm2** (可选) | `setup-iterm2-claude-notify.py` 需要 | macOS only |

### iTerm2 通知（可选）

```bash
python3 setup-iterm2-claude-notify.py           # 安装 iTerm2 + Claude Code + Codex 通知
python3 setup-iterm2-claude-notify.py --check  # 检查状态
python3 setup-iterm2-claude-notify.py --remove # 卸载受管配置
```

> 安装内容：
> 1. iTerm2 Notification Center alerts：统一承接通知中心提醒
> 2. Claude Code hooks：完成提醒、权限提醒、idle 提醒，走 iTerm2 `notify`
> 3. Codex `[tui]` 通知：approval prompts + completed turns，走 iTerm2 `notify`
> 4. tmux passthrough：在 iTerm2 内启动 tmux 后仍可继续通知
>
> 运行前请关闭 iTerm2，或运行后重启使其生效。
>
> 说明：
> - 受管路径为 notify-only，不再安装 `BellTrigger`，也不再依赖 BEL 提醒
> - 若 `--check` 仍提示存在旧版受管 trigger，重新执行安装会自动迁移

---

## 快速开始

> Skills 以符号链接形式安装到 `~/.claude/skills/`，一次安装后所有项目通用。
> 前提：本仓库目录需保留在原地，不可删除或移动。

### 场景 A：综合需求（拆分 → 并行实施）

适用于：一个大需求需要拆成多个子功能并行开发。

```
Step 0: 探索需求（可选）
─────────────────────────────
  /opsx:explore "给项目添加完整的认证系统"

  → 探索问题空间、分析方案、可视化架构
  → 不产生代码，只产出思路

Step 1: 拆分需求为多个提案
─────────────────────────────
  /parall-new-proposal "给项目添加完整的认证系统"

  → 自动拆解为多个子方案，展示依赖图和 Wave 分组
  → 确认后批量创建 proposals + 注入 dependencies.yaml

Step 2: 并行实施所有提案
─────────────────────────────
  /parall-new-worktree-apply

  → 自动发现所有待执行的 changes
  → 按 Wave 并行 spawn Agent，在隔离 worktree 中实施
  → 完成后自动 rebase + merge 回主干

Step 3: 检查完成度
─────────────────────────────
  /check-changes-completed

  → 四维检查（任务 / artifacts / 代码落地 / 依赖 / 合规）
  → 自动补标记已交付但未勾选的任务
  → 输出"可归档"和"未完成"清单

Step 4: 归档已完成的 change
─────────────────────────────
  /opsx:archive <change-name>

  → 逐个归档检查通过的 change
```

### 场景 B：单个 Change（手动控制）

适用于：已有明确的小任务，需要隔离 worktree 实施。

```
Step 0: 创建 proposal
─────────────────────────────
  /opsx:propose add-user-auth

  → 生成 proposal.md / design.md / tasks.md 等 artifacts

Step 1: 在 worktree 中实施
─────────────────────────────
  /new-worktree-apply add-user-auth

  → 创建以 proposal 名命名的隔离分支
  → 验证 artifacts 完整性 → 执行实施 → 自动补标记 → 提交

Step 2: 合并回主干
─────────────────────────────
  /merge-worktree-return add-user-auth

  → rebase 到最新主干 → 合并 → 退出并清理 worktree

Step 3: 检查完成度
─────────────────────────────
  /check-changes-completed

  → 四维检查 + 自动补标记 + 合规检查

Step 4: 归档
─────────────────────────────
  /opsx:archive add-user-auth
```

---

## Skills 一览

### 核心 Skills（根目录 `*/SKILL.md`）

| Skill 名称 | 调用方式 | 用途 | 参数 |
|------------|---------|------|------|
| **parall-new-proposal** | `/parall-new-proposal` | 并行提案拆分 | 需求描述文本 |
| **parall-new-worktree-apply** | `/parall-new-worktree-apply` | 并行实施多个 changes | 无（自动发现） |
| **new-worktree-apply** | `/new-worktree-apply` | 单个 worktree 实施 | `<proposal-name> [--branch <name>]` |
| **merge-worktree-return** | `/merge-worktree-return` | worktree 合并回主干 | `[proposal-name]` |
| **check-changes-completed** | `/check-changes-completed` | 五维完成度检查 | 无 |
| **verify-impl-consistency** | `/verify-impl-consistency` | 三维语义一致性诊断 | `[change-name]` |

---

## 使用流程图（参考）

```
需求描述
   │
   ▼
┌─────────────────────────────┐
│  /opsx:explore              │  ← 可选：探索需求、分析方案
└──────────────┬──────────────┘
               │
        ┌──────┴──────┐
        │  需求规模?   │
        └──────┬──────┘
    ≤2 个子方案  │  ≥3 个子方案
           │    │
           ▼    ▼
 /opsx:propose  /parall-new-proposal
 (逐个创建)     (批量拆分+依赖图)
           │    │
           ▼    ▼
 ┌─────────┴────┴──────────┐
 │  proposals 已创建         │
 │  dependencies.yaml 已注入 │
 └──────────┬───────────────┘
            │
      ┌─────┴─────┐
      │ changes 数量│
      └─────┬─────┘
      =1    │    ≥2
      │     │     │
      ▼     │     ▼
/new-worktree-apply  /parall-new-worktree-apply
(单个 worktree 实施)  (并行 worktree 实施)
      │     │     │
      ▼     │     ▼
/merge-worktree-return  自动合并回主干
      │     │     │
      ▼     ▼     ▼
/check-changes-completed
(五维完成度检查+自动补标记+合规检查)
            │
            ▼
      /verify-impl-consistency  ← 可选：语义一致性深度诊断
      (Doc↔Code / Schema↔API / Tests↔Code)
            │
            ▼
      /opsx:archive
      (逐个归档)
```

---

## 各 Skill 详解与注意事项

### 1. parall-new-proposal

**做什么**: 将综合需求拆解为多个带依赖声明的 OpenSpec 提案。

**核心机制**:
- **三问判定**：每个候选子方案必须同时满足 "能独立测试"、"能独立理解"、"有独立价值"，否则合并到相关子方案
- **Wave 分组**：通过拓扑排序（Kahn 算法）将子方案分为可并行执行的 Wave
- **依赖注入**：为有依赖的子方案创建 `dependencies.yaml`

**注意事项**:
- 拆分结果 ≤ 2 个时会提示直接用 `/opsx:propose`
- 超过 6 个时会警告粒度可能过细
- 每 Wave 并行上限为 3，规划阶段即预览 Batch 划分
- 循环依赖会直接报错，需调整拆分方案
- **必须用户确认**后才会创建提案

### 2. parall-new-worktree-apply

**做什么**: 自动发现所有待执行 changes，按依赖图分 Wave 并行实施。

**核心机制**:
- 自动发现有未完成 `[ ]` 任务的 change
- 解析 `dependencies.yaml` 构建依赖图
- 同一 Wave 内的 changes 通过 Agent 在隔离 worktree 中并行 spawn
- 串行合并回主干（按字母序）
- 冲突智能解决（非重叠自动合并、语义可合并、无法解决则跳过）

**注意事项**:
- **必须在主分支上执行**，否则报错
- 待执行 changes = 0 时直接退出
- 待执行 changes = 1 时走简化路径（直接 apply，不 spawn Agent）
- 每 Wave 最多 3 个并行 Agent，超出自动分 Batch 串行执行
- Agent spawn 必须在同一消息中并行（同一 Batch 内）
- 合并必须串行，每个 Batch 完成后立即合并
- artifacts 不完整的 change 会被跳过
- 失败的 Agent/分支不阻塞其他

### 3. new-worktree-apply

**做什么**: 为单个 proposal 创建 git worktree 并在其中实施。

**核心机制**:
- 验证 proposal artifacts 完整性
- 通过 `EnterWorktree` 工具创建隔离分支
- 实施任务
- Post-apply 自动补标记（四规则检测）+ 强制提交 `tasks.md`

**注意事项**:
- 分支名必须符合 worktree 命名规则（kebab-case，max 64 chars）
- 若分支已存在则报错停止，**不覆盖**
- HEAD 会与主分支对比，不一致时自动 merge

### 4. merge-worktree-return

**做什么**: 将 worktree 的改动 rebase + merge 回主分支，然后退出 worktree。

**核心机制**:
- 验证在 worktree 中（检查 `.git` 是否为 `gitdir:` 文件）
- 可选验证 proposal 完成度（传参时）
- Rebase onto main → 处理冲突 → checkout main → merge → ExitWorktree

**注意事项**:
- 必须在 worktree 内运行，否则报错
- 未完成任务的 proposal 会警告并**询问用户确认**
- Rebase 失败时用 `git rebase --abort` 回到安全状态
- 所有步骤验证通过后才会调用 `ExitWorktree` 移除 worktree
- **绝不使用 --force 标志**

### 5. check-changes-completed

**做什么**: 五维完成度检查 + 智能补标记 + 项目合规检查。

**五维检查模型**:

| 维度 | 检查内容 |
|------|---------|
| D1 - Tasks | `tasks.md` 中 `[x]` vs `[ ]` 计数 |
| D2 - Artifacts | `openspec status --json` 的 artifact 状态 |
| D3 - Code 落地 | 产出文件是否存在 + git commits |
| D4 - 依赖 | `dependencies.yaml` 引用的 change 完整性 |
| D5 - 合规 | CLAUDE.md 定义的合规要求（测试同步/文档更新/API schema 等） |

**补标记机制**（当 D3=✓ 但 D1=✗ 时触发）:
- **Level-1 自动**: 四规则解析器（反引号路径、目录创建、frontmatter、实现关键词）
- **Level-2 需确认**: 自动无法匹配但 code 已交付时，询问用户

**合规检查机制**（D5 — 当项目有 CLAUDE.md 时触发）:
- 载入项目根目录和变更相关子目录中的 CLAUDE.md
- 提取合规要求（test-sync / doc-sync / api-schema-sync / changelog-sync）
- 通过 git diff 验证配套产出是否已同步
- 缺失时不自动补全，仅提示建议运行 `/opsx:explore` 分析
- 无 CLAUDE.md 时不阻塞归档

**注意事项**:
- 只修改 D3 通过但 D1 未通过的 `tasks.md`，其他 artifact 严格只读
- Level-1 自动无需确认，Level-2 需用户确认
- D5 合规缺失仅提示，不自动补全配套产出
- 检测循环依赖，防止无限递归
- 输出结果包含 "可归档" 和 "未完成" 的分类建议

### 6. verify-impl-consistency

**做什么**: 三维语义一致性诊断 — 深度验证文档/API Schema/集成测试与代码实现的一致性。

**核心机制**:
- 始终执行项目级扫描，检测到活跃 OpenSpec change 时追加增量验证
- 两种运行模式自动切换，无需用户选择

**三维检查模型**:

| 维度 | 检查内容 |
|------|---------|
| D1 - Doc ↔ Code | 从文档提取可验证声明（端点、函数名、参数等），与代码精确匹配 + 语义分析 |
| D2 - Schema ↔ API | 解析 OpenAPI/Swagger/Proto/GraphQL，与多语言路由定义交叉验证 |
| D3 - Tests ↔ Code | 从测试提取被测目标，验证存在性、场景覆盖和孤立测试 |

**分层验证策略**:
- **Layer 1 精确匹配**: Grep 模式匹配，快速分类 FOUND / NOT_FOUND / UNCERTAIN
- **Layer 2 语义分析**: Claude 阅读代码段，判定 ALIGNED / DRIFTED / CONFLICT

**多语言路由支持**: Express, Fastify, NestJS, FastAPI, Flask, Django, Gin, Echo, Spring

**注意事项**:
- 纯诊断工具，**不修改任何文件**，不做 pass/fail 判定
- 需要 Claude 语义理解能力（不设置 `disable-model-invocation`）
- 无 Schema 文件时 D2 自动跳过，无测试文件时 D3 自动跳过
- 与 `check-changes-completed` 互补：后者检查存在性，前者检查语义一致性

---

## 目录结构

```
my_dev_skills/
├── parall-new-proposal/SKILL.md
├── parall-new-worktree-apply/SKILL.md
├── new-worktree-apply/SKILL.md
├── merge-worktree-return/SKILL.md
├── check-changes-completed/SKILL.md
├── verify-impl-consistency/SKILL.md
├── setup-skills-env.py          # 环境配置脚本
└── setup-iterm2-claude-notify.py # iTerm2 通知配置
```

## 权限模型

所有 skill 的 `allowed-tools` 都遵循 `.claude/settings.local.json` 中定义的标准权限列表。`setup-skills-env.py` 负责生成和维护该列表。

关键权限包括：
- `Bash(openspec *)` — OpenSpec CLI 操作
- `Bash(git *)` — Git 操作（add, commit, merge, rebase, worktree 等）
- `Bash(mkdir -p /tmp/my-dev-skills-wt)` — worktree 临时目录
- `mcp__web-reader__webReader` — Web 读取

> 注意：`git push`, `git checkout`, `git rebase` 等虽有权限白名单，但各 Skill guardrails 明确禁止使用 --force 标志。
