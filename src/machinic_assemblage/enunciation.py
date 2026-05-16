"""Collective enunciation helpers.

See SPEC §2.3. Reference: Deleuze & Guattari, *Mille Plateaux* plateau 4
(Massumi tr. 1987 pp. 79–80) on "collective assemblage of enunciation".
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence

from machinic_assemblage.types import NodeId, Utterance


def record_utterance(speaker: NodeId, content: str, kind: str, timestamp_iso: str) -> Utterance:
    """Convenience constructor with validation. Use this rather than `Utterance(...)` directly."""
    if not content:
        raise ValueError("record_utterance.content must be non-empty")
    return Utterance(
        speaker=speaker,
        content=content,
        kind=kind,
        timestamp_iso=timestamp_iso,
    )


def collective_enunciation_signature(history: Sequence[Utterance]) -> str:
    """Stable SHA-256 over the ordered sequence of utterances.

    Used by report consumers to diff conversation histories without persisting `content`.
    """
    payload = [
        {"speaker": u.speaker, "kind": u.kind, "timestamp_iso": u.timestamp_iso} for u in history
    ]
    encoded = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
