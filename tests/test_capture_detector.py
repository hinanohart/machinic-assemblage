"""Capture detector tests."""

from __future__ import annotations

from machinic_assemblage import (
    Critique,
    DeploymentContext,
    SourceRef,
    evaluate_capture,
)


def _ctx(**kwargs):
    base = {
        "operator_org": "x",
        "revenue_model": "none",
        "end_users_consent_uri": "https://example.org/c",
        "used_in_optimization_for": frozenset(),
        "declared_at_iso": "2026-01-01",
        "environmental_kgco2eq_estimate": 0.0,
    }
    base.update(kwargs)
    return DeploymentContext(**base)


def test_no_revenue_no_consent_required():
    ctx = _ctx(revenue_model="none", end_users_consent_uri=None)
    out = evaluate_capture(ctx)
    assert out == ()


def test_ads_without_declared_critique_adds_lazzarato():
    ctx = _ctx(revenue_model="ads", end_users_consent_uri="https://example.org/c")
    out = evaluate_capture(ctx)
    assert any("Lazzarato" in c.source_ref.author for c in out)


def test_ads_with_declared_critique_does_not_duplicate():
    declared = Critique(
        text=(
            "Ad-targeting machinic enslavement is the central capture concern in this "
            "deployment, openly acknowledged."
        ),
        source_ref=SourceRef(
            author="Lazzarato",
            work="Signs and Machines",
            edition="Semiotext(e) 2014",
            pages="ch. 3",
        ),
        falsifiability_condition=(
            "Dissolves when targeting is replaced with explicit per-session opt-in."
        ),
    )
    ctx = _ctx(
        revenue_model="ads",
        end_users_consent_uri="https://example.org/c",
        used_in_optimization_for=frozenset({declared}),
    )
    out = evaluate_capture(ctx)
    assert len(out) == 1
    assert out[0] is declared


def test_data_sale_adds_terranova():
    ctx = _ctx(revenue_model="data_sale", end_users_consent_uri="https://example.org/c")
    out = evaluate_capture(ctx)
    assert any("Terranova" in c.source_ref.author for c in out)


def test_no_consent_with_revenue_adds_guattari():
    ctx = _ctx(revenue_model="subscription", end_users_consent_uri=None)
    out = evaluate_capture(ctx)
    assert any("Guattari" in c.source_ref.author for c in out)


def test_returned_critiques_are_valid_critiques():
    ctx = _ctx(revenue_model="ads", end_users_consent_uri=None)
    out = evaluate_capture(ctx)
    for c in out:
        assert isinstance(c, Critique)
        assert len(c.falsifiability_condition) >= 16
