import logging
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

# nomic-embed-text produces 768-dimensional vectors
EMBEDDING_DIM = 768


def get_ollama_embed_client():
    """Return a shared Ollama client for embedding requests."""
    global _ollama_embed_client
    if _ollama_embed_client is None:
        _ollama_embed_client = Client(host=settings.OLLAMA_BASE_URL)
        logger.info(
            'Ollama embedding client configured for %s (model: %s)',
            settings.OLLAMA_BASE_URL,
            settings.OLLAMA_EMBED_MODEL,
        )
    return _ollama_embed_client


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a list of texts using Ollama nomic-embed-text."""
    client = get_ollama_embed_client()
    response = client.embed(
        model=settings.OLLAMA_EMBED_MODEL,
        input=texts,
    )
    return response['embeddings']


def embed_query(query: str) -> list[float]:
    """Embed a single query string."""
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

    If an existing collection has the wrong vector size (e.g. 384 from a
    previous embedding model), it is deleted and recreated with the
    correct dimensions for nomic-embed-text (768).
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
                'Collection "%s" has vector size %d, expected %d. Recreating...',
                collection_name,
                existing_size,
                EMBEDDING_DIM,
            )
            client.delete_collection(collection_name)
        else:
            logger.info('Qdrant collection "%s" already exists with correct dimensions.', collection_name)
            return

    client.create_collection(
        collection_name=collection_name,
        vectors_config=VectorParams(
            size=EMBEDDING_DIM,  # nomic-embed-text output dimension
            distance=Distance.COSINE,
        ),
    )
    logger.info('Created Qdrant collection: %s (dim=%d)', collection_name, EMBEDDING_DIM)


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
