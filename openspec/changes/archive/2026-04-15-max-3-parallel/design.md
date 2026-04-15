## Context

当前 `parall-new-proposal` 和 `parall-new-worktree-apply` 两个 skill 协同工作：前者负责规划阶段的拆解，后者负责执行阶段的并行实施。两者通过 `dependencies.yaml` 文件传递依赖信息，通过 Wave（拓扑排序分层）表达可并行关系。

现状问题：
- `parall-new-proposal` 的颗粒度阈值为 `3-8 正常 / >8 警告`，对拆分数量过于宽松
- `parall-new-worktree-apply` 在 Step 4.1 中"Wave 内所有 change 同时 spawn Agent"，无上限
- 实测中 4+ 并行 Agent 会导致 Claude API 并发瓶颈、git worktree I/O 竞争、合并冲突概率指数增长
- 串行合并阶段（Step 5）的耗时与 Agent 数量正相关，过多并行反而拖慢整体

涉及文件（均为 SKILL.md 纯文本，无代码逻辑）：
- `parall-new-proposal/SKILL.md`（规划阶段）
- `parall-new-worktree-apply/SKILL.md`（执行阶段）
- `README.md`（文档）

## Goals / Non-Goals

**Goals:**
- 将每 Wave 并行上限固定为 3，超出按字母序分 Batch 串行执行
- 采用方案 A（每个 Batch 完成后立即合并），降低合并冲突面
- 规划阶段（parall-new-proposal）即预览 Batch 划分，让用户在确认前看到真实执行计划
- 调整颗粒度阈值为 `2-6 正常 / >6 警告`，引导用户控制子方案数量

**Non-Goals:**
- 不引入动态并发度（根据负载自动调整），硬编码 MAX_PARALLEL = 3
- 不修改 `dependencies.yaml` 格式
- 不影响其他 skill（new-worktree-apply、merge-worktree-return 等）
- 不引入 Agent 级别的重试机制

## Decisions

### D1: 并发上限硬编码为 3

**选择**: 在 `parall-new-worktree-apply` Step 4 中硬编码 `MAX_PARALLEL = 3`

**备选方案**:
- A) 硬编码 3 — 简单可靠，3 是实测最佳值
- B) 可配置（从 CLAUDE.md 或环境变量读取）— 增加复杂度，当前无此需求

**理由**: 3 个并行 Agent 在大多数场景下能充分利用资源而不造成瓶颈，且合并冲突概率可控。用户明确要求 3。

### D2: 每个 Batch 完成后立即合并（方案 A）

**选择**: Batch → 等待 Agent → 合并 → 下一个 Batch

**备选方案**:
- A) 每 Batch 完成即合并 — 合并冲突面最小，main HEAD 推进更频繁
- B) 整个 Wave 全部完成后再合并 — 简单但合并压力大

**理由**: Wave 内各 change 本就无互相依赖，每个 Batch 完成后立即合并不会破坏依赖语义。且 main HEAD 推进后，后续 Batch 的 worktree rebase 基线更准确，冲突更少。

### D3: 规划阶段预览 Batch 划分

**选择**: 在 `parall-new-proposal` Step 3 新增 3.4（批次划分），Step 4.1 展示中包含 Batch 信息

**理由**: 让用户在确认拆解方案时就能看到真实的执行计划（几个 Wave、几个 Batch、每批几个），而非只在执行阶段才发现分批情况。

### D4: 颗粒度阈值调整

**选择**: `≤1 建议 /opsx:propose`、`2-6 正常`、`>6 警告`

**备选方案**: 保持 `≤2 建议 / 3-8 正常 / >8 警告`

**理由**: 用户要求 2-6 为正常范围。≤1 个子方案时并行无意义，建议直接用 `/opsx:propose`。

## Risks / Trade-offs

- **[Batch 间串行增加总时间]** → 缓解：每 Batch 最多 3 个，通常 1-2 个 Batch 即可完成一个 Wave，额外等待时间有限
- **[Wave 内存在隐式文件重叠]** → 缓解：三问判定框架已确保子方案独立性，分批合并进一步降低冲突风险
- **[后续若需调整并发上限]** → 缓解：MAX_PARALLEL 只出现在两个固定位置，修改成本低
