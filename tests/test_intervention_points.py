"""SPEC §5 — ten intervention points must remain documented.

This test enforces M3: removing a checkpoint is a deliberate edit, not silent drift.
"""

from __future__ import annotations

import pathlib
import re

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _spec_section_5() -> str:
    spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    match = re.search(
        r"##\s+5\.\s+Pipeline & intervention points(.+?)\n##\s+\d",
        spec,
        flags=re.DOTALL,
    )
    assert match, "SPEC §5 not found"
    return match.group(1)


def test_intervention_points_count_is_at_least_ten():
    section = _spec_section_5()
    items = re.findall(r"(?m)^\s*\d+\.\s+", section)
    assert len(items) >= 10, f"SPEC §5 must list >= 10 checkpoints, found {len(items)}"


def test_spec_does_not_claim_fully_automatic():
    spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    forbidden = ("fully automatic", "fully-automatic", "完全自動", "fully automated")
    for phrase in forbidden:
        assert phrase.lower() not in spec.lower() or (
            f'not "{phrase}"' in spec.lower() or f'not "{phrase.lower()}"' in spec.lower()
        ), f"SPEC must not claim {phrase!r}"
