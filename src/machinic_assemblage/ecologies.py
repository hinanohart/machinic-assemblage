"""Three Ecologies KPI computation.

See SPEC §3.3. There is no composite. Three independent axes.
Reference: Guattari, *Les Trois Écologies* (Galilée 1989; Pindar & Sutton tr. 2000) §3.
"""

from __future__ import annotations

import math
import warnings
from collections import defaultdict
from collections.abc import Sequence

from machinic_assemblage.types import (
    Assemblage,
    DeploymentContext,
    NodeId,
    ThreeEcologiesKPI,
    Utterance,
)

_ENVIRONMENTAL_KG_THRESHOLD_DEFAULT: float = 50.0


def _mental(history: Sequence[Utterance]) -> float:
    if not history:
        return 0.0
    per_speaker: dict[NodeId, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for u in history:
        per_speaker[u.speaker][u.kind] += 1
    diversities: list[float] = []
    for kinds in per_speaker.values():
        total = sum(kinds.values())
        k = len(kinds)
        if total == 0 or k <= 1:
            diversities.append(0.0)
            continue
        h = -sum((c / total) * math.log(c / total) for c in kinds.values() if c > 0)
        diversities.append(h / math.log(k))
    if not diversities:
        return 0.0
    if any(d == 0.0 for d in diversities):
        return 0.0
    log_mean = sum(math.log(d) for d in diversities) / len(diversities)
    return math.exp(log_mean)


def _social(a: Assemblage) -> float:
    if not a.edges:
        return 0.0
    pair_counts: dict[tuple[NodeId, NodeId], int] = defaultdict(int)
    for edge in a.edges:
        members = sorted(edge.members)
        for i, x in enumerate(members):
            for y in members[i + 1 :]:
                pair_counts[(x, y)] += 1
    if not pair_counts:
        return 0.0
    reciprocated = sum(1 for c in pair_counts.values() if c >= 2)
    return reciprocated / len(pair_counts)


def _environmental(
    context: DeploymentContext,
    threshold_kg: float = _ENVIRONMENTAL_KG_THRESHOLD_DEFAULT,
) -> float:
    kg = context.environmental_kgco2eq_estimate
    if kg is None:
        warnings.warn(
            "DeploymentContext.environmental_kgco2eq_estimate is None; "
            "environmental axis defaults to 0.0. SPEC §3.3.",
            UserWarning,
            stacklevel=3,
        )
        return 0.0
    value = 1.0 - (kg / threshold_kg)
    return min(1.0, max(0.0, value))


def compute_three_ecologies(
    a: Assemblage,
    context: DeploymentContext,
    history: Sequence[Utterance] = (),
    environmental_threshold_kg: float = _ENVIRONMENTAL_KG_THRESHOLD_DEFAULT,
) -> ThreeEcologiesKPI:
    """Return three independent values. Aggregation is the operator's responsibility."""
    return ThreeEcologiesKPI(
        mental=_mental(history),
        social=_social(a),
        environmental=_environmental(context, threshold_kg=environmental_threshold_kg),
    )
