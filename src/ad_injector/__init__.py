"""Ad injector application package."""

from .models import Ad, AdPolicy, AdTargeting
from .qdrant_service import (
    create_collection,
    delete_ad,
    delete_collection,
    get_collection_info,
    query_ads,
    upsert_ad,
    upsert_ads,
)

__version__ = "0.1.0"
__all__ = [
    "Ad",
    "AdPolicy",
    "AdTargeting",
    "create_collection",
    "delete_collection",
    "upsert_ad",
    "upsert_ads",
    "query_ads",
    "delete_ad",
    "get_collection_info",
]
