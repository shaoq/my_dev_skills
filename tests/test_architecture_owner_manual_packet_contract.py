from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "architecture-design-workflow"
ADAPTER = ROOT / "multica-architecture-approval-adapter"


class ArchitectureOwnerManualPacketContractTest(unittest.TestCase):
    def test_core_packet_gate_accepts_explicit_owner_manual_readiness(self) -> None:
        surfaces = {
            CORE / "SKILL.md": (
                "access_verification_mode=owner_manual",
                "manual_check_required",
                "Owner 对完整材料已打开的显式声明",
            ),
            CORE / "references/approval-packet-and-human-gate.md": (
                "owner_manual",
                "manual_check_required",
                "content-decision activation gate",
                "不得声称 `opened`",
            ),
            CORE / "references/human-action-request.md": (
                "access_verification_mode=owner_manual",
                "manual_check_required",
                "材料打不开",
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
        self.assertFalse(failures, "owner-manual packet contract incomplete:\n" + "\n".join(failures))

    def test_multica_owner_attested_maps_to_portable_owner_manual(self) -> None:
        surfaces = (
            ADAPTER / "SKILL.md",
            ADAPTER / "references/human-accessible-evidence-links.md",
            ADAPTER / "references/reconciliation-projection-and-readiness.md",
        )
        marker = "owner_attested -> owner_manual"
        missing = [
            str(path.relative_to(ROOT))
            for path in surfaces
            if marker not in path.read_text(encoding="utf-8")
        ]
        self.assertFalse(missing, f"missing portable mode mapping in: {missing}")


if __name__ == "__main__":
    unittest.main()
