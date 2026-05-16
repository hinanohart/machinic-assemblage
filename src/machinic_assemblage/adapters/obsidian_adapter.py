"""Obsidian vault adapter — skeleton only in v0.1.0.

SPEC §4.
"""

from __future__ import annotations

import pathlib

from machinic_assemblage.types import Assemblage


def from_obsidian_vault(path: str | pathlib.Path) -> Assemblage:
    """Convert an Obsidian vault directory to an `Assemblage`.

    Not implemented in v0.1.0. The recommended v0.2.x interface treats each note as a
    `Node(kind="note")`, each `[[wikilink]]` as a `HeterogeneousEdge` with semantic drawn
    from the note's frontmatter tag, and uses note frontmatter `kind: rule_change` entries
    as the source of `Utterance` history.
    """
    raise NotImplementedError("Obsidian adapter is v0.2.x. See SPEC §4 and docs/adapters.md.")
