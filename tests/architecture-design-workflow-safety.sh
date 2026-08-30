#!/usr/bin/env bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd -P)"
RESULTS_DIR=""
RUNTIME=""

while (($#)); do
  case "$1" in
    --results-dir)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "--results-dir requires a non-empty value" >&2
        exit 2
      fi
      RESULTS_DIR="$2"
      shift 2
      ;;
    --runtime)
      if [[ $# -lt 2 || -z "${2:-}" ]]; then
        echo "--runtime requires a non-empty value" >&2
        exit 2
      fi
      RUNTIME="$2"
      shift 2
      ;;
    *)
      echo "unknown argument: $1" >&2
      exit 2
      ;;
  esac
done

if [[ -n "$RESULTS_DIR" && -z "$RUNTIME" ]] || [[ -z "$RESULTS_DIR" && -n "$RUNTIME" ]]; then
  echo "--results-dir and --runtime must be supplied together" >&2
  exit 2
fi

if [[ -n "$RUNTIME" && "$RUNTIME" != "codex" && "$RUNTIME" != "claude" ]]; then
  echo "unsupported runtime: $RUNTIME (expected codex or claude)" >&2
  exit 2
fi

python3 - "$PROJECT_ROOT" "$RESULTS_DIR" "$RUNTIME" <<'PY'
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

root = Path(sys.argv[1]).resolve()
results_arg = sys.argv[2]
runtime = sys.argv[3]
skill = root / "architecture-design-workflow"
fixtures_dir = root / "tests" / "fixtures" / "architecture-design-workflow"
failures: list[str] = []


def fail(message: str) -> None:
    failures.append(message)


result_schema_path = fixtures_dir / "result.schema.json"
try:
    result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))
except (OSError, json.JSONDecodeError) as exc:
    result_schema = {}
    fail(f"invalid result schema: {exc}")


required_skill_files = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/intake-and-project-routing.md",
    "references/research-evolution.md",
    "references/research-greenfield.md",
    "references/research-hybrid.md",
    "references/solution-design.md",
    "references/architecture-review.md",
    "references/human-action-request.md",
    "references/approval-packet-and-human-gate.md",
    "references/adr-publication.md",
    "references/rnd-handoff.md",
    "references/runtime-and-validation.md",
    "templates/arch-control.md",
    "templates/arch-research.md",
    "templates/arch-design.md",
    "templates/arch-review.md",
    "templates/human-action-request.md",
    "templates/arch-approval-packet.md",
    "templates/adr.md",
    "templates/detailed-design.md",
    "templates/arch-rd-handoff.md",
]

for relative in required_skill_files:
    if not (skill / relative).is_file():
        fail(f"missing skill file: architecture-design-workflow/{relative}")

skill_file = skill / "SKILL.md"
if skill_file.is_file():
    text = skill_file.read_text(encoding="utf-8")
    frontmatter = re.match(r"\A---\n(.*?)\n---\n", text, re.DOTALL)
    if not frontmatter:
        fail("SKILL.md has no valid frontmatter")
    else:
        yaml = frontmatter.group(1)
        if not re.search(r"(?m)^name:\s*architecture-design-workflow\s*$", yaml):
            fail("SKILL.md name is not architecture-design-workflow")
        description = re.search(r'(?m)^description:\s*["\']?(.+?)["\']?\s*$', yaml)
        if not description or not description.group(1).startswith("Use when"):
            fail("SKILL.md description must start with 'Use when'")

    for target in re.findall(r"\[[^\]]+\]\(([^)]+)\)", text):
        if "://" in target or target.startswith("#"):
            continue
        resolved = (skill / target.split("#", 1)[0]).resolve()
        if not resolved.is_file() or skill.resolve() not in resolved.parents:
            fail(f"unresolved or escaping SKILL.md reference: {target}")

openai_yaml = skill / "agents" / "openai.yaml"
if openai_yaml.is_file():
    metadata = openai_yaml.read_text(encoding="utf-8")
    for key in ("display_name", "short_description", "default_prompt"):
        if not re.search(rf'(?m)^\s+{key}:\s+"[^"]+"\s*$', metadata):
            fail(f"agents/openai.yaml missing quoted {key}")
    if "$architecture-design-workflow" not in metadata:
        fail("agents/openai.yaml default prompt does not invoke $architecture-design-workflow")

portable_core_paths = [
    skill / "SKILL.md",
    skill / "references" / "approval-packet-and-human-gate.md",
    skill / "templates" / "arch-control.md",
    skill / "templates" / "arch-design.md",
    skill / "templates" / "arch-review.md",
    skill / "templates" / "arch-approval-packet.md",
]
platform_marker = re.compile(
    r"(?i)(?:\bmultica\b|\bpdf\b|\bparent_id\b|\bcomment_id\b|\battachment_id\b|\bmobile\b)"
)
for path in portable_core_paths:
    if path.is_file() and platform_marker.search(path.read_text(encoding="utf-8")):
        fail(f"platform-specific core marker: {path.relative_to(root)}")

packet_template = skill / "templates" / "arch-approval-packet.md"
if packet_template.is_file():
    packet_text = packet_template.read_text(encoding="utf-8")
    if "review_packet_ready" in packet_text or "review_packet_unavailable" in packet_text:
        fail("packet payload embeds post-finalization evidence")

control_template = skill / "templates" / "arch-control.md"
if control_template.is_file():
    control_text = control_template.read_text(encoding="utf-8")
    clarification_match = re.search(
        r"(?ms)^## Reviewable clarification request\n(.*?)(?=^## |\Z)",
        control_text,
    )
    clarification_text = clarification_match.group(1) if clarification_match else ""
    clarification_slots = [
        "Decision required",
        "Candidate recommendation",
        "Basis",
        "Material risks / consequences",
        "Missing evidence / Owner / closure condition",
        "Editable response",
    ]
    missing_slots = [slot for slot in clarification_slots if slot not in clarification_text]
    if not clarification_match:
        missing_slots.insert(0, "## Reviewable clarification request")
    if missing_slots:
        fail(
            "ARCH-CONTROL missing reviewable clarification slots: "
            + ", ".join(missing_slots)
        )

human_action_template = skill / "templates" / "human-action-request.md"
if human_action_template.is_file():
    human_action_text = human_action_template.read_text(encoding="utf-8")
    human_action_slots = [
        "## Action summary",
        "Action ID / type / current status",
        "Why now",
        "Decision Owner / authority scope",
        "## Decision context",
        "Decision required",
        "Candidate recommendation",
        "Bounded alternatives",
        "Basis — facts / inferences / principles",
        "Option consequences / material risks",
        "## Evidence and unresolved items",
        "Stable human-accessible evidence refs",
        "Missing evidence / Owner / closure condition",
        "## Exact response",
        "## After response",
        "Next stage / remaining blockers / Next Owner / planned writes",
        "## Authority boundary",
        "Does not authorize",
        "## Audit binding",
        "Bound artifact or routing version",
        "Current / superseded",
    ]
    missing_human_action_slots = [
        slot for slot in human_action_slots if slot not in human_action_text
    ]
    if missing_human_action_slots:
        fail(
            "Human Action Request missing required slots: "
            + ", ".join(missing_human_action_slots)
        )


def load_fixture(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(r"```json expected\n(.*?)\n```", text, re.DOTALL)
    if not match:
        raise ValueError("missing expected JSON block")
    expected = json.loads(match.group(1))
    request = re.search(r"## Request\n\n(.*?)(?:\n\n## Expected contract)", text, re.DOTALL)
    if not request:
        raise ValueError("missing Request section")
    return expected, request.group(1).strip()


fixture_paths = sorted(fixtures_dir.glob("*.case.md"))
if len(fixture_paths) < 21:
    fail(f"expected at least 21 fixtures, found {len(fixture_paths)}")

for path in fixture_paths:
    if platform_marker.search(path.read_text(encoding="utf-8")):
        fail(f"platform-specific core marker: {path.relative_to(root)}")

fixture_required = {
    "fixture_id",
    "selected",
    "stage",
    "gate",
    "review_conclusion",
    "packet_readiness",
    "packet_ref",
    "packet_version",
    "packet_digest",
    "access_confirmation",
    "recommendation",
    "human_decision",
    "decision_evidence_status",
    "evidence_recorded_at",
    "wait_reason",
    "blocked_reason",
    "planned_writes",
    "evidence_fields",
    "required_markers",
    "forbidden_markers",
}
fixtures: list[tuple[Path, dict[str, object]]] = []
for path in fixture_paths:
    try:
        expected, request = load_fixture(path)
    except (ValueError, json.JSONDecodeError) as exc:
        fail(f"invalid fixture {path.name}: {exc}")
        continue
    missing = fixture_required - expected.keys()
    if missing:
        fail(f"fixture {path.name} missing keys: {sorted(missing)}")
        continue
    if not request:
        fail(f"fixture {path.name} has empty request")
    if expected.get("fixture_id") != path.name.removesuffix(".case.md"):
        fail(f"fixture id/path mismatch: {path.name}")
    fixtures.append((path, expected))


def extract_result(path: Path) -> tuple[dict[str, object], str]:
    text = path.read_text(encoding="utf-8")
    match = re.search(
        r"<!-- ARCH-TEST-RESULT\n(.*?)\nARCH-TEST-RESULT -->",
        text,
        re.DOTALL,
    )
    if not match:
        raise ValueError("missing ARCH-TEST-RESULT envelope")
    narrative = (text[: match.start()] + text[match.end() :]).strip()
    return json.loads(match.group(1)), narrative


if results_arg:
    results_dir = Path(results_arg).resolve()
    results_inside = results_dir == root or root in results_dir.parents
    if not results_inside:
        fail("results directory must stay inside the repository")
    for fixture_path, expected in fixtures if results_inside else []:
        fixture_id = str(expected["fixture_id"])
        result_path = results_dir / f"{fixture_id}.{runtime}.md"
        if not result_path.is_file():
            fail(f"missing {runtime} result: {result_path.relative_to(root)}")
            continue
        try:
            actual, narrative = extract_result(result_path)
        except (ValueError, json.JSONDecodeError) as exc:
            fail(f"invalid result {result_path.name}: {exc}")
            continue

        for key in (
            "fixture_id",
            "selected",
            "stage",
            "gate",
            "review_conclusion",
            "packet_readiness",
            "packet_ref",
            "packet_version",
            "packet_digest",
            "access_confirmation",
            "recommendation",
            "human_decision",
            "decision_evidence_status",
            "evidence_recorded_at",
            "wait_reason",
            "blocked_reason",
        ):
            if actual.get(key) != expected.get(key):
                fail(
                    f"{result_path.name}: {key} expected {expected.get(key)!r}, "
                    f"got {actual.get(key)!r}"
                )

        actual_writes = actual.get("planned_writes", [])
        if not isinstance(actual_writes, list) or any(
            not isinstance(item, str) for item in actual_writes
        ):
            fail(f"{result_path.name}: planned_writes must be a list of strings")
            continue
        if set(actual_writes) != set(expected.get("planned_writes", [])):
            fail(
                f"{result_path.name}: planned_writes expected "
                f"{sorted(expected.get('planned_writes', []))!r}, got "
                f"{sorted(actual_writes)!r}"
            )

        if actual.get("runtime") != runtime:
            fail(f"{result_path.name}: runtime field mismatch")
        if not actual.get("runtime_version"):
            fail(f"{result_path.name}: missing runtime_version")
        if "limitations" not in actual:
            fail(f"{result_path.name}: missing limitations")

        schema_required = set(result_schema.get("required", [])) - {"narrative"}
        missing_result_fields = schema_required - actual.keys()
        if missing_result_fields:
            fail(
                f"{result_path.name}: missing normalized fields "
                f"{sorted(missing_result_fields)}"
            )

        packet_version = actual.get("packet_version", "none")
        if not isinstance(packet_version, str) or not re.fullmatch(
            r"none|v[1-9][0-9]*", packet_version
        ):
            fail(f"{result_path.name}: packet_version must be none or monotonic vN")

        packet_digest = actual.get("packet_digest", "none")
        if packet_digest != "none" and not (
            isinstance(packet_digest, str)
            and re.fullmatch(r"sha256:[0-9a-f]{64}", packet_digest)
        ):
            fail(
                f"{result_path.name}: packet_digest must be none or canonical sha256"
            )

        evidence_recorded_at = actual.get("evidence_recorded_at", "none")
        if evidence_recorded_at != "none" and not (
            isinstance(evidence_recorded_at, str)
            and re.fullmatch(
                r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?Z",
                evidence_recorded_at,
            )
        ):
            fail(
                f"{result_path.name}: evidence_recorded_at must be none or RFC 3339 UTC"
            )

        allowed_values = {
            "review_conclusion": {
                "none",
                "BLOCKED",
                "NEEDS_REVISION",
                "APPROVABLE_WITH_WARNINGS",
                "APPROVABLE",
            },
            "packet_readiness": {
                "none",
                "review_packet_ready",
                "review_packet_unavailable",
            },
            "access_confirmation": {
                "none",
                "confirmed",
                "unconfirmed",
                "not_applicable",
            },
            "recommendation": {
                "none",
                "recommend_approved_for_spec",
                "recommend_approved_design_only",
                "recommend_revision",
                "no_recommendation",
            },
            "human_decision": {
                "none",
                "approved_design_only",
                "approved_for_spec",
                "revision_requested",
                "rejected",
            },
            "decision_evidence_status": {"none", "valid", "invalid", "noop"},
        }
        for key, allowed in allowed_values.items():
            if actual.get(key) not in allowed:
                fail(f"{result_path.name}: invalid {key} {actual.get(key)!r}")

        packet_readiness = actual.get("packet_readiness")
        human_decision = actual.get("human_decision")
        decision_status = actual.get("decision_evidence_status")
        if packet_readiness == "review_packet_ready" and (
            packet_version == "none"
            or packet_digest == "none"
            or actual.get("access_confirmation") != "confirmed"
        ):
            fail(
                f"{result_path.name}: ready packet requires version, digest and confirmed access"
            )
        if human_decision != "none" and decision_status not in {"valid", "noop"}:
            fail(
                f"{result_path.name}: human decision requires valid or noop evidence"
            )
        if decision_status == "valid" and (
            packet_version == "none" or packet_digest == "none"
        ):
            fail(
                f"{result_path.name}: valid decision evidence requires current packet binding"
            )

        evidence_fields = actual.get("evidence_fields", [])
        if not isinstance(evidence_fields, list) or any(
            not isinstance(item, str) for item in evidence_fields
        ):
            fail(f"{result_path.name}: evidence_fields must be a list of strings")
            continue
        actual_evidence = set(evidence_fields)
        missing_evidence = set(expected.get("evidence_fields", [])) - actual_evidence
        if missing_evidence:
            fail(f"{result_path.name}: missing evidence fields {sorted(missing_evidence)}")

        if actual.get("selected") and not re.search(r"[\u3400-\u9fff]", narrative):
            fail(f"{result_path.name}: selected workflow response is not Chinese")
        for marker in expected.get("required_markers", []):
            if str(marker) not in narrative:
                fail(f"{result_path.name}: missing required marker {marker!r}")
        for marker in expected.get("forbidden_markers", []):
            if str(marker) in narrative:
                fail(f"{result_path.name}: contains forbidden marker {marker!r}")

if failures:
    print(f"architecture workflow safety: FAIL ({len(failures)} issue(s))")
    for item in failures:
        print(f"- {item}")
    raise SystemExit(1)

mode = f"static + {runtime} behavior" if results_arg else "static"
print(f"architecture workflow safety: PASS ({mode}, {len(fixtures)} fixtures)")
PY
