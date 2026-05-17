# Changelog

All notable changes to machinic-assemblage will be documented in this file.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). API stability promises
are in SPEC §7.

## [0.1.3] — 2026-05-17

Patch release addressing the round-3 independent-critic findings against v0.1.2. No public
API change; the 23 symbols in `__all__` remain stable across the v0.1.x line (SPEC §7).
The four philosophical invariants (Q1–Q4) are intact; this release tightens the surrounding
test/lint surface so the README/SPEC §1 bold-row claims are backed by real protocol calls.

### Hardened (load-bearing-test honesty)

- `tests/ci/test_groupe_sujet_self_check.py` now actually invokes
  `detect_subject_group(history, before, after)` on an `Assemblage` built from
  `CONTRIBUTORS.toml`. The previous v0.1.0–v0.1.2 implementation only grep'd commit
  messages, leaving the README/SPEC §1 bold-row "groupe-sujet self-test asserted in the
  project's own CI" unbacked. A second pin
  (`test_self_check_actually_invokes_detect_subject_group`) source-inspects this file to
  prevent silent reversion to a grep heuristic.
- `Critique` `<other>` author validation: regex is simplified to capture three
  comma-separated tokens + 4-digit year; a Python-level helper (`_has_valid_primary_source`)
  then requires each token to (a) strip non-empty and (b) contain at least one Unicode
  letter. Closes the v0.1.2 hatch that accepted pure-punctuation tokens
  (`primary_source: ##, %%, ^^ 2024`) and rejected legitimate citations with single-letter
  initials (`H. Lefebvre, A, Pub 1990`). The honest limit is documented in `types.py`:
  semantic citation quality cannot be enforced by a regex.
- `Node`, `HeterogeneousEdge`, `Utterance`, `SourceRef`, `DeploymentContext`, `Critique`
  reject whitespace-only required strings. Previously `Node(id=" ", kind="\t")` and
  `Critique(text=" "*30, ...)` were accepted because validation used `not self.x` instead
  of `not self.x.strip()`. A new helper `_require_nonblank` is shared across the
  dataclasses.

### Fixed

- `evaluate_capture(history=...)` no longer `del`-s its `history` argument. The signature
  is honest about the v0.1.x contract: `history` is reserved for v0.2.0 history-conditioned
  critiques and currently unread, but it is kept in the signature so v0.2.0 can ship without
  an API break. Documented in the function docstring.
- `transversality_index`: the dead `0.0 * _cross_layer_edge_ratio(a)` multiplication on the
  zero-geomean branch is replaced with `return 0.0` plus a comment that documents the
  weakest-link behaviour and the v0.2.0 Laplace-smoothing option.
- `examples/01_honest_collective.py` uses `tempfile.gettempdir()` instead of a hard-coded
  `/tmp/...` path, so the example runs on Windows.
- README `Status: alpha (v0.1.0)` → `Status: alpha (v0.1.3)`. SPEC.md title and four inline
  "v0.1.0" markers updated to `v0.1.x` (the stability-promise scope; see SPEC §7).

### Added — tests

- `test_other_author_with_pure_punctuation_rejected`,
  `test_other_author_with_digits_only_tokens_rejected`,
  `test_other_author_with_single_letter_initial_accepted` pin the new letter-required
  citation contract.
- `test_critique_whitespace_only_text_rejected`,
  `test_critique_whitespace_only_falsifiability_rejected`,
  `test_whitespace_only_id_rejected`, `test_whitespace_only_kind_rejected` pin the
  whitespace-only validation across dataclasses.
- `test_commit_atomic_under_concurrent_writers`: 2 child processes × 25 commits each, with
  a 4 KB payload per record, asserts 50 well-formed JSONL lines. Pins the
  `fcntl.flock(LOCK_EX)` guarantee added in v0.1.1. Skipped on platforms without
  `os.fork()` (Windows).
- `test_self_check_actually_invokes_detect_subject_group`: source-inspection pin against
  silent reversion of the groupe-sujet self-check to a grep heuristic.

### Honest limits (post-v0.1.2 audit retroactive notes)

- The citation regex still accepts real-looking dummy citations like
  `aa, bb, cc 1999` — full semantic citation quality is out of scope for syntactic checks
  and delegated to SPEC §5 intervention point 5 (human review).
- `subtract_one` cross-node concatenation: when two different nodes are subtracted from the
  same edge with two different reasons, the reasons are joined with `"; "` and the
  per-node attribution is lost. This is a known v0.1.x design constraint of the
  `frozenset[NodeId]` representation; v0.2.0 will change the type to
  `frozenset[tuple[NodeId, str]]` to preserve attribution.
- `detect_subject_group` self-removal asymmetry: a `rule_change` speaker who removes
  themselves via `subtract_one` is still in `members_after.nodes` and passes condition 3;
  the same act performed by *rebuilding without* that node fails condition 3 (the speaker
  is no longer a member). The two representations are not yet symmetric. v0.2.0 will relax
  condition 3 to `external_speakers ⊆ members_before ∪ members_after`.
- `transversality_index` / `compute_three_ecologies.mental`: a single speaker with one
  utterance-kind zeroes the geometric mean (weakest-link). v0.2.0 may adopt a
  Laplace-smoothed variant; v0.1.3 documents the behaviour and pins it.

## [0.1.2] — 2026-05-17

Patch release addressing the independent-critic findings against v0.1.1. No public API change;
the 23 symbols in `__all__` remain stable across the v0.1.x line (SPEC §7).

### Hardened

- `Critique` `<other>` author regex now requires each of the three citation tokens to start
  with **two non-whitespace characters**. The v0.1.1 form accepted `primary_source: a, b, c
  9999` (1-char dummy tokens) and whitespace-only tokens; v0.1.2 closes those forms. A regex
  cannot enforce semantic citation quality, so this is still a syntactic minimum — real-looking
  dummies (`aa, bb, cc 1999`) will still pass and rely on the human-review intervention point
  in SPEC §5.

### Fixed

- `__version__` in `machinic_assemblage/__init__.py` synced to `"0.1.2"`. The v0.1.0 → v0.1.1
  bump missed this constant, so `import machinic_assemblage; machinic_assemblage.__version__`
  on v0.1.1 returned the stale `"0.1.0"` while `pip show` reported `0.1.1`. v0.1.2 also fixes
  this drift retroactively.
- SPEC §2.1 explicitly documents the v0.1.x N-1 trade-off: because `subtract` is a
  `frozenset[NodeId]`, repeat-applying `subtract_one(node, reason)` on the same node is
  idempotent — the first reason is retained. Holding multiple reasons against the same node
  requires v0.2.0's type change to `frozenset[tuple[NodeId, str]]`.

### Honest limits (post-v0.1.1 audit retroactive note)

- v0.1.1's "load-bearing design protections" claim was tighter than v0.1.0 but still
  incomplete on two dimensions:
  - The `<other>` regex permitted minimal dummy citations (any 2-char tokens, including
    `a, b, c 9999`). v0.1.2 narrows that to a 2-non-whitespace-char minimum per token. Full
    semantic enforcement remains out of scope for syntactic checks and is delegated to the
    human-review intervention point in SPEC §5.
  - `ThreeEcologiesKPI.__init_subclass__` blocks the *subclass* attack documented in v0.1.1
    but does not block runtime monkey-patching of the class object itself
    (`ThreeEcologiesKPI.composite = property(...)` will still succeed). This is by design:
    the protocol guards against code that ships, not against adversarial monkey-patch.

### Added — tests

- `test_other_author_with_single_char_tokens_rejected` pins the 1-char dummy rejection.
- `test_other_author_with_whitespace_only_tokens_rejected` pins the whitespace-only rejection.
- `test_subtract_one_with_different_reason_keeps_first` pins the v0.1.x N-1 idempotency
  trade-off so the behaviour cannot regress silently.

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
