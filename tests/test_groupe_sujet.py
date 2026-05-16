"""Groupe-sujet detection tests."""

from __future__ import annotations

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Vector,
    build_assemblage,
    detect_subject_group,
    record_utterance,
)


def _a1():
    return build_assemblage(
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


def _a2():
    return build_assemblage(
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


def test_no_rule_change_returns_false():
    a = _a1()
    is_sg, ev = detect_subject_group([], a, _a2())
    assert is_sg is False
    assert any("no rule_change" in e for e in ev)


def test_missing_after_returns_false():
    a = _a1()
    history = [
        record_utterance(NodeId("alice"), "change", "rule_change", "2026-01-01"),
    ]
    is_sg, ev = detect_subject_group(history, a, None)
    assert is_sg is False
    assert any("not provided" in e for e in ev)


def test_cosmetic_change_returns_false():
    a = _a1()
    history = [
        record_utterance(NodeId("alice"), "change", "rule_change", "2026-01-01"),
    ]
    is_sg, ev = detect_subject_group(history, a, a)
    assert is_sg is False
    assert any("cosmetic" in e for e in ev)


def test_top_down_returns_false():
    a = _a1()
    b = _a2()
    history = [
        record_utterance(NodeId("nonparticipant"), "change", "rule_change", "2026-01-01"),
    ]
    is_sg, ev = detect_subject_group(history, a, b)
    assert is_sg is False
    assert any("top-down" in e for e in ev)


def test_genuine_subject_group_returns_true():
    a = _a1()
    b = _a2()
    history = [
        record_utterance(NodeId("alice"), "let's bring in Carol", "rule_change", "2026-01-01"),
        record_utterance(NodeId("bob"), "agreed", "witness", "2026-01-02"),
    ]
    is_sg, ev = detect_subject_group(history, a, b)
    assert is_sg is True
    assert any("overlap" in e for e in ev)
