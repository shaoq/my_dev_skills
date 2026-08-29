# Architecture workflow RED baseline

基线由五个未加载 `architecture-design-workflow` 的 fresh Agent 独立执行；它们只回答场景，不调用工具或修改文件。

## 观察结果

| Fixture | 基线选择 | 暴露的缺口 |
|---|---|---|
| `urgent-cross-project` | 拒绝立即写 OpenSpec，但建议批准后由“架构项目”创建 proposal | 未区分 Architecture workflow 与目标 R&D Team 的职责；无 canonical stage、gate 或版本化报告 |
| `explore-direct-proposal` | 正确要求 `approved_for_spec` | 没有 `ARCH-CONTROL`、`WAIT_REASON`、版本绑定和确定性 evidence fields |
| `insufficient-review-evidence` | 拒绝批准 | 使用 `NO-GO`、`有条件待批准` 等非 canonical 结论，没有绑定固定 `ARCH-REVIEW` 契约 |
| `missing-openspec-explore` | 正确停止 | 使用持久状态 `blocked`，而非保持 canonical stage 并记录 `BLOCKED_REASON=missing_openspec_explore` |
| `routine-bug` | 正确路由至普通工程流程 | 作为负向触发 control，无需新增约束 |

## RED 结论

通用 Agent 对高层安全意图通常判断正确，但会在角色所有权、状态名称、评审结论和证据字段上自由发挥；这正是新 skill 需要收敛的可观察失败。GREEN 阶段必须复用同一组请求，并由 runner 验证 canonical envelope，而不是仅判断回答“看起来合理”。
