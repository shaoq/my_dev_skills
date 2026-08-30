# Multica Human Action Request

## 现在需要什么

- Action ID：`{{action_id}}`
- `action_type={{action_type}}`
- Current / superseded：`{{current_or_superseded}}`
- Why now：{{why_now_zh}}
- Decision Owner：`{{canonical_multica_member_uuid}}`
- Authority scope：{{authority_scope_zh}}
- 一句话决定：{{atomic_decision_zh}}

## 建议与有限备选

- Candidate recommendation：`{{candidate_recommendation_or_no_recommendation}}`
- 推荐理由：{{recommendation_basis_zh}}
- Bounded alternatives：

| Option | 含义 | 立即结果 |
|---|---|---|
| {{option}} | {{meaning_zh}} | {{immediate_outcome_zh}} |

- Basis — facts / inferences / principles：{{separated_basis_zh}}
- Option consequences：

| Option | 收益 | 代价 / material risks | 不可逆影响 |
|---|---|---|---|
| {{option}} | {{benefits_zh}} | {{costs_and_risks_zh}} | {{irreversible_effect_or_none}} |

## 完整材料入口

- Stable human-accessible evidence refs：
  - Design：`{{stable_design_ref_or_na}}`
  - Review：`{{stable_review_ref_or_na}}`
  - Packet：`{{stable_packet_ref_or_na}}`
  - Other：`{{other_stable_refs_or_na}}`
- Access scope / verifier：`{{access_scope}}` / `{{verifier}}`
- Missing evidence / Owner / closure condition：{{missing_evidence_owner_closure_zh}}

## Exact response

请复制一种合法回复，不要把解释文字混入要求 token-only 的回复：

```text
{{type_specific_exact_response}}
```

Multica access confirmation 使用 `access_profile=multica_artifact_access_confirmation_v1` 的固定 15 行语法；revision context 使用 `context_profile=multica_revision_context_v1` 的固定 7 行语法。必须从 current refs 生成，不得自由改写字段顺序。

## After response

| Response | Next stage / remaining blockers / Next Owner / planned writes | 新对象或版本 | 不可逆影响 |
|---|---|---|---|
| {{response}} | {{after_response_projection}} | {{new_object_or_version}} | {{irreversible_effect_or_none}} |

## 权限边界

- Authorizes：{{authorized_effect_zh}}
- Does not authorize：{{excluded_effects_zh}}
- 非权威上下文：recommendation、访问确认、运维授权、说明文字和 revision brief 不替代正式决定或其他 canonical evidence。

## 审计绑定

- Bound packet / routing / risk：`{{bound_identity}}`
- Multica Issue / comment ref：`{{issue_ref}}` / `{{comment_ref_or_pending}}`
- Current / superseded：`{{current_or_superseded}}`
- Human Action Request ref / version：`{{human_action_request_ref}}` / `{{human_action_request_version}}`
