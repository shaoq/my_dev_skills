# ARCH-DESIGN vN

## Identity and status

- Issue：
- Owner：
- Status：`draft|ready_for_review|superseded|approved`
- Subject Project：
- `ARCH-RESEARCH` 输入版本：
- Evidence snapshot：
- Artifact filename / encoding / raw-byte digest：`ARCH-DESIGN-vN.md` / `UTF-8` / `sha256:<64-lowercase-hex>`
- Design readiness：`incomplete|draft_complete|decision_ready|ready_for_review`
- Design maturity：`design_maturity=directional|spec_ready|implementation_ready`
- Supersedes：

## Executive summary

- Recommendation / rationale / confidence：
- Frozen architecture：
- Current default or PoC path：
- Decision/readiness limitation：

## Problem, current state and architecture drivers

- Problem and current state：
- Facts / assumptions / constraints / unknowns：
- Architecture drivers and quality attributes：

## Goals / Non-goals

## System context, responsibility boundaries and simplified architecture view

```text
<portable simplified architecture diagram>
```

- Component/responsibility boundary：
- Trust/ownership boundary：

## Architecture visual manifest

- Diagram requirement：`required|diagram_not_applicable`
- Not-applicable rationale / Reviewer acceptance：

| diagram_id | type | purpose / Design sections | source_ref / specification_sha256 | artifact_ref / artifact_sha256 | static_preview_ref / digest | receipt / capture | gates | supersedes |
|---|---|---|---|---|---|---|---|---|
|  | `architecture|workflow|sequence|dataflow|lifecycle` |  |  |  |  | `light` / `1440x900` | `delivery_validation=passed`; `browser_evidence=passed`; `visual_review=passed`; `semantic_findings=closed` |  |

Typed JSON、HTML 和 static preview 均为 `derived_non_authoritative`。正文必须解释每张图支持的结论；required visual 任一 gate 为 `failed|skipped`、receipt/digest 不匹配或 semantic finding 未关闭时，Design 不得进入正式 Review。Architecture 总览图之外最多两张附加图。

## Components, data flow, control flow, interfaces and consistency

- Components：
- Data flow / ownership / retention：
- Control flow / sequence：
- Interfaces / schema / versioning：
- Consistency / idempotency / transaction boundary：

## Normal and critical failure flows

| Flow | Trigger | System behavior | User/operational consequence | Recovery |
|---|---|---|---|---|
| Normal |  |  |  |  |
| Critical failure |  |  |  |  |

## Security and privacy

- Identity / authorization / tenant isolation：
- Data classification / minimization / encryption / audit：
- Threats / controls / residual risks：

## Reliability, performance, capacity and cost

- Availability / degradation / recovery：
- Performance and capacity model：
- Cost/TCO model and limits：

## Observability and evaluation

- Telemetry and SLO evidence：
- Evaluation metrics / rubric / dataset / versioning：
- Alerting / data quality / evaluator governance：

## Alternatives, trade-offs and rejected reasons

| Criterion | Weight/scale | Baseline | Option A | Option B | Evidence |
|---|---|---|---|---|---|

### Recommendation and rejected reasons

- Recommended option / conditions：
- Rejected or deferred options / reasons：

## Migration, rollout, rollback, roll-forward and exit

- Stages / entry and exit criteria：
- Compatibility / shadow / reconciliation：
- Rollback / roll-forward：
- Vendor/platform exit and data export：

## Operations / RACI

| Responsibility | Accountable Owner | Responsible Owner | Evidence / coverage gap |
|---|---|---|---|
|  |  |  |  |

## Organizational and cross-project impact

## Determined and undetermined matters

### Determined

### Undetermined

| Decision | Owner / authority scope | Architecture recommendation / confidence | Evidence that changes it | Closure condition |
|---|---|---|---|---|
|  |  |  |  |  |

### Maturity closure

| Remaining item | Owner | Evidence gap | 关闭条件 | 阻止的下游阶段 |
|---|---|---|---|---|
|  |  |  |  |  |

## Validation, acceptance and R&D decomposition

- Validation plan / common fixtures：
- Acceptance criteria：
- R&D decomposition / dependencies：

## Evidence and limitations

## Next action

- Reviewer：
- Review entry criteria：
- Canonical Markdown remains in the Issue/material delivery until approval; do not publish this draft to the formal architecture document directories.
- 若 Review approvable：由 Lead 创建新的 immutable approval packet；本设计不得预写 packet readiness 或 human decision。
