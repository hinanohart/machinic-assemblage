"""Core types for machinic-assemblage.

All public types are frozen / immutable. Type identity is structural — equality is by value and
hashes are stable across runs, so reports can be serialised and diffed safely.

Citations in this module:
- *Mille Plateaux* (D&G) — Massumi tr. 1987, plateau 4 (content/expression, territory/deterritory)
  and pp. 6, 21–22 ("Subtract the unique" / N-1).
- *Les Trois Écologies* (Guattari) — Pindar & Sutton tr. 2000, §3 (incommensurability of axes).
- Lazzarato 2014, ch. 3 (capitalist semiotic machine).
"""

from __future__ import annotations

import math
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Literal, NewType, get_args

NodeId = NewType("NodeId", str)


class Side(str, Enum):
    """Content / expression — *Mille Plateaux*, plateau 4 (Massumi 1987 pp. 88–89)."""

    CONTENT = "content"
    EXPRESSION = "expression"


class Vector(str, Enum):
    """Territorial / deterritorial — same plateau."""

    TERRITORIAL = "territorial"
    DETERRITORIAL = "deterritorial"


RevenueModel = Literal["none", "donation", "subscription", "ads", "data_sale", "other"]


@dataclass(frozen=True, order=False)
class Node:
    """A typed participant in an assemblage.

    `kind` is free-form but conventional values include "human", "agent", "dataset",
    "organisation", "instrument" — the heterogeneity is the point.
    """

    id: NodeId
    kind: str
    attrs: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.id:
            raise ValueError("Node.id must be non-empty")
        if not self.kind:
            raise ValueError("Node.kind must be non-empty")


@dataclass(frozen=True)
class HeterogeneousEdge:
    """An N-ary, typed, signed edge across heterogeneous node kinds.

    `subtract` encodes the N-1 form (cf. *Mille Plateaux*, Massumi 1987 pp. 6, 21–22). When
    `subtract` is non-empty, `subtract_reason` is required and becomes part of the hash. This
    means two N-1 operations against the same molar identity but with different reasons are
    distinct edges — `subtract` is not equivalent to "set difference on members".
    """

    members: frozenset[NodeId]
    semantic: str
    side: Side
    vector: Vector
    weight: float = 1.0
    subtract: frozenset[NodeId] = field(default_factory=frozenset)
    subtract_reason: str = ""

    def __post_init__(self) -> None:
        if not self.members:
            raise ValueError("HeterogeneousEdge.members must be non-empty")
        if not self.semantic:
            raise ValueError("HeterogeneousEdge.semantic must be non-empty")
        if not math.isfinite(self.weight):
            raise ValueError("HeterogeneousEdge.weight must be finite (no NaN/inf)")
        if self.weight < 0.0:
            raise ValueError("HeterogeneousEdge.weight must be non-negative")
        if self.subtract and not self.subtract_reason:
            raise ValueError(
                "HeterogeneousEdge.subtract requires subtract_reason "
                "(see SPEC §2.1: N-1 is not set difference)."
            )
        if self.subtract_reason and not self.subtract:
            raise ValueError(
                "HeterogeneousEdge.subtract_reason set without subtract; "
                "use subtract=frozenset({node_id}) or clear the reason."
            )


@dataclass(frozen=True)
class Assemblage:
    """A frozen pair of nodes and edges. Constructed via :func:`build_assemblage`."""

    nodes: frozenset[Node]
    edges: frozenset[HeterogeneousEdge]


@dataclass(frozen=True)
class Utterance:
    """A record of collective enunciation. `kind == "rule_change"` triggers groupe-sujet test."""

    speaker: NodeId
    content: str
    kind: str
    timestamp_iso: str

    def __post_init__(self) -> None:
        if not self.speaker:
            raise ValueError("Utterance.speaker must be non-empty")
        if not self.kind:
            raise ValueError("Utterance.kind must be non-empty")
        if not self.timestamp_iso:
            raise ValueError("Utterance.timestamp_iso must be ISO 8601 string, not empty")


@dataclass(frozen=True)
class SourceRef:
    """A citation. `pages` may be empty for derived critiques per SPEC §3.5."""

    author: str
    work: str
    edition: str
    pages: str = ""

    def __post_init__(self) -> None:
        if not self.author:
            raise ValueError("SourceRef.author must be non-empty")
        if not self.work:
            raise ValueError("SourceRef.work must be non-empty")
        if not self.edition:
            raise ValueError("SourceRef.edition must be non-empty")


_ALLOWED_CRITIQUE_AUTHORS = frozenset(
    {
        "Guattari",
        "Deleuze",
        "Deleuze & Guattari",
        "Lazzarato",
        "Terranova",
        "Berardi",
        "Stiegler",
    }
)

# Closes the `<other>` author hatch. The substring `"primary_source:"` alone is not enough —
# a real citation must follow: `Author, Work, Publisher YEAR`. Year must be a four-digit number.
# This is load-bearing: a bare `primary_source:` keyword would let unsourced critiques through.
_PRIMARY_SOURCE_RE = re.compile(
    r"primary_source:\s*[^,\n]{2,},\s*[^,\n]{2,},\s*[^,\n]{2,}\b\d{4}\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Critique:
    """A capture warning, in natural language, with a citation and a falsifiability condition.

    Replaces the rejected `CaptureRisk` enum — see SPEC §2.4. The closed enumeration of "risks"
    is itself the move Lazzarato (2014) critiques: it converts structural critique into a
    compliance checklist. A `Critique` is answerable, not categorical.

    The `<other>` author escape requires a regex-matched `primary_source:` citation of the
    form ``primary_source: Author, Work, Publisher YEAR``. Bare keyword substrings are
    rejected.
    """

    text: str
    source_ref: SourceRef
    falsifiability_condition: str

    def __post_init__(self) -> None:
        if not self.text or len(self.text) < 16:
            raise ValueError(
                "Critique.text must be a non-trivial natural-language description "
                "(>= 16 chars). Capture warnings are answerable, not categorical."
            )
        if not self.falsifiability_condition or len(self.falsifiability_condition) < 16:
            raise ValueError(
                "Critique.falsifiability_condition is required (>= 16 chars). "
                "A critique with no observable disconfirmation is dogma, not analysis."
            )
        author_ok = self.source_ref.author in _ALLOWED_CRITIQUE_AUTHORS or (
            self.source_ref.author == "<other>" and bool(_PRIMARY_SOURCE_RE.search(self.text))
        )
        if not author_ok:
            raise ValueError(
                f"Critique.source_ref.author must be one of {_ALLOWED_CRITIQUE_AUTHORS} "
                f"or '<other>' with a regex-matching 'primary_source: Author, Work, "
                f"Publisher YEAR' in text; got {self.source_ref.author!r}."
            )


@dataclass(frozen=True)
class DeploymentContext:
    """Mandatory argument to :func:`evaluate`. Records the operator's declared deployment.

    There is no research-mode bypass. SPEC §2.5: bypassing this requires forking the project.
    """

    operator_org: str
    revenue_model: RevenueModel
    end_users_consent_uri: str | None
    used_in_optimization_for: frozenset[Critique]
    declared_at_iso: str
    environmental_kgco2eq_estimate: float | None = None

    def __post_init__(self) -> None:
        if not self.operator_org:
            raise ValueError("DeploymentContext.operator_org must be non-empty")
        if not self.declared_at_iso:
            raise ValueError("DeploymentContext.declared_at_iso must be ISO 8601, not empty")
        if self.revenue_model not in get_args(RevenueModel):
            raise ValueError(
                f"DeploymentContext.revenue_model must be one of "
                f"{get_args(RevenueModel)}; got {self.revenue_model!r}"
            )
        if self.environmental_kgco2eq_estimate is not None:
            if not math.isfinite(self.environmental_kgco2eq_estimate):
                raise ValueError("DeploymentContext.environmental_kgco2eq_estimate must be finite")
            if self.environmental_kgco2eq_estimate < 0.0:
                raise ValueError(
                    "DeploymentContext.environmental_kgco2eq_estimate cannot be negative"
                )


@dataclass(frozen=True)
class ThreeEcologiesKPI:
    """mental / social / environmental — three independent axes.

    No `composite` property exists and none will be added. See SPEC §2.6. A static lint
    (tools/lint_composite_score.py) rejects any function in this codebase whose signature
    collapses this type to a single `float`. Subclassing is also blocked at class-creation
    time so that downstream code cannot re-introduce an aggregate score via
    `class Foo(ThreeEcologiesKPI): @property composite`.
    """

    mental: float
    social: float
    environmental: float

    def __init_subclass__(cls, **kwargs: Any) -> None:
        raise TypeError(
            "ThreeEcologiesKPI may not be subclassed. SPEC §2.6: a composite or aggregate "
            "score over (mental, social, environmental) is intentionally absent and cannot "
            "be re-introduced via inheritance or attribute injection. If you need a "
            "weighted summary for your own pipeline, compute it in your own code on the "
            "three values, and declare the tradeoff in your DeploymentContext."
        )

    def __post_init__(self) -> None:
        for label, value in (
            ("mental", self.mental),
            ("social", self.social),
            ("environmental", self.environmental),
        ):
            if not 0.0 <= value <= 1.0:
                raise ValueError(f"ThreeEcologiesKPI.{label} must be in [0, 1]; got {value!r}")


@dataclass(frozen=True)
class ProtocolReport:
    """Output of :func:`evaluate`. Persist with :func:`commit`."""

    timestamp_iso: str
    assemblage_signature: str
    transversality_index: float
    three_ecologies: ThreeEcologiesKPI
    is_subject_group: bool
    groupe_sujet_evidence: tuple[str, ...]
    capture_warnings: tuple[Critique, ...]
    context: DeploymentContext
