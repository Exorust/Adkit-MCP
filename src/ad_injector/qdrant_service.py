"""Qdrant service for ad storage and retrieval."""

import os
from pathlib import Path

from qdrant_client.models import Distance, PointStruct, VectorParams

from .config import COLLECTION_NAME, EMBEDDING_DIMENSION, get_qdrant_client
from .embedding_service import generate_embedding
from .models import Ad

# Debug log path - relative to workspace root
_DEBUG_LOG_PATH = Path(__file__).parent.parent.parent / ".cursor" / "debug.log"


def create_collection(dimension: int = EMBEDDING_DIMENSION) -> None:
    """Create the Qdrant collection if it doesn't exist.

    Args:
        dimension: Embedding vector dimension (default: 384 for BAAI/bge-small-en-v1.5)
    """
    client = get_qdrant_client()
    collections = [c.name for c in client.get_collections().collections]

    if COLLECTION_NAME not in collections:
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=dimension, distance=Distance.COSINE),
        )
        print(f"Created collection: {COLLECTION_NAME}")
    else:
        print(f"Collection already exists: {COLLECTION_NAME}")


def delete_collection() -> None:
    """Delete the Qdrant collection."""
    client = get_qdrant_client()
    client.delete_collection(COLLECTION_NAME)
    print(f"Deleted collection: {COLLECTION_NAME}")


def upsert_ad(ad: Ad, embedding: list[float]) -> None:
    """Upsert a single ad into Qdrant.

    Args:
        ad: The ad to upsert
        embedding: The embedding vector for the ad
    """
    client = get_qdrant_client()
    client.upsert(
        collection_name=COLLECTION_NAME,
        points=[
            PointStruct(
                id=ad.ad_id,
                vector=embedding,
                payload=ad.to_pinecone_metadata(),  # Reusing the same metadata format
            )
        ],
    )


def upsert_ads(ads: list[tuple[Ad, list[float]]]) -> None:
    """Upsert multiple ads into Qdrant.

    Args:
        ads: List of (ad, embedding) tuples
    """
    client = get_qdrant_client()
    points = [
        PointStruct(
            id=ad.ad_id,
            vector=embedding,
            payload=ad.to_pinecone_metadata(),
        )
        for ad, embedding in ads
    ]
    client.upsert(collection_name=COLLECTION_NAME, points=points)


def query_ads(
    embedding: list[float],
    top_k: int = 10,
    filter_dict: dict | None = None,
) -> list[dict]:
    """Query ads by embedding similarity.

    Args:
        embedding: Query embedding vector
        top_k: Number of results to return
        filter_dict: Optional Qdrant filter conditions

    Returns:
        List of matching ads with scores
    """
    client = get_qdrant_client()
    results = client.search(
        collection_name=COLLECTION_NAME,
        query_vector=embedding,
        limit=top_k,
        query_filter=filter_dict,
    )
    return [
        {
            "id": hit.id,
            "score": hit.score,
            "metadata": hit.payload,
        }
        for hit in results
    ]


def delete_ad(ad_id: str) -> None:
    """Delete an ad from Qdrant.

    Args:
        ad_id: The ID of the ad to delete
    """
    client = get_qdrant_client()
    client.delete(
        collection_name=COLLECTION_NAME,
        points_selector=[ad_id],
    )


def get_collection_info() -> dict:
    """Get information about the Qdrant collection.

    Returns:
        Collection info including vector count
    """
    # #region agent log
    import json
    import time
    _DEBUG_LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(_DEBUG_LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A", "location": "qdrant_service.py:125", "message": "get_collection_info entry", "data": {"collection_name": COLLECTION_NAME}, "timestamp": time.time() * 1000}) + "\n")
    # #endregion
    client = get_qdrant_client()
    info = client.get_collection(COLLECTION_NAME)
    # #region agent log
    with open(_DEBUG_LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "A,B,C,D,E", "location": "qdrant_service.py:131", "message": "info object type and attributes", "data": {"type": str(type(info)), "dir": [x for x in dir(info) if not x.startswith('_')], "hasattr_vectors_count": hasattr(info, 'vectors_count'), "hasattr_points_count": hasattr(info, 'points_count'), "hasattr_status": hasattr(info, 'status')}, "timestamp": time.time() * 1000}) + "\n")
    # #endregion
    # #region agent log
    try:
        points_count_val = info.points_count
    except Exception as e:
        points_count_val = f"ERROR: {e}"
    with open(_DEBUG_LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "B", "location": "qdrant_service.py:137", "message": "points_count access test", "data": {"points_count": str(points_count_val)}, "timestamp": time.time() * 1000}) + "\n")
    # #endregion
    # #region agent log
    try:
        status_val = info.status
    except Exception as e:
        status_val = f"ERROR: {e}"
    with open(_DEBUG_LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "C", "location": "qdrant_service.py:144", "message": "status access test", "data": {"status": str(status_val)}, "timestamp": time.time() * 1000}) + "\n")
    # #endregion
    # #region agent log
    try:
        if hasattr(info, 'result'):
            result_attrs = [x for x in dir(info.result) if not x.startswith('_')]
            result_has_vectors = hasattr(info.result, 'vectors_count')
        else:
            result_attrs = None
            result_has_vectors = False
    except Exception as e:
        result_attrs = f"ERROR: {e}"
        result_has_vectors = False
    with open(_DEBUG_LOG_PATH, 'a') as f:
        f.write(json.dumps({"sessionId": "debug-session", "runId": "run1", "hypothesisId": "D", "location": "qdrant_service.py:152", "message": "nested result attribute check", "data": {"has_result": hasattr(info, 'result'), "result_attrs": result_attrs, "result_has_vectors_count": result_has_vectors}, "timestamp": time.time() * 1000}) + "\n")
    # #endregion
    return {
        "name": COLLECTION_NAME,
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "status": info.status,
    }


def match_ads(text: str, top_k: int = 10) -> list[dict]:
    """Match ads by text query (read-only, safe wrapper).
    
    This is a safe wrapper around query_ads that:
    - Accepts text instead of embedding vectors
    - Generates embeddings internally
    - Explicitly disables filter_dict to prevent abuse
    
    Args:
        text: Text query to match against ads
        top_k: Number of results to return (default: 10)
        
    Returns:
        List of matching ads with scores and metadata
    """
    embedding = generate_embedding(text)
    # Explicitly pass filter_dict=None to prevent any filtering
    return query_ads(embedding=embedding, top_k=top_k, filter_dict=None)
