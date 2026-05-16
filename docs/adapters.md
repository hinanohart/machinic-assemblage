# Adapters

The core of machinic-assemblage has one runtime dependency (`pydantic`) and does not import
any third-party orchestrator. Adapters live in `src/machinic_assemblage/adapters/` and are
optional.

## LangGraph

`from_langgraph_state(state) -> Assemblage` (v0.2.x, skeleton in v0.1.0).

Recommended mapping:

- Each node in the compiled LangGraph is a `Node(kind="agent")`.
- Each edge in the compiled graph is a `HeterogeneousEdge` with `semantic` drawn from the
  edge label (or `"unlabeled"` if none).
- `Side`: heuristic — outgoing-to-LLM edges are `EXPRESSION`, outgoing-to-tool are `CONTENT`.
- `Vector`: an edge whose label is `Command(goto=...)` and changes the static topology is
  `DETERRITORIAL`; everything else is `TERRITORIAL`.
- `Utterance` history is drawn from the LangGraph message log; `rule_change` is the
  `Command(goto=...)` records.

## Obsidian

`from_obsidian_vault(path) -> Assemblage` (v0.2.x, skeleton in v0.1.0).

Recommended mapping:

- Each note is a `Node(kind="note")`.
- Each `[[wikilink]]` is a `HeterogeneousEdge` between source and target notes; `semantic`
  is drawn from the source note's frontmatter `kind:` field or the link's display alias.
- Frontmatter `kind: rule_change` entries become `Utterance(kind="rule_change", ...)`.

## AgentNet, HyperAgent

Adapters for these are welcome. The expected interface is the same shape as above. PRs that
keep the adapter import-free unless the user explicitly imports it are preferred.
