"""SPEC §0 — fixed-string assertion of the political statement.

Removing or paraphrasing this paragraph breaks CI. This is the C-new1 fix: the political
statement is a CI invariant, not a footnote that can be silently sanitised.
"""

from __future__ import annotations

import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]

POLITICAL_STATEMENT_FRAGMENTS = (
    "Integrated World Capitalism",
    "machinic enslavement",
    "Deleuzian capitalism",
    "Refusal of capture is",
    "deliberately not implemented",
    "inconvenient by design",
    "use LangGraph",
)


def test_spec_contains_political_statement():
    spec = (ROOT / "SPEC.md").read_text(encoding="utf-8")
    for fragment in POLITICAL_STATEMENT_FRAGMENTS:
        assert fragment in spec, (
            f"SPEC.md must contain the political statement fragment {fragment!r}. "
            f"See SPEC §0 — this is C-new1 invariant."
        )


def test_readme_links_to_political_statement():
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "Integrated World Capitalism" in readme, (
        "README must surface the political statement, not just link to SPEC."
    )
    assert "LangGraph" in readme, (
        "README must explicitly redirect non-political users to LangGraph."
    )
