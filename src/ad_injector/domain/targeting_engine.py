"""TargetingEngine: builds typed VectorFilters from MatchConstraints.

Semantics: see domain/match_semantics.py.
"""

from __future__ import annotations

from .filters import FieldFilter, FilterOp, VectorFilter
from ..models.mcp_requests import MatchConstraints, PlacementContext


class TargetingEngine:
    """Translate typed MatchConstraints into a domain VectorFilter.

    Rules (see match_semantics):
    - topics/verticals: any_of (intersection ANY)
    - locale: any_of [constraint, ""] (exact or global)
    - exclusions: always applied when non-empty
    - placement: annotate only, no filter
    """

    def build_filter(
        self,
        constraints: MatchConstraints,
        placement: PlacementContext,
    ) -> VectorFilter:
        must: list[FieldFilter] = []
        must_not: list[FieldFilter] = []

        if constraints.topics:
            must.append(FieldFilter(field="topics", op=FilterOp.any_of, value=constraints.topics))

        if constraints.locale:
            # Match exact or global (""): any_of [X, ""]
            must.append(
                FieldFilter(
                    field="locale",
                    op=FilterOp.any_of,
                    value=[constraints.locale, ""],
                )
            )

        if constraints.verticals:
            must.append(FieldFilter(field="verticals", op=FilterOp.any_of, value=constraints.verticals))

        if constraints.exclude_advertiser_ids:
            must_not.append(
                FieldFilter(
                    field="advertiser_id",
                    op=FilterOp.not_in,
                    value=constraints.exclude_advertiser_ids,
                )
            )

        if constraints.exclude_ad_ids:
            must_not.append(
                FieldFilter(field="ad_id", op=FilterOp.not_in, value=constraints.exclude_ad_ids)
            )

        return VectorFilter(must=must, must_not=must_not)
