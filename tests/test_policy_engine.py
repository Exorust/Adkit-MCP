"""PolicyEngine tests — prevent semantic drift."""

import pytest

from ad_injector.domain.policy_engine import PolicyEngine
from ad_injector.models.mcp_requests import MatchConstraints, PlacementContext
from ad_injector.ports.vector_store import VectorHit


def _make_hit(
    ad_id: str,
    score: float,
    *,
    sensitive: bool = False,
    age_restricted: bool = False,
    blocked_keywords: list[str] | None = None,
    advertiser_id: str = "adv-1",
) -> VectorHit:
    return VectorHit(
        ad_id=ad_id,
        advertiser_id=advertiser_id,
        score=score,
        payload={
            "ad_id": ad_id,
            "advertiser_id": advertiser_id,
            "title": f"Title {ad_id}",
            "body": f"Body {ad_id}",
            "cta_text": "Click",
            "landing_url": f"https://example.com/{ad_id}",
            "topics": ["tech"],
            "locale": ["en-US"],
            "verticals": ["technology"],
            "blocked_keywords": blocked_keywords or [],
            "sensitive": sensitive,
            "age_restricted": age_restricted,
        },
    )


class TestPolicySensitiveGating:
    """Sensitive: default deny, allow when sensitive_ok."""

    def test_sensitive_filtered_by_default(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-ok", 0.9), _make_hit("ad-sens", 0.8, sensitive=True)]
        constraints = MatchConstraints()
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement)
        ids = [h.ad_id for h in result]
        assert "ad-ok" in ids
        assert "ad-sens" not in ids

    def test_sensitive_allowed_when_opted_in(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-sens", 0.8, sensitive=True)]
        constraints = MatchConstraints(sensitive_ok=True)
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement)
        assert len(result) == 1
        assert result[0].ad_id == "ad-sens"


class TestPolicyAgeRestrictedGating:
    """Age-restricted: default deny, allow when age_restricted_ok."""

    def test_age_restricted_filtered_by_default(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-ok", 0.9), _make_hit("ad-age", 0.8, age_restricted=True)]
        constraints = MatchConstraints()
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement)
        ids = [h.ad_id for h in result]
        assert "ad-ok" in ids
        assert "ad-age" not in ids

    def test_age_restricted_allowed_when_opted_in(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-age", 0.8, age_restricted=True)]
        constraints = MatchConstraints(age_restricted_ok=True)
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement)
        assert len(result) == 1
        assert result[0].ad_id == "ad-age"


class TestPolicyBlockedKeywords:
    """Blocked keywords vs context_text (token/substring match)."""

    def test_blocked_keyword_in_context_drops_ad(self):
        engine = PolicyEngine()
        hits = [
            _make_hit("ad-ok", 0.9),
            _make_hit("ad-blocked", 0.8, blocked_keywords=["gambling"]),
        ]
        constraints = MatchConstraints()
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement, context_text="I want gambling tips")
        ids = [h.ad_id for h in result]
        assert "ad-ok" in ids
        assert "ad-blocked" not in ids

    def test_blocked_keyword_substring_drops_ad(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-blocked", 0.8, blocked_keywords=["gamb"])]
        constraints = MatchConstraints()
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement, context_text="gambling games")
        assert len(result) == 0

    def test_no_blocked_keywords_in_context_passes(self):
        engine = PolicyEngine()
        hits = [_make_hit("ad-ok", 0.9, blocked_keywords=["gambling"])]
        constraints = MatchConstraints()
        placement = PlacementContext()
        result = engine.apply(hits, constraints, placement, context_text="python tutorial")
        assert len(result) == 1
