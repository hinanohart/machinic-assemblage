"""Transversality index.

See SPEC §3.2. Reference: Guattari, *Psychanalyse et transversalité* (Maspero 1972),
re-read through Battiston et al. 2017 ("The new challenges of multiplex networks", Phys.
Rep. 544). The normative axis treatment is this project's contribution.
"""

from __future__ import annotations

import math
from collections import defaultdict
from collections.abc import Sequence

from machinic_assemblage.types import Assemblage, NodeId, Utterance


def _shannon_entropy_normalised(counts: dict[str, int]) -> float:
    total = sum(counts.values())
    if total == 0:
        return 0.0
    k = len(counts)
    if k <= 1:
        return 0.0
    h = -sum((c / total) * math.log(c / total) for c in counts.values() if c > 0)
    return h / math.log(k)


def _h_layer_per_node(a: Assemblage) -> dict[NodeId, float]:
    per_node: dict[NodeId, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for edge in a.edges:
        for member in edge.members:
            per_node[member][edge.semantic] += 1
    return {nid: _shannon_entropy_normalised(d) for nid, d in per_node.items()}


def _cross_layer_edge_ratio(a: Assemblage) -> float:
    if not a.edges:
        return 0.0
    node_layers: dict[NodeId, set[str]] = defaultdict(set)
    for edge in a.edges:
        for member in edge.members:
            node_layers[member].add(edge.semantic)
    cross = 0
    for edge in a.edges:
        seen: set[str] = set()
        for member in edge.members:
            seen.update(node_layers[member])
            if len(seen) >= 2:
                break
        if len(seen) >= 2:
            cross += 1
    return cross / len(a.edges)


def transversality_index(
    a: Assemblage,
    history: Sequence[Utterance] = (),
) -> float:
    """Return the transversality index T(A, history) in `[0, 1]`.

    `history` restricts the geometric mean to active speakers (those who have uttered at least
    once). When `history` is empty, all nodes are considered active.
    """
    h = _h_layer_per_node(a)
    if history:
        active = {u.speaker for u in history}
        h = {nid: v for nid, v in h.items() if nid in active}
    if not h:
        return 0.0
    values = list(h.values())
    if any(v == 0.0 for v in values):
        return 0.0 * _cross_layer_edge_ratio(a)
    log_mean = sum(math.log(v) for v in values) / len(values)
    geomean = math.exp(log_mean)
    return geomean * _cross_layer_edge_ratio(a)
