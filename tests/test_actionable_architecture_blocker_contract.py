from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "architecture-design-workflow"
ADAPTER = ROOT / "multica-architecture-approval-adapter"
PORTABLE_CASES = ROOT / "tests/fixtures/architecture-design-workflow/portable-v2-cases.json"
BLOCKER_CASES = ROOT / "tests/fixtures/multica-architecture-approval-adapter/actionable-blocker-cases.json"
HUMAN_REPLY_CASES = ROOT / "tests/fixtures/multica-architecture-approval-adapter/human-friendly-blocker-cases.json"

RESPONSIBILITIES = {
    "coordination",
    "research",
    "solution_design",
    "independent_review",
    "dependency_input",
    "human_decision",
    "downstream_delivery",
}
LEGACY_ROLE_MAP = {
    "Architecture Lead": "coordination",
    "Architecture Analyst": "research",
    "Solution Architect": "solution_design",
    "Architecture Reviewer": "independent_review",
}


def portable_outcome(case: dict[str, object]) -> str:
    profile = case["profile"]
    if profile == "execution_continuation_v1":
        return "migration_ready" if case["legacy_role"] in LEGACY_ROLE_MAP else "fail_closed"
    if profile != "execution_continuation_v2":
        return "fail_closed"
    if case["state"] != "terminal" and (
        case["next_actor_ref"] == "none" or case["next_actor_authority_ref"] == "none"
    ):
        return "fail_closed"
    if case["next_responsibility"] not in RESPONSIBILITIES:
        return "fail_closed"
    if case["state"] in {"accepted", "active"} and not case["has_claim"]:
        return "fail_closed"
    return str(case["state"])


def blocker_outcome(case: dict[str, object]) -> str:
    if not case["owner_unique"]:
        return "needs_new_mandate"

    profile = str(case.get("blocker_profile", "architecture_blocker_action_v1"))
    if profile == "architecture_blocker_action_v1" and case.get("new_write_requested", False):
        return "v2_supersede_required"
    if profile not in {"architecture_blocker_action_v1", "architecture_blocker_action_v2"}:
        return "blocked_noop"

    if profile == "architecture_blocker_action_v2" and not case["created_after"]:
        if not case.get("discovery_authorized", False):
            return "blocked_noop"
        discovery_result = case.get("discovery_result")
        if discovery_result == "unique_verified":
            if not case["mapping_unique"] or case["task_status"] == "none":
                return "blocked_rollback"
            return (
                "in_progress_discovery_active"
                if case["task_status"] == "running"
                else "in_progress_discovery_accepted"
            )
        if discovery_result == "multiple_verified":
            return "blocked_candidate_choice"
        if discovery_result in {"unavailable_with_evidence", "unique_unverified"}:
            return "blocked_request_discovery"
        return "blocked_noop"

    if not case["created_after"]:
        return "blocked_awaiting_input"

    response_mode = str(case.get("response_mode", "provide_input"))
    reply_valid = all(
        case[field]
        for field in (
            "reply_actor_matches",
            "current_action",
            "created_after",
            "unedited",
            "single_action",
        )
    )
    if response_mode == "provide_input":
        reply_valid = reply_valid and bool(case["fields_complete"])
        reply_valid = reply_valid and not bool(case.get("contains_placeholder", False))
    elif response_mode == "request_discovery":
        reply_valid = reply_valid and bool(case.get("discovery_authorized", False))
        reply_valid = reply_valid and int(case.get("edge_mention_count", 0)) <= 1
        reply_valid = reply_valid and "我不知道，请团队调查并给出建议" in str(
            case.get("reply_text", "")
        )
    else:
        reply_valid = False
    if not reply_valid:
        return "blocked_noop"
    if not case["mapping_unique"] or case["task_status"] == "none":
        return "blocked_rollback"
    if response_mode == "request_discovery":
        return (
            "in_progress_discovery_active"
            if case["task_status"] == "running"
            else "in_progress_discovery_accepted"
        )
    if case["task_status"] == "queued":
        return "in_progress_accepted"
    if case["task_status"] == "running":
        return "in_progress_active"
    return "blocked_rollback"


def normalize_human_reply(case: dict[str, object]) -> dict[str, str]:
    if not all(
        bool(case[field])
        for field in (
            "reply_actor_matches",
            "current_action",
            "created_after",
            "unedited",
            "single_action",
            "reread_verified",
        )
    ):
        return {"outcome": "blocked_noop"}

    action_id = str(case["action_id"])
    reply = str(case["reply_text"]).strip()
    own_reply = f"ACTION {action_id}: 由我负责"
    uncertain_reply = f"ACTION {action_id}: 我不确定，请团队给出建议"
    named_match = re.fullmatch(
        rf"ACTION {re.escape(action_id)}: 负责人是 (.+)",
        reply,
    )

    if reply == own_reply:
        mode = "provide_input"
        candidate = str(case["author_id"])
    elif named_match and named_match.group(1).strip() not in {"", "<可识别的人或团队>"}:
        mode = "provide_input"
        candidate = named_match.group(1).strip()
    elif reply == uncertain_reply:
        mode = "request_discovery"
        candidate = "none"
    else:
        return {"outcome": "blocked_noop"}

    return {
        "outcome": "normalized",
        "response_mode": mode,
        "candidate_actor": candidate,
        "authority_scope": str(case["frozen_business_scope"]),
        "evidence_ref": str(case["comment_ref"]),
        "evidence_revision": str(case["comment_revision"]),
        "evidence_date": str(case["created_at"]),
        "verification_state": "pending",
    }


class ActionableArchitectureBlockerContractTest(unittest.TestCase):
    def test_portable_fixtures_cover_v2_standalone_and_v1_migration(self) -> None:
        cases = json.loads(PORTABLE_CASES.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "standalone-current-session-active",
                "standalone-cross-session-unclaimed",
                "legacy-lead-migration",
                "legacy-unknown-role",
                "nonterminal-empty-actor",
            },
            {case["case_id"] for case in cases},
        )
        for case in cases:
            self.assertEqual(case["expected"], portable_outcome(case), case["case_id"])

    def test_blocker_fixtures_cover_publish_reply_resume_and_rollback(self) -> None:
        cases = json.loads(BLOCKER_CASES.read_text(encoding="utf-8"))
        expected_ids = {
            "publish-unique-owner",
            "missing-instruction-owner",
            "valid-reply-queued",
            "valid-reply-running",
            "wrong-reply-actor",
            "edited-reply",
            "incomplete-reply",
            "superseded-action",
            "resume-task-not-enqueued",
            "legacy-v1-new-write-requires-v2-supersession",
            "discovery-unique-binding-auto-resumes",
            "discovery-multiple-candidates-asks-simple-choice",
            "discovery-no-candidate-offers-request-discovery",
            "localized-request-discovery-with-edge-mention",
            "placeholder-binding-remains-noop",
            "unverified-discovery-cannot-bind-owner",
            "discovery-authority-expansion-is-rejected",
        }
        self.assertEqual(expected_ids, {case["case_id"] for case in cases})
        for case in cases:
            self.assertEqual(case["expected"], blocker_outcome(case), case["case_id"])

    def test_human_friendly_replies_are_exact_and_derive_machine_evidence(self) -> None:
        cases = json.loads(HUMAN_REPLY_CASES.read_text(encoding="utf-8"))
        self.assertEqual(
            {
                "current-user-declares-responsibility",
                "instruction-owner-nominates-another-owner",
                "instruction-owner-is-uncertain",
                "placeholder-owner-is-noop",
                "wrong-action-is-noop",
            },
            {case["case_id"] for case in cases},
        )
        for case in cases:
            self.assertEqual(case["expected"], normalize_human_reply(case), case["case_id"])

    def test_default_blocker_comment_is_a_plain_language_decision_surface(self) -> None:
        text = (ADAPTER / "templates/multica-blocker-comment.md").read_text(encoding="utf-8")
        for required in (
            "# 架构工作为什么暂停",
            "## 团队建议",
            "## 你只需要回答一个问题",
            "## 可以直接回复",
            "ACTION <action-id>: 由我负责",
            "ACTION <action-id>: 负责人是 <姓名或团队>",
            "ACTION <action-id>: 我不确定，请团队给出建议",
            "## 回复后会发生什么",
            "## 查看依据（可选）",
        ):
            self.assertIn(required, text)
        for forbidden in (
            "RACI",
            "组织目录",
            "服务目录",
            "策略批准记录",
            "owner_identity",
            "authority_scope",
            "evidence_ref",
            "unavailable_with_evidence",
            "multiple_verified",
        ):
            self.assertNotIn(forbidden, text)

    def test_core_surfaces_publish_complete_v2_and_blocker_contracts(self) -> None:
        surfaces = {
            CORE / "SKILL.md": (
                "architecture_workflow_mandate_v2",
                "execution_continuation_v2",
                "architecture-blocker-action.md",
                "dependency_input",
            ),
            CORE / "references/workflow-mandate-and-review-gates.md": (
                "architecture_workflow_mandate_v2",
                "v1 dual-read",
                "v2-only write",
                "needs_new_mandate_v1",
            ),
            CORE / "references/execution-continuation.md": (
                "execution_continuation_v2",
                "next_actor_ref",
                "next_actor_authority_ref",
                "next_responsibility",
                "local_session|shared_artifact|runtime_task|human_response",
            ),
            CORE / "references/architecture-blocker-action.md": (
                "architecture_blocker_action_v2",
                "architecture_blocker_action_v3",
                "automatic_before_human",
                "provide_input|request_discovery",
                "discovery_needed",
                "resolution_instruction_owner_ref",
                "requires_human_review=false",
                "needs_new_mandate_v1",
                "business_question",
                "human_declaration",
                "derive_machine_evidence_from_reply",
                "formal_source_policy=conditional",
            ),
            CORE / "templates/architecture-blocker-action.md": (
                "ACTION_ID",
                "DISCOVERY_SCOPE",
                "REQUEST_DISCOVERY_REPLY",
                "RESUME_ACTOR_REF",
                "BLOCKER_ACTION_STATE",
                "BUSINESS_QUESTION",
                "HUMAN_DECLARATION_REPLIES",
            ),
        }
        failures: list[str] = []
        for path, markers in surfaces.items():
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            failures.extend(
                f"{path.relative_to(ROOT)} missing {marker}"
                for marker in markers
                if marker not in text
            )
        self.assertFalse(failures, "portable v2/blocker surfaces incomplete:\n" + "\n".join(failures))

    def test_portable_required_contract_does_not_require_team_topology(self) -> None:
        mandate = (CORE / "references/workflow-mandate-and-review-gates.md").read_text(encoding="utf-8")
        continuation = (CORE / "references/execution-continuation.md").read_text(encoding="utf-8")
        for text, heading in ((mandate, "v2 canonical fields"), (continuation, "v2 canonical fields")):
            match = re.search(rf"(?ms)^### {re.escape(heading)}\n(.*?)(?=^### |\Z)", text)
            self.assertIsNotNone(match, f"missing {heading}")
            required_block = match.group(1)
            for forbidden in (
                "Architecture Lead",
                "Architecture Analyst",
                "Solution Architect",
                "Architecture Reviewer",
                "workspace_id",
                "issue_id",
                "member_id",
                "agent_id",
                "comment_id",
                "task_id",
            ):
                self.assertNotIn(forbidden, required_block)

    def test_adapter_surfaces_publish_projection_consumption_and_rollback(self) -> None:
        surfaces = {
            ADAPTER / "SKILL.md": (
                "architecture_workflow_mandate_v2",
                "architecture_blocker_action_v2",
                "architecture_blocker_action_v3",
                "request_discovery",
                "actionable-blocker-projection-and-reply.md",
            ),
            ADAPTER / "references/core-contract-compatibility.md": (
                "v1 dual-read",
                "v2-only write",
                "responsibility mapping",
            ),
            ADAPTER / "references/execution-handoff-and-task-readback.md": (
                "next_actor_ref",
                "next_responsibility",
                "accepted|active",
            ),
            ADAPTER / "references/actionable-blocker-projection-and-reply.md": (
                "BLOCKER_ACTION_STATE=discovering|awaiting_input|received|discovery_needed|superseded|unavailable",
                "automatic_before_human",
                "provide_input|request_discovery",
                "created-after-request",
                "single action",
                "blocked rollback",
                "in_progress --no-start",
                "metadata_capacity_exceeded",
                "stale current metadata",
                "human_declaration",
                "derive_machine_evidence_from_reply",
                "formal_source_policy=conditional",
            ),
            ADAPTER / "references/architecture-operation-manifest.md": (
                "8 KiB metadata bag",
                "pre-write byte budget",
                "do not retry the same oversized value",
                "compact current projection",
            ),
            ADAPTER / "templates/multica-blocker-comment.md": (
                "准确 Member mention",
                "架构工作为什么暂停",
                "团队建议",
                "你只需要回答一个问题",
                "我不确定，请团队给出建议",
                "回复后会发生什么",
                "查看依据（可选）",
            ),
        }
        failures: list[str] = []
        for path, markers in surfaces.items():
            text = path.read_text(encoding="utf-8") if path.is_file() else ""
            failures.extend(
                f"{path.relative_to(ROOT)} missing {marker}"
                for marker in markers
                if marker not in text
            )
        self.assertFalse(failures, "adapter blocker surfaces incomplete:\n" + "\n".join(failures))


if __name__ == "__main__":
    unittest.main()
