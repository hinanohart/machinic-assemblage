"""Groupe-sujet (subject-group) vs. groupe-assujetti (subjugated-group) detection.

See SPEC §3.4. Reference: Guattari, *Psychanalyse et transversalité* (Maspero 1972),
ch. "Le transfert" and *La Révolution moléculaire* (Recherches 1977) for the
groupe-sujet test apparatus.
"""

from __future__ import annotations

from collections.abc import Sequence

from machinic_assemblage.assemblage import structure_signature
from machinic_assemblage.types import Assemblage, NodeId, Utterance


def detect_subject_group(
    history: Sequence[Utterance],
    assemblage_before: Assemblage,
    assemblage_after: Assemblage | None = None,
) -> tuple[bool, tuple[str, ...]]:
    """Return `(is_subject_group, evidence)`.

    Subject-group activity requires **all three** conditions in SPEC §3.4:

    1. At least one `rule_change` utterance in history.
    2. `structure_signature(before)` differs from `structure_signature(after)` — non-cosmetic
       structural change.
    3. Every rule-change speaker is themselves a member of the resulting assemblage. A speaker
       who proposes a rule change but is *not* a participant in the assemblage they are
       reshaping is, by Guattari's reading, exercising top-down authority — the apparatus
       imposing rules from outside. The intersection rule-change-speakers ∩ members_after must
       cover every rule-change-speaker (no purely external imposers).

    `assemblage_after = None` means the structural change has not been applied yet; the
    test returns `False` with that evidence.
    """
    evidence: list[str] = []

    rule_change_speakers: set[NodeId] = {u.speaker for u in history if u.kind == "rule_change"}
    if not rule_change_speakers:
        evidence.append("no rule_change utterance in history")
        return False, tuple(evidence)
    evidence.append(f"rule_change speakers: {sorted(rule_change_speakers)}")

    if assemblage_after is None:
        evidence.append("assemblage_after not provided")
        return False, tuple(evidence)

    sig_before = structure_signature(assemblage_before)
    sig_after = structure_signature(assemblage_after)
    if sig_before == sig_after:
        evidence.append("structural signature unchanged: cosmetic-only")
        return False, tuple(evidence)
    evidence.append(f"signature changed: {sig_before[:8]}... -> {sig_after[:8]}...")

    members_after = {n.id for n in assemblage_after.nodes}
    external_speakers = rule_change_speakers - members_after
    if external_speakers:
        evidence.append(
            f"top-down imposition: speakers {sorted(external_speakers)} "
            "are not members of the resulting assemblage"
        )
        return False, tuple(evidence)

    overlap = rule_change_speakers & members_after
    evidence.append(f"overlap (rule_change ∩ members_after) = {sorted(overlap)}")
    return True, tuple(evidence)
