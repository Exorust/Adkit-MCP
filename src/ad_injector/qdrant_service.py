"""Qdrant service for ad storage and retrieval."""

from qdrant_client.models import Distance, PointStruct, VectorParams

from .config import COLLECTION_NAME, EMBEDDING_DIMENSION, get_qdrant_client
from .models import Ad


def create_collection(dimension: int = EMBEDDING_DIMENSION) -> None:
    """Create the Qdrant collection if it doesn't exist.

    Args:
        dimension: Embedding vector dimension (default: 1536 for OpenAI embeddings)
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
    client = get_qdrant_client()
    info = client.get_collection(COLLECTION_NAME)
    return {
        "name": COLLECTION_NAME,
        "vectors_count": info.vectors_count,
        "points_count": info.points_count,
        "status": info.status,
    }
