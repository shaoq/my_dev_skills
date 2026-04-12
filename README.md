# my_dev_skills - 使用指南

基于 OpenSpec 工作流的 Claude Code Skills 集合，提供从需求分析到并行实施、归档的完整开发流水线。

## 依赖项

| 依赖 | 说明 | 检查方式 |
|------|------|---------|
| **git** | 版本控制 | `git --version` |
| **OpenSpec CLI** | 工作流引擎，管理 change/artifact 生命周期 | `openspec --version` |
| **Claude Code** | 运行环境（CLI / Desktop / IDE） | 内置 |
| **Python 3.6+** | 仅 `setup-skills-env.py` 需要 | `python3 --version` |
| **iTerm2** (可选) | `setup-iterm2-claude-notify.py` 需要 | macOS only |

## 环境初始化

```bash
# 首次使用，运行配置脚本：
python3 setup-skills-env.py
```

该脚本自动完成：
1. 扫描根目录 `*/SKILL.md`，在 `.claude/skills/` 创建符号链接
2. 生成 `.claude/settings.local.json`（权限白名单）
3. 交叉校验 SKILL.md 的 `allowed-tools` 与标准权限列表一致性

### iTerm2 通知（可选）

```bash
python3 setup-iterm2-claude-notify.py    # 安装通知触发器
python3 setup-iterm2-claude-notify.py --check  # 检查状态
```

> 运行前请关闭 iTerm2，或运行后重启使其生效。

---

## Skills 一览

### 核心 Skills（根目录 `*/SKILL.md`）

| Skill 名称 | 调用方式 | 用途 | 参数 |
|------------|---------|------|------|
| **parall-new-proposal** | `/parall-new-proposal` | 并行提案拆分 | 需求描述文本 |
| **parall-new-worktree-apply** | `/parall-new-worktree-apply` | 并行实施多个 changes | 无（自动发现） |
| **new-worktree-apply** | `/new-worktree-apply` | 单个 worktree 实施 | `<proposal-name> [--branch <name>]` |
| **merge-worktree-return** | `/merge-worktree-return` | worktree 合并回主干 | `[proposal-name]` |
| **check-changes-completed** | `/check-changes-completed` | 四维完成度检查 | 无 |

### 基础命令（`.claude/commands/opsx/`）

| 命令 | 调用方式 | 用途 | 参数 |
|------|---------|------|------|
| **opsx:explore** | `/opsx:explore` | 思考/探索模式 | 可选话题 |
| **opsx:propose** | `/opsx:propose` | 创建单个 change 及其 artifacts | `<name>` 或描述 |
| **opsx:apply** | `/opsx:apply` | 实施 change 的任务 | `[change-name]` |
| **opsx:archive** | `/opsx:archive` | 归档已完成的 change | `[change-name]` |

---

## 使用顺序与流程

### 典型流程：从需求到归档

```
需求描述
   │
   ▼
┌─────────────────────────────┐
│  /opsx:explore <topic>      │  ← 可选：先探索思考
│  理解问题、分析方案          │
└──────────────┬──────────────┘
               │
               ▼
        ┌──────┴──────┐
        │  需求规模?   │
        └──────┬──────┘
        ≤2 个子方案  │  ≥3 个子方案
               │      │
               ▼      ▼
     /opsx:propose   /parall-new-proposal
     (逐个创建)      (批量拆分+依赖图)
               │      │
               ▼      ▼
     ┌─────────┴──────┴─────────┐
     │    proposals 已创建       │
     │    dependencies.yaml 已注入│
     └───────────┬──────────────┘
                 │
           ┌─────┴─────┐
           │ changes 数量│
           └─────┬─────┘
           =1    │    ≥2
           │     │     │
           ▼     │     ▼
  /new-worktree-apply│  /parall-new-worktree-apply
  (单个 worktree 实施)│  (并行 worktree 实施)
           │     │     │
           ▼     │     ▼
  /merge-worktree-return│  自动合并回主干
           │     │     │
           ▼     ▼     ▼
     /check-changes-completed
     (四维完成度检查+自动补标记)
                 │
                 ▼
           /opsx:archive
           (逐个归档)
```

### 何时用哪个 Skill

| 场景 | 推荐 Skill |
|------|-----------|
| 还不清楚要做什么，想先探讨 | `/opsx:explore` |
| 明确的小需求（1-2 个子功能） | `/opsx:propose` → `/new-worktree-apply` |
| 综合性大需求（3+ 子功能） | `/parall-new-proposal` → `/parall-new-worktree-apply` |
| 已有 proposal 需单个实施 | `/new-worktree-apply <name>` |
| 已有多个 proposal 需并行实施 | `/parall-new-worktree-apply` |
| worktree 实施完毕要合并 | `/merge-worktree-return [name]` |
| 想看所有 change 的完成状态 | `/check-changes-completed` |
| 确认完成后归档 | `/opsx:archive <name>` |

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
- 超过 8 个时会警告粒度可能过细
- 循环依赖会直接报错，需调整拆分方案
- **必须用户确认**后才会创建提案
- 内部循环调用 `/opsx:propose` 创建 artifacts

### 2. parall-new-worktree-apply

**做什么**: 自动发现所有待执行 changes，按依赖图分 Wave 并行实施。

**核心机制**:
- 自动扫描 `openspec/changes/` 下有未完成 `[ ]` 任务的 change
- 解析 `dependencies.yaml` 构建依赖图
- 同一 Wave 内的 changes 通过 Agent 在隔离 worktree 中并行 spawn
- 串行合并回主干（按字母序）
- 冲突智能解决（非重叠自动合并、语义可合并、无法解决则跳过）

**注意事项**:
- **必须在主分支上执行**，否则报错
- 待执行 changes = 0 时直接退出
- 待执行 changes = 1 时走简化路径（直接 apply，不 spawn Agent）
- Agent spawn 必须在同一消息中并行
- 合并必须串行，每个分支合并完再处理下一个
- artifacts 不完整的 change 会被跳过
- 失败的 Agent/分支不阻塞其他

### 3. new-worktree-apply

**做什么**: 为单个 proposal 创建 git worktree 并在其中实施。

**核心机制**:
- 验证 proposal artifacts 完整性
- 通过 `EnterWorktree` 工具创建隔离分支
- 调用 `/opsx:apply` 实施任务
- Post-apply 自动补标记（四规则检测）+ 强制提交 `tasks.md`

**注意事项**:
- 分支名必须符合 worktree 命名规则（kebab-case，max 64 chars）
- 若分支已存在则报错停止，**不覆盖**
- `openspec/` 在 `.gitignore` 中，`tasks.md` 需 `git add -f` 强制添加
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

**做什么**: 四维完成度检查 + 智能补标记。

**四维检查模型**:

| 维度 | 检查内容 |
|------|---------|
| D1 - Tasks | `tasks.md` 中 `[x]` vs `[ ]` 计数 |
| D2 - Artifacts | `openspec status --json` 的 artifact 状态 |
| D3 - Code 落地 | 产出文件是否存在 + git commits |
| D4 - 依赖 | `dependencies.yaml` 引用的 change 完整性 |

**补标记机制**（当 D3=✓ 但 D1=✗ 时触发）:
- **Level-1 自动**: 四规则解析器（反引号路径、目录创建、frontmatter、实现关键词）
- **Level-2 需确认**: 自动无法匹配但 code 已交付时，询问用户

**注意事项**:
- 只修改 D3 通过但 D1 未通过的 `tasks.md`，其他 artifact 严格只读
- Level-1 自动无需确认，Level-2 需用户确认
- 检测循环依赖，防止无限递归
- 输出结果包含 "可归档" 和 "未完成" 的分类建议

---

## 目录结构

```
my_dev_skills/
├── .claude/
│   ├── commands/opsx/          # 基础命令（explore, propose, apply, archive）
│   ├── skills/                  # 符号链接指向根目录各 skill
│   ├── settings.local.json      # 权限白名单（自动生成）
│   └── worktrees/               # git worktree 临时目录
├── openspec/
│   └── changes/                 # 所有 change proposals
│       ├── <change-name>/       # 活跃的 change
│       │   ├── proposal.md
│       │   ├── design.md
│       │   ├── tasks.md
│       │   ├── specs/
│       │   └── dependencies.yaml  #（有依赖时）
│       └── archive/             # 已归档的 changes
├── parall-new-proposal/SKILL.md
├── parall-new-worktree-apply/SKILL.md
├── new-worktree-apply/SKILL.md
├── merge-worktree-return/SKILL.md
├── check-changes-completed/SKILL.md
├── setup-skills-env.py          # 环境配置脚本
├── setup-iterm2-claude-notify.py # iTerm2 通知配置
└── .gitignore                   # 忽略 .claude/ 和 openspec/
```

## 权限模型

所有 skill 的 `allowed-tools` 都遵循 `.claude/settings.local.json` 中定义的标准权限列表。`setup-skills-env.py` 负责生成和维护该列表。

关键权限包括：
- `Bash(openspec *)` — OpenSpec CLI 操作
- `Bash(git *)` — Git 操作（add, commit, merge, rebase, worktree 等）
- `Bash(mkdir -p /tmp/my-dev-skills-wt)` — worktree 临时目录
- `mcp__web-reader__webReader` — Web 读取

> 注意：`git push`, `git checkout`, `git rebase` 等虽有权限白名单，但各 Skill guardrails 明确禁止使用 --force 标志。

## .gitignore 说明

```
.claude/
openspec/
```

这意味着 `openspec/` 下的 `tasks.md` 等文件不会被常规 `git add -A` 追踪。各 skill 通过 `git add -f openspec/changes/<name>/tasks.md` 强制添加关键文件。
