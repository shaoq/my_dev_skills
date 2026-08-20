from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import os
import tempfile
import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = PROJECT_ROOT / "setup-skills-env.py"


def load_setup_module():
    spec = importlib.util.spec_from_file_location("setup_skills_env", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load setup-skills-env.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillLinkTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_setup_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.source = self.root / "repo" / "demo-skill"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("---\nname: demo-skill\ndescription: demo\n---\n")
        self.skills = [("demo-skill", self.source / "SKILL.md")]
        self.claude_dir = self.root / "home" / ".claude" / "skills"
        self.codex_dir = self.root / "home" / ".codex" / "skills"

    def test_install_reports_create_skip_and_replacement(self) -> None:
        first = self.module.install_skill_symlinks(self.skills, self.claude_dir)
        self.assertEqual((first.created, first.skipped, first.replaced, first.warnings), (1, 0, 0, 0))
        self.assertEqual((self.claude_dir / "demo-skill").resolve(), self.source.resolve())

        second = self.module.install_skill_symlinks(self.skills, self.claude_dir)
        self.assertEqual((second.created, second.skipped, second.replaced, second.warnings), (0, 1, 0, 0))

        foreign = self.root / "foreign"
        foreign.mkdir()
        (self.claude_dir / "demo-skill").unlink()
        os.symlink(foreign, self.claude_dir / "demo-skill")
        third = self.module.install_skill_symlinks(self.skills, self.claude_dir)
        self.assertEqual((third.created, third.skipped, third.replaced, third.warnings), (0, 0, 1, 0))
        self.assertEqual((self.claude_dir / "demo-skill").resolve(), self.source.resolve())

    def test_install_preserves_regular_target(self) -> None:
        target = self.claude_dir / "demo-skill"
        target.mkdir(parents=True)
        marker = target / "keep.txt"
        marker.write_text("keep", encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            result = self.module.install_skill_symlinks(self.skills, self.claude_dir)

        self.assertEqual((result.created, result.skipped, result.replaced, result.warnings), (0, 0, 0, 1))
        self.assertEqual(marker.read_text(encoding="utf-8"), "keep")

    def test_uninstall_removes_owned_link_and_preserves_foreign_targets(self) -> None:
        self.module.install_skill_symlinks(self.skills, self.claude_dir)
        owned = self.module.uninstall_skill_symlinks(self.skills, self.claude_dir)
        self.assertEqual((owned.removed, owned.not_found, owned.warnings), (1, 0, 0))
        self.assertFalse((self.claude_dir / "demo-skill").exists())

        foreign = self.root / "foreign"
        foreign.mkdir()
        os.symlink(foreign, self.claude_dir / "demo-skill")
        with contextlib.redirect_stdout(io.StringIO()):
            preserved = self.module.uninstall_skill_symlinks(self.skills, self.claude_dir)
        self.assertEqual((preserved.removed, preserved.not_found, preserved.warnings), (0, 0, 1))
        self.assertTrue((self.claude_dir / "demo-skill").is_symlink())

    def test_install_processes_both_runtimes_when_one_conflicts(self) -> None:
        conflict = self.claude_dir / "demo-skill"
        conflict.mkdir(parents=True)
        (conflict / "keep.txt").write_text("keep", encoding="utf-8")

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.module.install_runtime_skill_links(
                self.skills,
                (("Claude Code", self.claude_dir), ("Codex", self.codex_dir)),
            )

        self.assertEqual(results["Claude Code"].warnings, 1)
        self.assertEqual(results["Codex"].created, 1)
        self.assertEqual((self.codex_dir / "demo-skill").resolve(), self.source.resolve())

    def test_uninstall_processes_both_runtimes_independently(self) -> None:
        self.module.install_skill_symlinks(self.skills, self.claude_dir)
        foreign = self.root / "foreign"
        foreign.mkdir()
        self.codex_dir.mkdir(parents=True)
        os.symlink(foreign, self.codex_dir / "demo-skill")

        with contextlib.redirect_stdout(io.StringIO()):
            results = self.module.uninstall_runtime_skill_links(
                self.skills,
                (("Claude Code", self.claude_dir), ("Codex", self.codex_dir)),
            )

        self.assertEqual(results["Claude Code"].removed, 1)
        self.assertEqual(results["Codex"].warnings, 1)
        self.assertTrue((self.codex_dir / "demo-skill").is_symlink())


class FullInstallerIsolationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_setup_module()
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)
        self.repo = self.root / "repo"
        skill = self.repo / "demo-skill"
        skill.mkdir(parents=True)
        (skill / "SKILL.md").write_text(
            "---\nname: demo-skill\ndescription: demo\nallowed-tools: Bash(openspec validate:*)\n---\n",
            encoding="utf-8",
        )
        self.home = self.root / "home"
        self.module.PROJECT_ROOT = self.repo
        self.module.HOME_CLAUDE_DIR = self.home / ".claude"
        self.module.HOME_CODEX_DIR = self.home / ".codex"
        self.module.GLOBAL_SETTINGS_PATH = self.module.HOME_CLAUDE_DIR / "settings.json"

    def test_full_install_creates_both_links_and_only_claude_settings(self) -> None:
        codex_config = self.module.HOME_CODEX_DIR / "config.toml"
        codex_config.parent.mkdir(parents=True)
        codex_config.write_text("model = 'preserve'\n", encoding="utf-8")

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.module.install()

        source = self.repo / "demo-skill"
        self.assertEqual((self.module.HOME_CLAUDE_DIR / "skills" / "demo-skill").resolve(), source.resolve())
        self.assertEqual((self.module.HOME_CODEX_DIR / "skills" / "demo-skill").resolve(), source.resolve())
        settings = json.loads(self.module.GLOBAL_SETTINGS_PATH.read_text(encoding="utf-8"))
        self.assertIn("Bash(openspec validate:*)", settings["permissions"]["allow"])
        self.assertEqual(codex_config.read_text(encoding="utf-8"), "model = 'preserve'\n")
        self.assertIn("Claude Code", output.getvalue())
        self.assertIn("Codex", output.getvalue())

    def test_full_uninstall_removes_owned_links_from_both_runtimes(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            self.module.install()
            self.module.uninstall()

        self.assertFalse((self.module.HOME_CLAUDE_DIR / "skills" / "demo-skill").exists())
        self.assertFalse((self.module.HOME_CODEX_DIR / "skills" / "demo-skill").exists())


class FrontmatterConsistencyTests(unittest.TestCase):
    def test_specific_read_only_bash_rules_are_recognized_by_command_prefix(self) -> None:
        module = load_setup_module()
        with tempfile.TemporaryDirectory() as temp_dir:
            skill_file = Path(temp_dir) / "SKILL.md"
            skill_file.write_text(
                "---\n"
                "name: review\n"
                "description: review\n"
                "allowed-tools: Bash(openspec status *) Bash(openspec validate *) "
                "Bash(git status *) Bash(git diff *) Read\n"
                "---\n",
                encoding="utf-8",
            )

            prefixes, disabled = module.parse_skill_frontmatter(skill_file)
            warnings = module.check_skill_consistency(
                [("review", skill_file)], module.STANDARD_PERMISSIONS
            )

        self.assertEqual(prefixes, ["openspec", "openspec", "git", "git"])
        self.assertFalse(disabled)
        self.assertEqual(warnings, 0)


if __name__ == "__main__":
    unittest.main()
