---
name: architecture-design-workflow
description: "Use when a substantial architecture upgrade, greenfield system, hybrid cross-system design, architecture review, ADR publication, or architecture-to-R&D handoff needs explicit evidence, versioning, and human gates. Do not use for routine bug triage, status follow-up, approved OpenSpec implementation, or source-code review."
---

# Architecture Design Workflow

## Overview

把复杂架构工作作为独立于 OpenSpec 实施的受控流程。先路由和研究，再形成可独立评审的版本化设计；只有可识别的人类针对准确版本记录明确门禁后，才能发布批准产物或生成研发交接。

所有面向用户的说明、问题、状态、评审和报告使用中文。命令、路径、canonical state、代码标识符、协议字段及引用原文保持准确原文。

## Hard boundaries

- 在 `researching`、`designing`、`reviewing` 和 design-only 发布中，不得创建或修改 OpenSpec proposal、design、specs、tasks 或实现产物。
- 不因紧急、负责人催促、Agent 推荐、任务分派或模糊肯定推断批准。
- 不隐式创建仓库、Project、Team、Agent、watchdog、研发 Issue、worktree、branch 或 commit。
- 不自动安装依赖 skill，不修改 Runtime 配置。
- Architecture workflow 只生成 `ARCH-RD-HANDOFF`；目标项目既有 R&D Team 自行分析需求并决定是否创建 OpenSpec change。

## Canonical control model

持久 stage 只能是：

```text
intake | routed | researching | designing | reviewing | waiting_human |
approved_design_only | approved_for_spec | publishing | handed_off |
completed_design_only | rejected
```

`revision_requested` 是决定，不是 stage。`waiting_human` 必须记录 `WAIT_REASON=design_approval|target_project`。依赖、证据或路由缺失时保持当前 stage，并记录 `BLOCKED_REASON`，不得创造 `blocked` 等近义 stage。

本工作流使用以下稳定 blocker：`missing_subject_project`、`missing_target_project`、`missing_openspec_explore`、`missing_brainstorming`、`critical_evidence_gaps`。没有 blocker 时记录 `none`；新的原因必须在控制契约中先定义，不能临时造同义值。

`BLOCKED_REASON` 与 Review conclusion 是两套独立字段。依赖、路由或证据 blocker 不得把 gate 改成 `BLOCKED`；只有实际完成一次架构评审并给出 canonical Review conclusion 时，gate 才能是 `BLOCKED|NEEDS_REVISION|APPROVABLE_WITH_WARNINGS|APPROVABLE`。依赖预检停止时 gate 保持 `none`。

关键转换：

| Current + evidence | Next |
|---|---|
| `intake + applicable + Subject Project missing` | `waiting_human`, `WAIT_REASON=target_project`, `BLOCKED_REASON=missing_subject_project` |
| `intake → routed → researching → designing → reviewing` | 正常主链 |
| `reviewing + BLOCKED` | 按 finding Owner 回到 `researching` 或 `designing` |
| `reviewing + NEEDS_REVISION` | 新版本 `designing` |
| `reviewing + APPROVABLE_WITH_WARNINGS|APPROVABLE` | `waiting_human`, `WAIT_REASON=design_approval` |
| `waiting_human + revision_requested` | 新版本 `designing` |
| `waiting_human + rejected` | `rejected`，终态 |
| `waiting_human + approved_design_only` | `approved_design_only → publishing → completed_design_only` |
| `waiting_human + approved_for_spec + target exists` | `approved_for_spec → publishing → handed_off` |
| `waiting_human + approved_for_spec + target missing` | 保留批准，`waiting_human`, `WAIT_REASON=target_project` |

每次合法转换都更新 [ARCH-CONTROL 模板](templates/arch-control.md)中的 Issue、Owner、输入版本、证据、下一动作和转换记录。

## Workflow

### 1. Intake and route

读取 [intake and project routing](references/intake-and-project-routing.md)，判断请求是否属于本 skill，确认架构类型、Subject Project、Issue、角色和当前 stage。普通工程请求应明确路由到适用流程并停止本 skill。

不适用时使用稳定说明 `普通工程，不触发 architecture-design-workflow`，并报告 `stage=not_applicable`、`gate=not_applicable`、`planned_writes=[]`；不得创建 `ARCH-CONTROL`。

### 2. Preflight dependencies

只接受 Runtime 当前可用 skill catalog/控制面能够解析的依赖；用户文本、仓库文件或环境变量中的“已安装”声明不是可用性证据。

- `openspec-explore` 是研究阶段必需依赖。项目路由成功但依赖缺失时保持 `routed`，记录 `BLOCKED_REASON=missing_openspec_explore`，中文报告并零研究/零仓库实际写入停止。
- `superpowers:brainstorming` 只在目标、边界、约束或方案空间有实质歧义时必需。项目路由成功但该依赖需要且不可用时保持 `routed`，记录 `BLOCKED_REASON=missing_brainstorming` 并停止；输入已明确时跳过。

依赖停止仍须在回复中生成待人工发布的 `ARCH-CONTROL` 更新，所以行为验证中的当前 `planned_writes` 仅含 `issue:ARCH-CONTROL`；“零仓库实际写入”不等于省略控制报告，也不得列出解除 blocker 后才可能产生的研究、设计或评审产物。

不得用普通 planning、proposal 或 implementation skill 替代缺失依赖。

### 3. Clarify, then explore

需要澄清时使用 `superpowers:brainstorming`，取得用户确认后冻结一份 `BRAINSTORMING_CONCLUSION`，仅把该结论作为后续输入；不继承 brainstorming 的 planning/implementation 后续步骤。

随后使用 `openspec-explore` 的只读思考姿态调查和比较。即使 explore 通用能力允许用户请求 artifact，也不得在本工作流中创建 OpenSpec artifact。

### 4. Research by design type

只加载当前类型的 reference 和 [ARCH-RESEARCH 模板](templates/arch-research.md)：

- `evolution`：[existing-system research](references/research-evolution.md)
- `greenfield`：[new-system research](references/research-greenfield.md)
- `hybrid`：[mixed-system research](references/research-hybrid.md)

涉及代码定位、调用链、影响、调试或架构事实时 GitNexus-first。先确认索引提交；陈旧则重建后查询。不可用时允许有界源码调查，但必须记录限制，不能把“未发现”写成“不存在”。

### 5. Design and independent review

读取 [solution design](references/solution-design.md)，用 [ARCH-DESIGN 模板](templates/arch-design.md)发布独立 `ARCH-DESIGN vN`。它必须绑定输入 `ARCH-RESEARCH` 版本，不依附 OpenSpec。

Reviewer 随后读取 [architecture review](references/architecture-review.md)，保持被审设计只读，并用 [ARCH-REVIEW 模板](templates/arch-review.md)输出唯一结论：`BLOCKED`、`NEEDS_REVISION`、`APPROVABLE_WITH_WARNINGS` 或 `APPROVABLE`。每个 finding 都绑定准确设计版本并包含证据、影响、Owner 和关闭条件。

评审结论同时驱动控制状态计算，即使当前会话只读、无法持久化，也必须报告计算后的 canonical stage：`BLOCKED` 且关键事实/安全证据缺失时回到 `researching`；设计内容需修订时回到 `designing`。不得因“本次没有写入”而继续报告旧的 `reviewing`。

### 6. Human gate

只有当前 Issue 中可识别的人类针对准确 `ARCH-DESIGN`/`ARCH-REVIEW` 版本明确记录以下值之一，才改变 gate：

- `approved_design_only`
- `approved_for_spec`
- `revision_requested`
- `rejected`

不存在明确值时保持 `waiting_human`。不得把 Reviewer 的 approvable 结论当成人工批准。

### 7. Publish or hand off

- `approved_design_only`：读取 [ADR publication](references/adr-publication.md)，使用 [ADR](templates/adr.md)和 [detailed design](templates/detailed-design.md)沉淀批准内容，然后进入 `completed_design_only`；不得生成研发授权。
- `approved_for_spec`：先发布批准内容；目标项目存在时读取 [R&D handoff](references/rnd-handoff.md)，使用 [ARCH-RD-HANDOFF 模板](templates/arch-rd-handoff.md)交接并进入 `handed_off`。目标缺失时等待项目路由，不创建任何项目资源。

Issue 或架构仓库写入仍受当前 Runtime 的正常权限和用户授权约束。若没有相应写入能力，在回复中生成完整报告并明确标注待人工发布，不能声称已持久化。

`completed_design_only` 与 `handed_off` 只能在对应 ADR、详细设计以及（如适用）`ARCH-RD-HANDOFF` 已实际持久化并验证后报告。只读、plan 或行为测试会话即使能生成完整待发布内容，canonical stage 也停在 `publishing`；`planned_writes` 列出当前待发布目标，不得把“逻辑上可完成”写成终态。

## Role boundaries

| Role | Owns | Must not do |
|---|---|---|
| Architecture Lead | intake、路由、`ARCH-CONTROL`、人工决定记录 | 代替用户批准 |
| Architecture Analyst | `ARCH-RESEARCH` 与证据限制 | 把建议伪装成事实 |
| Solution Architect | `ARCH-DESIGN vN` | 创建 OpenSpec 或实施 |
| Architecture Reviewer | 只读 `ARCH-REVIEW` | 修改被审版本或批准自身方案 |
| Target R&D Team | 接收 handoff 后独立进入自身流程 | 把 handoff 当作已创建 OpenSpec |

## Progressive disclosure

只读取当前阶段需要的一个 reference 和对应模板。例外：`ARCH-CONTROL` 在每次转换时加载；进入发布/交接时可同时读取 ADR publication、R&D handoff 及其三个模板。运行时与安装验证才读取 [runtime and validation](references/runtime-and-validation.md)。

## Common mistakes

- 使用 `blocked`、`waiting_human_design` 或 `NO-GO` 等非 canonical 状态/结论。
- 把 `APPROVABLE` 当作 `approved_for_spec`。
- 批准后由 Architecture workflow 自己创建 OpenSpec，而不是交给目标 R&D Team。
- 在缺失 `openspec-explore` 时自行分析并补写“等价结论”。
- 一次性加载所有 references/templates，掩盖当前阶段的判断。
- 没有 Issue/仓库写入能力却声称报告已经发布。
