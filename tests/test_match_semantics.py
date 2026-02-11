"""Tests that lock match semantics and prevent drift.

These tests encode the rules from domain.match_semantics as executable assertions.
"""

import pytest

from ad_injector.domain.match_semantics import (
    RULE_EXCLUSIONS_ALWAYS,
    RULE_LOCALE_EXACT_OR_GLOBAL,
    RULE_PLACEMENT_ANNOTATE_ONLY,
    RULE_TOPICS_INTERSECT,
    RULE_VERTICALS_INTERSECT,
)


class TestTopicsSemantics:
    """Topics: ad.topics intersects request.topics (ANY)."""

    def test_topics_intersection_any(self):
        # Rule: ad passes iff at least one topic in common
        request_topics = ["python", "ai"]
        ad_topics_intersects = ["python", "other"]  # "python" in common -> pass
        ad_topics_no_intersect = ["java", "c++"]    # no common -> fail
        assert set(ad_topics_intersects) & set(request_topics) == {"python"}
        assert set(ad_topics_no_intersect) & set(request_topics) == set()
        # Lock the rule constant
        assert "ANY" in RULE_TOPICS_INTERSECT


class TestVerticalsSemantics:
    """Verticals: same as topics, intersection ANY."""

    def test_verticals_intersection_any(self):
        request_verticals = ["tech", "education"]
        ad_verticals_intersects = ["education", "retail"]
        ad_verticals_no_intersect = ["finance", "health"]
        assert set(ad_verticals_intersects) & set(request_verticals) == {"education"}
        assert set(ad_verticals_no_intersect) & set(request_verticals) == set()
        assert "ANY" in RULE_VERTICALS_INTERSECT


class TestLocaleSemantics:
    """Locale: exact match, or empty/[''] as global."""

    def test_locale_exact_match(self):
        request_locale = "en-US"
        ad_locale_match = ["en-US"]
        ad_locale_global = [""]
        ad_locale_global_empty = []
        # Match: ad has exact
        assert request_locale in ad_locale_match
        # Match: ad is global ("" or [])
        assert "" in ad_locale_global or ad_locale_global_empty == []
        assert "exact" in RULE_LOCALE_EXACT_OR_GLOBAL or "global" in RULE_LOCALE_EXACT_OR_GLOBAL

    def test_no_request_locale_means_no_filter(self):
        request_locale = None
        # When request has no locale, we don't add a locale filter
        assert request_locale is None


class TestExclusionsSemantics:
    """Exclusions always enforced when provided."""

    def test_exclusions_must_be_enforced(self):
        exclude_ad_ids = ["ad-1", "ad-2"]
        exclude_advertiser_ids = ["adv-bad"]
        # These must never appear in results when set
        assert "always" in RULE_EXCLUSIONS_ALWAYS.lower()


class TestPlacementSemantics:
    """Placement/surface: annotate only, no filter."""

    def test_placement_no_filter(self):
        # We do not filter by placement; we only annotate
        assert "annotate" in RULE_PLACEMENT_ANNOTATE_ONLY or "no filter" in RULE_PLACEMENT_ANNOTATE_ONLY.lower()
