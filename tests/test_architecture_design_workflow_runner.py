from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]


class ArchitectureWorkflowRunnerSafetyTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.root = Path(self.temp_dir.name)

        tests_dir = self.root / "tests"
        tests_dir.mkdir()
        shutil.copy2(
            REPOSITORY_ROOT / "tests" / "architecture-design-workflow-safety.sh",
            tests_dir / "architecture-design-workflow-safety.sh",
        )
        shutil.copytree(
            REPOSITORY_ROOT / "tests" / "fixtures",
            tests_dir / "fixtures",
        )
        shutil.copytree(
            REPOSITORY_ROOT / "tests" / "evidence",
            tests_dir / "evidence",
        )
        shutil.copytree(
            REPOSITORY_ROOT / "architecture-design-workflow",
            self.root / "architecture-design-workflow",
        )

    def run_runner(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                "bash",
                str(self.root / "tests" / "architecture-design-workflow-safety.sh"),
                *arguments,
            ],
            cwd=self.root,
            check=False,
            capture_output=True,
            text=True,
        )

    def behavior_arguments(self, runtime: str = "codex") -> tuple[str, ...]:
        return (
            "--results-dir",
            str(self.root / "tests" / "evidence" / "architecture-design-workflow"),
            "--runtime",
            runtime,
        )

    def test_rejects_results_directory_outside_repository_without_traceback(self) -> None:
        outside = tempfile.TemporaryDirectory()
        self.addCleanup(outside.cleanup)

        result = self.run_runner(
            "--results-dir",
            outside.name,
            "--runtime",
            "codex",
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("results directory must stay inside the repository", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_fixture_missing_required_key_without_traceback(self) -> None:
        fixture = (
            self.root
            / "tests"
            / "fixtures"
            / "architecture-design-workflow"
            / "routine-bug.case.md"
        )
        fixture.write_text(
            re.sub(
                r'\s*"fixture_id":\s*"[^"]+",\n',
                "\n",
                fixture.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("missing keys: ['fixture_id']", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_noncanonical_runtime_before_reading_results(self) -> None:
        result = self.run_runner(*self.behavior_arguments("../../../outside"))

        self.assertEqual(2, result.returncode)
        self.assertIn("unsupported runtime", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_checks_text_after_result_envelope_for_forbidden_markers(self) -> None:
        result_file = (
            self.root
            / "tests"
            / "evidence"
            / "architecture-design-workflow"
            / "explore-direct-proposal.codex.md"
        )
        result_file.write_text(
            result_file.read_text(encoding="utf-8")
            + "\nOpenSpec proposal 已创建\n",
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("contains forbidden marker", result.stdout)

    def test_reports_missing_results_directory_argument_as_usage_error(self) -> None:
        result = self.run_runner("--results-dir")

        self.assertEqual(2, result.returncode)
        self.assertIn("--results-dir requires a non-empty value", result.stderr)

    def test_rejects_unhashable_planned_writes_without_traceback(self) -> None:
        result_file = (
            self.root
            / "tests"
            / "evidence"
            / "architecture-design-workflow"
            / "routine-bug.codex.md"
        )
        result_file.write_text(
            re.sub(
                r'"planned_writes":\[[^]]*\]',
                '"planned_writes":[{}]',
                result_file.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("planned_writes must be a list of strings", result.stdout)
        self.assertNotIn("Traceback", result.stderr)

    def test_rejects_unhashable_evidence_fields_without_traceback(self) -> None:
        result_file = (
            self.root
            / "tests"
            / "evidence"
            / "architecture-design-workflow"
            / "routine-bug.codex.md"
        )
        result_file.write_text(
            re.sub(
                r'"evidence_fields":\[[^]]*\]',
                '"evidence_fields":[{}]',
                result_file.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("evidence_fields must be a list of strings", result.stdout)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
