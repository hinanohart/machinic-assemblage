# Limits

Things machinic-assemblage v0.1.0 cannot or should not do.

## Second-order capture (Gödel-style regress)

The capture detector itself is a piece of code that can be captured. v0.1.0 acknowledges
the regress and bounds it at one layer: we do not run the capture detector on the capture
detector. We accept this as an instance of the kind of incompleteness that Gödel makes
inevitable in self-referential systems; the protocol's job is to make the layer visible,
not to dissolve it.

A v0.3.x design sketch for a meta-detector is in `docs/open_questions.md`.

## Heuristic gaming

`detect_subject_group` is a heuristic. False positives (cosmetic renames flagged as
rule changes) and false negatives (a real molecular revolution that doesn't touch
`structure_signature`) are both possible. SPEC §3.4 chooses to surface the verdict as a
`UserWarning` rather than a hard CI failure precisely because hard assertion on a heuristic
incentivises gaming the heuristic. Reviewers are expected to read the warning.

## Diagnostic / clinical use

The protocol is **not** a diagnostic tool. Output must not drive decisions about a person's
mental health, legal status, or medical condition. The mental ecology axis measures
diversity of utterance kinds across speakers, not any psychological construct about a
named person. See SPEC §6.

## Environmental axis precision

`environmental_kgco2eq_estimate` is operator-supplied. The protocol cannot verify it. The
threshold-based normalisation is intentionally crude — see `docs/environmental.md`.

## Cultural and translation specificity

Guattari's concepts are read through specific editions; their use in this codebase
inevitably reflects those translations. The required edition tags on every citation are
the protocol's response to that — they make the inheritance auditable, not invisible.

## Scale

The reference implementation uses Python sets and dataclasses. It is fine for
assemblages up to a few hundred nodes and a few thousand edges. Larger assemblages will
benefit from a v0.2.x rewrite that uses `networkx` or a custom CSR backing store; until
then, slowness above ~10k edges is expected.
