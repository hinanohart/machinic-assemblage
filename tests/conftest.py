"""Shared fixtures."""

from __future__ import annotations

import pytest

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
    record_utterance,
)


@pytest.fixture()
def simple_assemblage():
    nodes = [
        Node(id=NodeId("alice"), kind="human"),
        Node(id=NodeId("bob"), kind="human"),
        Node(id=NodeId("agent-1"), kind="agent"),
        Node(id=NodeId("ds-medical"), kind="dataset"),
    ]
    edges = [
        HeterogeneousEdge(
            members=frozenset({NodeId("alice"), NodeId("bob"), NodeId("agent-1")}),
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
            semantic="lookup",
            side=Side.CONTENT,
            vector=Vector.DETERRITORIAL,
        ),
    ]
    return build_assemblage(nodes, edges)


@pytest.fixture()
def minimal_context():
    return DeploymentContext(
        operator_org="example-research-collective",
        revenue_model="none",
        end_users_consent_uri="https://example.org/consent/v1",
        used_in_optimization_for=frozenset(),
        declared_at_iso="2026-05-17T00:00:00+00:00",
        environmental_kgco2eq_estimate=2.5,
    )


@pytest.fixture()
def sample_history():
    return (
        record_utterance(
            NodeId("alice"), "I want to amend the rule.", "rule_change", "2026-05-17T01:00:00+00:00"
        ),
        record_utterance(NodeId("bob"), "Agreed.", "witness", "2026-05-17T01:01:00+00:00"),
        record_utterance(NodeId("alice"), "Done.", "rule_change", "2026-05-17T01:05:00+00:00"),
    )


@pytest.fixture()
def lazzarato_critique():
    return Critique(
        text=(
            "This deployment optimises engagement-time, which Lazzarato 2014 names "
            "as the asymmetric semiotic capture of attention."
        ),
        source_ref=SourceRef(
            author="Lazzarato",
            work="Signs and Machines",
            edition="Semiotext(e) 2014",
            pages="ch. 3",
        ),
        falsifiability_condition=(
            "Dissolves if engagement-time is replaced with task-completion as the "
            "primary objective and the change is documented publicly."
        ),
    )
