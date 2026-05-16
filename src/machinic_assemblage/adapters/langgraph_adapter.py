"""LangGraph adapter — skeleton only in v0.1.0.

SPEC §4: documents the interface; full implementation is v0.2.x. We do not depend on
LangGraph at install time, and we do not import it at module level — that keeps the core
free of an optional 1.5GB transitive footprint.
"""

from __future__ import annotations

from typing import Any

from machinic_assemblage.types import Assemblage


def from_langgraph_state(state: Any) -> Assemblage:
    """Convert a LangGraph runtime state to an `Assemblage`.

    Not implemented in v0.1.0. The recommended v0.2.x interface treats each node in the
    LangGraph compiled graph as a `Node(kind="agent")`, each edge as a heterogeneous edge
    with `semantic` drawn from the LangGraph edge label, and uses the active `Command(goto=...)`
    record as the source of `Utterance` history.
    """
    raise NotImplementedError("LangGraph adapter is v0.2.x. See SPEC §4 and docs/adapters.md.")
