# my_dev_skills - 使用指南

面向 Claude Code 与 Codex 的研发 Skills 集合，覆盖复杂架构研究与决策，以及从 OpenSpec 需求分析、提案审查到隔离实施、合并和归档的完整开发流水线。

## 安装

```bash
# 1. 克隆仓库
git clone git@github.com:shaoq/my_dev_skills.git
cd my_dev_skills

# 2. 全局安装（双端符号链接 + Claude Code 权限合并）
python3 setup-skills-env.py

# 卸载（移除全局符号链接和权限，不影响本仓库）
python3 setup-skills-env.py --uninstall
```

> **重要**：Skills 通过符号链接同时安装在 `~/.claude/skills/` 和 `~/.codex/skills/`，指向同一份仓库源文件。安装器只合并 `~/.claude/settings.json` 权限，不创建或覆盖 Codex 配置。
> **不要删除或移动本仓库目录**，否则所有项目中已安装的 Skills 将失效。

### 依赖项

| 依赖 | 说明 | 检查方式 |
|------|------|---------|
| **git** | 版本控制 | `git --version` |
| **OpenSpec CLI** | 工作流引擎，管理 change/artifact 生命周期 | `openspec --version` |
| **Claude Code 或 Codex** | Skill 运行环境 | 对应产品内置 |
| **Python 3.9+** | `setup-skills-env.py` 和测试需要 | `python3 --version` |
| **iTerm2** (可选) | `setup-iterm2-claude-notify.py` 需要 | macOS only |

### iTerm2 通知（可选）

```bash
python3 setup-iterm2-claude-notify.py           # 安装 iTerm2 + Claude Code + Codex 通知
python3 setup-iterm2-claude-notify.py --check  # 检查状态
python3 setup-iterm2-claude-notify.py --remove # 卸载受管配置
```

> 安装内容：
> 1. iTerm2 Notification Center alerts：统一承接通知中心提醒
> 2. Claude Code hooks：完成提醒（`Stop`）、权限提醒（`permission_prompt`）、退出感知（`SessionEnd`），走 iTerm2 `notify`
> 3. Claude `preferredNotifChannel`：受管切换为 `notifications_disabled`，关闭内建 60 秒 idle 提醒
> 4. Codex `[tui]` 通知：approval prompts + completed turns，走 iTerm2 `notify`
> 5. tmux passthrough：在 iTerm2 内启动 tmux 后仍可继续通知
>
> 运行前请关闭 iTerm2，或运行后重启使其生效。
>
> 说明：
> - 受管路径为 notify-only，不再安装 `BellTrigger`，也不再依赖 BEL 提醒
> - Claude 完成提醒默认只保留 `Stop` 作为用户提醒来源；`Notification(idle_prompt)` 即使被 Claude 事件层触发，也会被受管 helper 直接抑制
> - Claude 内建 `preferredNotifChannel` 会受管设置为 `notifications_disabled`，避免 60 秒后再收到第二次等待输入提醒
> - 运行时 helper 内置去重逻辑，防止重复 `Stop` 投递和旧版遗留 `idle_prompt` 再次提醒
> - `/exit` 和 `/clear` 退出时不会触发完成提醒（通过 `SessionEnd` hook 感知退出语义）
> - 当前焦点 iTerm2 session 完成时不弹通知，后台 session 仍正常提醒（精确 tty 比较）
> - 焦点 session 抑制在 tmux 下自动降级：无法可靠判断时仍发送提醒
> - 若 `--check` 仍提示存在旧版受管 trigger 或 idle_prompt，重新执行安装会自动迁移
>
> 受管链路边界：
> - 退出抑制和焦点 session 抑制仅对受管 Claude hooks 生效，不处理用户自定义的非受管 hooks
> - 该安装器只消除 Claude 内建通知与受管 helper 的重复，不保证消除所有非受管第三方通知
> - `SessionEnd` 受管 hook 仅用于退出语义识别，不直接发送用户通知
>
> 升级说明：
> - 从旧版升级后，需重启 Claude Code 会话以使新 hooks 生效
> - 重装时安装器会自动移除旧版受管 `idle_prompt` hook group
> - 新增 `SessionEnd` 受管 hook，安装后 `--check` 会显示其安装状态
> - 新增 `preferredNotifChannel` 受管状态，安装后 `--check` 会显示 Claude 内建通知通道是否已禁用
> - 注意：Claude 内建通知通道属于全局配置库 `~/.claude.json`，不属于 hooks 所在的 `~/.claude/settings.json`

---

## 快速开始

> Skills 以符号链接形式安装到 `~/.claude/skills/` 和 `~/.codex/skills/`，一次安装后两个运行时的所有项目通用。
> 前提：本仓库目录需保留在原地，不可删除或移动。

### 场景 0：复杂架构设计（研究 → 评审 → 人工批准 → 发布/交接）

适用于：复杂架构升级、全新系统、跨系统混合方案、独立架构评审或架构到研发的正式交接。

```text
/architecture-design-workflow    # Claude Code
$architecture-design-workflow    # Codex

→ 先确认 Subject Project、设计类型和运行时依赖
→ 研究与架构设计阶段不创建 OpenSpec artifacts
→ ARCH-DESIGN 经独立 ARCH-REVIEW 后等待明确的人类门禁
→ approved_design_only 只发布 ADR/详细设计
→ approved_for_spec 额外生成 ARCH-RD-HANDOFF，由目标 R&D Team 自行决定是否创建 OpenSpec
→ 普通 bug、已批准 change 实施和代码 Review 不触发本流程
```

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

Step 2: 逐个审查待实施提案
─────────────────────────────
  /openspec-review-change <change-name>     # Claude Code
  $openspec-review-change <change-name>     # Codex

  → 只读审查目标、设计、Specs、追踪性和任务就绪度
  → BLOCKED / NEEDS_REVISION 时先修订，READY 后再实施

Step 3: 并行实施所有提案
─────────────────────────────
  /parall-new-worktree-apply

  → 自动发现所有待执行的 changes
  → 要求确认的目标分支已由 clean worktree 持有，不切换或自动提交它
  → 按 Wave 并行从冻结 commit hash 创建 `worktree-<proposal>`，在隔离 worktree 中实施
  → 串行合并冻结的 post-rebase commit；验证或普通清理失败时保留来源现场

Step 4: 检查完成度（按 target 分组）
─────────────────────────────
  /check-changes-completed --target develop --change change-a --change change-b

  → 五维检查（任务 / artifacts / 代码落地 / 依赖 / 合规）
  → 默认只读报告可回填项；加 `--backfill` 才补标记
  → 输出"可归档"和"未完成"清单

Step 5: 归档已完成的 change
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

Step 1: 实施前只读审查
─────────────────────────────
  /openspec-review-change add-user-auth                    # Claude Code
  $openspec-review-change add-user-auth                    # Codex
  /openspec-review-change add-user-auth --openspec-root twin-rag

  → 严格校验 OpenSpec artifacts 并执行语义、事实和任务就绪度审查
  → 首版完整支持 spec-driven；非支持 Schema 失败关闭

Step 2: 在 worktree 中实施
─────────────────────────────
  /new-worktree-apply add-user-auth --target develop                    # Claude Code
  $new-worktree-apply add-user-auth --target develop                    # Codex
  /new-worktree-apply add-user-auth                                    # inferred target，确认后执行
  /new-worktree-apply add-user-auth --target develop --openspec-root twin-rag
  $new-worktree-apply add-user-auth --target develop --dry-run

  → 显式 target 直接走确定性路径；省略时按共享优先级推断并展示完整计划确认一次
  → 目标必须已由 clean worktree 持有，并冻结 `TARGET_HEAD`
  → `--openspec-root twin-rag` 精确选择 `twin-rag/openspec/changes/add-user-auth`
  → 显式命令、明确自然语言、Team/subagent 或其他 Skill 都可传递有限实施意图；调用来源不会扩大授权范围
  → 显式 target 完整预检和最终复检稳定后直接执行；推断 target 确认后再复检；`--dry-run` 始终只读且不确认写入
  → 验证 commit 中完整仓库相对 artifacts 与预检快照完全一致
  → 从该 hash 创建 `worktree-add-user-auth` → 执行实施 → 补标记 → 提交

Step 3: 合并回目标分支
─────────────────────────────
  /merge-worktree-return add-user-auth --target develop  # 显式 target + clean source：不二次确认
  /merge-worktree-return add-user-auth                   # inferred target：展示完整计划并确认

  → 明确 return 请求 + 显式 `--target` + clean source 经独立最终复检后直接执行
  → inferred target 或 dirty source 保留一次 interactive compatibility plan；dirty source 逐项展示待提交文件
  → rebase 后冻结 `POST_REBASE_SOURCE_HEAD` → 目标只合并该 hash
  → 仅在完整 `CLEANUP_READY` 为 true 时普通清理；否则保留 worktree 和 branch

Step 4: 检查完成度
─────────────────────────────
  /check-changes-completed --target develop --change add-user-auth

  → 显式选择集 + 冻结目标基线 + 五维检查 + 安全补标记

Step 5: 归档
─────────────────────────────
  /opsx:archive add-user-auth
```

---

## Skills 一览

### 核心 Skills（根目录 `*/SKILL.md`）

| Skill 名称 | 调用方式 | 用途 | 参数 |
|------------|---------|------|------|
| **architecture-design-workflow** | Claude Code: `/architecture-design-workflow`<br>Codex: `$architecture-design-workflow` | 受控架构研究、设计、评审、发布与研发交接 | 架构需求或当前 `ARCH-*` 状态 |
| **parall-new-proposal** | `/parall-new-proposal` | 并行提案拆分 | 需求描述文本 |
| **openspec-review-change** | Claude Code: `/openspec-review-change`<br>Codex: `$openspec-review-change` | 实施前只读提案审查 | `[change-name] [--openspec-root <repo-relative-path>]` |
| **parall-new-worktree-apply** | `/parall-new-worktree-apply` | 并行实施多个 changes | `[--target <target-branch>]` |
| **new-worktree-apply** | `/new-worktree-apply` / `$new-worktree-apply` | 单个 worktree 实施 | `<proposal-name> [--target <branch>] [--openspec-root <path>] [--dry-run]` |
| **merge-worktree-return** | `/merge-worktree-return` | worktree 合并回目标分支 | `[proposal-name] [--target <target-branch>]` |
| **check-changes-completed** | `/check-changes-completed` | 目标感知的五维完成度检查 | `--target <branch> --change <name> [--change <name> ...]` |
| **verify-impl-consistency** | `/verify-impl-consistency` | 三维语义一致性诊断 | `[<change-name> --base <target-branch>]` |

---

## 使用流程图（参考）

```
需求描述
   │
   ▼
┌─────────────────────────────┐
│  是否为复杂架构决策？        │
└──────────────┬──────────────┘
       是      │      否/普通研发
       │       │
       ▼       ▼
/architecture-design-workflow  /opsx:explore
       │                       （可选）
       ▼
ARCH-RESEARCH → ARCH-DESIGN → ARCH-REVIEW
       │
       ▼
明确人类门禁：approved_design_only / approved_for_spec
       │                              │
       ▼                              ▼
ADR + 详细设计                 ARCH-RD-HANDOFF
                                      │
                                      ▼
                         目标 R&D Team 自行决定是否创建 OpenSpec

普通研发/OpenSpec 路径：
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
            ▼
 /openspec-review-change <change>
 (只读门禁：BLOCKED / NEEDS_REVISION /
  READY_WITH_WARNINGS / READY)
            │
      ┌─────┴─────┐
      │ changes 数量│
      └─────┬─────┘
      =1    │    ≥2
      │     │     │
      ▼     │     ▼
/new-worktree-apply  /parall-new-worktree-apply
(冻结 TARGET_HEAD)   (冻结 BATCH_TARGET_HEAD)
      │     │     │
      ▼     │     ▼
/merge-worktree-return  并行 Controller
(source=worktree-<proposal>)  (每个 worktree-<proposal>)
      │     │     │
      ▼     │     ▼
冻结 POST_REBASE_SOURCE_HEAD 并串行 exact-hash merge
      │     │     │
      ▼     ▼     ▼
CLEANUP_READY=true 才普通清理；否则保留来源
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

### 0. architecture-design-workflow

**做什么**：把复杂架构研究、方案设计、独立评审、人工批准、架构发布和研发交接组织成独立于 OpenSpec 实施的受控流程。

**适用范围**：

- 复杂架构升级、全新系统、跨系统 hybrid 方案
- 独立架构 Review、ADR/详细设计发布
- 经批准后向目标研发项目生成 `ARCH-RD-HANDOFF`

普通 bug 调查、状态跟进、已批准 OpenSpec change 的实施、源码 Review 和无架构影响的局部重构不触发本 Skill。

**核心机制**：

- canonical 主路径为 `intake → routed → researching → designing → reviewing → waiting_human`；`ARCH-DESIGN-vN.md` 是唯一 mandatory Design 和唯一 human-canonical 总体方案
- current writer 分离 `human_review_surface_v1` 与 `architecture_internal_evidence_v1`：人类只看一份 Design、成熟度、简短 Review/风险/推荐和一个 Action；Research、Control、完整 Review、machine-only Packet、continuation/handoff/readback、retry 和 reconciliation 保存在内部证据
- Design maturity 为 `directional|spec_ready|implementation_ready`；`directional` 禁止 `approved_for_spec`，后两者保留各自的 OpenSpec handoff/直接实施指导边界
- Reviewer approvable 后生成 machine-only immutable `ARCH-APPROVAL-PACKET` manifest 并取得 readiness evidence；current Action 继承准确 snapshot，Owner 无需人工打开 Review、Packet、Control 或复制 packet digest
- 用户明确开始、继续或重试当前阶段时建立平台无关的 `architecture_workflow_mandate_v2`；`v1` 只读审计；准备、交付、访问验证、状态、retry 和审计自动完成，只有 `design_input|architecture_review|architecture_approval` 的真实方案决定暂停等待人类
- `openspec-explore` 是研究阶段必需依赖；只有目标、边界、约束或方案空间存在实质歧义时才要求 `superpowers:brainstorming`
- 依赖缺失时保持当前 stage，记录稳定 `BLOCKED_REASON` 并 fail-closed；不自动安装依赖，也不修改 Runtime 配置
- Review 只允许 `BLOCKED`、`NEEDS_REVISION`、`APPROVABLE_WITH_WARNINGS`、`APPROVABLE`；Review 结论、packet readiness 和 `ARCHITECTURE_RECOMMENDATION` 都不等于人类批准
- 人工 gate 只接受准确 Decision Owner 针对 current Action 的 `approved_design_only`、`approved_for_spec`、`revision_requested` 或 `rejected`；owner-attested 仍要求 `materials_opened`
- 新输入先生成 `architecture_design_impact_v1`：无架构影响只更新内部 evidence；有影响或 unknown 新建 Design/Review 并 supersede Action/manifest
- complex Design 默认使用 Archify Architecture 总览图；required visual 只有 deliver/browser/visual/semantic 四项全部通过才可进入正式 Review，light/1440×900 preview 必须来自同一成功 receipt
- standalone `local_file` profile 要求当前人类确认 shared workspace scope；仅 Agent 能读取本地路径时保持 `reviewing` 并记录 `review_packet_unavailable`
- 发布前重新验证 packet/design/review 原始 bytes；不匹配时保持 `publishing` 和原批准，记录 `approved_artifact_unavailable`，禁止从审核简报重建近似正文
- `approved_design_only` 只发布 ADR 和详细设计；`approved_for_spec` 额外生成 `ARCH-RD-HANDOFF`，但 Architecture workflow 本身不创建 OpenSpec proposal
- 只读或 plan 会话可以生成完整待发布内容，但 stage 保持 `publishing`；只有产物实际持久化并验证后才能报告终态
- 升级前已经持久化的 `waiting_human` 记录不自动降级或伪造 readiness；显式 refresh 或新 design/review version 后执行新 packet gate
- 旧三附件 attempt 只读保留，绝不原地转换为新单 Design Action

**调用与角色边界**：

- Claude Code 使用 `/architecture-design-workflow`，Codex 使用 `$architecture-design-workflow`；明确自然语言架构请求也可自动路由
- Skill 不设置模型覆盖，使用调用方当前模型；不要求 Team 驱动，普通 Codex/Claude Code 会话可以直接执行
- Architecture Lead、Analyst、Solution Architect、Reviewer 和目标 R&D Team 是责任边界，不代表必须创建对应 Team/Agent
- 不隐式创建仓库、Project、Issue、Team、Agent、watchdog、worktree、branch 或 commit
- 涉及现有代码事实、调用链、影响或调试时 GitNexus-first；索引陈旧时先重建

**验证**：

```bash
bash tests/architecture-design-workflow-safety.sh
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime codex
bash tests/architecture-design-workflow-safety.sh --results-dir tests/evidence/architecture-design-workflow --runtime claude
python3 -m unittest tests/test_architecture_design_workflow_runner.py
```

上述 core contract 使用同一仓库源、Markdown artifacts 和 portable evidence，可在没有 Multica adapter 的 Claude Code/Codex 环境通过 shared local files 独立运行；不会要求强制 renderer、附件或评论字段。

### 0.1 multica-architecture-approval-adapter

**做什么**：这是 `architecture-design-workflow` 的独立 sibling skill，用于把已经交付、兼容且仍为 current 的 `ARCH-APPROVAL-PACKET` 映射到一个已明确指定的既有 Multica Issue。它不改变 core 状态机，也不使 Multica 成为 core 的安装或触发依赖：只安装 core 时，standalone profile 仍可工作；adapter 只有在已提供 compatible packet、既有 workspace/Issue 以及当前任务明确要求 Issue delivery 时才触发。

**审核材料**：adapter 评论展示 Design 版本/maturity、简短 Reviewer conclusion/findings、Architecture Team recommendation 及中文理由/风险、一个 current Action 和四种决定后果，并且恰好附带一份 canonical Design Markdown。无需人工打开 Review、Packet、Control 或 Research；它们通过 `architecture_internal_evidence_v1` 回读。PDF、Archify HTML 与 receipt-bound preview 均为 `derived_non_authoritative` supporting resources。

**Archify 角色最小化**：四个 Archify 目标 Agent 是 Architecture Team 的 Solution Architect（author）、Architecture Reviewer（review-only），以及 R&D Team 的 Product & Spec Engineer（conditional author）、Solution Review Architect（review-only）。其他 Lead/Analyst/Development/Code Review/QA/Integration/Watchdog 默认不绑定。required visual 的 `deliver=passed`、`browser_evidence=passed`、`visual_review=passed` 和 semantic findings closed 任一不满足都 fail closed。

仓库内可复用配置源见 [unidocs-rag Architecture/R&D Team profile](multica-architecture-approval-adapter/deployment-profiles/unidocs-rag-architecture-rd-teams.yaml)。它记录 `allen@qq.com` / `unidocs-rag` 的 Team/Agent 名称、四个目标 Agent 的 author/review-only 指令、非目标 Agent、版本/digest 和 conflict-fail + additive 重新导入顺序；文件不含凭据，也不会自行写入真实 workspace。

**安全边界**：adapter 从 current mandate 自动派生 immutable `architecture_operation_manifest_v1`，冻结目标、输入/输出 digest、ordered writes、postconditions、retained objects 与 retry/supersession。任一事实不确定时输出 unavailable evidence 并保留对象；不猜测、不删除、不编辑历史，也不要求用户批准内部操作。Recommendation、Review conclusion、metadata、reaction、Issue status 和 Agent/system 评论均不构成人工批准。

**激活不是普通 Issue delivery 的副作用**：只有用户明确要求“实施并激活”或等价任务时才建立 activation mandate，对指定既有 workspace/Agent 执行 conflict-fail import、additive binding 和逐 Agent readback。仓库安装不修改真实用户 home；可在隔离临时 HOME 验证 Claude/Codex 链接 bytes。旧三附件 attempt 只读，兼容 pair 和 Archify binding 只对新 attempt 生效。详见 [activation runbook](multica-architecture-approval-adapter/references/activation-runbook.md)、[Archify Agent bindings](multica-architecture-approval-adapter/references/archify-agent-bindings.md) 与 [sandbox acceptance checklist](multica-architecture-approval-adapter/references/sandbox-acceptance-checklist.md)。

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

### 2. openspec-review-change

**做什么**: 在 change 进入 apply 前，只读审查 OpenSpec 提案质量与实施就绪度。

**核心机制**:
- 读取当前 `spec-driven` Schema 的 `status`、artifact `instructions` 和安全展开后的实际文件
- 运行 `openspec validate --strict`，并继续检查目标范围、项目事实、设计、Spec 可测试性、跨 artifact 一致性、追踪链和任务颗粒度
- 输出 `BLOCKED`、`NEEDS_REVISION`、`READY_WITH_WARNINGS` 或 `READY`，每个 finding 包含证据、实施影响和修改建议
- 支持仓库根或显式 `--openspec-root <repo-relative-path>` 嵌套项目
- Codex 使用 `$openspec-review-change`，Claude Code 使用 `/openspec-review-change`；两端复用同一份 `SKILL.md`

**注意事项**:
- 默认严格只读；即使同一请求要求“review 并修复”，也先返回稳定证据快照并要求独立修订流程
- 首版只完整支持 `spec-driven`，其他 Schema 返回 `BLOCKED`
- 部分实施或 tasks 全部完成的 active change 仍可审查，但会声明当前工作树不是实施前基线
- 不替代 `verify-impl-consistency` 的实现一致性诊断，也不替代归档完成度检查

### 3. parall-new-worktree-apply

**做什么**: 自动发现所有待执行 changes，按依赖图分 Wave 并行实施。

**核心机制**:
- 目标分支按"显式 `--target` → 主工作树当前分支 → `origin/HEAD` 本地同名分支 → `main`/`master`/`trunk`"选择，并且必须已由唯一、干净的注册 worktree 持有
- 自动发现有未完成 `[ ]` 任务的 change
- 在创建前从冻结 target commit 递归验证 `.openspec.yaml`、proposal/design/tasks、全部 delta specs 和实际使用的 `dependencies.yaml` 路径及内容完全一致
- 解析已经通过 manifest 验证的 `dependencies.yaml` 构建依赖图
- 只读预检（Discovery + 依赖图 + 目标/工作树状态）后展示完整计划，**等待用户明确确认**，确认后复检快照才执行写操作
- 不 checkout/switch 或 Auto-commit 主工作树和其他现有 worktree；目标 dirty 或映射漂移时失败关闭
- Agent spawn 前控制器持久进入目标工作树；控制器用 `EXPECTED_TARGET_HEAD` 只接纳自身已验证 merge 的推进
- 同一 Batch 共享冻结的 `BATCH_TARGET_HEAD`，每个 child 使用规范 branch `worktree-<proposal>` 和 `.claude/worktrees/<proposal>`，从该 commit hash 显式创建
- 串行合并前在 child 中 rebase 并冻结 `POST_REBASE_SOURCE_HEAD`，目标只 merge 该 hash，不 merge 可继续移动的 source branch ref
- Worker 和 Controller 对每个 child 独立分类任务：普通未完成任务阻止交付；精确 `[post-merge-verification]` 任务由用户后续在 target 执行，流程不执行、不勾选、不提交
- 每个 child 独立执行 post-merge checks 和 `CLEANUP_READY`；全部为 true 才普通移除 worktree 并安全删除本地 branch
- 只有延期任务的 child 在结构性交付通过后可清理、推进 `EXPECTED_TARGET_HEAD` 和依赖 Wave，但 proposal 保持 incomplete / non-archivable，最终摘要列出用户待办
- 冲突只在当前 rebase 内处理；无法可靠解决时 abort 未完成 rebase 并保留来源

**注意事项**:
- **所有 Git 写操作只在显式确认之后执行**；拒绝/取消/模糊确认时不创建 worktree、不 spawn Agent、不 commit
- 待执行 changes = 0 时直接退出
- **即使只发现 1 个 change，也走隔离 worktree 实施 + 目标合并流程**（不再直接 apply）
- 每 Wave 最多 3 个并行 Agent，超出自动分 Batch 串行执行
- Agent spawn 必须在同一消息中并行（同一 Batch 内）
- 合并必须串行绑定目标分支，每个 Batch 完成后立即合并
- artifacts 不完整的 change 会被跳过
- 普通未完成任务或 task 分类 unknown 的 child 不合并、不清理，也不解锁依赖 Wave
- 失败或漂移的 Agent/分支不阻塞其他安全项，失败 worktree 与 branch 保留待人工处理
- merge 后验证失败不会自动 reset/revert，也不会换参数重试 merge
- 普通 cleanup 因 Windows 路径锁、进程占用或平台锁失败时保留现场并在报告中列出精确恢复对象

### 4. new-worktree-apply

**做什么**: 为单个 proposal 创建 git worktree 并在其中实施。

**核心机制**:
- 可由 Claude `/new-worktree-apply`、Codex `$new-worktree-apply`、明确自然语言、Team/subagent 或其他 skill 按实施意图路由；不设置 `model:`，始终继承调用方当前模型
- 目标分支按“显式 `--target` → 主工作树登记的命名本地分支 → `origin/HEAD` 本地同名分支 → `main`/`master`/`trunk`”选择；候选资格只看来源能否解析为现有本地 ref，显式目标无效不回退，选中候选后的 topology/identity/clean 检查失败也不尝试低优先级候选
- 调用路由、写入授权、工具权限和安全验证是独立控制：`allowed-tools` 只预批准工具，不决定模型或调用入口；GitNexus 等工具仍按正常 Runtime 权限流程使用
- 明确实施请求提供显式 target 时走 deterministic path，完整只读预检和最终复检稳定后不二次确认；推断 target 时走 interactive path，展示目标来源、冻结 hash 和完整写计划并确认一次；授权仅覆盖规范来源 worktree 创建、OpenSpec apply、proposal 范围本地验证和来源提交
- `--dry-run` 使用相同的 target、拓扑、source parent 物理包含、manifest 和计划写入预检，但不创建 branch/worktree、不 apply、不 stage、不 commit；其快照不能复用于后续真实调用
- 已移除 `--authorized-by-issue` 和 `issue-authorization/v1`：传入旧选项零写失败并提示改为上述显式调用；`--authorized`、`--yes` 等泛化批准选项也不是别名
- OpenSpec 项目根默认为仓库根 `.`；`--openspec-root twin-rag` 精确表示
  `twin-rag/openspec/changes/<proposal>`，可与 `--target` 任意排序且不会递归搜索、猜测或回退
- 目标分支必须已被一个注册且 clean 的 worktree 持有；流程不会为了满足目标条件切换或自动提交其他 worktree
- deterministic path 只冻结一次不可变 `PREFLIGHT_SNAPSHOT`；interactive path 为每次确认冻结带轮次的 snapshot 并指向最新确认轮次。最终写前复检逐字段比较；deterministic 漂移要求 fresh invocation，interactive 漂移先使旧确认失效，最新事实有 blocker 时停止，仍合法时才展示新计划并重新确认
- 规范映射固定为 proposal `<proposal>`、branch `worktree-<proposal>`、path `.claude/worktrees/<proposal>`；任何现有 ref/path/worktree 冲突都停止，不复用或追加后缀
- 从显式冻结的不可变 commit hash 精确创建：`git worktree add <path> -b worktree-<proposal> <TARGET_HEAD>`
- 创建前要求 `.claude/worktrees` 已作为仓库内的真实物理目录存在且没有父级符号链接逃逸，并递归验证完整 artifact manifest 已存在于 `TARGET_HEAD` 且与预检内容逐字节一致；创建后还须重新验证来源项目物理路径、OpenSpec 状态和 manifest，才从已验证项目目录 apply
- Post-apply 自动补标记（四规则检测）+ 强制提交 `tasks.md`

**注意事项**:
- **BREAKING**：旧 `--branch` 已由 `--target` 替代；传 `--branch` 时不产生任何 Git 写操作，只显示迁移命令
- 省略 `--openspec-root` 与显式 `--openspec-root .` 完全等价；非法、越界或符号链接逃逸路径均在确认前失败关闭
- 所有 Git 写操作只在不可变预检基线最终复检之后执行；deterministic path 漂移时零写并要求 fresh invocation；interactive path 漂移时旧确认失效并完整重检，若出现 blocker 就停止，只有仍为合法计划时才建立下一轮确认。两个路径都不自动换目标或重试
- 默认范围不授权 merge、发布、部署、生产写入、不可逆迁移、数据删除、提权、真实凭据或无关 Git 清理；proposal 要求此类动作时在动作前阻塞并交由独立授权流程
- 分支名必须符合 worktree 命名规则（kebab-case，max 64 chars）
- 若规范 branch/path 已存在则报错停止，**不覆盖、不复用、不自动清理**
- 即使目标 ref 在最后检查后推进，实际创建仍使用冻结 `TARGET_HEAD`，不会从未冻结的新 tip 创建
- 创建后验证注册 path、current branch、branch ref 与 worktree HEAD；任一不一致停止 apply 并保留现场

### 5. merge-worktree-return

**做什么**: 将 worktree 的改动 rebase + merge 回目标分支，然后退出 worktree。

**核心机制**:
- 目标分支按"显式 `--target` → 主工作树当前分支 → `origin/HEAD` 本地同名分支 → `main`/`master`/`trunk`"选择
- 只接受规范来源映射：当前 branch 必须是 `worktree-<proposal>`，当前 path 必须是 `.claude/worktrees/<proposal>`；返回流程只精确移除一个 `worktree-` 前缀反解 proposal
- 验证来源≠目标，目标已经由注册且 clean 的 worktree 持有；不会 checkout/switch 或自动提交其他 worktree
- 明确 return 请求使用显式 `--target` + clean source 时选择 deterministic path：展示完整计划，独立复检稳定后不请求第二次确认
- inferred target 或 dirty source 时选择 interactive path：展示目标来源、全部 pending 文件、commit/merge/cleanup 计划并等待一次明确确认
- 两个路径都使用不可覆盖的 `PREFLIGHT_SNAPSHOT` 与独立 `REVALIDATION_SNAPSHOT`；deterministic 漂移或冲突要求 fresh invocation，不能偷偷转为 interactive
- 在来源 worktree rebase 到授权并冻结的 target hash，随后冻结 `POST_REBASE_SOURCE_HEAD`；进入目标前重新验证 source/target 注册、branch、HEAD/ref 和 clean 状态
- 目标只执行一次 `git merge <POST_REBASE_SOURCE_HEAD>`，并记录 post-merge target hash
- 将未勾选任务分为普通任务与同一行带精确 `[post-merge-verification]` 标签的延期任务；普通任务阻止 cleanup，只有延期任务时允许在其他安全门通过后清理
- 延期任务由用户后续在 target worktree 执行；Skill 不执行、不勾选、不 stage、不 commit，并报告 proposal 仍为 incomplete / non-archivable
- 显式计算 `CLEANUP_READY`：目标真实 CWD、来源规范映射与 clean、delivery commits、source HEAD/ref 冻结、merge 成功、target ref/HEAD 一致、精确 containment、无 source-only commits和全部 post-merge 验证必须同时为 true
- 只有 `CLEANUP_READY=true` 才执行普通 `git worktree remove` 和安全 `git branch -d`

**注意事项**:
- 必须在 worktree 内运行，否则报错
- 目标工作树必须干净；来源 detached HEAD 或来源==目标时报错停止
- 普通未完成任务、延期任务清单、目标脏状态等风险并入同一 audit plan，不为单项风险追加确认
- deterministic path 仅授权 clean source；interactive path 才能在完整 pending-file plan 获确认后提交来源改动
- 未完成的 Rebase 无法解决时可 abort；成功 merge 后验证失败不自动 reset/revert
- 任一 post-merge 或 cleanup gate 失败时**不移除**来源 worktree/branch，也不自动重试 merge
- 普通 worktree removal 或安全 branch deletion 失败时保留现场；不升级为强制 ref 删除，也不删除远端分支

### 6. check-changes-completed

**做什么**: 五维完成度检查 + 智能补标记 + 项目合规检查。

**调用示例**:

```text
/check-changes-completed --target develop --change change-a --change change-b
/check-changes-completed --target release-next --change release-candidate
/check-changes-completed --target develop --change change-a --backfill
```

调用必须显式指定一个本地 target 和至少一个不重复的 active change。不同 target 的 changes 要
分组调用；未选择的 change 不扫描、不进入结论，也不会被回填。

**五维检查模型**:

| 维度 | 检查内容 |
|------|---------|
| D1 - Tasks | `tasks.md` 中 `[x]` vs `[ ]` 计数 |
| D2 - Artifacts | `openspec status --json` 的 artifact 状态 |
| D3 - Code 落地 | 产出文件是否存在 + git commits |
| D4 - 依赖 | `dependencies.yaml` 引用的 change 完整性 |
| D5 - 合规 | CLAUDE.md 定义的合规要求（测试同步/文档更新/API schema 等） |

默认调用严格只读，只报告补标记候选。只有恰好一个裸 `--backfill` 才授权所选 change 的确定性 task marker 写入；重复、带值或畸形参数在读取 artifacts 前失败。

**补标记机制**（`--backfill` 且 D3=✓、D1=✗ 时触发）:
- **Level-1 自动**: 四规则解析器（反引号路径、目录创建、frontmatter、实现关键词）
- **Level-2 需确认**: 自动无法匹配但 code 已交付时，询问一次；缺失、否定或模糊回答保持未完成

**合规检查机制**（D5 — 当项目有 CLAUDE.md 时触发）:
- 载入项目根目录和变更相关子目录中的 CLAUDE.md
- 提取合规要求（test-sync / doc-sync / api-schema-sync / changelog-sync）
- 将 target 与当前 HEAD 冻结为 `BASE_HEAD`/`CURRENT_HEAD`，通过同一
  `<BASE_HEAD>..<CURRENT_HEAD>` 范围验证提交和配套产出
- 缺失时不自动补全，仅提示建议运行 `/opsx:explore` 分析
- 无 CLAUDE.md 时不阻塞归档

**注意事项**:
- 默认零写；带 `--backfill` 时只修改选择集中 D3 通过但 D1 未通过的 `tasks.md`，其他 artifact 严格只读
- target 必须是 `CURRENT_HEAD` 的祖先；非祖先直接阻塞全部所选 changes，例如 feature 并非从
  `release-next` 派生时，`check-changes-completed --target release-next --change feature-change` 会失败，不会用 merge-base 猜测比较范围
- 最终写入前再次检查 target ref 和 current HEAD；任一漂移都丢弃回填计划，零 stage、零 commit，
  可存档状态报告为 unknown/blocked
- `--backfill` 已授权 Level-1，无需再次确认；Level-2 仍需用户明确确认
- D5 合规缺失仅提示，不自动补全配套产出
- 检测循环依赖，防止无限递归
- 输出结果包含 "可归档" 和 "未完成" 的分类建议

### 7. verify-impl-consistency

**做什么**: 三维语义一致性诊断 — 深度验证文档/API Schema/集成测试与代码实现的一致性。

**核心机制**:
- `/verify-impl-consistency`：只运行全仓项目级 D1/D2/D3，不自动选择 active change
- `/verify-impl-consistency add-auth --base develop`：仅为显式 change 增加 OpenSpec 增量验证
- 增量模式冻结本地 `develop` 和当前 HEAD 为 `BASE_HEAD`/`CURRENT_HEAD`，所有归因统一使用
  `<BASE_HEAD>..<CURRENT_HEAD>`；项目级扫描仍覆盖全仓

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
- 增量模式要求 target 是 current HEAD 的祖先；非祖先时项目级诊断继续，但增量维度明确标为
  `not executed`，例如 `verify-impl-consistency add-auth --base release-next` 在当前分支并非从 `release-next` 派生时不会回退 `main` 或替换成 merge-base
- 最终报告显示显式 change、target、冻结 commits、比较范围和 target/current 稳定性；漂移时
  保留冻结诊断并标记为 `stale evidence`
- 需要 Claude 语义理解能力（不设置 `disable-model-invocation`）
- 无 Schema 文件时 D2 自动跳过，无测试文件时 D3 自动跳过
- 与 `check-changes-completed` 互补：后者检查存在性，前者检查语义一致性

---

## 目录结构

```
my_dev_skills/
├── architecture-design-workflow/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   ├── references/
│   └── templates/
├── parall-new-proposal/SKILL.md
├── openspec-review-change/
│   ├── SKILL.md
│   ├── agents/openai.yaml
│   └── references/
├── parall-new-worktree-apply/SKILL.md
├── new-worktree-apply/SKILL.md
├── merge-worktree-return/SKILL.md
├── check-changes-completed/SKILL.md
├── verify-impl-consistency/SKILL.md
├── tests/
│   ├── architecture-design-workflow-safety.sh
│   ├── test_architecture_design_workflow_runner.py
│   ├── fixtures/architecture-design-workflow/
│   └── evidence/architecture-design-workflow/
├── setup-skills-env.py          # 环境配置脚本
└── setup-iterm2-claude-notify.py # iTerm2 通知配置
```

## 权限模型

声明了 `allowed-tools` 的 skill 会由 `setup-skills-env.py` 将 Bash 前缀与标准权限列表交叉校验。未声明该字段是合法的，表示工具调用走 Runtime 正常权限流程；它不代表禁用模型调用。安装器把标准列表合并到 `~/.claude/settings.json`；Codex 侧仅安装 skill 链接，不写入 Codex 配置。

关键权限包括：
- `Bash(openspec *)` — OpenSpec CLI 操作
- `Bash(git *)` — Git 操作（add, commit, merge, rebase, worktree 等）
- `Bash(mkdir -p /tmp/my-dev-skills-wt)` — worktree 临时目录
- `mcp__web-reader__webReader` — Web 读取

> 注意：权限白名单只表示命令可被调用，不代表任何 Skill 获得了额外授权。worktree lifecycle 流程不得为满足目标条件而 checkout/switch 其他会话持有的 worktree，不得 auto-commit 目标，也不得使用强制清理或自动回滚/重试作为恢复路径。
