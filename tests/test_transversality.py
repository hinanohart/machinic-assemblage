"""Transversality index tests."""

from __future__ import annotations

import math

from machinic_assemblage import (
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Vector,
    build_assemblage,
    transversality_index,
)


def _single_layer_assemblage():
    nodes = [Node(id=NodeId(f"n{i}"), kind="agent") for i in range(4)]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId(f"n{i}"), NodeId(f"n{(i + 1) % 4}")}),
            semantic="only-layer",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        )
        for i in range(4)
    ]
    return build_assemblage(nodes, edges)


def _multi_layer_assemblage():
    nodes = [Node(id=NodeId(f"n{i}"), kind="agent") for i in range(4)]
    layers = ["consult", "lookup", "review"]
    edges = []
    for i in range(4):
        for j, layer in enumerate(layers):
            edges.append(
                HeterogeneousEdge(
                    members=frozenset({NodeId(f"n{i}"), NodeId(f"n{(i + j + 1) % 4}")}),
                    semantic=layer,
                    side=Side.CONTENT,
                    vector=Vector.TERRITORIAL,
                )
            )
    return build_assemblage(nodes, edges)


def test_single_layer_yields_zero():
    a = _single_layer_assemblage()
    t = transversality_index(a)
    assert t == 0.0


def test_multi_layer_yields_positive():
    a = _multi_layer_assemblage()
    t = transversality_index(a)
    assert t > 0.0
    assert t <= 1.0


def test_transversality_bounded():
    a = _multi_layer_assemblage()
    t = transversality_index(a)
    assert 0.0 <= t <= 1.0
    assert not math.isnan(t)
