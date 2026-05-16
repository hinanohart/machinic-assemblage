# machinic-assemblage — Protocol Specification v0.1.0

Status: alpha. The protocol is small, opinionated, and deliberately inconvenient. Names, types and
operations are stable for the v0.1.x line; semantics may sharpen in v0.2.x.

## 0. Political Statement (CI-enforced)

> machinic-assemblage is a protocol for **evaluating collective enunciation under three irreducible
> ecologies (mental, social, environmental)**. It is written against the capture of Guattari and
> Deleuze concepts by Integrated World Capitalism — what Lazzarato calls "machinic enslavement"
> reduced to engagement metrics, and what Terranova calls "Deleuzian capitalism" reduced to
> dynamic-topology marketing. This project does not attempt to be neutral. Refusal of capture is
> a load-bearing design requirement; convenience switches that would erase that refusal are
> deliberately not implemented. If you want a neutral multi-agent orchestrator, use LangGraph.

This paragraph is fixed-string asserted by `tests/ci/test_readme_political_statement.py` —
removing or paraphrasing breaks CI.

## 1. Why this exists

There is no shortage of multi-agent orchestrators. The honest comparison:

| Capability                                                        | LangGraph | AgentNet | HyperAgent | Obsidian + CW | machinic-assemblage |
|-------------------------------------------------------------------|-----------|----------|------------|----------------|---------------------|
| Dynamic graph topology                                            | yes       | yes      | yes        | partial        | yes                 |
| Hyperedge / N-ary relations                                       | no        | no       | yes        | no             | yes                 |
| Three-ecology (mental/social/environmental) Pareto KPI            | no        | no       | no         | no             | yes                 |
| `evaluate()` refuses to run without `DeploymentContext`           | no        | no       | no         | no             | **yes**             |
| Groupe-sujet self-test asserted in the project's own CI           | no        | no       | no         | no             | **yes**             |
| Composite "alignment score" intentionally absent                  | n/a       | n/a      | n/a        | n/a            | **yes**             |
| Critique type (text + edition+page citation + falsifiability)     | no        | no       | no         | no             | **yes**             |

The bold rows are this project's reason to exist. If they are not load-bearing for your work,
**use one of the other tools — they are larger, faster, and more mature**.

## 2. Concepts → Primitives (with citations)

Every primitive in the implementation carries a docstring with edition+page references. Editions
used for citation throughout:

- *Mille Plateaux*, Deleuze & Guattari — Minuit 1980 / Massumi 1987 / 河出書房新社 1994.
- *Les Trois Écologies*, Guattari — Galilée 1989 / Pindar & Sutton 2000 / 平凡社 2008.
- *Chaosmose*, Guattari — Galilée 1992 / Bains & Pefanis 1995.
- Lazzarato, *Signs and Machines*, Semiotext(e) 2014.
- Terranova, *Network Culture: Politics for the Information Age*, Pluto Press 2004.

### 2.1 `Node` and `HeterogeneousEdge`

A `Node` is a typed participant (human, agent, dataset, organisation, instrument).
A `HeterogeneousEdge` is an N-ary relation across nodes of possibly different kinds, carrying:

- `members: frozenset[NodeId]` — the participants
- `semantic: str` — relation label (free-form, but stable within a project)
- `side: Side` — `CONTENT` or `EXPRESSION` (*Mille Plateaux*, plateau 4)
- `vector: Vector` — `TERRITORIAL` or `DETERRITORIAL` (same plateau)
- `weight: float` — non-negative, default 1.0
- `subtract: frozenset[NodeId]` — the "N-1" form (*Mille Plateaux*, "Subtract the unique";
  Massumi 1987 pp. 6, 21–22). An edge with non-empty `subtract` represents the multiplicity that
  results from withdrawing those nodes from the molar identity, not the same edge with fewer
  members.
- `subtract_reason: str` — required iff `subtract` is non-empty. The reason becomes part of the
  edge's hash, so two N-1 operations with different motivations are not collapsed.

`exclude_axis: NodeId | None` (mentioned in earlier design drafts) is **not** used: a single
excluded node is just a hypergraph convenience; the protocol takes N-1 seriously and requires the
reason.

### 2.2 `Assemblage`

An `Assemblage` is a frozen pair `(nodes: frozenset[Node], edges: frozenset[HeterogeneousEdge])`.
Constructors validate that every edge's members are a subset of `nodes`.

`structure_signature(a) -> str` returns a stable SHA-256 hex over the canonical encoding of nodes
and edges (members sorted; subtract included). Used by `detect_subject_group` to recognise
self-modification.

### 2.3 `Utterance`

A `Utterance` is a record of collective enunciation:

```python
Utterance(speaker: NodeId, content: str, kind: str, timestamp_iso: str)
```

`kind` is free-form but conventional values include `"rule_change"`, `"question"`, `"refusal"`,
`"witness"`. `rule_change` is the trigger searched by the groupe-sujet test.

### 2.4 `Critique` — capture warnings, not enums

Earlier drafts proposed a `CaptureRisk` enum (`engagement_max`, `ad_targeting`, …).
**That representation is rejected.** A closed enumeration of capture risks is itself the move
Lazzarato critiques: it converts a structural problem (subjugation to capitalist semiotic
machines) into a compliance checklist. The protocol instead uses:

```python
Critique(text: str, source_ref: SourceRef, falsifiability_condition: str)
```

- `text` — free-form natural language description of the suspected capture mechanism.
- `source_ref` — author, work, edition, page range. Must reference at least one of Guattari /
  Deleuze / Lazzarato / Terranova / Berardi / Stiegler / direct primary source.
- `falsifiability_condition` — a sentence describing what observable evidence would dissolve this
  critique. Empty strings are rejected at construction.

This forces capture warnings to be answerable. Adding a new critique without a falsifiability
condition is a `ValueError`, not a lint warning.

### 2.5 `DeploymentContext` — mandatory argument

`evaluate()` will not run without a `DeploymentContext`:

```python
DeploymentContext(
    operator_org: str,
    revenue_model: Literal["none", "donation", "subscription", "ads", "data_sale", "other"],
    end_users_consent_uri: str | None,
    used_in_optimization_for: frozenset[Critique],   # the critiques the operator declares
    declared_at_iso: str,
)
```

There is no `mode="research"` flag and there will not be one. A research deployment is still a
deployment; the operator still owes a context. Bypassing this requires forking the project, which
is deliberate friction — *inconvenient by design*.

### 2.6 `ThreeEcologiesKPI` — three numbers, no composite

```python
ThreeEcologiesKPI(mental: float, social: float, environmental: float)
```

A composite/weighted score is **intentionally absent** and will not be added. The three ecologies
are incommensurable by argument (Guattari, *Les Trois Écologies* §3); reducing them to one number
re-enacts the KPI monoculture this protocol exists to refuse. Optimisation against the report must
be done explicitly across the three axes by the operator, who must then declare their tradeoff in
`DeploymentContext`.

A static-analysis lint (`tools/lint_composite_score.py`) rejects any function in this codebase
whose signature returns a single `float` from a `ThreeEcologiesKPI` input.

### 2.7 `ProtocolReport`

```python
ProtocolReport(
    timestamp_iso: str,
    assemblage_signature: str,
    transversality_index: float,
    three_ecologies: ThreeEcologiesKPI,
    is_subject_group: bool,
    groupe_sujet_evidence: tuple[str, ...],
    capture_warnings: tuple[Critique, ...],
    context: DeploymentContext,
)
```

The report is `frozen=True`. Persistence is the caller's responsibility; `protocol.commit(report,
path)` appends a JSON line.

## 3. Operations

### 3.1 `evaluate`

```python
def evaluate(
    assemblage: Assemblage,
    context: DeploymentContext,
    history: Sequence[Utterance] = (),
    assemblage_after: Assemblage | None = None,
) -> ProtocolReport
```

The optional `assemblage_after` argument supplies the post-rule-change structure for the
groupe-sujet test (§3.4). When `None`, the test reports `False` with that as evidence.

Steps:

1. Compute `transversality_index` (§3.2).
2. Compute `three_ecologies` (§3.3) — three independent values, no aggregation.
3. Run `detect_subject_group(history, assemblage, assemblage_after)` (§3.4).
4. Run `evaluate_capture(context, history)` (§3.5).
5. Assemble and return a frozen `ProtocolReport`.

### 3.2 Transversality index

```
T(A) = geomean_{n in speakers} H_layer(n)  ×  cross_layer_edge_ratio(A)
```

- `H_layer(n)` — Shannon entropy of the distribution of `semantic` labels on edges incident to
  node `n`, normalised by `log(k)` where `k` is the number of distinct labels. Entropy is in
  `[0, 1]`.
- `cross_layer_edge_ratio(A)` — fraction of edges whose members touch more than one `semantic`
  layer.

T = 0 means every speaker lives in one layer (Guattari's "vertical" institution). T = 1 means
every speaker is statistically saturated across all layers, which is itself suspicious (totalising
abstraction) — the operator is expected to read T as a Pareto axis, not a target.

The construction is close to Battiston et al. 2017's multiplex participation coefficient; the
contribution here is treating it as a normative axis with documented limits, not a fitness signal.

### 3.3 Three Ecologies KPI

- `mental`: per-speaker diversity of utterance kinds, geometric-mean-aggregated across speakers.
- `social`: ratio of reciprocated edges (incident in both directions when edges are read as
  member-pairs) to total edges; 1.0 = perfect reciprocity.
- `environmental`: a non-positive number drawn from `context.environmental_kgco2eq_estimate` if
  the operator supplied one, otherwise `0.0` with a warning. **CodeCarbon integration is not in
  v0.1.0**; the protocol just exposes the slot.

Each value is in `[0, 1]` (environmental is `min(1.0, max(0.0, 1 - kg/threshold))`); the threshold
default is documented in `docs/environmental.md`.

### 3.4 Groupe-sujet detection

```python
def detect_subject_group(
    history: Sequence[Utterance],
    assemblage_before: Assemblage,
    assemblage_after: Assemblage | None = None,
) -> tuple[bool, tuple[str, ...]]
```

Implements *Psychanalyse et transversalité* (Maspero 1972) chapter on subject-groups vs.
subjugated-groups. A history is treated as evidence of subject-group activity when **all three**
hold within a sliding window:

1. At least one `Utterance` with `kind == "rule_change"`.
2. `structure_signature(assemblage_before) != structure_signature(assemblage_after)`.
3. Every rule-change speaker is themselves a member of `assemblage_after`. A speaker who
   proposes a rule change without being a participant in the assemblage they are reshaping is
   exercising top-down authority — the apparatus imposing rules from outside.

**Self-application** (`tests/ci/test_groupe_sujet_self_check.py`) runs this on the project's own
git history + a `CONTRIBUTORS.toml` file. **The test emits a `UserWarning` and a GitHub Actions
warning annotation when the project itself fails the check; it does not fail CI.** Reasoning: hard
assertion on a heuristic creates a perverse incentive to game the heuristic (cosmetic renames as
"rule changes"). The warning is surfaced in PR review instead.

### 3.5 Capture detection

`evaluate_capture(context, history) -> tuple[Critique, ...]`:

1. Returns `context.used_in_optimization_for` as a baseline.
2. Adds derived critiques (keyword match is word-boundary regex, not substring):
   - `revenue_model == "ads"` and no declared critique mentions ad-targeting → Lazzarato 2014 ch. 3.
   - `revenue_model == "data_sale"` and no declared mentions surveillance/dispossession → Terranova 2004 ch. 3.
   - `end_users_consent_uri is None` and `revenue_model != "none"` → Guattari, *Les Trois Écologies* §1.

Derived critiques carry empty `source_ref` page ranges; the operator must resolve or accept them.

## 4. Adapters (optional)

`adapters/langgraph_adapter.py` and `adapters/obsidian_adapter.py` are stubs. They are not
imported by the core. Real adapters live in `adapters/` and may add optional dependencies. v0.1.0
ships **skeletons only** to document the interface; full adapters are v0.2.x.

## 5. Pipeline & intervention points

The protocol is not "fully automatic". v0.1.0 ships **ten human-in-the-loop checkpoints**, none
hidden:

1. Operator authors `DeploymentContext` (manual, by definition).
2. Operator chooses thresholds in `docs/environmental.md` for `environmental_kgco2eq_estimate`.
3. Operator authors `CONTRIBUTORS.toml` used by the CI self-check.
4. CI self-check warnings require human review on each PR.
5. New `Critique` instances must carry citations; reviewer judges them.
6. `Utterance.kind == "rule_change"` is human-tagged.
7. `kluster.ai` review may flag false positives — human triage.
8. GitHub API rate limit during release flow is a human reset.
9. Citing Guattari/Lazzarato/Terranova in docs requires checking edition rights — human task.
10. v0.1.0 issue triage in the first 30 days is fully human; no bots.

Referenced by `tests/test_intervention_points.py` (count >= 10; removals are deliberate edits).

## 6. Non-goals

machinic-assemblage is **not**:

- a diagnostic tool for any mental-health, legal, or medical condition. Output must not be used
  to make individual diagnostic, treatment, or compliance decisions about a person.
  日本国・薬機法/医師法/弁護士法/精神保健福祉法等の規制対象行為には用いないこと。
- an "alignment evaluation framework". There is no composite score.
- a replacement for LangGraph / AgentNet / HyperAgent / Obsidian. For coordination, use those.
- guaranteed to be politically inert. It is not.

## 7. Stability promise (v0.1.x)

- Public API surface (the 23 symbols re-exported from `machinic_assemblage/__init__.py`) is stable
  across v0.1.x. Additions are allowed; deletions and signature changes require a v0.2.0.
- The political statement (§0) is fixed across v0.1.x. Editing it requires a v0.2.0.
- The "ten intervention points" list (§5) may grow; it will not shrink.

## 8. Out of scope for v0.1.0 (tracked for later)

- `arXiv:2512.19734` ("Deleuzian Representation Hypothesis") primitive-overlap analysis;
  see `docs/open_questions.md`.
- `os-climate` integration (environmental axis) and full LangGraph adapter — both v0.2.0.
- A second-order capture detector (detector of capture of the detector). Gödel-style infinite
  regress is acknowledged and bounded at one layer; see `docs/limits.md`.
