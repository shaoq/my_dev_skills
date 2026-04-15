## 1. 脚本骨架与权限定义

- [x] 1.1 创建 `setup-skills-env.py`，包含 shebang、模块文档、`STANDARD_PERMISSIONS` 列表（含 openspec、git、mkdir、mcp__web-reader 等 22 条标准权限）
- [x] 1.2 实现 `generate_settings()` 函数：接收权限列表，生成 JSON 结构，写入 `.claude/settings.local.json`
- [x] 1.3 实现幂等合并逻辑：读取已有 settings（若存在），合并标准权限，保留用户自定义条目，去重后写入

## 2. Skill 符号链接安装

- [x] 2.1 实现 `scan_custom_skills()` 函数：glob 扫描根目录 `*/SKILL.md`（排除 `.claude/` 和 `openspec/`），返回 skill 名称和源路径列表
- [x] 2.2 实现 `install_skill_symlinks()` 函数：对每个 skill，创建 `.claude/skills/<name>/` 目录，创建相对路径 symlink `../../<name>/SKILL.md`
- [x] 2.3 实现幂等检查：若 symlink 已存在且有效 → 跳过；若 symlink 目标失效 → 重建；若为普通文件 → 跳过并警告

## 3. SKILL.md 扫描与解析

- [x] 3.1 实现 `parse_skill_frontmatter()` 函数：读取 SKILL.md，解析 frontmatter 提取 `allowed-tools` 和 `disable-model-invocation` 字段
- [x] 3.2 实现 `allowed-tools` 解析：提取 `Bash(xxx *)` 模式，转为 bash 命令前缀集合
- [x] 3.3 实现 `disable-model-invocation` 检测：检查 frontmatter 是否包含 `disable-model-invocation: true`

## 4. 交叉校验

- [x] 4.1 实现缺失权限警告：对比 skill 的 bash 前缀与标准权限列表，skill 使用但标准列表没有的打印警告
- [x] 4.2 实现无 guardrails 警告：对无 `allowed-tools` 且无 `disable-model-invocation` 的 skill 打印警告

## 5. 主入口与输出

- [x] 5.1 实现 `main()` 函数：调用 install symlinks → scan → check → generate 流程
- [x] 5.2 打印执行摘要：symlink 安装结果、权限配置结果、校验警告数
- [x] 5.3 添加 `if __name__ == "__main__"` 入口
