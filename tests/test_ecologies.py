"""Three Ecologies KPI tests."""

from __future__ import annotations

import warnings

from machinic_assemblage import (
    DeploymentContext,
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Vector,
    build_assemblage,
    compute_three_ecologies,
    record_utterance,
)


def _ctx(env_kg=None):
    return DeploymentContext(
        operator_org="x",
        revenue_model="none",
        end_users_consent_uri="https://example.org/c",
        used_in_optimization_for=frozenset(),
        declared_at_iso="2026-01-01",
        environmental_kgco2eq_estimate=env_kg,
    )


def _empty_assemblage():
    return build_assemblage([Node(id=NodeId("a"), kind="human")], [])


def test_environmental_warning_when_none():
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        eco = compute_three_ecologies(_empty_assemblage(), _ctx(env_kg=None))
        assert any("environmental" in str(x.message).lower() for x in w)
        assert eco.environmental == 0.0


def test_environmental_above_threshold_clamped_to_zero():
    eco = compute_three_ecologies(_empty_assemblage(), _ctx(env_kg=10_000.0))
    assert eco.environmental == 0.0


def test_environmental_below_threshold_positive():
    eco = compute_three_ecologies(_empty_assemblage(), _ctx(env_kg=10.0))
    assert eco.environmental > 0.0
    assert eco.environmental <= 1.0


def test_social_reciprocity_zero_for_single_edge():
    a = build_assemblage(
        [Node(id=NodeId("x"), kind="h"), Node(id=NodeId("y"), kind="h")],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("x"), NodeId("y")}),
                semantic="s",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )
        ],
    )
    eco = compute_three_ecologies(a, _ctx(env_kg=0.0))
    assert eco.social == 0.0


def test_social_reciprocity_positive_with_two_edges_same_pair():
    a = build_assemblage(
        [Node(id=NodeId("x"), kind="h"), Node(id=NodeId("y"), kind="h")],
        [
            HeterogeneousEdge(
                members=frozenset({NodeId("x"), NodeId("y")}),
                semantic="s1",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            ),
            HeterogeneousEdge(
                members=frozenset({NodeId("x"), NodeId("y")}),
                semantic="s2",
                side=Side.EXPRESSION,
                vector=Vector.DETERRITORIAL,
            ),
        ],
    )
    eco = compute_three_ecologies(a, _ctx(env_kg=0.0))
    assert eco.social == 1.0


def test_mental_zero_for_single_kind_utterances():
    history = (
        record_utterance(NodeId("a"), "x", "witness", "2026-01-01"),
        record_utterance(NodeId("a"), "y", "witness", "2026-01-02"),
    )
    eco = compute_three_ecologies(_empty_assemblage(), _ctx(env_kg=0.0), history=history)
    assert eco.mental == 0.0


def test_mental_positive_for_diverse_kinds():
    history = (
        record_utterance(NodeId("a"), "x", "witness", "2026-01-01"),
        record_utterance(NodeId("a"), "y", "rule_change", "2026-01-02"),
        record_utterance(NodeId("a"), "z", "refusal", "2026-01-03"),
    )
    eco = compute_three_ecologies(_empty_assemblage(), _ctx(env_kg=0.0), history=history)
    assert eco.mental > 0.0
