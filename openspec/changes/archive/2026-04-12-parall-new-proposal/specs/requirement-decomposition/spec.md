## ADDED Requirements

### Requirement: 接收综合需求描述并分析功能边界
系统 SHALL 接收用户提供的需求描述文本，分析其中的功能边界，将需求拆解为多个可独立执行的子方案。

#### Scenario: 拆解综合需求为多个子方案
- **WHEN** 用户提供综合需求描述（如"给项目添加完整的认证系统"）
- **THEN** 系统 SHALL 分析需求，识别功能边界，输出 N 个子方案列表，每个子方案包含 kebab-case 名称和简要描述

#### Scenario: 用户未提供输入
- **WHEN** 用户调用 `/parall-new-proposal` 但未提供任何需求描述
- **THEN** 系统 SHALL 使用 AskUserQuestion 工具询问用户想要构建什么，且不自动推进流程

### Requirement: 拆解颗粒度遵循交付单元原则
系统 SHALL 按功能切片（可独立交付的功能单元）维度拆分需求，对每个候选子方案执行三问判定，不通过者合并到相关提案，避免为并行而过度拆分。

#### Scenario: 三问判定 — 全部通过则独立
- **WHEN** 候选子方案 "auth-jwt-service" 通过三问判定（Q1 可独立测试、Q2 可独立理解、Q3 产出有独立价值）
- **THEN** 系统 SHALL 将该子方案保留为独立提案

#### Scenario: 三问判定 — 未通过则合并
- **WHEN** 候选子方案 "user-repository" 仅改了数据访问层文件，无法独立测试（依赖 user-model），无法独立理解（是 user-model 的内部步骤），无独立价值
- **THEN** 系统 SHALL 将该子方案合并到相关的 "auth-user-model" 提案中，不作为独立提案

#### Scenario: 数量上限检测
- **WHEN** 拆解后子方案数量超过 8 个
- **THEN** 系统 SHALL 在展示方案时标注警告"拆分粒度可能过细，建议检查是否可合并部分子方案"，由用户决定是否调整

#### Scenario: 需求过小无需拆分
- **WHEN** 需求经分析后仅产生 1-2 个子方案
- **THEN** 系统 SHALL 提示用户"需求规模较小，建议直接使用 /opsx:propose 创建单个提案"，并询问是否继续

### Requirement: 构建依赖图并预览 Wave 分组
系统 SHALL 为拆解后的子方案构建依赖图，使用拓扑排序生成分波次执行计划（Wave），展示各 Wave 的并行执行情况。

#### Scenario: 生成依赖图和 Wave 分组
- **WHEN** 子方案拆解完成且存在依赖关系
- **THEN** 系统 SHALL 输出 ASCII 依赖图，按 Wave 分组展示，同一 Wave 内的子方案无互相依赖可并行执行

#### Scenario: 无依赖的子方案
- **WHEN** 所有子方案之间无依赖关系
- **THEN** 系统 SHALL 将所有子方案归入 Wave 1，标注"全部可并行"

#### Scenario: 检测循环依赖
- **WHEN** 拆解后的子方案存在循环依赖（A 依赖 B，B 依赖 A）
- **THEN** 系统 SHALL 报错并提示用户调整拆解方案消除循环

### Requirement: 用户确认拆解方案
系统 SHALL 在创建任何提案之前，展示完整的拆解方案并等待用户确认。

#### Scenario: 用户确认方案
- **WHEN** 系统展示拆解方案（子方案列表 + 依赖图 + Wave 分组）
- **THEN** 系统 SHALL 使用 AskUserQuestion 工具请求用户确认，用户可选择"确认执行"、"调整方案"或"取消"

#### Scenario: 用户要求调整
- **WHEN** 用户选择"调整方案"并提供修改意见
- **THEN** 系统 SHALL 根据用户反馈调整拆解方案并重新展示
