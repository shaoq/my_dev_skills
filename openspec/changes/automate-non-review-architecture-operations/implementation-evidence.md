# Implementation evidence

## Scope

- Upstream contract: `uni-architecture/openspec/changes/automate-non-review-architecture-operations`.
- Target repository baseline: branch `main`, HEAD `e45602444d7173e20dc0f2e4d0c5b8826ca56e37`.
- Modified runtime surfaces: `architecture-design-workflow` portable contract and `multica-architecture-approval-adapter` sibling adapter.
- Not modified: Multica core、`unidocs-rag` 业务代码、Agent 指令、Team/Squad/Issue/Agent 资源身份、用户 Runtime 配置。
- Live activation/regression writes: 原 ID overwrite 两个既有 Skill；在既有 UNIDRAG-12 发布一次 current workflow mandate、一次九段式 Decision Brief + 三附件，并在全部 postconditions 通过后自动投影 `in_review`。未创建缺失资源。
- User test decision: 不新增测试文件或 fixtures；只更新现有 contract assertions 以匹配新契约，并运行现有验证。

## Implemented contract

- portable core 新增 `architecture_workflow_mandate_v1` 与 `requires_human_review` 派生规则。
- 新人工 Review action 仅允许 `design_input|architecture_review|architecture_approval`。
- routing/Owner scope 缺口改为新任务指令边界；访问、准备、交付、状态、relay、retry 和 verification 不再生成 Human Action。
- Adapter 新增 immutable `architecture_operation_manifest_v1`、single consumption、ordered postconditions、bounded retry 与 legacy request supersession。
- 旧 `multica_operational_scope_v1` / `AUTHORIZE OPERATION` 只保留 audit parser/template，不得用于新请求。
- Decision Brief 成功交付后自动 `in_review --no-start`；有效 current 回复自动 `in_progress --no-start`。
- activation/sandbox 由明确自然语言任务建立新 mandate，不拆分 token 授权；不自动创建缺失资源。

## Independence evidence

- `architecture-design-workflow` 的主说明和 required references/templates 不包含平台专有 identity/command required fields。
- core standalone copy 的 `quick_validate.py`：PASS。
- architecture workflow safety 的 platform-marker guard：PASS，27 fixtures。
- Adapter 只从 sibling path 引用 portable mandate contract；core 不反向引用 Adapter。

## Validation

| Check | Result |
|---|---|
| Target OpenSpec strict validation | PASS |
| `architecture-design-workflow` quick validation | PASS |
| `multica-architecture-approval-adapter` quick validation | PASS |
| `tests/architecture-design-workflow-safety.sh` | PASS, static, 27 fixtures |
| Existing unit/contract/installer tests | PASS, 31 tests |
| `git diff --check` | PASS |
| GitNexus `detect-changes --scope all` | PASS, 30 files / 102 symbols / 0 affected processes / low risk |

## Packages

- Activated package directory: `/tmp/architecture-skills-activation.JImp6x`（临时验证产物，不纳入仓库）。
- `architecture-design-workflow.skill`: `sha256:9b323e0da5f598232be1055424a539c298d7b0db254e1f26620189ebdc78fc4a`; source aggregate `sha256:79cbe468fd6052d56523b0c6c268af669cafce827f815f289f9d48fabea8cd1e`.
- `multica-architecture-approval-adapter.skill`: `sha256:c7cb1cea606c82e2a4de468d1367ecd89288804ce48ede3761975c7b423690d1`; source aggregate `sha256:279bf38c32e20b6dfdac10951ac893420cf14b550bd1cfbcd81622f888d62bc5`.
- 两个 zip integrity checks、package integrity 与 quick validation：PASS。

## Activation and live regression

```text
activation=passed
activation_manifest=MCA-ACTIVATE-ARCH-SKILLS-20260831-01
activation_manifest_digest=sha256:0d16bc265b578b34738d4b7859658433ed0adb977cff3ffc7481dee445611a02
core_skill=b93d9e63-027c-4227-a760-4591444e3334@2026-08-31T09:59:24Z
adapter_skill=bbe335c1-e83a-4e27-8922-4fd511b461d7@2026-08-31T09:59:44Z
unidrag_12_retry=passed
workflow_trigger_comment=01a05751-7bd7-7437-91b6-13a2ac927bb2
delivery_comment=01a05760-5d1e-7b13-a207-e0a4314773cf
delivery_task=01a05751-7bf3-7165-a809-259d677a83f6@completed
issue_status=in_review@revision-53
operational_authorization_token=none
resources_created=none
```

- 两个既有 Skill 均原 ID overwrite，既有 Architecture Lead binding 保持不变；没有 additive binding 或资源创建。
- 直接 `issue rerun` 的 New Assignment 首次只产生 `no_action`，证明纯 rerun 不携带新 mandate；随后用用户 current continue/retry 指令发布精确 `architecture_workflow_mandate_v1` comment trigger，并在同一 bounded retry 中完成真实交付。
- 旧 attempt 4 operational request `01a056e1-ce75-7d59-a2fd-12adf2026b5c` 保留为 superseded audit-only，未生成、relay 或消费新旧 operation token。
- 新 Brief 第一行准确 mention allen，只包含一个 `design_input` action；九段式摘要、简图、建议/理由/置信度、已确定/未确定、备选后果、回复投影和完整 Design/Research/Control 均已交付。
- 三份新附件 raw-byte digest 与固定输入一致；真实 Web session 与 `390×844` mobile emulation 均验证 HTTP 200、完整字节和 identity marker。实体手机未单独实测，证据边界在 Brief 中明确披露。
- comment/attachment/访问 postconditions 全部通过后才自动执行 `in_review --no-start`；最终 Issue revision 53，task 无 error。
