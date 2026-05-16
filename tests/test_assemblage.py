"""Assemblage construction and structural signature tests."""

from __future__ import annotations

import pytest
from hypothesis import HealthCheck, given, settings
from hypothesis import strategies as st

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Vector,
    build_assemblage,
    structure_signature,
    subtract_one,
)


def test_build_assemblage_rejects_unknown_member():
    nodes = [Node(id=NodeId("a"), kind="human")]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    with pytest.raises(ValueError, match="unknown node ids"):
        build_assemblage(nodes, edges)


def test_signature_stable_under_input_ordering():
    nodes_a = [Node(id=NodeId("a"), kind="human"), Node(id=NodeId("b"), kind="human")]
    nodes_b = list(reversed(nodes_a))
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    sig_a = structure_signature(build_assemblage(nodes_a, edges))
    sig_b = structure_signature(build_assemblage(nodes_b, edges))
    assert sig_a == sig_b


def test_signature_changes_on_subtract():
    nodes = [Node(id=NodeId("a"), kind="human"), Node(id=NodeId("b"), kind="human")]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    a = build_assemblage(nodes, edges)
    a2 = subtract_one(a, NodeId("a"), reason="withdrew consent on 2026-05-17")
    assert structure_signature(a) != structure_signature(a2)


def test_subtract_requires_nontrivial_reason():
    nodes = [Node(id=NodeId("a"), kind="human")]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    a = build_assemblage(nodes, edges)
    with pytest.raises(ValueError, match="non-trivial"):
        subtract_one(a, NodeId("a"), reason="x")


def test_subtract_unknown_node_rejected():
    nodes = [Node(id=NodeId("a"), kind="human")]
    a = build_assemblage(nodes, [])
    with pytest.raises(ValueError, match="unknown"):
        subtract_one(a, NodeId("z"), reason="reasonable reason")


@settings(suppress_health_check=[HealthCheck.too_slow], deadline=None, max_examples=30)
@given(
    node_ids=st.lists(
        st.text(
            alphabet=st.characters(min_codepoint=97, max_codepoint=122), min_size=1, max_size=4
        ),
        min_size=1,
        max_size=6,
        unique=True,
    ),
)
def test_signature_independent_of_node_iteration_order(node_ids):
    nodes_forward = [Node(id=NodeId(nid), kind="human") for nid in node_ids]
    nodes_reverse = list(reversed(nodes_forward))
    sig_f = structure_signature(build_assemblage(nodes_forward, []))
    sig_r = structure_signature(build_assemblage(nodes_reverse, []))
    assert sig_f == sig_r
