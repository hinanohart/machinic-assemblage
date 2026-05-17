"""Type validation tests."""

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
    ThreeEcologiesKPI,
    Utterance,
    Vector,
)


class TestNode:
    def test_empty_id_rejected(self):
        with pytest.raises(ValueError, match="id"):
            Node(id=NodeId(""), kind="human")

    def test_empty_kind_rejected(self):
        with pytest.raises(ValueError, match="kind"):
            Node(id=NodeId("a"), kind="")

    def test_whitespace_only_id_rejected(self):
        """v0.1.3 M5: whitespace-only required strings must be rejected like empty."""
        with pytest.raises(ValueError, match=r"Node\.id"):
            Node(id=NodeId("   "), kind="human")

    def test_whitespace_only_kind_rejected(self):
        with pytest.raises(ValueError, match=r"Node\.kind"):
            Node(id=NodeId("a"), kind="\t\n")

    def test_frozen(self):
        n = Node(id=NodeId("a"), kind="human")
        with pytest.raises(Exception):
            n.id = NodeId("b")  # type: ignore[misc]


class TestHeterogeneousEdge:
    def test_empty_members_rejected(self):
        with pytest.raises(ValueError, match="members"):
            HeterogeneousEdge(
                members=frozenset(),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )

    def test_empty_semantic_rejected(self):
        with pytest.raises(ValueError, match="semantic"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a")}),
                semantic="",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
            )

    def test_nan_weight_rejected(self):
        import math

        with pytest.raises(ValueError, match="finite"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
                weight=math.nan,
            )

    def test_inf_weight_rejected(self):
        import math

        with pytest.raises(ValueError, match="finite"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
                weight=math.inf,
            )

    def test_negative_weight_rejected(self):
        with pytest.raises(ValueError, match="weight"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
                weight=-0.1,
            )

    def test_subtract_requires_reason(self):
        with pytest.raises(ValueError, match="subtract_reason"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a"), NodeId("b")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
                subtract=frozenset({NodeId("a")}),
            )

    def test_reason_without_subtract_rejected(self):
        with pytest.raises(ValueError, match="subtract_reason set without subtract"):
            HeterogeneousEdge(
                members=frozenset({NodeId("a")}),
                semantic="x",
                side=Side.CONTENT,
                vector=Vector.TERRITORIAL,
                subtract_reason="some reason",
            )

    def test_distinct_reasons_produce_distinct_edges(self):
        e1 = HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
            subtract=frozenset({NodeId("a")}),
            subtract_reason="reason-A",
        )
        e2 = HeterogeneousEdge(
            members=frozenset({NodeId("a"), NodeId("b")}),
            semantic="x",
            side=Side.CONTENT,
            vector=Vector.TERRITORIAL,
            subtract=frozenset({NodeId("a")}),
            subtract_reason="reason-B",
        )
        assert e1 != e2
        assert {e1, e2} != {e1}


class TestUtterance:
    def test_empty_speaker_rejected(self):
        with pytest.raises(ValueError, match="speaker"):
            Utterance(speaker=NodeId(""), content="x", kind="x", timestamp_iso="2026-01-01")

    def test_empty_kind_rejected(self):
        with pytest.raises(ValueError, match="kind"):
            Utterance(speaker=NodeId("a"), content="x", kind="", timestamp_iso="2026-01-01")


class TestCritique:
    def test_short_text_rejected(self):
        with pytest.raises(ValueError, match="non-trivial"):
            Critique(
                text="too short",
                source_ref=SourceRef(author="Guattari", work="X", edition="Y"),
                falsifiability_condition="enough characters here to pass length check",
            )

    def test_empty_falsifiability_rejected(self):
        with pytest.raises(ValueError, match="falsifiability"):
            Critique(
                text="a sufficient text body for the critique to be considered valid",
                source_ref=SourceRef(author="Guattari", work="X", edition="Y"),
                falsifiability_condition="",
            )

    def test_disallowed_author_rejected(self):
        with pytest.raises(ValueError, match="author"):
            Critique(
                text="a sufficient text body for the critique to be considered valid",
                source_ref=SourceRef(author="Habermas", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_requires_primary_source(self):
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text="a sufficient text body for the critique to be considered valid",
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_primary_source_accepted(self):
        c = Critique(
            text=(
                "a sufficient text body — primary_source: Foucault, Surveiller et Punir, "
                "Gallimard 1975"
            ),
            source_ref=SourceRef(author="<other>", work="X", edition="Y"),
            falsifiability_condition="dissolves if criterion C is publicly demonstrated",
        )
        assert c is not None

    def test_other_author_with_bare_keyword_rejected(self):
        """CRITICAL-1: substring 'primary_source:' alone must not bypass author validation."""
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text="a sufficient text body — primary_source: bad",
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_no_year_rejected(self):
        """CRITICAL-1: 'primary_source:' citation without a 4-digit year is rejected."""
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text=(
                    "a sufficient text body — primary_source: Foucault, "
                    "Surveiller et Punir, Gallimard"
                ),
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_pure_punctuation_rejected(self):
        """v0.1.3 M1 bypass-pin: punctuation-only tokens with a year must be rejected."""
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text="a sufficient text body — primary_source: ##, %%, ^^ 2024",
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_digits_only_tokens_rejected(self):
        """v0.1.3 M1 bypass-pin: digit-only tokens (no letters) must be rejected."""
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text="a sufficient text body — primary_source: 1, 2, 3 9999",
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_whitespace_only_tokens_rejected(self):
        """v0.1.2 bypass-pin: whitespace-only citation tokens must be rejected."""
        with pytest.raises(ValueError, match="primary_source"):
            Critique(
                text="a sufficient text body — primary_source:  ,  ,   1975",
                source_ref=SourceRef(author="<other>", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_other_author_with_single_letter_initial_accepted(self):
        """v0.1.3 F4: legitimate citations with single-letter initials/titles must pass.

        v0.1.2 over-rejected H. Lefebvre-style citations. The v0.1.3 regex requires each
        token to contain at least one letter but allows length 1 — `A` is a real work title.
        """
        c = Critique(
            text=("a sufficient text body — primary_source: H. Lefebvre, A, Pub 1990"),
            source_ref=SourceRef(author="<other>", work="X", edition="Y"),
            falsifiability_condition="dissolves if criterion C is publicly demonstrated",
        )
        assert c is not None

    def test_critique_whitespace_only_text_rejected(self):
        """v0.1.3 M5: whitespace-only text strings must be rejected even at >=16 chars."""
        with pytest.raises(ValueError, match="non-trivial"):
            Critique(
                text=" " * 30,
                source_ref=SourceRef(author="Guattari", work="X", edition="Y"),
                falsifiability_condition="dissolves if criterion C is publicly demonstrated",
            )

    def test_critique_whitespace_only_falsifiability_rejected(self):
        """v0.1.3 M5: whitespace-only falsifiability conditions must be rejected."""
        with pytest.raises(ValueError, match="falsifiability"):
            Critique(
                text="a sufficient text body for the critique to be considered valid",
                source_ref=SourceRef(author="Guattari", work="X", edition="Y"),
                falsifiability_condition="\t" * 20,
            )


class TestDeploymentContext:
    def test_empty_org_rejected(self):
        with pytest.raises(ValueError, match="operator_org"):
            DeploymentContext(
                operator_org="",
                revenue_model="none",
                end_users_consent_uri=None,
                used_in_optimization_for=frozenset(),
                declared_at_iso="2026-01-01",
            )

    def test_invalid_revenue_model_rejected(self):
        with pytest.raises(ValueError, match="revenue_model"):
            DeploymentContext(
                operator_org="x",
                revenue_model="Ads",  # type: ignore[arg-type]
                end_users_consent_uri=None,
                used_in_optimization_for=frozenset(),
                declared_at_iso="2026-01-01",
            )

    def test_negative_kgco2_rejected(self):
        with pytest.raises(ValueError, match="environmental_kgco2eq_estimate"):
            DeploymentContext(
                operator_org="x",
                revenue_model="none",
                end_users_consent_uri=None,
                used_in_optimization_for=frozenset(),
                declared_at_iso="2026-01-01",
                environmental_kgco2eq_estimate=-1.0,
            )


class TestThreeEcologiesKPI:
    @pytest.mark.parametrize("field", ["mental", "social", "environmental"])
    def test_out_of_range_rejected(self, field):
        kwargs = {"mental": 0.5, "social": 0.5, "environmental": 0.5}
        kwargs[field] = 1.5
        with pytest.raises(ValueError, match=field):
            ThreeEcologiesKPI(**kwargs)

    def test_no_composite_attribute(self):
        k = ThreeEcologiesKPI(mental=0.5, social=0.5, environmental=0.5)
        assert not hasattr(k, "composite")
        assert not hasattr(k, "score")
        assert not hasattr(k, "total")

    def test_subclassing_blocked(self):
        """CRITICAL-2: subclasses cannot re-introduce a composite/score via inheritance."""
        with pytest.raises(TypeError, match="may not be subclassed"):

            class CompositeKPI(ThreeEcologiesKPI):
                pass

    def test_subclassing_with_property_blocked(self):
        """CRITICAL-2: even the dangerous case (composite as @property on a subclass) fails."""
        with pytest.raises(TypeError, match="may not be subclassed"):

            class WeightedKPI(ThreeEcologiesKPI):
                @property
                def composite(self) -> float:
                    return 0.5 * self.mental + 0.3 * self.social + 0.2 * self.environmental
