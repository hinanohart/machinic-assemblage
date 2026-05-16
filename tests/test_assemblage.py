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


def test_subtract_one_is_idempotent_on_repeat_apply():
    """CRITICAL-3: applying the same (node, reason) twice must not change the signature."""
    nodes = [Node(id=NodeId("a"), kind="human"), Node(id=NodeId("b"), kind="human")]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    a0 = build_assemblage(nodes, edges)
    a1 = subtract_one(a0, NodeId("a"), reason="withdrew consent 2026-05-17")
    a2 = subtract_one(a1, NodeId("a"), reason="withdrew consent 2026-05-17")
    assert structure_signature(a1) == structure_signature(a2)


def test_subtract_one_with_different_reason_keeps_first():
    """v0.1.x design pin (SPEC §2.1): same-node repeat-subtract retains the first reason.

    This is the explicit trade-off documented in SPEC §2.1: because `subtract` is a
    `frozenset[NodeId]`, multiple reasons against the same node cannot be held simultaneously.
    The first reason wins; v0.2.0 is expected to change the type to
    `frozenset[tuple[NodeId, str]]` to remove this limit.
    """
    nodes = [Node(id=NodeId("a"), kind="human"), Node(id=NodeId("b"), kind="human")]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
    ]
    a0 = build_assemblage(nodes, edges)
    a1 = subtract_one(a0, NodeId("a"), reason="first reason here")
    a2 = subtract_one(a1, NodeId("a"), reason="a different second reason here")
    # Signature unchanged: the second reason is silently dropped per the v0.1.x design.
    assert structure_signature(a1) == structure_signature(a2)


def test_signature_stable_under_float_drift():
    """MAJOR-4: weight from `0.1 + 0.2` must hash identically to `0.3`."""
    nodes = [Node(id=NodeId("a"), kind="human")]
    e_drift = HeterogeneousEdge(
        members=frozenset({NodeId("a")}),
        semantic="x",
        side=Side.CONTENT,
        vector=Vector.TERRITORIAL,
        weight=0.1 + 0.2,
    )
    e_clean = HeterogeneousEdge(
        members=frozenset({NodeId("a")}),
        semantic="x",
        side=Side.CONTENT,
        vector=Vector.TERRITORIAL,
        weight=0.3,
    )
    sig_a = structure_signature(build_assemblage(nodes, [e_drift]))
    sig_b = structure_signature(build_assemblage(nodes, [e_clean]))
    assert sig_a == sig_b


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
