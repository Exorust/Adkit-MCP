"""Match semantics — executable rules for targeting and policy.

These constants and docstrings lock the semantics. Tests in test_match_semantics.py
encode these as assertions to prevent accidental drift.

RULES (must never be ambiguous):
--------------------------------

1. TOPICS MATCHING
   If request has topics, require: ad.targeting.topics intersects request.topics (ANY match).
   Ad passes iff at least one of its topics is in the request topics.

2. VERTICALS MATCHING
   Same as topics: require intersection ANY.
   Ad passes iff at least one of its verticals is in the request verticals.

3. LOCALE RULE
   Exact match, or allow empty locale as "global" (ad targets everyone).
   - If request has locale X: ad must have locale containing X, or locale empty/[""] (global).
   - If request has no locale: any ad matches (no filter applied).
   - Convention: global ads use locale=[""] or locale=[].

4. EXCLUSIONS
   exclude_ad_ids and exclude_advertiser_ids must ALWAYS be enforced when provided.
   These are hard filters; no ad in these lists may appear in results.

5. SURFACE/PLACEMENT
   We annotate only; no filtering by placement or surface.
"""

# Rule names for reference in tests and audit
RULE_TOPICS_INTERSECT = "topics: ad.topics intersects request.topics (ANY)"
RULE_VERTICALS_INTERSECT = "verticals: ad.verticals intersects request.verticals (ANY)"
RULE_LOCALE_EXACT_OR_GLOBAL = "locale: exact match or empty/'' as global"
RULE_EXCLUSIONS_ALWAYS = "exclusions: exclude_ad_ids, exclude_advertiser_ids always enforced"
RULE_PLACEMENT_ANNOTATE_ONLY = "placement: annotate only, no filter"
