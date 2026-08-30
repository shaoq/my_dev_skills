from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path
from typing import Any


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
FIXTURE_ROOT = REPOSITORY_ROOT / "tests" / "fixtures" / "multica-architecture-approval-adapter"
CASES_ROOT = FIXTURE_ROOT / "cases"
SCHEMA_PATH = FIXTURE_ROOT / "result.schema.json"
HUMAN_ACTION_CASES_ROOT = FIXTURE_ROOT / "human-action-cases"
HUMAN_ACTION_SCHEMA_PATH = FIXTURE_ROOT / "human-action.schema.json"
REQUIRED_ADAPTER_SURFACES = (
    "multica-architecture-approval-adapter/SKILL.md",
    "multica-architecture-approval-adapter/templates/multica-approval-comment.md",
    "multica-architecture-approval-adapter/templates/multica-readiness-evidence.md",
    "multica-architecture-approval-adapter/templates/multica-decision-evidence.md",
    "multica-architecture-approval-adapter/templates/multica-human-action-request.md",
    "multica-architecture-approval-adapter/templates/multica-operational-authorization.md",
    "multica-architecture-approval-adapter/references/delivery-mapping-and-marker.md",
    "multica-architecture-approval-adapter/references/reconciliation-projection-and-readiness.md",
    "multica-architecture-approval-adapter/references/human-decision-binding.md",
    "multica-architecture-approval-adapter/references/durable-evidence-records.md",
    "multica-architecture-approval-adapter/references/operational-authorization.md",
)
EXPECTED_HUMAN_ACTION_FAMILIES = {
    "buried-approval-choices": "decision_first_approval",
    "missing-operational-authorization": "operational_authorization",
    "partial-failure-retry": "retry_authorization",
    "per-artifact-mobile-access": "per_artifact_access",
    "token-plus-prose-revision": "decision_context_separation",
}
EXPECTED_FAMILIES = {
    "activation-boundary": "activation_boundary",
    "capability-missing": "capability_missing",
    "core-absent": "core_absent",
    "core-incompatible": "core_incompatible",
    "digest-mismatch": "digest_mismatch",
    "edited-decision": "edited_decision",
    "invalid-nontarget-decision": "invalid_nontarget_decision",
    "missing-decision-binding": "missing_decision_binding",
    "retry-reconciliation": "retry_reconciliation",
    "successful-delivery": "successful_delivery",
    "superseded-decision": "superseded_decision",
    "target-human-decision": "target_human_decision",
}


def validate_json_schema(instance: Any, schema: dict[str, Any], root: dict[str, Any], path: str = "$") -> None:
    if "$ref" in schema:
        reference = schema["$ref"]
        if not reference.startswith("#/"):
            raise ValueError(f"{path}: unsupported ref {reference}")
        resolved: Any = root
        for segment in reference[2:].split("/"):
            resolved = resolved[segment]
        validate_json_schema(instance, resolved, root, path)
        return

    if "oneOf" in schema:
        failures: list[str] = []
        for candidate in schema["oneOf"]:
            try:
                validate_json_schema(instance, candidate, root, path)
                return
            except ValueError as error:
                failures.append(str(error))
        raise ValueError(f"{path}: no oneOf branch matched ({'; '.join(failures)})")

    expected_type = schema.get("type")
    types = expected_type if isinstance(expected_type, list) else [expected_type]
    if expected_type is not None:
        matches_type = {
            "object": isinstance(instance, dict),
            "array": isinstance(instance, list),
            "string": isinstance(instance, str),
            "boolean": isinstance(instance, bool),
        }
        if not any(matches_type.get(candidate, False) for candidate in types):
            raise ValueError(f"{path}: expected type {expected_type}")

    if "enum" in schema and instance not in schema["enum"]:
        raise ValueError(f"{path}: value {instance!r} is not in enum")
    if isinstance(instance, str):
        if "minLength" in schema and len(instance) < schema["minLength"]:
            raise ValueError(f"{path}: string is shorter than minLength")
        if "pattern" in schema and re.fullmatch(schema["pattern"], instance) is None:
            raise ValueError(f"{path}: string does not match pattern")
    if isinstance(instance, dict):
        properties = schema.get("properties", {})
        for key in schema.get("required", []):
            if key not in instance:
                raise ValueError(f"{path}: missing required key {key}")
        if schema.get("additionalProperties") is False:
            unexpected = set(instance) - set(properties)
            if unexpected:
                raise ValueError(f"{path}: unexpected keys {sorted(unexpected)}")
        for key, value in instance.items():
            if key in properties:
                validate_json_schema(value, properties[key], root, f"{path}.{key}")
    if isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            raise ValueError(f"{path}: fewer than minItems")
        if "maxItems" in schema and len(instance) > schema["maxItems"]:
            raise ValueError(f"{path}: more than maxItems")
        if "items" in schema:
            for index, value in enumerate(instance):
                validate_json_schema(value, schema["items"], root, f"{path}[{index}]")


def validate_fixture(instance: dict[str, Any], schema: dict[str, Any]) -> None:
    validate_json_schema(instance, schema, schema)
    result = instance["expected_result"]
    readiness = result["readiness"]
    if readiness["state"] == "review_packet_ready":
        review = result["review"]
        packet = result["packet"]
        delivery = result["delivery"]
        target_human = result["target_human"]
        if review["conclusion"] not in {"APPROVABLE_WITH_WARNINGS", "APPROVABLE"}:
            raise ValueError("$.expected_result.review.conclusion: ready requires approvable conclusion")
        if packet["digest"] == "none" or readiness["packet_digest"] == "none" or packet["digest"] != readiness["packet_digest"]:
            raise ValueError("$.expected_result.readiness.packet_digest: ready requires current non-none packet digest")
        if delivery["state"] != "ready" or delivery["fence_outcome"] != "current":
            raise ValueError("$.expected_result.delivery: ready requires ready/current delivery")
        if delivery["delivery_evidence_ref"] == "none" or readiness["delivery_evidence_ref"] != delivery["delivery_evidence_ref"]:
            raise ValueError("$.expected_result.delivery_evidence_ref: ready requires matching non-none delivery evidence")
        if not readiness["evidence_ref"].startswith("workspace://"):
            raise ValueError("$.expected_result.readiness.evidence_ref: ready requires workspace sidecar")
        if (
            target_human["mapping_status"] != "unique"
            or target_human["actor_id"] == "none"
            or target_human["mapping_evidence_ref"] == "none"
            or target_human["access_confirmation"] != "confirmed"
        ):
            raise ValueError("$.expected_result.target_human: ready requires unique confirmed target human")
        artifact_kinds = [artifact["artifact_kind"] for artifact in readiness["artifacts"]]
        if len(artifact_kinds) != 3 or set(artifact_kinds) != {"design", "review", "packet"}:
            raise ValueError("$.expected_result.readiness.artifacts: ready requires unique design, review, packet artifacts")
        for artifact in readiness["artifacts"]:
            if artifact["expected_digest"] == "none" or artifact["verified_digest"] == "none" or artifact["expected_digest"] != artifact["verified_digest"]:
                raise ValueError("$.expected_result.readiness.artifacts: ready requires matching non-none digests")
            if artifact["issue_ref"] != delivery["issue_ref"] or artifact["comment_ref"] != delivery["comment_ref"]:
                raise ValueError("$.expected_result.readiness.artifacts: ready artifact must match delivery identity")
            if artifact["target_human_mapping_evidence_ref"] != target_human["mapping_evidence_ref"]:
                raise ValueError("$.expected_result.readiness.artifacts: ready artifact mapping must match target mapping")
            if not artifact["target_human_mapping_evidence_ref"].startswith("workspace://"):
                raise ValueError("$.expected_result.readiness.artifacts: ready artifact mapping must be workspace sidecar")
            if artifact["stable_access_ref"] == "none" or artifact["verifier"] == "none" or artifact["verified_at"] == "none":
                raise ValueError("$.expected_result.readiness.artifacts: ready artifact requires durable verification")
            stable_ref = artifact["stable_access_ref"].lower()
            if "download_url" in stable_ref or "signature" in stable_ref or "x-amz-" in stable_ref:
                raise ValueError("$.expected_result.readiness.artifacts: signed download URL is not durable")

    decision = result["decision"]
    if decision != "none" and decision["evidence_status"] == "valid":
        packet = result["packet"]
        delivery = result["delivery"]
        target_human = result["target_human"]
        workflow = result["workflow"]
        if readiness["state"] != "review_packet_ready":
            raise ValueError("$.expected_result.decision: valid decision requires current ready readiness")
        if decision["author_type"] != "member" or decision["author_id"] != target_human["actor_id"]:
            raise ValueError("$.expected_result.decision: valid decision requires canonical member author")
        if decision["target_human_mapping_evidence_ref"] != target_human["mapping_evidence_ref"]:
            raise ValueError("$.expected_result.decision: valid decision mapping must match readiness")
        if (decision["packet_ref"], decision["packet_version"], decision["packet_digest"]) != (packet["ref"], packet["version"], packet["digest"]):
            raise ValueError("$.expected_result.decision: valid decision packet identity must match current packet")
        if decision["reread_status"] != "verified":
            raise ValueError("$.expected_result.decision: valid decision requires verified reread")
        for field in ("binding_profile", "evidence_ref", "content_digest", "created_at", "updated_at", "recorded_at"):
            if decision[field] == "none":
                raise ValueError(f"$.expected_result.decision.{field}: valid decision requires evidence")
        if not decision["evidence_ref"].startswith("workspace://"):
            raise ValueError("$.expected_result.decision.evidence_ref: valid decision requires workspace sidecar")
        if decision["binding_profile"] == "multica_packet_comment_reply_v1":
            if delivery["comment_ref"] not in decision["parent_chain"]:
                raise ValueError("$.expected_result.decision.parent_chain: reply must contain exact delivery comment")
        elif decision["binding_profile"] == "multica_explicit_packet_reference_v1":
            if decision["explicit_packet_identity"] != packet:
                raise ValueError("$.expected_result.decision.explicit_packet_identity: explicit decision must name current packet")
        else:
            raise ValueError("$.expected_result.decision.binding_profile: valid decision requires supported profile")
        token_stage = {
            "approved_design_only": "approved_design_only",
            "approved_for_spec": "approved_for_spec",
            "revision_requested": "designing",
            "rejected": "rejected",
        }
        if workflow["stage"] != token_stage[decision["token"]]:
            raise ValueError("$.expected_result.workflow.stage: valid decision token/stage mismatch")


class MulticaArchitectureApprovalAdapterContractTest(unittest.TestCase):
    def load_schema(self) -> dict[str, Any]:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    def load_cases(self) -> dict[str, dict[str, Any]]:
        return {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(CASES_ROOT.glob("*.json"))
        }

    def load_human_action_schema(self) -> dict[str, Any]:
        return json.loads(HUMAN_ACTION_SCHEMA_PATH.read_text(encoding="utf-8"))

    def load_human_action_cases(self) -> dict[str, dict[str, Any]]:
        return {
            path.stem: json.loads(path.read_text(encoding="utf-8"))
            for path in sorted(HUMAN_ACTION_CASES_ROOT.glob("*.json"))
        }

    def test_each_case_preserves_its_required_failure_or_success_boundary(self) -> None:
        cases = self.load_cases()
        results = {name: case["expected_result"] for name, case in cases.items()}
        self.assertEqual("reviewing", results["capability-missing"]["workflow"]["stage"])
        self.assertEqual("reviewing", results["digest-mismatch"]["workflow"]["stage"])
        self.assertEqual("review_packet_unavailable", results["capability-missing"]["workflow"]["blocker"])
        self.assertEqual("review_packet_ready", results["successful-delivery"]["readiness"]["state"])
        self.assertEqual(
            "multica://issues/I-3/comments/C-3#adapter-delivery-evidence-v1",
            results["successful-delivery"]["delivery"]["delivery_evidence_ref"],
        )
        self.assertEqual(
            results["successful-delivery"]["delivery"]["delivery_evidence_ref"],
            results["successful-delivery"]["readiness"]["delivery_evidence_ref"],
        )
        digest_mismatch_artifacts = results["digest-mismatch"]["readiness"]["artifacts"]
        self.assertEqual(1, len(digest_mismatch_artifacts))
        self.assertEqual("packet", digest_mismatch_artifacts[0]["artifact_kind"])
        self.assertEqual("bound", digest_mismatch_artifacts[0]["binding_status"])
        self.assertEqual("digest_mismatch", digest_mismatch_artifacts[0]["reread_status"])
        self.assertEqual("sha256:" + "b" * 64, digest_mismatch_artifacts[0]["observed_digest"])
        self.assertEqual("repaired_projection", results["retry-reconciliation"]["delivery"]["reconciliation_outcome"])
        self.assertEqual("approved_for_spec", results["target-human-decision"]["workflow"]["stage"])
        self.assertEqual("valid", results["target-human-decision"]["decision"]["evidence_status"])
        self.assertEqual("waiting_human", results["invalid-nontarget-decision"]["workflow"]["stage"])
        self.assertEqual("none", results["invalid-nontarget-decision"]["workflow"]["blocker"])
        self.assertEqual("noop", results["superseded-decision"]["decision"]["evidence_status"])
        self.assertEqual("changed", results["edited-decision"]["decision"]["reread_status"])
        self.assertEqual("missing", results["missing-decision-binding"]["decision"]["reread_status"])
        self.assertEqual("intake", results["core-absent"]["workflow"]["stage"])
        self.assertEqual("none", results["core-absent"]["workflow"]["blocker"])
        self.assertEqual("unavailable", results["core-absent"]["availability"]["core_packet"])
        self.assertEqual("intake", results["activation-boundary"]["workflow"]["stage"])
        self.assertEqual("none", results["activation-boundary"]["workflow"]["blocker"])
        self.assertEqual("not_activated", results["activation-boundary"]["availability"]["activation"])

    def test_fixture_validator_rejects_malformed_nested_fields(self) -> None:
        schema = self.load_schema()
        cases = self.load_cases()
        missing_attachment = copy.deepcopy(cases["successful-delivery"])
        del missing_attachment["expected_result"]["readiness"]["artifacts"][0]["attachment_ref"]
        with self.assertRaisesRegex(ValueError, r"attachment_ref"):
            validate_fixture(missing_attachment, schema)

        invalid_decision_digest = copy.deepcopy(cases["target-human-decision"])
        invalid_decision_digest["expected_result"]["decision"]["content_digest"] = "sha256:short"
        with self.assertRaisesRegex(ValueError, r"content_digest"):
            validate_fixture(invalid_decision_digest, schema)

        ready_missing_artifact = copy.deepcopy(cases["successful-delivery"])
        ready_missing_artifact["expected_result"]["readiness"]["artifacts"].pop()
        with self.assertRaisesRegex(ValueError, r"fewer than minItems"):
            validate_fixture(ready_missing_artifact, schema)

        ready_repeated_kind = copy.deepcopy(cases["successful-delivery"])
        ready_repeated_kind["expected_result"]["readiness"]["artifacts"][2]["artifact_kind"] = "review"
        with self.assertRaisesRegex(ValueError, r"unique design, review, packet"):
            validate_fixture(ready_repeated_kind, schema)

        ready_without_evidence = copy.deepcopy(cases["successful-delivery"])
        ready_without_evidence["expected_result"]["delivery"]["delivery_evidence_ref"] = "none"
        with self.assertRaisesRegex(ValueError, r"matching non-none delivery evidence"):
            validate_fixture(ready_without_evidence, schema)

        ready_with_unconfirmed_target = copy.deepcopy(cases["successful-delivery"])
        ready_with_unconfirmed_target["expected_result"]["target_human"]["access_confirmation"] = "unconfirmed"
        with self.assertRaisesRegex(ValueError, r"unique confirmed target human"):
            validate_fixture(ready_with_unconfirmed_target, schema)

        valid_agent_decision = copy.deepcopy(cases["target-human-decision"])
        valid_agent_decision["expected_result"]["decision"]["author_type"] = "agent"
        with self.assertRaisesRegex(ValueError, r"canonical member author"):
            validate_fixture(valid_agent_decision, schema)

        valid_unread_decision = copy.deepcopy(cases["target-human-decision"])
        valid_unread_decision["expected_result"]["decision"]["reread_status"] = "missing"
        with self.assertRaisesRegex(ValueError, r"verified reread"):
            validate_fixture(valid_unread_decision, schema)

        ready_without_sidecar = copy.deepcopy(cases["successful-delivery"])
        ready_without_sidecar["expected_result"]["readiness"]["evidence_ref"] = "none"
        with self.assertRaisesRegex(ValueError, r"ready requires workspace sidecar"):
            validate_fixture(ready_without_sidecar, schema)

        valid_decision_without_sidecar = copy.deepcopy(cases["target-human-decision"])
        valid_decision_without_sidecar["expected_result"]["decision"]["evidence_ref"] = "E-6"
        with self.assertRaisesRegex(ValueError, r"valid decision requires workspace sidecar"):
            validate_fixture(valid_decision_without_sidecar, schema)

    def test_fixtures_match_the_normalized_result_schema(self) -> None:
        schema = self.load_schema()
        cases = self.load_cases()
        self.assertEqual(EXPECTED_FAMILIES, {name: case["family"] for name, case in cases.items()})
        for name, case in cases.items():
            with self.subTest(case=name):
                self.assertEqual(name, case["fixture_id"])
                validate_fixture(case, schema)

        artifacts = cases["successful-delivery"]["expected_result"]["readiness"]["artifacts"]
        self.assertEqual({"design", "review", "packet"}, {artifact["artifact_kind"] for artifact in artifacts})
        self.assertEqual(3, len(artifacts))
        self.assertTrue(all(artifact["expected_digest"] == artifact["verified_digest"] for artifact in artifacts))

    def test_required_adapter_production_surfaces_are_present(self) -> None:
        missing = [surface for surface in REQUIRED_ADAPTER_SURFACES if not (REPOSITORY_ROOT / surface).is_file()]
        self.assertFalse(missing, "missing required adapter production surface(s): " + ", ".join(missing))

    def test_human_action_fixtures_match_contract(self) -> None:
        schema = self.load_human_action_schema()
        cases = self.load_human_action_cases()
        self.assertEqual(
            EXPECTED_HUMAN_ACTION_FAMILIES,
            {name: case["family"] for name, case in cases.items()},
        )
        for name, case in cases.items():
            with self.subTest(case=name):
                self.assertEqual(name, case["fixture_id"])
                validate_json_schema(case, schema, schema)

        self.assertEqual(
            "non_binding_fresh_token_required",
            cases["token-plus-prose-revision"]["expected"]["decision_authority"],
        )
        self.assertEqual(
            ["design", "review", "packet"],
            cases["per-artifact-mobile-access"]["expected"]["artifact_checks"],
        )
        self.assertEqual(
            "no_write",
            cases["missing-operational-authorization"]["expected"]["write_outcome"],
        )
        self.assertEqual(
            "incremental_only",
            cases["partial-failure-retry"]["expected"]["retry_scope"],
        )

    def test_human_action_rendering_contract_is_present(self) -> None:
        human_action = REPOSITORY_ROOT / "multica-architecture-approval-adapter/templates/multica-human-action-request.md"
        operational = REPOSITORY_ROOT / "multica-architecture-approval-adapter/templates/multica-operational-authorization.md"
        approval = REPOSITORY_ROOT / "multica-architecture-approval-adapter/templates/multica-approval-comment.md"
        decision = REPOSITORY_ROOT / "multica-architecture-approval-adapter/templates/multica-decision-evidence.md"
        readiness = REPOSITORY_ROOT / "multica-architecture-approval-adapter/templates/multica-readiness-evidence.md"

        missing_files = [str(path.relative_to(REPOSITORY_ROOT)) for path in (human_action, operational) if not path.is_file()]
        self.assertFalse(missing_files, "missing human action template(s): " + ", ".join(missing_files))

        required_slots = {
            human_action: (
                "## 现在需要什么", "action_type={{action_type}}", "Decision Owner",
                "Candidate recommendation", "Bounded alternatives", "Option consequences",
                "Stable human-accessible evidence refs", "Exact response", "After response",
                "Does not authorize", "Current / superseded",
            ),
            operational: (
                "action_type=operational_authorization", "Existing target identities",
                "Exact planned writes", "Authorized paths / scope", "Retained objects",
                "Failure behavior", "Excluded operations", "Risks",
                "Exact authorize / deny response", "canonical_percent_escaped_reason",
            ),
            approval: (
                "## 现在需要你决定", "只发布批准文档", "R&D handoff",
                "新设计迭代", "终态", "Stable Design ref", "Stable Review ref",
                "Stable Packet ref", "推荐不是批准", "Remaining blockers", "Next Owner",
                "none|approved_artifact_unavailable", "## 准确回复", "## 审计信息",
            ),
            decision: (
                "decision_context_ref", "decision_context_digest", "revision_scope",
                "non_authoritative_context", "fresh_token_required",
            ),
            readiness: (
                "human_action_request_ref", "human_action_request_version",
                "brief_rendering_status", "design_access_confirmation",
                "review_access_confirmation", "packet_access_confirmation",
                "desktop", "mobile",
            ),
        }
        failures: list[str] = []
        for path, slots in required_slots.items():
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            failures.extend(
                f"{path.relative_to(REPOSITORY_ROOT)} missing {slot}"
                for slot in slots
                if slot not in text
            )
        self.assertFalse(failures, "human action rendering contract incomplete:\n" + "\n".join(failures))

        operational_text = operational.read_text(encoding="utf-8")
        for token in ("approved_design_only", "approved_for_spec", "revision_requested", "rejected"):
            self.assertNotIn(token, operational_text, f"operational authorization must not contain approval token {token}")

        protocol_slots = {
            REPOSITORY_ROOT / "multica-architecture-approval-adapter/references/human-decision-binding.md": (
                "context_profile=multica_revision_context_v1",
                "revision_brief_ref=",
                "revision_brief_digest=sha256:",
            ),
            REPOSITORY_ROOT / "multica-architecture-approval-adapter/references/target-human-mapping.md": (
                "access_profile=multica_artifact_access_confirmation_v1",
                "design_desktop=opened|unavailable",
                "review_mobile=opened|unavailable",
                "packet_mobile=opened|unavailable",
            ),
            REPOSITORY_ROOT / "multica-architecture-approval-adapter/references/operational-authorization.md": (
                "scope_profile=multica_operational_scope_v1",
                "scope_digest=sha256:",
                "raw UTF-8 bytes",
                "LF",
                "canonical percent encoding",
            ),
        }
        protocol_failures: list[str] = []
        for path, slots in protocol_slots.items():
            if not path.is_file():
                protocol_failures.append(f"missing {path.relative_to(REPOSITORY_ROOT)}")
                continue
            text = path.read_text(encoding="utf-8")
            protocol_failures.extend(
                f"{path.relative_to(REPOSITORY_ROOT)} missing {slot}"
                for slot in slots
                if slot not in text
            )
        self.assertFalse(protocol_failures, "human action protocol incomplete:\n" + "\n".join(protocol_failures))


if __name__ == "__main__":
    unittest.main()
