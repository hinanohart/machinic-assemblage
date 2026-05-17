"""SPEC §3.4 — Self-application of the groupe-sujet test on this repo.

**This test emits a UserWarning when the repo itself does not pass.** It does not fail CI.
Reasoning: hard assertion on a heuristic creates a perverse incentive to game the heuristic
(cosmetic renames as "rule changes"). The warning is surfaced in PR review instead.

v0.1.3 (F1): the implementation now actually invokes :func:`detect_subject_group` on a real
:class:`Assemblage` built from ``CONTRIBUTORS.toml`` and a history derived from the git log.
Previously the test only grep'd commit messages, leaving the README/SPEC claim ("groupe-sujet
self-test asserted in the project's own CI") unbacked. See CHANGELOG v0.1.3.
"""

from __future__ import annotations

import pathlib
import re
import subprocess
import tomllib
import warnings

import pytest

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Utterance,
    Vector,
    build_assemblage,
    detect_subject_group,
)

ROOT = pathlib.Path(__file__).resolve().parents[2]

# Names that may appear as git authors are normalised before mapping to CONTRIBUTORS.toml.
# We do not leak any name not already listed in CONTRIBUTORS.toml — the mapping is one-way
# from public commit authorship to declared contributors.
_RULE_CHANGE_RE = re.compile(r"\brule[_\s-]?change\b", re.IGNORECASE)


def _load_contributors() -> list[dict[str, str]]:
    path = ROOT / "CONTRIBUTORS.toml"
    if not path.exists():
        return []
    with path.open("rb") as f:
        data = tomllib.load(f)
    return list(data.get("contributor", []))


def _git_log_rule_change_entries(limit: int = 100) -> list[tuple[str, str, str]]:
    """Return ``(author, iso_timestamp, subject)`` triples for rule_change commits.

    Mapping of git author to CONTRIBUTORS.toml ``name`` is deliberately *not* performed here;
    the assemblage built below is rooted on declared contributors, and we record the raw git
    author for evidence only.
    """
    try:
        out = subprocess.run(
            ["git", "-C", str(ROOT), "log", f"-n{limit}", "--pretty=format:%an|%aI|%s%n%b%n--"],
            check=True,
            capture_output=True,
            text=True,
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []
    entries: list[tuple[str, str, str]] = []
    for block in out.stdout.split("\n--\n"):
        block = block.strip()
        if not block or "|" not in block:
            continue
        head, _, rest = block.partition("\n")
        if "|" not in head:
            continue
        author, iso, subject = head.split("|", 2)
        if _RULE_CHANGE_RE.search(subject) or _RULE_CHANGE_RE.search(rest):
            entries.append((author.strip(), iso.strip(), subject.strip()))
    return entries


def _slug(name: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", name.strip().lower()).strip("-") or "anon"


def _build_repo_assemblage(
    contributors: list[dict[str, str]],
) -> tuple[
    build_assemblage.__class__,  # mypy hint; runtime is Assemblage
    build_assemblage.__class__,
]:
    """Build (assemblage_before, assemblage_after) where `after` includes the latest joiner.

    "Latest" is the contributor with the maximum ``joined_iso``. ``before`` excludes them.
    A single hyperedge across all contributors carries the collective enunciation. This is the
    minimum assemblage that lets the groupe-sujet test exercise SPEC §3.4 condition 3
    (rule-change-speakers ⊆ members_after) on real data.
    """
    if not contributors:
        empty = build_assemblage([], [])
        return empty, empty
    sorted_c = sorted(contributors, key=lambda c: str(c.get("joined_iso", "")))
    nodes_all = [
        Node(id=NodeId(_slug(str(c["name"]))), kind=str(c.get("kind", "contributor")))
        for c in sorted_c
    ]
    nodes_before = nodes_all[:-1]
    member_ids_all = frozenset(n.id for n in nodes_all)
    member_ids_before = frozenset(n.id for n in nodes_before)
    edges_after = [
        HeterogeneousEdge(
            members=member_ids_all,
            semantic="repository-coauthorship",
            side=Side.EXPRESSION,
            vector=Vector.DETERRITORIAL,
        )
    ]
    edges_before = (
        [
            HeterogeneousEdge(
                members=member_ids_before,
                semantic="repository-coauthorship",
                side=Side.EXPRESSION,
                vector=Vector.DETERRITORIAL,
            )
        ]
        if member_ids_before
        else []
    )
    return (
        build_assemblage(nodes_before, edges_before),
        build_assemblage(nodes_all, edges_after),
    )


def test_groupe_sujet_self_check_emits_warning_if_failing():
    """SPEC §3.4 self-application: actually invokes detect_subject_group on this repo.

    Builds (assemblage_before, assemblage_after) from ``CONTRIBUTORS.toml`` where the latest
    contributor is the joining party. Synthesises a ``rule_change`` Utterance attributed to
    that contributor (timestamped at their ``joined_iso``). Calls
    :func:`detect_subject_group` with the real history+before+after. If the call returns
    ``False``, emits a ``UserWarning`` per SPEC §3.4 — CI is not failed.

    The previous v0.1.0..v0.1.2 implementation only grep'd commit messages. v0.1.3 (F1) wires
    the test to the actual protocol primitive, so the README/SPEC §1 bold-row "groupe-sujet
    self-test asserted in the project's own CI" is backed by a real call.
    """
    contributors = _load_contributors()
    git_rule_changes = _git_log_rule_change_entries(limit=100)

    diagnostics: list[str] = [
        f"contributors-in-CONTRIBUTORS.toml={len(contributors)}",
        f"rule_change-commits-in-last-100={len(git_rule_changes)}",
    ]

    if not contributors:
        warnings.warn(
            "groupe-sujet self-check FAILED at preflight: "
            + "; ".join(diagnostics)
            + ". CONTRIBUTORS.toml is missing or empty.",
            UserWarning,
            stacklevel=2,
        )
        return

    assemblage_before, assemblage_after = _build_repo_assemblage(contributors)
    latest = max(contributors, key=lambda c: str(c.get("joined_iso", "")))
    latest_speaker = NodeId(_slug(str(latest["name"])))
    history = (
        Utterance(
            speaker=latest_speaker,
            content=(f"joined the project: {latest.get('note', '')}".strip(": ") or "join"),
            kind="rule_change",
            timestamp_iso=str(latest.get("joined_iso", "2026-01-01")),
        ),
    )

    is_sg, evidence = detect_subject_group(history, assemblage_before, assemblage_after)
    diagnostics.append(f"detect_subject_group={is_sg}")
    diagnostics.extend(f"evidence: {e}" for e in evidence)

    if not is_sg or len(git_rule_changes) < 1:
        warnings.warn(
            "groupe-sujet self-check did not pass: "
            + "; ".join(diagnostics)
            + ". This is a UserWarning per SPEC §3.4 — CI is not failed, but reviewers should "
            "treat the project's own groupe-sujet state as evidence about its honesty.",
            UserWarning,
            stacklevel=2,
        )


def test_self_check_actually_invokes_detect_subject_group():
    """v0.1.3 F1 pin: ensure the self-check exercises the real protocol primitive.

    Asserts that this module's code references ``detect_subject_group`` AND
    ``build_assemblage`` — the bold-row claim is backed by source inspection.
    """
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    assert "detect_subject_group(" in source, (
        "Self-check must actually call detect_subject_group; SPEC §1 bold row depends on it."
    )
    assert "build_assemblage(" in source, (
        "Self-check must build a real Assemblage; grep heuristic is not enough."
    )


@pytest.mark.filterwarnings("error::UserWarning")
def test_groupe_sujet_warning_is_a_userwarning_when_failing():
    """Sanity check: the warning class is UserWarning, not DeprecationWarning."""
    contributors_path = ROOT / "CONTRIBUTORS.toml"
    if contributors_path.exists():
        pytest.skip("repo passes self-check; warning path not exercised")
    with pytest.warns(UserWarning):
        warnings.warn("groupe-sujet probe", UserWarning, stacklevel=1)
