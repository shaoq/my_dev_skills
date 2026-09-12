# ARCH-REVIEW vN

## Identity

- Issue：
- Reviewer：
- Status：`complete`
- Reviewed `ARCH-DESIGN`：精确版本
- Reviewed design ref / media type / raw-byte digest：
- Review artifact ref / media type / raw-byte digest：
- Reviewed evidence snapshot：
- Read-only confirmation：未修改被审设计

## Gate conclusion

`BLOCKED|NEEDS_REVISION|APPROVABLE_WITH_WARNINGS|APPROVABLE`

## Findings

| ID | Severity | Evidence | Impact | Recommendation | Owner | Closure condition | Design section |
|---|---|---|---|---|---|---|---|

方案内容发生变化时必须由新 Design 版本关闭；不得在 Review 中复制或补写替代方案正文。

## Visual findings

| diagram_id | node ID / edge ID / message ID / state ID | Evidence | Semantic/visual impact | Owner | Closure condition | Status |
|---|---|---|---|---|---|---|
|  |  |  |  |  |  | `open|closed` |

- Current visual receipt/digest readback：
- `visual_review=passed|failed|skipped`

## Accepted non-blocking risks

| Risk ID | Condition / review point | Acceptance evidence | Decision Owner / authority scope | Human Action Request ref / status |
|---|---|---|---|---|

未取得 acceptance evidence 时不得写入“已接受”。每个不同 Owner 的风险使用独立 `action_type=architecture_review`、`review_subtype=risk_acceptance` 请求；不得提供跨 Owner 的“接受全部”。

## Traceability and evidence limitations

## Next action

- Next stage：
- Next Owner：
- Human decision required：
- Current Human Action Request refs：
- Approval packet action：`none for BLOCKED|NEEDS_REVISION`；`create new delivered packet for APPROVABLE_WITH_WARNINGS|APPROVABLE`
- Review conclusion 与 packet readiness、recommendation、human decision、`BLOCKED_REASON` 必须分字段记录。
