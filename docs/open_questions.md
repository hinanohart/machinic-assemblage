# Open questions

Items deliberately deferred from v0.1.0. Each is tracked here rather than carried as a
TODO in code, so that reviewers can see what was chosen *not* to be in scope.

## arXiv:2512.19734 — Deleuzian Representation Hypothesis (ICLR 2026)

The paper proposes a Deleuze-explicit alternative to sparse-autoencoder-style mechanistic
interpretability. It overlaps this protocol on at least: assemblage, deterritorialisation
as a representational vector, and a critique of single-axis "feature importance".

A primitive-overlap analysis was not completed before v0.1.0 freeze. Action: for v0.1.1
(documentation patch) read the paper end-to-end and either (a) document compatibility, or
(b) document primitive renaming if our names conflict with theirs.

## os-climate integration

The environmental axis currently takes a single `kgco2eq` number. os-climate
(https://github.com/os-climate) supplies a much richer planetary data layer. Plan: add
an `[env]` extra in v0.2.0 that exposes an `os_climate_environmental_axis(...)` function
returning the axis value from os-climate's data, alongside (not replacing) the simple
threshold-based estimator.

## Second-order capture detector

Sketch: a meta-detector that watches whether `evaluate_capture` itself becomes a
checklist used to bless deployments. Operationalisation is unresolved — what evidence
would falsify the meta-claim? Until that question has an answer, the second-order
detector is not in the protocol. See `docs/limits.md` on Gödel-style regress.

## LangGraph full adapter

Skeleton only in v0.1.0. Full adapter (with end-to-end translation including
`Command(goto=...)` records into `Utterance(kind="rule_change", ...)`) tracked for v0.2.0.

## CONTRIBUTORS.toml — schema evolution

Currently free-form-but-conventional. A future revision should consider whether to
include explicit consent records and revocation entries (per SPEC §2.5 spirit).
