# Implementation evidence

## Scope

- Upstream contract: `uni-architecture/openspec/changes/automate-non-review-architecture-operations`.
- Target repository baseline: branch `main`, HEAD `e45602444d7173e20dc0f2e4d0c5b8826ca56e37`.
- Modified runtime surfaces: `architecture-design-workflow` portable contract、`multica-architecture-approval-adapter` sibling adapter，以及 Multica shared frontend `packages/views/rich-content` 的已知附件链接路由。
- Not modified: Multica 后端/API/数据库、`unidocs-rag` 业务代码、Agent 指令、Team/Squad/Issue/Agent 资源身份、用户 Runtime 配置。
- Live activation/regression writes: 原 ID overwrite 两个既有 Skill；在既有 UNIDRAG-12 发布一次 current workflow mandate、一次九段式 Decision Brief + 三附件。旧 fetch-only 证据曾错误投影 `in_review`，本次已自动纠正为 `in_progress`。未创建缺失资源。
- User test decision: 不新增测试文件或 fixtures；只更新现有 contract assertions 以匹配新契约，并运行现有验证。

## Implemented contract

- portable core 新增 `architecture_workflow_mandate_v1` 与 `requires_human_review` 派生规则。
- 新人工 Review action 仅允许 `design_input|architecture_review|architecture_approval`。
- routing/Owner scope 缺口改为新任务指令边界；访问、准备、交付、状态、relay、retry 和 verification 不再生成 Human Action。
- Adapter 新增 immutable `architecture_operation_manifest_v1`、single consumption、ordered postconditions、bounded retry 与 legacy request supersession。
- 旧 `multica_operational_scope_v1` / `AUTHORIZE OPERATION` 只保留 audit parser/template，不得用于新请求。
- Decision Brief 成功交付后自动 `in_review --no-start`；有效 current 回复自动 `in_progress --no-start`。
- activation/sandbox 由明确自然语言任务建立新 mandate，不拆分 token 授权；不自动创建缺失资源。

## Independence evidence

- `architecture-design-workflow` 的主说明和 required references/templates 不包含平台专有 identity/command required fields。
- core standalone copy 的 `quick_validate.py`：PASS。
- architecture workflow safety 的 platform-marker guard：PASS，27 fixtures。
- Adapter 只从 sibling path 引用 portable mandate contract；core 不反向引用 Adapter。

## Validation

| Check | Result |
|---|---|
| Target OpenSpec strict validation | PASS |
| `architecture-design-workflow` quick validation | PASS |
| `multica-architecture-approval-adapter` quick validation | PASS |
| `tests/architecture-design-workflow-safety.sh` | PASS, static, 27 fixtures |
| Existing unit/contract/installer tests | PASS, 31 tests |
| `git diff --check` | PASS |
| GitNexus `detect-changes --scope all` | PASS, 30 files / 102 symbols / 0 affected processes / low risk |
| Multica RichContent/attachment 定向测试 | PASS, 85 tests |
| Multica `@multica/views` typecheck | PASS |
| Multica changed-file ESLint | PASS |
| Multica frontend production Docker build | PASS |

## Packages

- Activated package directory: `/tmp/architecture-skills-activation.JImp6x`（临时验证产物，不纳入仓库）。
- 早期 `.skill` 包 digest 只保留为历史 activation 证据；preview-first 修正后的 current source aggregate 为：core `sha256:e050ab25f258154c6879684bafaba88e5733fc04277406c2764cdd84b539b612`，adapter `sha256:29244facd13752a24e7def107e699adc3517aebdf8acf8d685d53b59ccd9765c`。
- `~/.codex/skills/architecture-design-workflow` 与 `~/.codex/skills/multica-architecture-approval-adapter` 均为指向本仓库 current source 的 symlink，修改即时激活，无需另建 Skill identity 或 additive binding。
- 两个 zip integrity checks、package integrity 与 quick validation：PASS。

## Activation and live regression

```text
activation=passed
activation_manifest=MCA-ACTIVATE-ARCH-SKILLS-20260831-01
activation_manifest_digest=sha256:0d16bc265b578b34738d4b7859658433ed0adb977cff3ffc7481dee445611a02
core_skill=b93d9e63-027c-4227-a760-4591444e3334@2026-08-31T09:59:24Z
adapter_skill=bbe335c1-e83a-4e27-8922-4fd511b461d7@2026-08-31T09:59:44Z
unidrag_12_retry=passed
workflow_trigger_comment=01a05751-7bd7-7437-91b6-13a2ac927bb2
delivery_comment=01a05760-5d1e-7b13-a207-e0a4314773cf
delivery_task=01a05751-7bf3-7165-a809-259d677a83f6@completed
issue_status=in_progress@revision-54
operational_authorization_token=none
resources_created=none
```

- 两个既有 Skill 均原 ID overwrite，既有 Architecture Lead binding 保持不变；没有 additive binding 或资源创建。
- 直接 `issue rerun` 的 New Assignment 首次只产生 `no_action`，证明纯 rerun 不携带新 mandate；随后用用户 current continue/retry 指令发布精确 `architecture_workflow_mandate_v1` comment trigger，并在同一 bounded retry 中完成真实交付。
- 旧 attempt 4 operational request `01a056e1-ce75-7d59-a2fd-12adf2026b5c` 保留为 superseded audit-only，未生成、relay 或消费新旧 operation token。
- 新 Brief 第一行准确 mention allen，只包含一个 `design_input` action；九段式摘要、简图、建议/理由/置信度、已确定/未确定、备选后果、回复投影和完整 Design/Research/Control 均已交付。
- 三份新附件 raw-byte digest 与固定输入一致；当时的 Web session 与 `390×844` mobile emulation 仅验证了 HTTP fetch、完整字节和 identity marker，没有实际点击评论入口并检查 Markdown 渲染。该访问结论已被后续 Chrome `com.apple.quarantine`/download-only 发现 supersede，只保留为传输与完整性证据，不能作为 human-accessible evidence。
- 当时基于上述不充分访问 postcondition 自动执行了 `in_review --no-start`（Issue revision 53，task 无 error）；该状态回归结论现标记为无效，必须在 preview-first Skill 与 Multica shared view 激活后用新的 attempt 重验。

## Inline preview correction and current state

- Multica 仅修改 `packages/views/rich-content/rich-content.tsx` 与对应既有测试文件；普通 Markdown 链接命中当前 attachment metadata 时，主点击调用既有 `AttachmentPreviewModal`，原始 `href` 与 modal 内 Download 保留为次要路径。未新增后端接口。
- RED 证明旧行为不会请求 attachment text content 且会外部打开；GREEN 证明点击已知 `.md` attachment 会读取 `/content`、呈现 Markdown 正文且不调用 `window.open`。
- 本地 Docker frontend 已重建并运行 image `sha256:ba7035d7c894f3b4368b567a1934dea34c509cce3edf494d1edb65fe92a33cca`；changed `rich-content.tsx` digest 为 `sha256:fb5348ef213a90112fad1b894300298d9f8c20a44a97886ffc3681b9d4b79692`。
- 旧 Web/mobile HTTP fetch 证据明确标记为 superseded；HTTP 200、raw bytes 或 download-only 均不再构成 `human_accessible=true`。
- 状态纠正使用 immutable manifest `/tmp/UNIDRAG-12-preview-readiness-correction-v1.manifest`，digest `sha256:605b64399604195a5dc135bd61d31d2cb7fe9a643ff70b7eb6d16c690ab756b5`；precondition 绑定 revision 53，写入后回读为 `in_progress@revision-54`。
- Codex bundled browser RPC 当时仍指向已删除的 `browser/26.825.32147`；独立 Chromium 可访问新部署但未带 Multica 登录态。用户于 2026-08-31 明确选择后续自行执行实际网页点击/下载验收，因此不把该项虚报为 automated PASS，也不再为此请求人工授权；实现验收以自动化回归、构建、部署与状态回读收口。
