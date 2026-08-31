## 1. 边界与契约

- [x] 1.1 确认上游 `uni-architecture` change、目标仓库、两个 Skill identity 与 GitNexus 影响边界
- [x] 1.2 记录用户明确豁免新增测试；保留现有验证矩阵，不虚报新增 RED/GREEN
- [x] 1.3 定义 portable workflow mandate、Review 分类和状态语义

## 2. Portable core

- [x] 2.1 更新 `architecture-design-workflow` 主说明、Human Action reference 和控制模板
- [x] 2.2 移除 access confirmation、routing 和内部操作作为 Review action 的生成路径
- [x] 2.3 明确 standalone profile、失效条件与新任务指令边界

## 3. Multica adapter

- [x] 3.1 定义 `architecture_operation_manifest_v1` 的生成、冻结、重验和单次消费
- [x] 3.2 自动执行 preparation、comment/attachment delivery、task-result、status 与有界 retry
- [x] 3.3 将旧 operational authorization 协议和模板降级为 legacy audit-only
- [x] 3.4 更新成功、失败、回复处理和旧 request supersession 规则

## 4. 验证与交付

- [x] 4.1 运行现有 architecture workflow safety、adapter contract/unit tests 和两个 Skill quick validation
- [x] 4.2 严格验证本 change 并运行 `git diff --check`、GitNexus `detect-changes`
- [x] 4.3 生成并校验两个 Skill package，记录实施证据
- [x] 4.4 激活既有 Agent 后以新 attempt 验证 UNIDRAG-12；不创建缺失资源
