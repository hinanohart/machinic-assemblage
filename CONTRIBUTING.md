# Contributing to machinic-assemblage

Thanks for considering a contribution. Before opening a PR, please read this — the project has
deliberate non-conventional rules, and they are load-bearing.

## What kind of contributions are welcome

- Bug fixes in the reference implementation.
- New `Critique` instances backed by citations to Guattari / Deleuze / Lazzarato / Terranova /
  Berardi / Stiegler (or `<other>` with an explicit `primary_source: ...` in the text).
- Adapter implementations (LangGraph, Obsidian, AgentNet, HyperAgent), provided they keep the
  core import-free.
- Sharper falsifiability conditions on existing critiques.
- Documentation improvements — especially citations with edition + page range.
- Tests, especially adversarial ones that try to game the heuristics.

## What is **not** welcome

- A `mode="research"` flag, a `bypass_context=True` kwarg, or any other switch that lets
  `evaluate()` run without a `DeploymentContext`. See SPEC §2.5. This is not a debate.
- A composite score / weighted aggregate of the three ecologies. See SPEC §2.6.
- Replacing `Critique` with an enum. See SPEC §2.4.
- Removing or paraphrasing the political statement in SPEC §0. CI will reject it.
- Reducing the count of intervention points below ten. See SPEC §5.

## Citation conventions

Every `Critique` and every claim referencing Guattari et al. must carry edition and page range.
Editions in use:

- *Mille Plateaux*: Minuit 1980 / Massumi tr. 1987 / 河出書房新社 1994.
- *Les Trois Écologies*: Galilée 1989 / Pindar & Sutton tr. 2000 / 平凡社 2008.
- *Chaosmose*: Galilée 1992 / Bains & Pefanis tr. 1995.
- Lazzarato, *Signs and Machines*: Semiotext(e) 2014.
- Terranova, *Network Culture*: Pluto Press 2004.

If you cite a different translation, declare which one.

## Development setup

```bash
git clone <repo-url>
cd machinic-assemblage
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"
pytest -q
ruff check .
mypy --strict src/machinic_assemblage
```

## Self-application

Per SPEC §3.4, the project runs the groupe-sujet test on its own commit log and on a
`CONTRIBUTORS.toml` file. The test emits a `UserWarning` rather than failing CI. We treat
the warning as evidence about the project's own honesty; a PR that ignores a fresh warning
will be asked to address it before merge.

`CONTRIBUTORS.toml` is appended-to (not edited), one entry per contributor, with their
own self-described `kind` (human / agent / collective / organisation / instrument). This is
not a CLA; it is a registry of who is enunciating.

## Commit messages

- Subject line: imperative, < 72 chars.
- Body: explain *why*. The code says *what*.
- Use `rule_change:` in the subject line when a commit changes the protocol, the SPEC, or the
  `_ALLOWED_CRITIQUE_AUTHORS` set. This makes the groupe-sujet self-check possible.

## Issues

For the first 30 days of v0.1.0, issue triage is fully human (SPEC §5 #10). Expect slow
responses; expect them to engage with citations.
