## ADDED Requirements

### Requirement: 循环调用 /opsx:propose 创建子方案提案
系统 SHALL 按确认后的拆解方案，对每个子方案逐一调用 `/opsx:propose`（通过 Skill 工具），为其创建完整的 OpenSpec artifacts（proposal、design、specs、tasks）。

#### Scenario: 为单个子方案创建完整 artifacts
- **WHEN** 用户确认拆解方案后，系统处理子方案 "auth-core-model"
- **THEN** 系统 SHALL 调用 Skill 工具执行 `/opsx:propose`，传入子方案名称和详细描述，等待其完成所有 artifacts 创建

#### Scenario: 多个子方案按顺序创建
- **WHEN** 拆解方案包含 5 个子方案
- **THEN** 系统 SHALL 按顺序为每个子方案调用 `/opsx:propose`，每次等待前一个完成后再创建下一个

#### Scenario: /opsx:propose 创建失败
- **WHEN** 某个子方案的 `/opsx:propose` 执行过程中遇到错误
- **THEN** 系统 SHALL 记录失败原因，询问用户是否跳过该子方案继续处理剩余子方案

### Requirement: 为子方案准备精确描述
系统 SHALL 在调用 `/opsx:propose` 前，为每个子方案准备精确的需求描述文本，包含子方案的 what/why 和与整体需求的关系。

#### Scenario: 生成子方案描述
- **WHEN** 系统准备为子方案 "auth-middleware" 调用 `/opsx:propose`
- **THEN** 系统 SHALL 构建包含子方案名称、功能描述、依赖关系说明的精确描述文本，传入 Skill 工具作为参数
