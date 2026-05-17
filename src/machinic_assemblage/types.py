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


def _require_nonblank(value: str, name: str) -> None:
    """Reject empty *and* whitespace-only strings for required fields.

    A field that is required but accepts ``' '`` or ``'\\t' * 10`` is functionally optional;
    SPEC §2 treats required strings as positive content, not placeholders.
    """
    if not value or not value.strip():
        raise ValueError(f"{name} must be non-empty and not whitespace-only")


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
        _require_nonblank(self.id, "Node.id")
        _require_nonblank(self.kind, "Node.kind")


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
        _require_nonblank(self.semantic, "HeterogeneousEdge.semantic")
        if not math.isfinite(self.weight):
            raise ValueError("HeterogeneousEdge.weight must be finite (no NaN/inf)")
        if self.weight < 0.0:
            raise ValueError("HeterogeneousEdge.weight must be non-negative")
        if self.subtract and not self.subtract_reason.strip():
            raise ValueError(
                "HeterogeneousEdge.subtract requires subtract_reason "
                "(see SPEC §2.1: N-1 is not set difference)."
            )
        if self.subtract_reason.strip() and not self.subtract:
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
        _require_nonblank(self.speaker, "Utterance.speaker")
        _require_nonblank(self.kind, "Utterance.kind")
        _require_nonblank(self.timestamp_iso, "Utterance.timestamp_iso")


@dataclass(frozen=True)
class SourceRef:
    """A citation. `pages` may be empty for derived critiques per SPEC §3.5."""

    author: str
    work: str
    edition: str
    pages: str = ""

    def __post_init__(self) -> None:
        _require_nonblank(self.author, "SourceRef.author")
        _require_nonblank(self.work, "SourceRef.work")
        _require_nonblank(self.edition, "SourceRef.edition")


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
# a real citation must follow: `Author, Work, Publisher YEAR`. The regex captures three
# comma-separated tokens followed by a 4-digit year; Python-level validation then requires each
# token to contain at least one Unicode letter AND have length >= 2 after stripping.
#
# Honest limits documented in CHANGELOG v0.1.3:
# - A regex cannot enforce *semantic* citation quality. Real-looking but dummy citations like
#   `aa, bb, cc 1999` will still pass and rely on human review per SPEC §5 intervention point 5.
# - Legitimate citations with single-letter author initials (e.g. `H. Lefebvre, A, Pub 1990`)
#   pass because tokens are length>=2 (`H.`, `A` after strip is length 1 — but `A` is a single
#   letter and we accept it; v0.1.2 incorrectly rejected this).
_PRIMARY_SOURCE_RE = re.compile(
    r"primary_source:\s*([^,\n]+),\s*([^,\n]+),\s*([^,\n]+?)\s+(\d{4})\b",
    re.IGNORECASE,
)


def _has_valid_primary_source(text: str) -> bool:
    """Validate ``primary_source: Author, Work, Publisher YEAR`` citation in ``text``.

    Each of the three tokens must (a) strip to a non-empty string and (b) contain at least one
    Unicode letter. Pure-punctuation tokens (``##, %%, ^^ 2024``) and whitespace-only tokens
    are rejected. Single-letter tokens like ``A`` are accepted (legitimate citations contain
    initials and short titles).
    """
    m = _PRIMARY_SOURCE_RE.search(text)
    if not m:
        return False
    for raw in (m.group(1), m.group(2), m.group(3)):
        stripped = raw.strip()
        if not stripped:
            return False
        if not any(ch.isalpha() for ch in stripped):
            return False
    return True


@dataclass(frozen=True)
class Critique:
    """A capture warning, in natural language, with a citation and a falsifiability condition.

    Replaces the rejected `CaptureRisk` enum — see SPEC §2.4. The closed enumeration of "risks"
    is itself the move Lazzarato (2014) critiques: it converts structural critique into a
    compliance checklist. A `Critique` is answerable, not categorical.

    The `<other>` author escape requires a regex-matched `primary_source:` citation of the
    form ``primary_source: Author, Work, Publisher YEAR``. Pure-punctuation, whitespace-only,
    and letterless tokens are rejected.
    """

    text: str
    source_ref: SourceRef
    falsifiability_condition: str

    def __post_init__(self) -> None:
        if not self.text or len(self.text.strip()) < 16:
            raise ValueError(
                "Critique.text must be a non-trivial natural-language description "
                "(>= 16 non-whitespace chars). Capture warnings are answerable, not categorical."
            )
        if not self.falsifiability_condition or len(self.falsifiability_condition.strip()) < 16:
            raise ValueError(
                "Critique.falsifiability_condition is required (>= 16 non-whitespace chars). "
                "A critique with no observable disconfirmation is dogma, not analysis."
            )
        author_ok = self.source_ref.author in _ALLOWED_CRITIQUE_AUTHORS or (
            self.source_ref.author == "<other>" and _has_valid_primary_source(self.text)
        )
        if not author_ok:
            raise ValueError(
                f"Critique.source_ref.author must be one of {_ALLOWED_CRITIQUE_AUTHORS} "
                f"or '<other>' with a regex-matching 'primary_source: Author, Work, "
                f"Publisher YEAR' in text (each citation token must contain a letter); "
                f"got {self.source_ref.author!r}."
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
        _require_nonblank(self.operator_org, "DeploymentContext.operator_org")
        _require_nonblank(self.declared_at_iso, "DeploymentContext.declared_at_iso")
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
