"""machinic-assemblage — protocol for evaluating collective enunciation.

See SPEC.md for the political statement and design rationale. Read README.md before importing.
"""

from __future__ import annotations

from machinic_assemblage.assemblage import (
    build_assemblage,
    structure_signature,
    subtract_one,
)
from machinic_assemblage.capture_detector import evaluate_capture
from machinic_assemblage.ecologies import compute_three_ecologies
from machinic_assemblage.enunciation import (
    collective_enunciation_signature,
    record_utterance,
)
from machinic_assemblage.groupe_sujet import detect_subject_group
from machinic_assemblage.protocol import commit, evaluate
from machinic_assemblage.transversality import transversality_index
from machinic_assemblage.types import (
    Assemblage,
    Critique,
    DeploymentContext,
    HeterogeneousEdge,
    Node,
    NodeId,
    ProtocolReport,
    Side,
    SourceRef,
    ThreeEcologiesKPI,
    Utterance,
    Vector,
)

__all__ = [
    "Assemblage",
    "Critique",
    "DeploymentContext",
    "HeterogeneousEdge",
    "Node",
    "NodeId",
    "ProtocolReport",
    "Side",
    "SourceRef",
    "ThreeEcologiesKPI",
    "Utterance",
    "Vector",
    "build_assemblage",
    "collective_enunciation_signature",
    "commit",
    "compute_three_ecologies",
    "detect_subject_group",
    "evaluate",
    "evaluate_capture",
    "record_utterance",
    "structure_signature",
    "subtract_one",
    "transversality_index",
]

__version__ = "0.1.3"
