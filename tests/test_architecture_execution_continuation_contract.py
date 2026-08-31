from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "architecture-design-workflow"
ADAPTER = ROOT / "multica-architecture-approval-adapter"
CASES = ROOT / "tests/fixtures/multica-architecture-approval-adapter/execution-continuation-cases.json"


class ArchitectureExecutionContinuationContractTest(unittest.TestCase):
    def test_portable_core_declares_platform_neutral_continuation_gate(self) -> None:
        reference = CORE / "references/execution-continuation.md"
        self.assertTrue(reference.is_file(), "missing portable execution continuation contract")
        text = reference.read_text(encoding="utf-8")
        for marker in (
            "execution_continuation_v1",
            "continuation_id",
            "next_executor_ref",
            "next_executor_role",
            "input_artifact_ref",
            "input_artifact_version",
            "completion_condition",
            "planned|accepted|active|waiting_human|blocked|terminal",
            "platform_status_intent=agent_working",
            "accepted|active",
            "evidence_ref",
        ):
            self.assertIn(marker, text, f"portable continuation contract missing {marker}")
        for platform_marker in (
            "mention://member/",
            "multica issue",
            "queued|running",
            "member UUID",
        ):
            self.assertNotIn(platform_marker, text, f"portable core leaked {platform_marker}")

    def test_adapter_declares_dedicated_handoff_and_task_readback(self) -> None:
        reference = ADAPTER / "references/execution-handoff-and-task-readback.md"
        self.assertTrue(reference.is_file(), "missing Multica execution handoff contract")
        text = reference.read_text(encoding="utf-8")
        for marker in (
            "multica_execution_handoff_v1",
            "next_executor_id",
            "next_executor_role",
            "input_artifact_ref",
            "input_artifact_version",
            "completion_condition",
            "handoff_id",
            "queued_task_id",
            "accepted_task_status=queued|waiting_local_directory",
            "active_task_status=running",
            "predecessor_task_id",
            "same in_place directory lock",
            "dedicated handoff comment",
            "self-handoff",
            "single-consumption",
            "ARCH-CONTROL",
            "requires_human_review=false",
            "in_progress + WAIT_REASON=none",
        ):
            self.assertIn(marker, text, f"adapter handoff contract missing {marker}")

    def test_fixture_cases_cover_orphan_self_cross_member_and_replay(self) -> None:
        cases = json.loads(CASES.read_text(encoding="utf-8"))
        by_id = {case["case_id"]: case for case in cases}
        self.assertEqual(
            {
                "orphaned-in-progress",
                "arch-control-self-mention",
                "cross-member-queued",
                "cross-member-waiting-local-directory",
                "dedicated-self-handoff-running",
                "replayed-handoff",
            },
            set(by_id),
        )
        self.assertEqual("fail_closed", by_id["orphaned-in-progress"]["expected"])
        self.assertEqual("no_trigger", by_id["arch-control-self-mention"]["expected"])
        self.assertEqual("accepted", by_id["cross-member-queued"]["expected"])
        self.assertEqual("accepted", by_id["cross-member-waiting-local-directory"]["expected"])
        self.assertEqual("active", by_id["dedicated-self-handoff-running"]["expected"])
        self.assertEqual("reconciliation_noop", by_id["replayed-handoff"]["expected"])

    def test_existing_skill_surfaces_route_to_continuation_contracts(self) -> None:
        required = {
            CORE / "SKILL.md": ("execution_continuation_v1", "execution-continuation.md"),
            CORE / "references/workflow-mandate-and-review-gates.md": (
                "execution_continuation_v1",
                "accepted|active",
            ),
            CORE / "templates/arch-control.md": (
                "Execution continuation",
                "Completion condition",
                "Continuation evidence",
            ),
            ADAPTER / "SKILL.md": (
                "multica_execution_handoff_v1",
                "execution-handoff-and-task-readback.md",
            ),
            ADAPTER / "references/architecture-operation-manifest.md": (
                "handoff_id",
                "queued_task_id",
                "queued_task_status",
            ),
        }
        failures: list[str] = []
        for path, markers in required.items():
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            failures.extend(
                f"{path.relative_to(ROOT)} missing {marker}"
                for marker in markers
                if marker not in text
            )
        self.assertFalse(failures, "continuation surfaces incomplete:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
