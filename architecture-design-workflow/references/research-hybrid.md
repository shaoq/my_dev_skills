# Hybrid research

Research output belongs to `architecture_internal_evidence_v1`; only conclusions necessary to understand the Design are synthesized into `ARCH-DESIGN-vN.md`. Do not publish progress as ordinary human comments.

用于同时修改现有系统并建设新能力的方案。

先分别满足 evolution 与 greenfield 的适用证据，再补充：

- 旧系统与新系统的精确责任边界
- 接口、事件、数据所有权和一致性模型
- 迁移顺序、双写/双读/旁路阶段及退出条件
- 跨系统超时、重试、幂等、降级和级联失败模式
- 版本兼容窗口与消费者迁移清单
- 部署、观测和事故响应的跨团队 Owner
- 回滚无法覆盖的数据变化及前滚恢复方案
- 每阶段成本、容量和组织依赖

不得把两份独立设计简单拼接成 hybrid。接口、迁移次序和跨系统失败模式必须形成可验证的端到端路径，才可进入 `designing`。
