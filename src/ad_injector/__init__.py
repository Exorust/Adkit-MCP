"""Ad injector application package."""

from .models import Ad, AdPolicy, AdTargeting
from .qdrant_service import (
    get_collection_info,
    match_ads,
)

__version__ = "0.1.0"
__all__ = [
    "Ad",
    "AdPolicy",
    "AdTargeting",
    "match_ads",
    "get_collection_info",
]
