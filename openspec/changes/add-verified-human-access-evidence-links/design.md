## Context

UNIDRAG-12 中 `ARCH-DESIGN v1` 实际已有约 1.4 万字符并包含系统边界、候选方案、数据接口、安全、可靠性和迁移等内容，但它只存在于较早的长评论里。最新人工入口则是约 2.2 万字符、九个权限域混排的 Human Action Request，并以无法点击的 `multica://issues/...` 指向历史评论。于是“方案本体”“决策入口”“审计控制”在用户界面上既没有稳定边界，也没有可靠的网页/手机访问路径。

本设计采用两层交付：完整、版本化的架构方案作为附件；评论作为简洁的 `Architecture Decision Brief`。核心 Skill 定义文档完整性和平台无关访问证据，Multica sibling adapter 负责附件、评论链接与客户端验证，不修改 Multica 核心。

## Goals / Non-Goals

**Goals:**

- 让每个进入人工决策的 `ARCH-DESIGN vN` 都是一篇高级架构师可独立阅读的完整文档。
- 让完整方案以 canonical Markdown 附件交付，并在需要时提供非权威 PDF 阅读副本。
- 让评论只承担决策摘要、建议、后果、准确回复和材料导航，不复制完整方案或堆叠多 Owner 问卷。
- 让当前读者只被请求处理其 authority scope 内的一项原子决定。
- 分别验证网页和手机端的附件/链接可打开性与准确材料身份。

**Non-Goals:**

- 不修改 Multica Web/App 的附件或路由实现。
- 不把草稿写入 `uni-architecture/docs`；未批准版本仍只保留在 Issue/附件中。
- 不把 PDF、渲染正文或评论摘要变成 canonical 设计 bytes。
- 不在本次本地实施中导入 Skill、绑定 Agent、上传 Issue 附件、重试 UNIDRAG-12 或声称手机端已验证。

## Decisions

### 1. `ARCH-DESIGN` 是完整、独立、附件可交付的文档

`ARCH-DESIGN vN` 的 canonical 载体是 UTF-8 Markdown 文件 `ARCH-DESIGN-vN.md`。它不依赖 OpenSpec、评论上下文或审计日志才能理解，至少包含：

1. Identity/status/input evidence；
2. 执行摘要、推荐结论与置信度；
3. 问题、现状、架构驱动因素和约束；
4. Goals / Non-goals；
5. 系统上下文、责任边界和简化架构图；
6. 组件、数据流、控制流、接口与一致性语义；
7. 正常流程和关键失败流程；
8. 安全、隐私、可靠性、容量、性能、成本、可观测和评测设计；
9. 候选方案、权衡、推荐与淘汰理由；
10. 迁移、灰度、回滚、前滚和退出路径；
11. 运维/RACI、风险、假设、已确定与未确定内容；
12. 验证计划、验收标准和后续研发拆分。

证据不足可以阻止 `decision_ready` 或最终平台选择，但不能用缺少某个供应商结论替代完整的总体架构。文档必须明确区分“已冻结的总体架构”“当前推荐的 PoC/默认路径”“仍需人决定的变量”“会改变推荐的证据”。

### 2. Design 附件是必需材料，PDF 是条件式阅读副本

每个需要人类设计输入、风险接受或正式批准的入口，都必须绑定并上传准确 `ARCH-DESIGN-vN.md`。附件原始 bytes、版本和 digest 与 Human Action Request 绑定；同版本不可就地修改，修订产生新版本。

若 Multica Markdown 预览在网页和手机端都通过目标账号实测，Markdown 是唯一必需附件。若任一客户端无法舒适阅读 Markdown，则在同一授权交付中增加 `ARCH-DESIGN-vN.pdf`：内容与 Markdown 一致、标记 `derived_non_authoritative=true`，不参与设计身份、批准 digest 或后续发布重建。

Research 与 Control 必须给出可点击的完整入口。若既有 comment permalink 在目标客户端验证通过，可直接引用；否则把对应原始 Markdown 作为同一 material bundle 的附件。不能因为文件名出现在 attachment card 上就推断目标人类可打开。

### 3. 评论固定为 `Architecture Decision Brief`

评论首屏和主体只保留以下顺序：

1. 当前方案的一段式摘要；
2. 简化架构图；
3. Architecture Team 的总体建议、理由和置信度；
4. 已确定与尚未确定的内容；
5. 最重要的备选及后果；
6. 当前读者真正有权决定的一项内容；
7. 回复后会发生什么；
8. 可点击的完整 Design、Research、Control 入口；
9. 可复制的准确回复与最小审计绑定。

完整设计、九域问卷、长证据表、digest 和 reconciliation 细节不复制到评论。审计字段只保留判断 current/superseded 与准确回复所需的最小集合，其余通过 Control/sidecar 重读。

### 4. 一个 brief 只请求当前 Decision Owner 的一个决定

renderer 必须先把当前 Multica member 与 core `Decision Owner / authority scope` 做准确绑定。只有绑定唯一且当前 action 未回答时，评论才能用命令式语言请求该决定。

其他 Owner 的 action 仅在“尚未确定”中列出依赖摘要、Owner 和关闭条件，不展示它们的 accept/modify/reject 表单。Owner 未绑定时，当前动作只能是 routing/owner-binding，不得让任意读者代替 Privacy、Security、SRE、Finance 或 API Owner 做内容决定。

该选择避免把“九个问题都写全”误当成“当前用户可决策”。

### 5. Multica 使用附件优先的材料 bundle

adapter 新增 `multica_human_action_material_bundle_v1`：

- exact existing Issue、Human Action Request、Design/Research/Control identities；
- canonical Design Markdown path/digest；
- 条件式 PDF 与 Research/Control fallback paths/digests；
- 一次评论+附件写入所需的 exact operational authorization；
- 平台返回的 comment/attachment IDs、卡片或稳定 endpoint；
- 每个材料在 `web|mobile` 的验证状态。

评论引用同评论附件时，平台渲染出的 attachment card 可以作为可点击入口，但必须经过发布后验证；不要求在首次写入前猜测未知 attachment URL。对于既有 comment-backed Research/Control，可使用：

```text
<app_base_url>/<workspace_slug>/issues/<issue_identifier>#comment-<comment_id>
```

该 `multica_web_comment_permalink_v1` 的 base URL 来自明确的当前人类入口，slug/identifier/comment ID 来自平台读回。`multica://issues/...` 只可作为历史内部审计身份，未经客户端能力验证不能出现在人类材料入口。

### 6. 发布后验证是决策请求的门禁

对每个 Design/Research/Control 入口分别验证：

- attachment card 或 anchor 存在且可点击；
- 导航/打开后是准确 artifact type/version/comment/attachment；
- 完整内容可读取，而不是只有名称、摘要或 Agent 下载能力；
- canonical Markdown 可重新下载并匹配 digest；
- `web` 与 `mobile` 分别记录 `opened|unavailable|not_run`、verifier 和 UTC time。

Web 成功不能推断 mobile；Agent CLI 下载不能推断人类客户端。任一必需 scope 未验证时，评论可作为不可用报告保留，但不能声称“可评审”或请求正式内容决定。

由于新附件的 exact client evidence 只能在首次发布后产生，首次 material bundle 的唯一 action 必须是 `access_confirmation`，预期的设计输入/风险接受/批准只作为 non-actionable pending context。访问证据通过后，core 生成新的 current Human Action Request 版本；adapter 使用新的独立运维授权发布新的 Decision Brief。不得编辑首次评论来激活内容决定，也不得把访问确认解释为内容批准。

### 7. 运维授权边界保持独立

附件上传、评论、可选 PDF 和任何 retry 都是 Multica/shared-scope 写入，必须由当前 `multica_operational_scope_v1` 精确覆盖 Issue、attempt、输入路径、planned writes 和 retained objects。更新本地 Skill 不授权激活或 Issue 写入；激活和 UNIDRAG-12 重试继续需要彼此独立的新授权。

## Risks / Trade-offs

- [附件卡片在不同客户端行为不同] → Web/mobile 分别实测；失败时上传已授权 PDF 或关闭为 unavailable，不根据桌面结果推断。
- [同一评论写入前不知道附件 URL] → 以平台返回并绑定的 attachment card/identity 作为入口，发布后验证；不猜测 URL，不用第二次未授权编辑修补。
- [PDF 与 Markdown 漂移] → Markdown 是唯一 canonical bytes；PDF 标记 non-authoritative，并在生成时绑定 source digest。
- [完整文档较长] → 长内容只在附件；评论固定为 Decision Brief，不复制正文。
- [多 Owner 造成大量评论] → 只为当前可识别 Decision Owner 渲染当前 action；其他事项留在依赖摘要和 Control，不批量请求无权读者。
- [平台路由或附件 endpoint 变化] → 每次交付执行当前客户端验证；历史成功不替代当前验证。

## Migration Plan

1. 增加会在当前实现上失败的完整 Design、Decision Brief、单 Owner、附件 bundle 和网页/手机访问契约测试。
2. 更新核心 `ARCH-DESIGN` reference/template 和 Human Action Request contract，保持平台无关。
3. 更新 Multica adapter 的 Human Action renderer、材料 bundle、operational authorization/readback 和 sandbox acceptance。
4. 运行相关测试、Skill validation、OpenSpec strict validation 和 GitNexus change analysis。
5. 本地实施完成后停止；另行请求 Skill activation 授权。
6. 激活完成后，再为 UNIDRAG-12 生成只包含增量附件/评论/retry 的新授权，并由目标账号完成网页和手机验证。

回滚只回退本地 Skill/spec/test 文件。已上传的 Issue 对象一律保留审计，不删除、不覆盖；后续尝试使用新版本和新授权。

## Open Questions

无提案阻断项。实际 Multica attachment card 是否在目标手机客户端直接预览 Markdown，必须在新授权的 sandbox/retry 中观察；失败时按条件式 PDF 路径处理。
