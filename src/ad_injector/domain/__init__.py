"""Domain types shared across the application."""

from .filters import FieldFilter, FilterOp, VectorFilter
from .match_semantics import (
    RULE_EXCLUSIONS_ALWAYS,
    RULE_LOCALE_EXACT_OR_GLOBAL,
    RULE_PLACEMENT_ANNOTATE_ONLY,
    RULE_TOPICS_INTERSECT,
    RULE_VERTICALS_INTERSECT,
)

__all__ = [
    "FieldFilter",
    "FilterOp",
    "VectorFilter",
    "RULE_EXCLUSIONS_ALWAYS",
    "RULE_LOCALE_EXACT_OR_GLOBAL",
    "RULE_PLACEMENT_ANNOTATE_ONLY",
    "RULE_TOPICS_INTERSECT",
    "RULE_VERTICALS_INTERSECT",
]
