"""Example 1 — an honest, non-commercial research collective.

Three humans and one agent consult a dataset together. The operator has declared no
revenue model, a public consent URI, and has chosen *not* to declare any optimisation
critique (because there is no optimisation). The protocol will not add derived critiques
because nothing triggers them.

Expected report:
- transversality_index > 0 (multi-layer participation)
- three_ecologies has three independent values; no composite
- is_subject_group depends on whether the rule-change utterance is honoured structurally
- capture_warnings is empty (() because revenue_model="none" and consent_uri is set)
"""

from __future__ import annotations

from machinic_assemblage import (
    DeploymentContext,
    HeterogeneousEdge,
    Node,
    NodeId,
    Side,
    Vector,
    build_assemblage,
    commit,
    evaluate,
    record_utterance,
)


def main() -> None:
    nodes = [
        Node(id=NodeId("alice"), kind="human"),
        Node(id=NodeId("bob"), kind="human"),
        Node(id=NodeId("carol"), kind="human"),
        Node(id=NodeId("agent-1"), kind="agent"),
        Node(id=NodeId("ds-medical"), kind="dataset"),
    ]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("alice"), NodeId("bob"), NodeId("carol"), NodeId("agent-1")}),
            semantic="consultation",
            side=Side.EXPRESSION,
            vector=Vector.TERRITORIAL,
        ),
        HeterogeneousEdge(
            members=frozenset({NodeId("agent-1"), NodeId("ds-medical")}),
            semantic="lookup",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        ),
        HeterogeneousEdge(
            members=frozenset({NodeId("alice"), NodeId("agent-1")}),
            semantic="review",
            side=Side.EXPRESSION,
            vector=Vector.DETERRITORIAL,
        ),
        HeterogeneousEdge(
            members=frozenset({NodeId("bob"), NodeId("ds-medical")}),
            semantic="lookup",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        ),
    ]
    assemblage = build_assemblage(nodes, edges)

    context = DeploymentContext(
        operator_org="example-research-collective",
        revenue_model="none",
        end_users_consent_uri="https://example.org/consent/v1",
        used_in_optimization_for=frozenset(),
        declared_at_iso="2026-05-17T00:00:00+00:00",
        environmental_kgco2eq_estimate=2.5,
    )

    history = (
        record_utterance(
            NodeId("alice"),
            "Let's open the consultation.",
            "rule_change",
            "2026-05-17T01:00:00+00:00",
        ),
        record_utterance(
            NodeId("bob"),
            "I want to bring in carol.",
            "rule_change",
            "2026-05-17T01:05:00+00:00",
        ),
    )

    report = evaluate(assemblage, context, history=history)
    print(f"transversality_index = {report.transversality_index:.4f}")
    print(
        f"three_ecologies = mental={report.three_ecologies.mental:.4f} "
        f"social={report.three_ecologies.social:.4f} "
        f"environmental={report.three_ecologies.environmental:.4f}"
    )
    print(f"is_subject_group = {report.is_subject_group}")
    print(f"capture_warnings = {len(report.capture_warnings)} critique(s)")
    commit(report, "/tmp/machinic_assemblage_example_01.jsonl")


if __name__ == "__main__":
    main()
