from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "architecture-design-workflow"
ADAPTER = ROOT / "multica-architecture-approval-adapter"
CORE_CASES = ROOT / "tests/fixtures/architecture-design-workflow/simplified-deliverables-cases.json"
ADAPTER_CASES = ROOT / "tests/fixtures/multica-architecture-approval-adapter/simplified-delivery-cases.json"
ADAPTER_SCHEMA = ROOT / "tests/fixtures/multica-architecture-approval-adapter/simplified-delivery.schema.json"


class SimplifiedArchitectureDeliverablesContractTest(unittest.TestCase):
    def test_core_declares_two_surfaces_and_one_human_canonical_design(self) -> None:
        surfaces = {
            CORE / "SKILL.md": (
                "human_review_surface_v1",
                "architecture_internal_evidence_v1",
                "唯一 mandatory human artifact",
                "ARCH-DESIGN-vN.md",
            ),
            CORE / "references/solution-design.md": (
                "design_maturity=directional|spec_ready|implementation_ready",
                "唯一 human_canonical",
                "Owner",
                "关闭条件",
                "阻止的下游阶段",
            ),
            CORE / "references/architecture-review.md": (
                "version-bound",
                "不得复制 Design",
                "新 Design 版本",
            ),
            CORE / "references/approval-packet-and-human-gate.md": (
                "machine_only",
                "current Action",
                "不要求人类打开",
                "不要求复制 packet digest",
            ),
        }
        missing: list[str] = []
        for path, markers in surfaces.items():
            text = path.read_text(encoding="utf-8")
            missing.extend(f"{path.relative_to(ROOT)} missing {marker}" for marker in markers if marker not in text)
        self.assertFalse(missing, "\n".join(missing))

    def test_core_contract_fixtures_cover_maturity_impact_visual_and_legacy(self) -> None:
        cases = json.loads(CORE_CASES.read_text(encoding="utf-8"))
        self.assertEqual({"directional", "spec_ready", "implementation_ready"}, {case["maturity"] for case in cases["maturity_cases"]})
        self.assertEqual("fail_closed", cases["maturity_cases"][0]["expected"])
        self.assertEqual("architecture_impact", cases["impact_cases"][-1]["classification"])
        self.assertEqual("must_not_reinterpret_as_v2", cases["legacy_attempt"]["writer"])
        self.assertEqual("return_to_architecture_team", cases["rnd_cases"]["architecture_boundary_change"]["expected"])
        self.assertFalse(cases["rnd_cases"]["internal_handoff"]["presentation_diagram"])
        visual_by_id = {case["case_id"]: case for case in cases["visual_cases"]}
        for case_id in ("browser-failed", "browser-skipped", "review-failed", "review-skipped", "semantic-open", "stale-preview"):
            self.assertEqual("fail_closed", visual_by_id[case_id]["expected"])
        self.assertEqual("light/1440x900", visual_by_id["all-passed"]["preview"])

    def test_visual_contract_is_complete_and_fail_closed(self) -> None:
        required = {
            CORE / "references/solution-design.md": (
                "architecture_visual_manifest_v1",
                "diagram_not_applicable",
                "最多两张附加图",
                "quality_profile=showcase",
                "light",
                "1440x900",
            ),
            CORE / "references/architecture-review.md": (
                "diagram_id",
                "node ID",
                "edge ID",
                "message ID",
                "state ID",
                "visual_review=passed",
            ),
            CORE / "templates/arch-design.md": (
                "Architecture visual manifest",
                "static_preview_ref",
                "browser_evidence=passed",
                "visual_review=passed",
            ),
        }
        missing: list[str] = []
        for path, markers in required.items():
            text = path.read_text(encoding="utf-8")
            missing.extend(f"{path.relative_to(ROOT)} missing {marker}" for marker in markers if marker not in text)
        self.assertFalse(missing, "\n".join(missing))

    def test_impact_and_internal_handoff_contracts_replace_human_comments(self) -> None:
        required = {
            CORE / "references/architecture-design-impact.md": (
                "architecture_design_impact_v1",
                "no_architecture_impact",
                "architecture_impact",
                "unknown",
                "supersede",
            ),
            CORE / "references/execution-continuation.md": (
                "architecture_internal_evidence_v1",
                "不得生成 dedicated human handoff comment",
                "accepted|active",
            ),
            CORE / "references/rnd-handoff.md": (
                "design_maturity=spec_ready|implementation_ready",
                "批准图",
                "architecture_design_impact_v1",
                "最多一次终态人类摘要",
            ),
        }
        missing: list[str] = []
        for path, markers in required.items():
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            missing.extend(f"{path.relative_to(ROOT)} missing {marker}" for marker in markers if marker not in text)
        self.assertFalse(missing, "\n".join(missing))

    def test_adapter_uses_one_design_and_internal_evidence(self) -> None:
        required = {
            ADAPTER / "SKILL.md": (
                "multica_human_action_material_bundle_v2",
                "恰好一份 canonical Design Markdown attachment",
                "architecture_internal_evidence_v1",
                "不得生成 dedicated Agent handoff comment",
            ),
            ADAPTER / "references/human-action-material-bundle.md": (
                "multica_human_action_material_bundle_v2",
                "exactly one",
                "derived_non_authoritative",
                "legacy",
            ),
            ADAPTER / "references/execution-handoff-and-task-readback.md": (
                "internal task evidence",
                "zero ordinary Issue comments",
                "accepted|active",
            ),
            ADAPTER / "templates/multica-approval-comment.md": (
                "Design maturity",
                "Reviewer conclusion",
                "恰好一份",
                "材料打不开",
            ),
        }
        missing: list[str] = []
        for path, markers in required.items():
            text = path.read_text(encoding="utf-8")
            missing.extend(f"{path.relative_to(ROOT)} missing {marker}" for marker in markers if marker not in text)
        self.assertFalse(missing, "\n".join(missing))

    def test_archify_binding_profile_is_additive_and_role_minimized(self) -> None:
        cases = json.loads(ADAPTER_CASES.read_text(encoding="utf-8"))
        schema = json.loads(ADAPTER_SCHEMA.read_text(encoding="utf-8"))
        self.assertEqual(set(schema["required"]), set(cases))
        self.assertEqual(
            schema["properties"]["current_writer"]["properties"]["canonical_attachments"]["const"],
            cases["current_writer"]["canonical_attachments"],
        )
        self.assertEqual(4, len(cases["archify_bindings"]))
        self.assertEqual("additive", cases["activation"]["binding_mode"])
        self.assertTrue(cases["activation"]["new_attempts_only"])
        self.assertEqual("retain_and_report_not_active", cases["activation"]["partial_binding_failure"])
        self.assertEqual("forbidden", cases["activation"]["non_target_binding"])
        self.assertEqual(
            {"ready", "unavailable"},
            {case["expected"] for case in cases["visual_activation_cases"]},
        )
        profile = ADAPTER / "references/archify-agent-bindings.md"
        text = profile.read_text(encoding="utf-8") if profile.is_file() else ""
        for marker in (
            "bb71ccdd64cd3a74ba7cbd25bbacc7382da34410",
            "ed178d2ddd8861db1b8e867f32be7764bdec221d44568c37b6ae157c5e7f111c",
            "Solution Architect",
            "Architecture Reviewer",
            "Product & Spec Engineer",
            "Solution Review Architect",
            "review-only",
            "additive",
        ):
            self.assertIn(marker, text)

    def test_readme_describes_current_and_legacy_contracts(self) -> None:
        text = (ROOT / "README.md").read_text(encoding="utf-8")
        for marker in (
            "唯一 mandatory Design",
            "human_review_surface_v1",
            "architecture_internal_evidence_v1",
            "无需人工打开 Review、Packet、Control",
            "required visual",
            "四个 Archify 目标 Agent",
            "旧三附件 attempt 只读",
        ):
            self.assertIn(marker, text)

    def test_workspace_export_profile_records_four_targets_without_live_write(self) -> None:
        path = ADAPTER / "deployment-profiles/unidocs-rag-architecture-rd-teams.yaml"
        text = path.read_text(encoding="utf-8")
        for marker in (
            "account: allen@qq.com",
            "workspace_slug: unidocs-rag",
            "import_mode: conflict_fail",
            "binding_mode: additive",
            "name: Solution Architect",
            "name: Architecture Reviewer",
            "name: Product & Spec Engineer",
            "name: Solution Review Architect",
            "live_write: not_run",
        ):
            self.assertIn(marker, text)


if __name__ == "__main__":
    unittest.main()
