"""Capture detector — produces `Critique` warnings, never categorical risk enums.

See SPEC §3.5 and §2.4. Reference: Lazzarato 2014 ch. 3, Terranova 2004 ch. 3,
Guattari *Les Trois Écologies* §1.
"""

from __future__ import annotations

import re
from collections.abc import Sequence

from machinic_assemblage.types import Critique, DeploymentContext, SourceRef, Utterance

# Word-boundary regex prevents substring false-suppression (e.g. "adversarial" matching "ad").
# These are load-bearing: a silent false-negative here would let the very capture the protocol
# is meant to flag pass through unannotated.
_AD_TARGETING_RE = re.compile(
    r"\b(ads?|ad[-_\s]?targeting|targeting|attention[-_\s]?capture)\b",
    re.IGNORECASE,
)
_DATA_SALE_RE = re.compile(
    r"\b(data[-_\s]?sale|surveillance|dispossession)\b",
    re.IGNORECASE,
)
_CONSENT_RE = re.compile(r"\bconsent\b", re.IGNORECASE)

_LAZZARATO_AD_TARGETING = Critique(
    text=(
        "Operator declares revenue_model='ads' without an explicit critique referencing "
        "the asymmetric semiotic capture of attention by ad-targeting machines. "
        "Lazzarato (2014) ch. 3 names this 'machinic enslavement': subjectivity is "
        "produced by the apparatus rather than expressed through it."
    ),
    source_ref=SourceRef(
        author="Lazzarato",
        work="Signs and Machines: Capitalism and the Production of Subjectivity",
        edition="Semiotext(e) 2014",
        pages="",
    ),
    falsifiability_condition=(
        "This critique dissolves if the operator provides public documentation that targeting "
        "decisions are user-controlled, end-to-end auditable, and revocable at the individual "
        "session level — and that revocation is not penalised in service quality."
    ),
)

_TERRANOVA_DATA_SALE = Critique(
    text=(
        "Operator declares revenue_model='data_sale' without an explicit critique referencing "
        "surveillance dispossession. Terranova (2004) ch. 3 frames this as the conversion of "
        "free labour and ambient interaction into salable network value, which is structurally "
        "different from a service exchange."
    ),
    source_ref=SourceRef(
        author="Terranova",
        work="Network Culture: Politics for the Information Age",
        edition="Pluto Press 2004",
        pages="",
    ),
    falsifiability_condition=(
        "This critique dissolves if every data-sale transaction is documented with itemised "
        "consent, the affected users receive a share commensurate with the sale value, and "
        "users can withdraw both prospectively and retroactively without penalty."
    ),
)

_GUATTARI_NO_CONSENT = Critique(
    text=(
        "Operator runs a revenue-generating deployment with no end_users_consent_uri. "
        "Guattari, *Les Trois Écologies* §1, treats the mental ecology as constitutively "
        "non-extractive; running a paying deployment without locating consent abolishes "
        "that distinction."
    ),
    source_ref=SourceRef(
        author="Guattari",
        work="Les Trois Écologies",
        edition="Galilée 1989 / Pindar & Sutton tr. 2000",
        pages="",
    ),
    falsifiability_condition=(
        "This critique dissolves if the operator publishes a consent URI that is "
        "machine-readable, versioned, and references the specific subjectivities at stake."
    ),
)


def _matches(critique: Critique, pattern: re.Pattern[str]) -> bool:
    return bool(pattern.search(critique.text))


def evaluate_capture(
    context: DeploymentContext,
    history: Sequence[Utterance] = (),
) -> tuple[Critique, ...]:
    """Return the list of capture warnings for this deployment.

    Starts with the operator-declared `used_in_optimization_for` set, then adds derived
    critiques (one per missing-but-implied concern). Derived critiques are deliberately
    redundant with operator declarations to keep the operator honest — if a concern is
    declared, no derived critique is appended; if it is not, the protocol adds the citation
    itself.

    Keyword matching uses word-boundary regex (case-insensitive). Substring matches such as
    ``"adversarial"`` containing ``"ad"`` no longer falsely suppress the Lazzarato
    ad-targeting critique. This is load-bearing: a silent false-negative here would let the
    very capture this detector exists to flag pass through unannotated.
    """
    del history  # v0.1.0: history-conditioned critiques are tracked for v0.2.0
    out: list[Critique] = list(context.used_in_optimization_for)
    declared = tuple(out)
    if context.revenue_model == "ads" and not any(_matches(c, _AD_TARGETING_RE) for c in declared):
        out.append(_LAZZARATO_AD_TARGETING)
    if context.revenue_model == "data_sale" and not any(
        _matches(c, _DATA_SALE_RE) for c in declared
    ):
        out.append(_TERRANOVA_DATA_SALE)
    if context.end_users_consent_uri is None and context.revenue_model != "none":
        if not any(_matches(c, _CONSENT_RE) for c in declared):
            out.append(_GUATTARI_NO_CONSENT)
    return tuple(out)
