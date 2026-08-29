# Evolution research

用于以现有系统改造为主体的架构设计。

## Evidence minimum

- 目标仓库、分支/提交、服务与责任边界
- 当前调用链、数据流、接口和依赖
- GitNexus 索引时间与 indexed commit
- 直接和传递影响、兼容性消费者、失败传播
- 安全、可靠性、性能、容量、可观测性现状
- 数据/接口迁移、灰度、回滚或前滚策略
- 已知限制、未知项与验证计划

## GitNexus-first sequence

1. 检查仓库索引与 HEAD；陈旧时先重建。
2. 用 query/exploring 找相关流程，再对关键 symbol 用 context。
3. 对计划修改的现有关键 symbol 用 upstream impact；HIGH/CRITICAL 风险在推荐前显式警告。
4. 报告仓库、提交、查询、symbol/flow/file:line 与限制。

GitNexus 不可用时只做有界源码和官方文档调查，记录 `EVIDENCE_LIMITATION`；absence of evidence 不是 evidence of absence。

当前状态、影响半径、兼容性、迁移和回滚均有可引用证据，关键未知项有 Owner 与验证办法，才能进入 `designing`。
