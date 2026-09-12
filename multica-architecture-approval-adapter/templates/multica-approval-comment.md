[@{{decision_owner_display_name}}](mention://member/{{decision_owner_member_id}})，请处理下面唯一一项架构决定。

# 架构方案审批

## 方案摘要

{{one_paragraph_solution_summary_zh}}

- Design maturity：`{{directional_or_spec_ready_or_implementation_ready}}`
- Reviewer conclusion：`{{review_conclusion}}`
- Reviewer concise findings：{{concise_findings_or_none_zh}}
- 关键风险 / accepted warnings：{{critical_risks_or_none_zh}}
- Architecture recommendation / 理由 / 置信度：`{{recommendation}}` / {{rationale_zh}} / `{{confidence}}`

## 一份完整方案

本评论附带恰好一份 canonical `ARCH-DESIGN-vN.md`：

- Design：`{{design_filename}}` / `{{design_version}}`
- Stable entry：{{stable_design_entry}}
- Required visual preview：{{light_1440x900_preview_or_not_applicable}}

请打开完整 Design 后决定。Review、Packet、Control、Research 和执行记录均由机器按 digest 回读，不是必读附件；Archify HTML/PDF/preview 均为 `derived_non_authoritative`，不会产生第二个 mandatory entry。

## 当前 Action

- Action ID：`{{action_id}}`
- Decision Owner：`{{decision_owner_member_id}}`
- Current / superseded：`current`
- Access mode / state：`{{automatic_or_owner_attested}}` / `{{opened_or_manual_check_required}}`

| 决定 | 后果 | 下游边界 |
|---|---|---|
| `approved_design_only` | 发布批准文档并完成 design-only 流程 | 不生成 R&D handoff |
| `approved_for_spec` | 发布并交接目标 R&D Team | 仅 `spec_ready|implementation_ready`；不自动创建 OpenSpec/Issue/代码 |
| `revision_requested` | 新建 Design/Review/Action，旧对象只读 | 不改写旧 manifest |
| `rejected` | current work item 进入终态 | 继续需要新的明确任务 |

## 准确回复

Automatic：`ACTION {{action_id}}: decision={{legal_decision}}`

Owner-attested：`ACTION {{action_id}}: materials_opened; decision={{legal_decision}}`

若 Design 或 preview 打不开：`ACTION {{action_id}}: 材料打不开`。该回复只触发入口修复，不形成内容决定。

## 非批准边界

Recommendation、Reviewer conclusion、材料可访问性、Issue status 与内部 readiness 均不等于批准。Action 从 machine-only manifest 继承准确 Design/Review snapshot；Owner 无需复制 packet digest。

<!-- multica-architecture-approval-adapter:v2 action_id={{action_id_escaped}} design_ref={{design_ref_escaped}} design_version={{design_version}} design_digest={{design_digest}} -->
