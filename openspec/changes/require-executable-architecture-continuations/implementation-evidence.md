# Implementation evidence

## Production surfaces

- portable core：`architecture-design-workflow/references/execution-continuation.md`、`SKILL.md`、workflow mandate 和 `arch-control` template。
- optional adapter：`multica-architecture-approval-adapter/references/execution-handoff-and-task-readback.md`、`SKILL.md` 与 operation manifest。
- tests：`tests/test_architecture_execution_continuation_contract.py` 和 `execution-continuation-cases.json`。
- portable core 未包含 Multica member/mention/CLI/task required fields；Multica 状态映射只存在于 optional adapter。

## TDD evidence

- RED：新增 targeted tests 初次运行 4 项中 3 项失败，明确缺少 portable continuation、adapter handoff reference 与既有 surface routing。
- GREEN：targeted 4/4 PASS；发现真实 `waiting_local_directory` 锁依赖后新增第六个 fixture，再次 RED/GREEN。
- full unit tests：35/35 PASS。
- architecture workflow safety：27 fixtures PASS。
- Skill quick validator：core 与 adapter 均 `Skill is valid!`。
- OpenSpec strict validation 与 `git diff --check`：PASS。

## Activated package readback

- core Skill：`b93d9e63-027c-4227-a760-4591444e3334`，local/remote 24/24 files，mismatches=`[]`。
- adapter Skill：`bbe335c1-e83a-4e27-8922-4fd511b461d7`，local/remote 21/21 files，mismatches=`[]`。
- Architecture Lead 两个 binding 均 enabled。

## Platform-specific accepted/active mapping

- `queued` → portable `accepted`。
- `running` → portable `active`。
- `waiting_local_directory` → 只有 runtime online、task attribution 准确、`predecessor_task_id` 为当前 task、且同一 `in_place` 目录锁 evidence 可重读时才为 `accepted`；这允许前序结束释放目录，避免“前序等下游 running、下游等前序释放目录”的死锁。
- 其他 waiting/unknown 状态不构成 accepted/active，必须继续恢复或进入真实 review/blocked/terminal。

## Live validation

UNIDRAG-12 的 Lead task 发布独立 Analyst handoff后，Analyst task `01a0585f-949c-7706-b483-97144c319c9f` 先进入 `waiting_local_directory`，随后在 Lead task `01a05857-f29b-7bdc-a377-33142c333b76` 结束释放目录的同一时间进入 `running`。Issue 保持 `in_progress`，Analyst 为 `working`，continuation metadata 为 `accepted` 并绑定准确 comment/task evidence。

Multica core 未修改。
