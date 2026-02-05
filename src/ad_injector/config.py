"""Qdrant configuration and client setup."""

import os

from dotenv import load_dotenv
from qdrant_client import QdrantClient

load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", "6333"))
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME", "ads")
EMBEDDING_DIMENSION = 384  # BAAI/bge-small-en-v1.5 dimension


def get_qdrant_client() -> QdrantClient:
    """Get a configured Qdrant client for local instance."""
    return QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
