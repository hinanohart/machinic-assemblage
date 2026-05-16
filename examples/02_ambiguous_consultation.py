"""Example 2 — a paid consultation with a thoughtful operator declaration.

A subscription service runs a triage assistant. The operator has declared one explicit
critique (asymmetric trust in the agent's recommendations) and supplies a consent URI.
The capture detector adds no derived critique here, because every relevant concern is
already declared.

Expected report:
- one explicitly-declared critique in capture_warnings
- no derived critique appended (operator covered the relevant bases)
"""

from __future__ import annotations

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


def main() -> None:
    nodes = [
        Node(id=NodeId("user"), kind="human"),
        Node(id=NodeId("agent-triage"), kind="agent"),
        Node(id=NodeId("op-org"), kind="organisation"),
    ]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("user"), NodeId("agent-triage")}),
            semantic="consultation",
            side=Side.EXPRESSION,
            vector=Vector.TERRITORIAL,
        ),
        HeterogeneousEdge(
            members=frozenset({NodeId("agent-triage"), NodeId("op-org")}),
            semantic="reporting",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        ),
    ]
    assemblage = build_assemblage(nodes, edges)

    declared_critique = Critique(
        text=(
            "The user defers to the agent's recommendations more than horizontal collegial "
            "consultation would warrant. We treat this as a deterritorialisation of trust "
            "in the direction of the apparatus (cf. Guattari) and flag it openly."
        ),
        source_ref=SourceRef(
            author="Guattari",
            work="Les Trois Écologies",
            edition="Galilée 1989 / Pindar & Sutton tr. 2000",
            pages="§1",
        ),
        falsifiability_condition=(
            "Dissolves when the user reliably initiates dissent against the agent's "
            "recommendations in at least 20% of consultations and the operator does not "
            "penalise such dissent in service quality."
        ),
    )

    context = DeploymentContext(
        operator_org="example-paid-service",
        revenue_model="subscription",
        end_users_consent_uri="https://example.org/consent/v1",
        used_in_optimization_for=frozenset({declared_critique}),
        declared_at_iso="2026-05-17T00:00:00+00:00",
        environmental_kgco2eq_estimate=12.0,
    )

    history = (
        record_utterance(
            NodeId("user"),
            "I have a question.",
            "question",
            "2026-05-17T01:00:00+00:00",
        ),
        record_utterance(
            NodeId("agent-triage"),
            "Here's what I suggest.",
            "witness",
            "2026-05-17T01:01:00+00:00",
        ),
        record_utterance(
            NodeId("user"),
            "I will not follow that suggestion.",
            "refusal",
            "2026-05-17T01:05:00+00:00",
        ),
    )

    report = evaluate(assemblage, context, history=history)
    print(f"transversality_index = {report.transversality_index:.4f}")
    print(f"three_ecologies = {report.three_ecologies}")
    print(f"capture_warnings ({len(report.capture_warnings)}):")
    for c in report.capture_warnings:
        print(
            f"  - {c.source_ref.author} ({c.source_ref.edition}): "
            f"falsifiable iff: {c.falsifiability_condition[:80]}..."
        )


if __name__ == "__main__":
    main()
