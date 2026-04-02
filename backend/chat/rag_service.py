import logging
import math
from typing import List

from django.conf import settings
from ollama import Client
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    PointStruct,
    VectorParams,
)

logger = logging.getLogger(__name__)

# Global instances (lazy loaded)
_ollama_embed_client = None
_qdrant_client = None

# Matryoshka Representation Learning (MRL) Configuration
# nomic-embed-text produces 768-dimensional vectors, but supports MRL
# We truncate to 256 dimensions for faster search with minimal quality loss
FULL_EMBEDDING_DIM = 768  # Original dimension from nomic-embed-text
MRL_EMBEDDING_DIM = 256   # Truncated dimension for MRL
EMBEDDING_DIM = MRL_EMBEDDING_DIM  # Active dimension used in Qdrant


def get_ollama_embed_client():
    """Return a shared Ollama client for embedding requests."""
    global _ollama_embed_client
    if _ollama_embed_client is None:
        _ollama_embed_client = Client(host=settings.OLLAMA_BASE_URL)
        logger.info(
            'Ollama embedding client configured for %s (model: %s, MRL dim: %d)',
            settings.OLLAMA_BASE_URL,
            settings.OLLAMA_EMBED_MODEL,
            MRL_EMBEDDING_DIM,
        )
    return _ollama_embed_client


def normalize_vector(vector: list[float]) -> list[float]:
    """L2 normalize a vector for cosine similarity."""
    norm = math.sqrt(sum(x * x for x in vector))
    if norm == 0:
        return vector
    return [x / norm for x in vector]


def apply_mrl(embeddings: list[list[float]], target_dim: int = MRL_EMBEDDING_DIM) -> list[list[float]]:
    """Apply Matryoshka Representation Learning by truncating and normalizing vectors.
    
    MRL-trained models (like nomic-embed-text) produce embeddings where the first N
    dimensions capture the most important semantic information. By truncating to a
    smaller dimension and re-normalizing, we get compact vectors that retain most
    of the original quality.
    
    Args:
        embeddings: List of full-dimensional embedding vectors
        target_dim: Target dimension to truncate to (default: 256)
    
    Returns:
        List of truncated and normalized embedding vectors
    """
    truncated = []
    for emb in embeddings:
        # Truncate to first target_dim dimensions
        truncated_emb = emb[:target_dim]
        # Re-normalize for cosine similarity
        normalized_emb = normalize_vector(truncated_emb)
        truncated.append(normalized_emb)
    return truncated


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Ollama nomic-embed-text with MRL truncation."""
    client = get_ollama_embed_client()
    response = client.embed(
        model=settings.OLLAMA_EMBED_MODEL,
        input=texts,
    )
    full_embeddings = response['embeddings']
    # Apply MRL: truncate to 256 dimensions and normalize
    return apply_mrl(full_embeddings, MRL_EMBEDDING_DIM)


def embed_query(query: str) -> list[float]:
    """Embed a single query string with MRL truncation."""
    vectors = embed_texts([query])
    return vectors[0]


def get_qdrant():
    global _qdrant_client
    if _qdrant_client is None:
        _qdrant_client = QdrantClient(
            host=settings.QDRANT_HOST,
            port=settings.QDRANT_PORT,
            check_compatibility=False,
        )
        logger.info('Connected to Qdrant at %s:%s', settings.QDRANT_HOST, settings.QDRANT_PORT)
    return _qdrant_client


def ensure_collection():
    """Create the Qdrant collection if it doesn't already exist.

    Uses Matryoshka Representation Learning (MRL) with 256 dimensions
    instead of the full 768 dimensions from nomic-embed-text. This provides:
    - ~3x faster similarity search
    - ~3x less memory usage
    - Minimal quality degradation (MRL-trained models preserve semantics)
    
    If an existing collection has the wrong vector size, it is deleted
    and recreated with the correct MRL dimensions.
    """
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION
    collections = [c.name for c in client.get_collections().collections]

    if collection_name in collections:
        # Verify the vector size matches
        info = client.get_collection(collection_name)
        existing_size = info.config.params.vectors.size
        if existing_size != EMBEDDING_DIM:
            logger.warning(
                'Collection "%s" has vector size %d, expected %d (MRL). Recreating...',
                collection_name,
                existing_size,
                EMBEDDING_DIM,
            )
            client.delete_collection(collection_name)
        else:
            logger.info('Qdrant collection "%s" already exists with correct MRL dimensions (%d).', collection_name, EMBEDDING_DIM)
            return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,  # MRL truncated dimension (256)
            distance=Distance.COSINE,
        ),
    )
    logger.info('Created Qdrant collection: %s (MRL dim=%d)', collection_name, EMBEDDING_DIM)


def ingest_documents(documents: list[dict]):
    """Ingest a list of documents into Qdrant.

    Each document should have:
      - id: unique int
      - title: str
      - content: str  (the text that will be embedded)
      - metadata: dict (extra payload stored alongside)
    """
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION

    texts = [d['content'] for d in documents]
    embeddings = embed_texts(texts)

    points = [
        PointStruct(
            id=doc['id'],
            vector=emb,
            payload={
                'title': doc.get('title', ''),
                'content': doc['content'],
                **doc.get('metadata', {}),
            },
        )
        for doc, emb in zip(documents, embeddings)
    ]

    client.upsert(collection_name=collection_name, points=points)
    logger.info('Ingested %d documents into Qdrant.', len(points))


def search_similar(query: str, top_k: int = 3) -> List[dict]:
    """Return the top_k most relevant documents for the given query."""
    client = get_qdrant()
    collection_name = settings.QDRANT_COLLECTION

    query_vector = embed_query(query)

    results = client.query_points(
        collection_name=collection_name,
        query=query_vector,
        limit=top_k,
    )

    docs = []
    for hit in results.points:
        docs.append({
            'id': hit.id,
            'score': hit.score,
            'title': hit.payload.get('title', ''),
            'content': hit.payload.get('content', ''),
            'category': hit.payload.get('category', ''),
            'severity': hit.payload.get('severity', ''),
            'resolution': hit.payload.get('resolution', ''),
        })
    return docs
