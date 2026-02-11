"""PolicyEngine: non-negotiable post-query filtering.

Semantics: see domain/match_semantics.py.
Policy is enforced after retrieval; filters cannot bypass it.
"""

from __future__ import annotations

import re

from ..models.mcp_requests import MatchConstraints, PlacementContext
from ..ports.vector_store import VectorHit

_WHITESPACE_RE = re.compile(r"\s+")


def _tokenize_context(text: str) -> set[str]:
    """Deterministic tokenization: split on whitespace, lowercase."""
    return {t.lower() for t in _WHITESPACE_RE.split(text.strip()) if t}


class PolicyEngine:
    """Filter vector hits by policy rules.

    Rules:
    1. age_restricted + not age_restricted_ok -> drop
    2. sensitive + not sensitive_ok -> drop
    3. blocked_keywords intersects context_text keywords -> drop (substring or token match)
    """

    def apply(
        self,
        hits: list[VectorHit],
        constraints: MatchConstraints,
        placement: PlacementContext,
        context_text: str = "",
    ) -> list[VectorHit]:
        """Return only hits that pass all policy checks."""
        eligible: list[VectorHit] = []
        for hit in hits:
            if self._allowed(hit, constraints, context_text):
                eligible.append(hit)
        return eligible

    def reason(
        self,
        hit: VectorHit,
        constraints: MatchConstraints,
        placement: PlacementContext,
        context_text: str = "",
    ) -> str:
        """Return audit reason for this hit: 'allowed' or 'denied: <reason>'."""
        meta = hit.payload
        if meta.get("age_restricted", False) and not constraints.age_restricted_ok:
            return "denied: age_restricted"
        if meta.get("sensitive", False) and not constraints.sensitive_ok:
            return "denied: sensitive"
        if self._blocked_keywords_intersect(hit, context_text):
            return "denied: blocked_keywords"
        return "allowed"

    def _allowed(
        self,
        hit: VectorHit,
        constraints: MatchConstraints,
        context_text: str,
    ) -> bool:
        meta = hit.payload
        if meta.get("age_restricted", False) and not constraints.age_restricted_ok:
            return False
        if meta.get("sensitive", False) and not constraints.sensitive_ok:
            return False
        if self._blocked_keywords_intersect(hit, context_text):
            return False
        return True

    def _blocked_keywords_intersect(self, hit: VectorHit, context_text: str) -> bool:
        """True if ad.blocked_keywords intersects context_text tokens (substring or exact)."""
        blocked = hit.payload.get("blocked_keywords") or []
        if not blocked:
            return False
        tokens = _tokenize_context(context_text)
        for kw in blocked:
            kw_lower = kw.lower()
            if kw_lower in tokens:
                return True
            if any(kw_lower in t for t in tokens):
                return True
        return False
