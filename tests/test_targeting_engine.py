"""TargetingEngine tests — prevent semantic drift."""

import pytest

from ad_injector.domain.filters import FieldFilter, FilterOp, VectorFilter
from ad_injector.domain.targeting_engine import TargetingEngine
from ad_injector.models.mcp_requests import MatchConstraints, PlacementContext


def _build_filter(**constraint_kwargs) -> VectorFilter:
    engine = TargetingEngine()
    constraints = MatchConstraints(**constraint_kwargs)
    placement = PlacementContext(placement="inline", surface="chat")
    return engine.build_filter(constraints, placement)


class TestTargetingEngineLocale:
    """Locale match + global fallback (any_of [X, ''])."""

    def test_locale_includes_global_fallback(self):
        vf = _build_filter(locale="en-US")
        locale_filters = [f for f in vf.must if f.field == "locale"]
        assert len(locale_filters) == 1
        assert locale_filters[0].op == FilterOp.any_of
        assert set(locale_filters[0].value) == {"en-US", ""}

    def test_no_locale_constraint_means_no_locale_filter(self):
        vf = _build_filter()
        locale_filters = [f for f in vf.must if f.field == "locale"]
        assert len(locale_filters) == 0


class TestTargetingEngineTopicsVerticals:
    """Topics/verticals: any_of (intersection ANY)."""

    def test_topics_adds_any_of_filter(self):
        vf = _build_filter(topics=["python", "ai"])
        topic_filters = [f for f in vf.must if f.field == "topics"]
        assert len(topic_filters) == 1
        assert topic_filters[0].op == FilterOp.any_of
        assert topic_filters[0].value == ["python", "ai"]

    def test_verticals_adds_any_of_filter(self):
        vf = _build_filter(verticals=["tech", "education"])
        vert_filters = [f for f in vf.must if f.field == "verticals"]
        assert len(vert_filters) == 1
        assert vert_filters[0].op == FilterOp.any_of
        assert vert_filters[0].value == ["tech", "education"]


class TestTargetingEngineExclusions:
    """Exclude lists always applied when non-empty."""

    def test_exclude_advertiser_ids_adds_must_not(self):
        vf = _build_filter(exclude_advertiser_ids=["bad-adv"])
        adv_filters = [f for f in vf.must_not if f.field == "advertiser_id"]
        assert len(adv_filters) == 1
        assert adv_filters[0].op == FilterOp.not_in
        assert adv_filters[0].value == ["bad-adv"]

    def test_exclude_ad_ids_adds_must_not(self):
        vf = _build_filter(exclude_ad_ids=["bad-ad-1"])
        ad_filters = [f for f in vf.must_not if f.field == "ad_id"]
        assert len(ad_filters) == 1
        assert ad_filters[0].op == FilterOp.not_in
        assert ad_filters[0].value == ["bad-ad-1"]

    def test_both_exclusions_when_provided(self):
        vf = _build_filter(
            exclude_advertiser_ids=["adv-1"],
            exclude_ad_ids=["ad-1", "ad-2"],
        )
        assert len(vf.must_not) == 2


class TestTargetingEngineEmptyConstraints:
    """Empty constraints still returns VectorFilter (never None)."""

    def test_empty_constraints_returns_vector_filter(self):
        vf = _build_filter()
        assert isinstance(vf, VectorFilter)
        assert vf.must == []
        assert vf.must_not == []
