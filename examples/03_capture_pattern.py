"""Example 3 — an explicit capture pattern.

An ad-funded deployment with no declared optimisation critique and no consent URI. The
operator has filled in the `DeploymentContext` honestly, which means the capture detector
will append derived critiques pointing at Lazzarato (ads) and Guattari (missing consent).
This is the protocol working as designed: it produces answerable critiques, not pass/fail
scores.
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
    evaluate,
)


def main() -> None:
    nodes = [
        Node(id=NodeId("user"), kind="human"),
        Node(id=NodeId("agent-feed"), kind="agent"),
        Node(id=NodeId("op-org"), kind="organisation"),
        Node(id=NodeId("advertiser"), kind="organisation"),
    ]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("user"), NodeId("agent-feed")}),
            semantic="consumption",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        ),
        HeterogeneousEdge(
            members=frozenset({NodeId("agent-feed"), NodeId("advertiser"), NodeId("op-org")}),
            semantic="targeting",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
        ),
    ]
    assemblage = build_assemblage(nodes, edges)

    context = DeploymentContext(
        operator_org="example-ad-funded-platform",
        revenue_model="ads",
        end_users_consent_uri=None,
        used_in_optimization_for=frozenset(),
        declared_at_iso="2026-05-17T00:00:00+00:00",
        environmental_kgco2eq_estimate=80.0,
    )

    report = evaluate(assemblage, context)
    print(f"transversality_index = {report.transversality_index:.4f}")
    print(
        f"three_ecologies = mental={report.three_ecologies.mental:.4f} "
        f"social={report.three_ecologies.social:.4f} "
        f"environmental={report.three_ecologies.environmental:.4f}"
    )
    print(f"capture_warnings ({len(report.capture_warnings)}):")
    for c in report.capture_warnings:
        print(f"  - {c.source_ref.author}: {c.text[:100]}...")
        print(f"      falsifiable iff: {c.falsifiability_condition[:100]}...")


if __name__ == "__main__":
    main()
