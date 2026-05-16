# Changelog

All notable changes to machinic-assemblage will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). API stability promises
are in SPEC §7.

## [0.1.1] — 2026-05-17

Patch release. Closes four load-bearing-design bypasses discovered by post-publication audit;
no public API changes (the 23 symbols in `__all__` are unchanged). SPEC line-count brought into
the 200–300 band.

### Hardened (load-bearing design protections)

- `Critique` `<other>` author now requires a regex-matching `primary_source: Author, Work,
  Publisher YEAR` citation. The previous substring check accepted any text containing
  `"primary_source:"`, including `"primary_source: nothing"`. Closes the SPEC §2.4 hatch.
- `ThreeEcologiesKPI` blocks subclassing at class-creation time via `__init_subclass__`.
  Previously a downstream `class CompositeKPI(ThreeEcologiesKPI): @property composite` could
  re-introduce an aggregate score that the AST lint never sees. Closes the SPEC §2.6 hatch.
- `subtract_one(node, reason)` is now idempotent on repeat application. Previously two
  identical applications produced `"reason; reason"` and a different `structure_signature`,
  silently breaking SPEC §2.1 algebraic stability.
- `evaluate_capture` keyword match is word-boundary regex (`\bads?\b`, `\bconsent\b`, …).
  Previously the substring check let `"adversarial"` or `"adapter"` falsely suppress the
  Lazzarato ad-targeting critique — i.e. let the very capture this detector is meant to flag
  pass through unannotated.

### Fixed

- `commit()` writes the JSONL line in a single `write()` call protected by `fcntl.flock`
  on POSIX, preventing interleaved half-lines under concurrent writers. Best-effort on
  non-POSIX platforms.
- `structure_signature` normalises edge `weight` via `f"{w:.12g}"`. Previously
  `weight=0.1 + 0.2` and `weight=0.3` produced different hashes for the same logical
  assemblage, violating the SPEC §2.2 order-independence promise across caller arithmetic
  paths.
- `collective_enunciation_signature` adds `sort_keys=True` to its canonical JSON encoding.
- `protocol.evaluate()` renamed local `warnings` to `capture_warnings_list` to avoid
  shadowing a future `import warnings`.
- SPEC §3.1 step-3 now passes `assemblage_after` (3-arg) to `detect_subject_group`,
  matching the actual call site and §3.4 definition.
- SPEC §3.4 adds an explicit typed signature block.
- README political block now contains the full `"inconvenient by design"` clause that
  appears in SPEC §0.
- SPEC.md trimmed to 300 lines (was 308 after §3.4 signature addition).

### Added — tests

- `test_other_author_with_bare_keyword_rejected` and `test_other_author_with_no_year_rejected`
  pin the new `<other>` regex.
- `test_subclassing_blocked` and `test_subclassing_with_property_blocked` pin the KPI
  subclass refusal.
- `test_subtract_one_is_idempotent_on_repeat_apply` pins the N-1 algebra.
- `test_adversarial_text_does_not_silence_ad_targeting_critique` and
  `test_consent_keyword_uses_word_boundary` pin the word-boundary capture detector.
- `test_signature_stable_under_float_drift` pins the canonical weight encoding.

## [0.1.0] — 2026-05-17

Initial release.

### Added

- Core protocol types: `Node`, `HeterogeneousEdge`, `Assemblage`, `Utterance`, `Critique`,
  `SourceRef`, `DeploymentContext`, `ThreeEcologiesKPI`, `ProtocolReport`.
- Operations: `build_assemblage`, `structure_signature`, `subtract_one`,
  `transversality_index`, `compute_three_ecologies`, `detect_subject_group`,
  `evaluate_capture`, `record_utterance`, `collective_enunciation_signature`,
  `evaluate`, `commit`.
- Adapter skeletons (not imported by core): `langgraph_adapter.from_langgraph_state`,
  `obsidian_adapter.from_obsidian_vault`.
- SPEC.md (this is the source of truth).
- CI: ruff, mypy --strict, pytest --cov, fixed-string political-statement assertion,
  warning-only groupe-sujet self-check.
- Examples: `01_honest_collective.py`, `02_ambiguous_consultation.py`,
  `03_capture_pattern.py`.

### Intentionally absent

- No `mode=` kwarg on `evaluate()`.
- No composite/aggregate score on `ThreeEcologiesKPI` or `ProtocolReport`.
- No closed enumeration of capture risks (no `CaptureRisk`).
- No automatic dependency on LangGraph / NetworkX in the core; both are optional.

### Known limits (tracked for v0.2.x)

- LangGraph / Obsidian adapters are skeletons.
- No os-climate integration on the environmental axis; manual `kgco2eq` estimate only.
- The Deleuzian Representation Hypothesis (arXiv:2512.19734) has not been reconciled with
  this protocol's primitives. See `docs/open_questions.md`.
