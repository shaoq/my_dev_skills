## Context

项目根目录下有 5 个自定义 skill，源文件在 `*/SKILL.md`（git tracked）。同时 `.claude/skills/` 下有 openspec 核心技能（gitignored，用户手动安装）。`.claude/settings.local.json` 维护全局权限白名单（gitignored）。新 clone 后需一键配置：创建 symlink 统一 skill 入口、生成 settings、交叉校验一致性。

## Goals / Non-Goals

**Goals:**
- 为根目录自定义 skill 在 `.claude/skills/` 创建符号链接，统一管理入口
- 一键生成 `.claude/settings.local.json`
- 交叉校验 SKILL.md 的 allowed-tools 与 settings 的一致性
- 幂等执行，可重复运行

**Non-Goals:**
- 不处理 openspec 核心技能的安装（用户手动管理 `.claude/skills/openspec-*/`）
- 不处理 `.claude/commands/opsx/` 的安装（用户手动管理）
- 不自动从 SKILL.md 提取生成 settings（粒度不匹配）
- 不修改任何 SKILL.md 文件

## Decisions

### Decision 1: 使用相对路径符号链接

**选择**: `os.symlink("../../<name>/SKILL.md", ".claude/skills/<name>/SKILL.md")`

**替代方案**:
- A) 复制文件 — 源文件更新后副本不同步
- B) 绝对路径 symlink — 不可移植

**理由**: 相对路径 symlink 保证源文件更新后立即生效，且可跨机器使用。

### Decision 2: 标准权限列表硬编码在脚本内

**选择**: 脚本内维护 `STANDARD_PERMISSIONS` 列表作为 truth

**替代方案**:
- 从 SKILL.md 自动提取生成 — 粒度不匹配，2 个 skill 无 allowed-tools

**理由**: 权限列表相对稳定，脚本即文档。

### Decision 3: 交叉校验仅输出警告不自动修复

**理由**: settings 的权限粒度比 skill 更细（`git add:*` vs `git *`），自动修复会丢失细粒度控制。

### Decision 4: 幂等设计——已有 symlink 检查有效性

**选择**: 若 symlink 已存在且目标有效 → 跳过；若目标失效 → 重新创建

**理由**: 支持重复执行不报错，同时修复失效链接。

## Risks / Trade-offs

| 风险 | 影响 | 缓解 |
|------|------|------|
| Windows 不支持 symlink | Windows 用户需管理员权限或开发者模式 | 检测 OS，Windows 上提示或 fallback 为复制 |
| 新增 skill 后需手动更新脚本中的权限列表 | 低风险 | 脚本会检测并警告缺失权限 |
| 已有同名文件（非 symlink）在 .claude/skills/ 下 | 可能覆盖用户手动创建的内容 | 检测：若是普通文件 → 跳过并警告，不覆盖 |
