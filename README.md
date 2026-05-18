# machinic-assemblage

A small, opinionated protocol for evaluating **collective enunciation** —
the entanglement of humans, agents, datasets, and organisations that
produces decisions in multi-agent systems — under three irreducible
ecologies: mental, social, environmental.

Status: alpha (v0.1.3). Python 3.11+. MIT.

> machinic-assemblage is a protocol for **evaluating collective enunciation under three
> irreducible ecologies (mental, social, environmental)**. It is written against the capture
> of Guattari and Deleuze concepts by Integrated World Capitalism — what Lazzarato calls
> "machinic enslavement" reduced to engagement metrics, and what Terranova calls
> "Deleuzian capitalism" reduced to dynamic-topology marketing. This project does not
> attempt to be neutral. Refusal of capture is a load-bearing design requirement;
> convenience switches that would erase that refusal are deliberately not implemented —
> inconvenient by design. If you want a neutral multi-agent orchestrator, use LangGraph.

The above paragraph is fixed-string asserted by CI; see
[SPEC §0](SPEC.md#0-political-statement-ci-enforced).

## What this is and is not

**It is**: a ~300-line protocol specification + a reference implementation in one Python
package. The protocol forces three things at the type level that other multi-agent
frameworks make optional:

1. `evaluate(...)` will not run without a `DeploymentContext`. The operator must
   declare their revenue model, consent URI, and the capture concerns they are
   optimising against. No `mode="research"` bypass exists. ([SPEC §2.5](SPEC.md#25-deploymentcontext--mandatory-argument))
2. Output is a triple of axes — mental, social, environmental — with **no composite
   score**. A static lint rejects any function in this codebase that collapses the
   triple to one number. ([SPEC §2.6](SPEC.md#26-threeecologieskpi--three-numbers-no-composite))
3. Capture warnings are not enum values. They are `Critique` instances carrying
   natural-language text, a citation with edition and page range, and a
   falsifiability condition. A critique that cannot be disconfirmed is rejected
   at construction. ([SPEC §2.4](SPEC.md#24-critique--capture-warnings-not-enums))

**It is not**: a diagnostic tool, an "alignment evaluation framework", or a
replacement for LangGraph / AgentNet / HyperAgent. See
[SPEC §6](SPEC.md#6-non-goals).

## Honest comparison

| Capability                                                        | LangGraph | AgentNet | HyperAgent | Obsidian + CW | machinic-assemblage |
|-------------------------------------------------------------------|-----------|----------|------------|----------------|---------------------|
| Dynamic graph topology                                            | yes       | yes      | yes        | partial        | yes                 |
| Hyperedge / N-ary relations                                       | no        | no       | yes        | no             | yes                 |
| Three-ecology Pareto KPI                                          | no        | no       | no         | no             | yes                 |
| `evaluate()` refuses to run without `DeploymentContext`           | no        | no       | no         | no             | **yes**             |
| Groupe-sujet self-test asserted in the project's own CI           | no        | no       | no         | no             | **yes**             |
| Composite "alignment score" intentionally absent                  | n/a       | n/a      | n/a        | n/a            | **yes**             |
| Critique type (text + citation + falsifiability)                  | no        | no       | no         | no             | **yes**             |

If the bold rows are not load-bearing for your work, the other tools are larger,
faster, more mature. Use them.

## Quickstart

```python
from machinic_assemblage import (
    Critique,
    DeploymentContext,
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    SourceRef,
    Vector,
    build_assemblage,
    evaluate,
    record_utterance,
)

nodes = [
    Node(id=NodeId("alice"), kind="human"),
    Node(id=NodeId("bob"), kind="human"),
    Node(id=NodeId("agent-1"), kind="agent"),
]
edges = [
    HeterogeneousEdge(
        members=frozenset({NodeId("alice"), NodeId("bob"), NodeId("agent-1")}),
        semantic="consultation",
        side=Side.EXPRESSION,
        vector=Vector.TERRITORIAL,
    ),
]
assemblage = build_assemblage(nodes, edges)

# DeploymentContext is mandatory. There is no research-mode bypass.
context = DeploymentContext(
    operator_org="example-research-collective",
    revenue_model="none",
    end_users_consent_uri="https://example.org/consent/v1",
    used_in_optimization_for=frozenset({
        Critique(
            text=(
                "This deployment is non-commercial research; we still flag the risk of "
                "later capture if we accept funding tied to engagement-time metrics."
            ),
            source_ref=SourceRef(
                author="Lazzarato",
                work="Signs and Machines",
                edition="Semiotext(e) 2014",
                pages="ch. 3",
            ),
            falsifiability_condition=(
                "Dissolves once we publish a binding refusal of engagement-time funding."
            ),
        ),
    }),
    declared_at_iso="2026-05-17T00:00:00+00:00",
    environmental_kgco2eq_estimate=2.5,
)

report = evaluate(assemblage, context, history=())
print(report.transversality_index)
print(report.three_ecologies)      # three numbers, no composite
print(report.capture_warnings)     # tuple[Critique, ...]
```

See [`examples/`](examples/) for three worked examples: honest collective use,
ambiguous consultation, and an explicit capture pattern.

## Install

```bash
pip install machinic-assemblage           # core: stdlib only, no runtime deps
pip install machinic-assemblage[viz]      # adds networkx for export
pip install machinic-assemblage[dev]      # tests + lint + types
```

## What the CI enforces

GitHub Actions runs:

- `ruff check` + `ruff format --check`
- `mypy --strict` against `src/machinic_assemblage`
- `pytest --cov` with `>= 80%` line coverage
- `tests/ci/test_readme_political_statement.py` — fixed-string assertion of the
  political statement in SPEC §0 and README. Removing it breaks CI.
- `tests/ci/test_groupe_sujet_self_check.py` — runs the protocol's groupe-sujet
  test on this repo's own commit log + `CONTRIBUTORS.toml`. **Emits a
  UserWarning** when the project itself fails the check; does *not* fail CI.
  (Reason: SPEC §3.4. Hard assertion on a heuristic incentivises gaming the
  heuristic.) Reviewers are expected to treat the warning as evidence.

## Intentional design choices

- No "research mode" / no `mode=` switch on `evaluate()`. Bypassing
  `DeploymentContext` requires forking.
- No composite score. A static lint enforces this in-repo.
- No closed enumeration of capture risks. Every capture warning is an answerable
  `Critique`.
- No silent dependencies. Adapters for LangGraph / Obsidian are skeleton-only in
  v0.1.x and not imported by the core.

These are not omissions; they are the spec.

## Non-goals

- Not a diagnostic tool for any mental-health, legal, or medical condition.
  日本国・薬機法/医師法/弁護士法/精神保健福祉法等の規制対象行為には用いないこと。
- Not a replacement for LangGraph / AgentNet / HyperAgent / Obsidian.
- Not politically inert. It is not designed to be.

See [SPEC §6](SPEC.md#6-non-goals) for the binding statement.

## Documentation

- [SPEC.md](SPEC.md) — the protocol specification. This is the source of truth.
- [docs/environmental.md](docs/environmental.md) — environmental axis threshold.
- [docs/adapters.md](docs/adapters.md) — interface notes for LangGraph / Obsidian.
- [docs/limits.md](docs/limits.md) — known limits, including Gödel-style
  self-application bounds.
- [docs/open_questions.md](docs/open_questions.md) — open items deferred to v0.2.x.
- [CONTRIBUTING.md](CONTRIBUTING.md) — how to contribute, citation conventions.
- [CHANGELOG.md](CHANGELOG.md) — versioned changes.

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgements

The thinking that this protocol tries not to betray belongs to Félix Guattari, Gilles
Deleuze, Maurizio Lazzarato, Tiziana Terranova, Franco "Bifo" Berardi, and Bernard
Stiegler. Errors in operationalisation are this project's, not theirs.
