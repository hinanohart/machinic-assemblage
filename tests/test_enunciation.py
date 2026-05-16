"""Enunciation helper tests."""

from __future__ import annotations

import pytest

from machinic_assemblage import (
    NodeId,
    collective_enunciation_signature,
    record_utterance,
)


def test_record_utterance_rejects_empty_content():
    with pytest.raises(ValueError, match="content"):
        record_utterance(NodeId("a"), "", "witness", "2026-01-01")


def test_signature_deterministic():
    history = (
        record_utterance(NodeId("a"), "x", "witness", "2026-01-01"),
        record_utterance(NodeId("b"), "y", "rule_change", "2026-01-02"),
    )
    s1 = collective_enunciation_signature(history)
    s2 = collective_enunciation_signature(history)
    assert s1 == s2


def test_signature_excludes_content():
    """Two histories with same speaker/kind/time but different content should hash the same."""
    h1 = (record_utterance(NodeId("a"), "first content", "witness", "2026-01-01"),)
    h2 = (record_utterance(NodeId("a"), "different content", "witness", "2026-01-01"),)
    assert collective_enunciation_signature(h1) == collective_enunciation_signature(h2)
