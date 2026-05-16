# Changelog

All notable changes to machinic-assemblage will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). API stability promises
are in SPEC §7.

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
