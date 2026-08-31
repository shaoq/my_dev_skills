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
        shutil.copy2(
            REPOSITORY_ROOT / "tests" / "architecture_design_workflow_safety.py",
            tests_dir / "architecture_design_workflow_safety.py",
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

    def test_rejects_noncanonical_packet_digest(self) -> None:
        result_file = (
            self.root
            / "tests"
            / "evidence"
            / "architecture-design-workflow"
            / "routine-bug.codex.md"
        )
        result_file.write_text(
            re.sub(
                r'"packet_digest":"none"',
                '"packet_digest":"SHA256:not-canonical"',
                result_file.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("packet_digest must be none or canonical sha256", result.stdout)

    def test_rejects_noncanonical_evidence_timestamp(self) -> None:
        result_file = (
            self.root
            / "tests"
            / "evidence"
            / "architecture-design-workflow"
            / "routine-bug.codex.md"
        )
        result_file.write_text(
            re.sub(
                r'"evidence_recorded_at":"none"',
                '"evidence_recorded_at":"2026-08-30 12:00"',
                result_file.read_text(encoding="utf-8"),
                count=1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner(*self.behavior_arguments())

        self.assertEqual(1, result.returncode)
        self.assertIn("evidence_recorded_at must be none or RFC 3339 UTC", result.stdout)

    def test_rejects_platform_specific_core_marker(self) -> None:
        control_template = self.root / "architecture-design-workflow" / "templates" / "arch-control.md"
        control_template.write_text(
            control_template.read_text(encoding="utf-8") + "\n- parent_id: forbidden\n",
            encoding="utf-8",
        )

        result = self.run_runner()

        self.assertEqual(1, result.returncode)
        self.assertIn("platform-specific core marker", result.stdout)

    def test_rejects_readiness_embedded_in_packet_payload(self) -> None:
        packet_template = (
            self.root
            / "architecture-design-workflow"
            / "templates"
            / "arch-approval-packet.md"
        )
        packet_template.parent.mkdir(parents=True, exist_ok=True)
        packet_template.write_text(
            "# ARCH-APPROVAL-PACKET vN\n\n- review_packet_ready: true\n",
            encoding="utf-8",
        )

        result = self.run_runner()

        self.assertEqual(1, result.returncode)
        self.assertIn("packet payload embeds post-finalization evidence", result.stdout)

    def test_static_contract_accepts_repository_skill(self) -> None:
        result = self.run_runner()

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn("architecture workflow safety: PASS", result.stdout)

    def test_rejects_incomplete_reviewable_clarification_contract(self) -> None:
        control_template = self.root / "architecture-design-workflow" / "templates" / "arch-control.md"
        control_template.write_text(
            control_template.read_text(encoding="utf-8").replace(
                "- Candidate recommendation：具体候选值；或 `no_recommendation` 及原因",
                "",
                1,
            ),
            encoding="utf-8",
        )

        result = self.run_runner()

        self.assertEqual(1, result.returncode)
        self.assertIn("ARCH-CONTROL missing reviewable clarification slots", result.stdout)

    def test_rejects_incomplete_human_action_contract(self) -> None:
        action_template = (
            self.root
            / "architecture-design-workflow"
            / "templates"
            / "human-action-request.md"
        )
        action_template.parent.mkdir(parents=True, exist_ok=True)
        action_template.write_text(
            "# Human Action Request\n\n## Action summary\n",
            encoding="utf-8",
        )

        result = self.run_runner()

        self.assertEqual(1, result.returncode)
        self.assertIn("Human Action Request missing required slots", result.stdout)

    def test_rejects_incomplete_standalone_architecture_design_contract(self) -> None:
        design_template = (
            self.root
            / "architecture-design-workflow"
            / "templates"
            / "arch-design.md"
        )
        design_template.write_text(
            "# ARCH-DESIGN vN\n\n## Summary\n\n## Open questions\n",
            encoding="utf-8",
        )

        result = self.run_runner()

        self.assertEqual(1, result.returncode)
        self.assertIn("ARCH-DESIGN missing standalone architecture slots", result.stdout)


if __name__ == "__main__":
    unittest.main()
