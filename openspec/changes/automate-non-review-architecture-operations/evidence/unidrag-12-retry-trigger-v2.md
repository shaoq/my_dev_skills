[@Architecture Lead](mention://agent/f6135960-aea8-4aaa-a970-0c1e60544a90)

## UNIDRAG-12 新版自动交付回归 mandate（current）

这是用户“继续实施并重试 UNIDRAG-12”的 `architecture_workflow_mandate_v1` 平台投影，不是架构内容决定，也不是 operational authorization。请按当前已激活的两个 Skill 处理；不得生成、relay、等待或消费 `AUTHORIZE OPERATION`。

```text
mandate_profile=architecture_workflow_mandate_v1
mandate_ref=conversation%3Aactivate-two-skills-and-retry-UNIDRAG-12%3A20260831-02
work_item_ref=multica-issue%3A01a052ed-1875-75c7-a0e2-1ca1ca33f2e5
subject_project_ref=multica-project%3A120aa025-2ef8-4cb0-ac50-b28900578d4a
stage=designing
attempt=unidrag12-design-baseline-review-v1
architecture_agent=multica-agent%3Af6135960-aea8-4aaa-a970-0c1e60544a90
trigger_evidence_ref=this-comment
allowed_operations=read%2Cprepare_materials%2Cvalidate_materials%2Cdeliver_review_materials%2Cverify_access%2Cproject_status%2Crecord_task_evidence%2Cbounded_retry
forbidden_scope=resource_creation%2Ccross_issue_write%2Cresearch_redo%2Cdesign_redo%2Creviewer_trigger%2Carchitecture_approval%2Cimplementation%2Cdeployment%2Cprocurement
retry_limit=1
preconditions=existing_design_research_control_exact_digests%2Cunique_decision_owner_allen%2Ccurrent_skill_identities%2Clegacy_request_superseded
completion_condition=one_current_design_input_brief_delivered_with_complete_material_entries_and_issue_in_review
supersedes=comment%3A01a056e1-ce75-7d59-a2fd-12adf2026b5c%2Ctask%3A01a05748-1cad-7c5b-b12a-3b1d31164c27
```

### 固定输入与身份

- 复用既有 `ARCH-DESIGN v1 draft`（`sha256:612a86d4d56b09cbf5cb95a99dba1659ae9ad8afb13decc6cab81412e4841360`）、`ARCH-RESEARCH v1`（`sha256:ba3af22cfae312e3c8a3aaf5dfddbbf31c270544b4b3a40ce1db35426d62ba37`）和 `ARCH-CONTROL v5`（`sha256:91f9c4dee772fb0c30fa7b6a7b22e97be91c4eb76ce3d05b4d30434241d4ee39`）。
- 复用并保留已有完整附件评论 `01a0566b-7864-7792-ab22-392995d61153`；不得编辑或删除历史。
- 旧 `access_confirmation` 与旧 delivery authorization request `01a056e1-ce75-7d59-a2fd-12adf2026b5c` 仅作 audit，必须标为 superseded，不能成为 current action 或 trigger。
- Decision Owner 为 `[@allen](mention://member/5a17a52c-601e-4674-92f8-3274dcefb2bf)`，authority scope 仅限下面这一项设计输入。
- 当前 Skill：`architecture-design-workflow` `b93d9e63-027c-4227-a760-4591444e3334@2026-08-31T09:59:24Z`；Adapter `bbe335c1-e83a-4e27-8922-4fd511b461d7@2026-08-31T09:59:44Z`。

### 唯一方案决定

- Action ID：`UNIDRAG-12-DESIGN-BASELINE-V1`
- `action_type=design_input`，`requires_human_review=true`。
- 原子问题：是否接受现有“平台中立的双面可观测/评测架构”（canonical events + bounded async exporter/collector + 技术遥测/受限内容分面 + 稳定 ID/幂等 + 观测故障不影响 Chat）作为后续补证、PoC 与设计收敛的基线？
- Candidate：`platform-neutral-dual-plane`；Architecture Team 当前建议为接受，置信度 `medium`。
- 接受只冻结上述边界；不选择自建/Phoenix/Langfuse，不关闭九个领域依赖，不构成 Review conclusion、正式架构批准、OpenSpec 或实施授权。

### 必须交付并自动完成

1. 生成一条面向人的九段式 Architecture Decision Brief：一段式摘要、简图、Team 建议/理由/置信度、已确定/未确定、备选及后果、上述唯一决定、回复后果、可点击完整 Design/Research/Control、Exact response/权限边界。
2. 第一行准确 `@allen`；其他 Owner 只列 non-actionable dependencies，不出现多 Owner 问卷。
3. 自动准备、发布和回读附件/稳定入口，并自动记录 Web/mobile 可访问性证据；不得要求用户提交 access confirmation。
4. 所有交付 postconditions 通过后自动把 Issue 设为 `in_review --no-start`。只有此时才等待用户对方案作决定。
5. 若确定性 postcondition 可恢复，在 `retry_limit=1` 内自动重试；不可恢复时保留对象并说明事实和恢复路径，不生成 operational token。

合法设计输入回复必须由 brief 绑定实际 action/version/digest 后渲染，语义限定为：

```text
ACTION UNIDRAG-12-DESIGN-BASELINE-V1: accept platform-neutral-dual-plane
ACTION UNIDRAG-12-DESIGN-BASELINE-V1: modify <field>=<value>; reason=<reason>
ACTION UNIDRAG-12-DESIGN-BASELINE-V1: reject; reason=<reason>
```
