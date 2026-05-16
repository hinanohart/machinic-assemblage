"""Assemblage construction, structural signature, and N-1 subtract.

See SPEC §2.1–2.2.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Iterable

from machinic_assemblage.types import Assemblage, HeterogeneousEdge, Node, NodeId


def build_assemblage(
    nodes: Iterable[Node],
    edges: Iterable[HeterogeneousEdge],
) -> Assemblage:
    """Build a validated :class:`Assemblage`. Every edge's members must be a subset of nodes.

    Order of input is irrelevant; the resulting `Assemblage` is frozen and hashable.
    """
    node_set = frozenset(nodes)
    node_ids = {n.id for n in node_set}
    edge_list = list(edges)
    for edge in edge_list:
        missing = edge.members - node_ids
        if missing:
            raise ValueError(
                f"Edge {edge.semantic!r} references unknown node ids: {sorted(missing)}"
            )
        if edge.subtract and not edge.subtract <= node_ids:
            raise ValueError(
                f"Edge {edge.semantic!r} subtracts unknown node ids: "
                f"{sorted(edge.subtract - node_ids)}"
            )
    return Assemblage(nodes=node_set, edges=frozenset(edge_list))


def _canonical_node(n: Node) -> dict[str, object]:
    return {"id": n.id, "kind": n.kind, "attrs": list(n.attrs)}


def _canonical_edge(e: HeterogeneousEdge) -> dict[str, object]:
    return {
        "members": sorted(e.members),
        "semantic": e.semantic,
        "side": e.side.value,
        "vector": e.vector.value,
        "weight": e.weight,
        "subtract": sorted(e.subtract),
        "subtract_reason": e.subtract_reason,
    }


def structure_signature(a: Assemblage) -> str:
    """Stable SHA-256 hex of the canonical encoding of `a`. Order-independent."""
    payload = {
        "nodes": sorted((_canonical_node(n) for n in a.nodes), key=lambda d: str(d["id"])),
        "edges": sorted(
            (_canonical_edge(e) for e in a.edges),
            key=lambda d: (
                str(d["semantic"]),
                str(d["side"]),
                str(d["vector"]),
                str(d["members"]),
                str(d["subtract"]),
                str(d["subtract_reason"]),
            ),
        ),
    }
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def subtract_one(a: Assemblage, node_id: NodeId, reason: str) -> Assemblage:
    """Return an assemblage with `node_id` marked as N-1 across all edges that contain it.

    Per SPEC §2.1, this is *not* edge.members - {node_id}: the subtraction is recorded as
    `subtract = {node_id}` with the supplied `reason`, preserving the multiplicity reading.
    """
    if not reason or len(reason) < 8:
        raise ValueError(
            "subtract_one(reason=...) must be non-trivial (>= 8 chars). "
            "N-1 is not anonymous deletion."
        )
    if node_id not in {n.id for n in a.nodes}:
        raise ValueError(f"subtract_one: unknown node id {node_id!r}")
    new_edges: set[HeterogeneousEdge] = set()
    for edge in a.edges:
        if node_id in edge.members:
            new_edges.add(
                HeterogeneousEdge(
                    members=edge.members,
                    semantic=edge.semantic,
                    side=edge.side,
                    vector=edge.vector,
                    weight=edge.weight,
                    subtract=edge.subtract | {node_id},
                    subtract_reason=(
                        f"{edge.subtract_reason}; {reason}".lstrip("; ")
                        if edge.subtract_reason
                        else reason
                    ),
                )
            )
        else:
            new_edges.add(edge)
    return Assemblage(nodes=a.nodes, edges=frozenset(new_edges))
