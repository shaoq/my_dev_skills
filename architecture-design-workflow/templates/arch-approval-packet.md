# ARCH-APPROVAL-PACKET vN

## Identity

- Work Item：
- Owner：
- `payload_status=delivered`
- Created at：RFC 3339 UTC `Z`
- Supersedes：`none|ARCH-APPROVAL-PACKET vN`
- Packet digest：由 payload 最终冻结后在外部计算并记录

## Frozen design input

- `ARCH-DESIGN` ref：
- Version：
- Media type：`text/markdown; charset=utf-8|<portable media type>`
- Digest：`sha256:<64 lowercase hex characters>`
- Verification profile：`local_file|durable_platform_ref|<portable extension>`
- Availability scope：
- Target human actor：
- Access confirmation ref / confirmed at：
- Verifier / verified at：

## Frozen review input

- `ARCH-REVIEW` ref：
- Version：
- Media type：`text/markdown; charset=utf-8|<portable media type>`
- Digest：`sha256:<64 lowercase hex characters>`
- Reviewer conclusion：`APPROVABLE_WITH_WARNINGS|APPROVABLE`
- Verification profile：
- Availability scope：
- Target human actor：
- Access confirmation ref / confirmed at：
- Verifier / verified at：

## Architecture recommendation — not human approval

- `ARCHITECTURE_RECOMMENDATION`：`recommend_approved_for_spec|recommend_approved_design_only|recommend_revision|no_recommendation`
- 中文理由：
- 适用条件：
- 关键风险：

> 本建议不构成人工批准，不得驱动 stage、gate、发布或研发授权。

## Human review brief

- Decision Owner / authority scope：
- Why now：
- 审核对象与 Stable human-accessible evidence refs：
- 关键决定：
- Candidate recommendation：
- 风险与条件：
- 待确认项：

| 合法决定 | 中文后果 | Next stage / remaining blockers / Next Owner / planned writes | OpenSpec / implementation boundary | Irreversible impact |
|---|---|---|---|---|
| `approved_design_only` | 只发布批准文档，完成 design-only 流程 |  | 不产生研发授权 |  |
| `approved_for_spec` | 发布批准文档并在目标存在时交接 R&D |  | R&D Team 独立分析；不自动创建 OpenSpec 或实现 |  |
| `revision_requested` | 进入新设计迭代，旧 packet 保持不变 |  | revision brief 不是批准；新 packet 需重新 Review |  |
| `rejected` | current work item 进入终态 |  | 不授权后续工作 | rejected 终态 |

- Exact response：必须包含本 packet ref/version 及外部计算的 packet digest
- Human Action Request ref：

## External verification boundary

本 payload 不内嵌任何验证自身 digest 的 post-finalization evidence。外部记录通过 packet ref/version/digest 绑定本 payload；后续 supersession 只更新控制投影，不改写本文件。
