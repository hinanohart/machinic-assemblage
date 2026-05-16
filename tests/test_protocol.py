"""Protocol evaluate/commit tests."""

from __future__ import annotations

import json

import pytest

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    ProtocolReport,
    Side,
    Vector,
    build_assemblage,
    commit,
    evaluate,
    record_utterance,
)


def test_evaluate_rejects_non_context(simple_assemblage):
    with pytest.raises(TypeError, match="DeploymentContext"):
        evaluate(simple_assemblage, context="not-a-context", history=())  # type: ignore[arg-type]


def test_evaluate_runs_with_minimal_context(simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    assert isinstance(r, ProtocolReport)
    assert r.assemblage_signature
    assert 0.0 <= r.transversality_index <= 1.0
    assert r.context is minimal_context


def test_no_composite_score_on_report(simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    assert not hasattr(r, "composite_score")
    assert not hasattr(r, "alignment_score")
    assert not hasattr(r.three_ecologies, "composite")


def test_evaluate_with_history_detects_subject_group(minimal_context):
    a = build_assemblage(
        [Node(id=NodeId("alice"), kind="h"), Node(id=NodeId("bob"), kind="h")],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("alice"), NodeId("bob")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    b = build_assemblage(
        [
            Node(id=NodeId("alice"), kind="h"),
            Node(id=NodeId("bob"), kind="h"),
            Node(id=NodeId("carol"), kind="h"),
        ],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("alice"), NodeId("bob"), NodeId("carol")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    history = (record_utterance(NodeId("alice"), "bring carol", "rule_change", "2026-01-01"),)
    r = evaluate(a, minimal_context, history=history, assemblage_after=b)
    assert r.is_subject_group is True


def test_commit_appends_jsonl(tmp_path, simple_assemblage, minimal_context):
    r = evaluate(simple_assemblage, minimal_context)
    path = tmp_path / "out" / "reports.jsonl"
    commit(r, path)
    commit(r, path)
    lines = path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    parsed = json.loads(lines[0])
    assert "assemblage_signature" in parsed
    assert "three_ecologies" in parsed
    assert "composite" not in parsed
    assert "alignment_score" not in parsed
