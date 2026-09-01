# ARCHITECTURE-BLOCKER-ACTION

- Blocker profile / `ACTION_ID`：`architecture_blocker_action_v3` / `<unique-current-id>`
- Work item / stage / attempt：`<ref>` / `<stage>` / `<attempt>`
- Blocker reason / blocked responsibility：`<stable reason>` / `<responsibility>`
- Resolution instruction owner / authority：`<actor-ref>` / `<authority-ref>`
- Requested input kind / object：`owner_binding|routing|scope|evidence_reference` / `<one bounded object>`
- Discovery policy：`automatic_before_human`
- `DISCOVERY_SCOPE`：`<authorized read-only sources and forbidden scope>`
- Discovery actor / authority / responsibility：`<actor-ref>` / `<authority-ref>` / `coordination|research`
- Discovery completion condition：`unique_verified|multiple_verified|unavailable_with_evidence`
- Discovery result / evidence：`<result>` / `<refs>`
- Response modes：`provide_input|request_discovery`
- Provide-input profiles：`verified_binding|human_declaration`
- `BUSINESS_QUESTION`：`<one plain-language question; scope frozen by this Action>`
- `HUMAN_DECLARATION_REPLIES`：`ACTION <ACTION_ID>: I am responsible` / `ACTION <ACTION_ID>: the responsible party is <identifiable person or group>`
- `REQUEST_DISCOVERY_REPLY`：`ACTION <ACTION_ID>: I am not sure; provide a recommendation`
- Machine evidence derivation：`derive_machine_evidence_from_reply=actor identity|frozen business scope|comment ref/revision/time|reread`
- Formal source：`formal_source_policy=conditional`
- Context refs：`<refs>`
- Recommendation / rationale / confidence：`<value|no_recommendation>` / `<basis>` / `<boundary>`
- Closing condition：`<observable condition>`
- `RESUME_ACTOR_REF` / responsibility：`<actor-ref>` / `<responsibility>`
- `BLOCKER_ACTION_STATE`：`discovering|awaiting_input|received|discovery_needed|superseded|unavailable`
- Requires human review：`false`
- Request / response evidence：`<refs>|none`
- Resume continuation：`<execution_continuation_v2-ref>|none`
- Supersedes：`<action-id>|none`

这不是方案 Review。先执行 discovery；唯一 verified binding 自动继续，多个候选只请求简单选择，没有候选时只问一个普通业务问题。用户可声明自己负责、指定负责人或表示不确定；系统派生机器证据并由后续 actor 验证。内部 binding schema 和正式来源不得成为默认人类表单。
