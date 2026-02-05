"""Embedding service using FastEmbed for local embeddings."""

import numpy as np
from fastembed import TextEmbedding


# Lazy-loaded model instance
_model: TextEmbedding | None = None


def get_embedding_model() -> TextEmbedding:
    """Get or initialize the FastEmbed model (lazy loading).
    
    Returns:
        Initialized TextEmbedding model instance (defaults to BAAI/bge-small-en-v1.5)
    """
    global _model
    if _model is None:
        # Default model is BAAI/bge-small-en-v1.5 (384 dimensions)
        _model = TextEmbedding()
    return _model


def generate_embedding(text: str) -> list[float]:
    """Generate embedding vector for the given text.
    
    Args:
        text: Text to embed
        
    Returns:
        Embedding vector as list of floats (384 dimensions)
    """
    model = get_embedding_model()
    # FastEmbed.embed() returns a generator that yields numpy arrays
    # For a single text, we get one embedding
    embedding = next(model.embed([text]))
    # Convert numpy array to list of floats
    return embedding.tolist()
